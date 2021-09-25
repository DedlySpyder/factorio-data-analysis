import datetime
import re
import subprocess

START_MOD_PARSING_FLAG = '<<START - FactorioDataRawDump>>'
END_MOD_PARSING_FLAG = '<<DONE - FactorioDataRawDump>>'
START_SUB_STAGE_PARSING_FLAG = '<<START>>'
END_SUB_STAGE_PARSING_FLAG = '<<DONE>>'

SUB_STAGE_PATTERN = re.compile(r'.*<<START>><<(.*)>><<(.*)>>')
PROTOTYPE_PATTERN = re.compile(r'.*FactorioDataRawDump\(<<(.*?)>>,<<(.*?)>>,<<(.*?)>>\)', re.MULTILINE | re.DOTALL)


def git_stub(self, *args, fail_on_err=True):
    return 0, ''


# TODO - perf - future - parse while Factorio is running
class Data_Parser:
    parsing = False
    sub_stage_parsing = False
    open_prototype = False
    prototype = ''

    mod_name = 'Uninitialized'
    data_stage = 'Uninitialized'

    # Debug is some extra printing, trace is very noisy
    def __init__(self, output_dir, debug=False, trace=False, skip_git=False):
        self.output_dir = output_dir

        self.debug = debug
        self.trace = trace

        self.skip_git = skip_git
        if skip_git:
            self._run_git = git_stub

    def d_print(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def t_print(self, *args, **kwargs):
        if self.trace:
            print(*args, **kwargs)

    def _run_git(self, *args, fail_on_err=True):
        args = [str(a) for a in list(args)]
        self.d_print('Running git with args:', args)
        proc = subprocess.Popen(
            ['git'] + list(args),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        self.t_print('Git stdout:')
        stdout = []
        for line in iter(proc.stdout.readline, None):
            if not line:
                break
            line = line.decode('utf-8')
            stdout.append(line)
            self.t_print(line, end='')
        proc.wait()

        if proc.returncode > 0:
            if fail_on_err:
                print('Git stderr:')
                print(proc.stderr.read().decode('utf-8'))
                raise RuntimeError('ERROR: Git command failed to run')
            else:
                self.d_print('Git command failed (not failing), stderr:', proc.stderr.read().decode('utf-8'))
                output = ''.join(stdout)
                self.d_print('stdout:', output)
                return proc.returncode, output
        return 0, ''

    def start_parsing(self):
        self.d_print('Starting mod output parsing')
        self.parsing = True
        branch_name = f'diff-{datetime.datetime.now().replace(microsecond=0).isoformat().replace(":", "-")}'
        if not self.skip_git:
            print(f'Creating diff branch: {branch_name}')
        self._run_git('checkout', '-b', branch_name)
        self._run_git('add', self.output_dir)
        self._run_git(
            'commit',
            '-m', f'Empty data_raw',
            fail_on_err=False
        )

    def start_sub_stage(self, line):
        self.t_print(f'Starting sub stage parsing for line: {line}')
        self.sub_stage_parsing = True
        matches = SUB_STAGE_PATTERN.match(line)
        if not matches:
            raise RuntimeError(f'Line is invalid for sub stage start: {line}')
        
        self.mod_name = matches[1]
        self.data_stage = matches[2]
        
        print(f'Sub stage parsing started for mod {self.mod_name}, in data stage {self.data_stage}')

    def parse_prototype(self, prototype):
        self.t_print('Parsing prototype for line:', prototype)
        matches = PROTOTYPE_PATTERN.match(prototype)
        if not matches:
            raise RuntimeError(f'Line is invalid for prototype: {prototype}')

        category, name, prototype = matches[1], matches[2], matches[3]
        self.t_print('Parsed prototype:', category, '-', name)
        self.write_prototype(category, name, prototype)

    def write_prototype(self, category, name, prototype):
        path = self.output_dir / category / name
        self.t_print('Writing prototype to', path, '--', category, '-', name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            f.write(prototype)

    def end_sub_stage(self):
        print(f'Ending sub stage parsing for mod {self.mod_name}, in data stage {self.data_stage}')
        self._run_git('add', self.output_dir)
        code, stdout = self._run_git(
            'commit',
            '-m', f'{self.mod_name} changes from {self.data_stage} stage',
            fail_on_err=False
        )
        if code > 0:
            if 'no changes added to commit' in stdout or 'nothing added to commit' in stdout:
                print(f'No changes for {self.mod_name} for {self.data_stage} stage')
            else:
                raise RuntimeError('ERROR: Git commit failed to run with changes')
        self.sub_stage_parsing = False

    def end_parsing(self):
        self.d_print('Ending parsing mod output')

    def parse_lines(self, lines):
        for l in lines:
            if self.parsing:
                if self.sub_stage_parsing:
                    if self.open_prototype:
                        self.prototype += l
                        if '>>)' in l:
                            self.parse_prototype(self.prototype)
                            self.open_prototype = False
                    else:
                        if END_SUB_STAGE_PARSING_FLAG in l:
                            self.end_sub_stage()
                        elif 'FactorioDataRawDump(' in l:
                            self.open_prototype = True
                            self.prototype = l
                else:
                    if START_SUB_STAGE_PARSING_FLAG in l:
                        self.start_sub_stage(l)
                    elif END_MOD_PARSING_FLAG in l:
                        self.end_parsing()

            elif START_MOD_PARSING_FLAG in l:
                self.start_parsing()
