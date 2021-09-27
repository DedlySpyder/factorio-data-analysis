import re
import subprocess

START_MOD_PARSING_FLAG = '<<START - FactorioDataRawDump>>'
END_MOD_PARSING_FLAG = '<<DONE - FactorioDataRawDump>>'
START_SUB_STAGE_PARSING_FLAG = '<<START>>'
END_SUB_STAGE_PARSING_FLAG = '<<DONE>>'
START_PROTOTYPE_FLAG = 'FactorioDataAnalysisPrototypeStart('
END_PROTOTYPE_FLAG = ')FactorioDataAnalysisPrototypeEnd'

SUB_STAGE_PATTERN = re.compile(r'.*<<START>><<(.*)>><<(.*)>>')
PROTOTYPE_PATTERN = re.compile(r'.*FactorioDataRawDump\(<<(.*?)>>,<<(.*?)>>,<<(.*?)>>\)', re.MULTILINE | re.DOTALL)


# TODO - perf - future - parse while Factorio is running
class DataParser:
    parsing = False
    sub_stage_parsing = False
    open_prototype = False
    prototype = ''

    mod_name = 'Uninitialized'
    data_stage = 'Uninitialized'

    # Debug is some extra printing, trace is very noisy
    def __init__(self, output_dir, debug=False, trace=False):
        self.output_dir = output_dir
        self.debug = debug
        self.trace = trace

    def d_print(self, *args, **kwargs):
        if self.debug:
            print(*args, **kwargs)

    def t_print(self, *args, **kwargs):
        if self.trace:
            print(*args, **kwargs)

    # Any work before the mod parsing starts
    def start_parsing(self):
        raise NotImplementedError("Start parsing method not implemented")

    # Any work after parsing the sub stage start line (mod_name and data_stage will be populated here)
    def start_sub_stage(self):
        raise NotImplementedError("Start sub stage method not implemented")

    # Any work after parsing is complete for each sub stage
    def end_sub_stage(self):
        raise NotImplementedError("End sub stage method not implemented")

    # Any work after parsing is complete for all sub stages
    def end_parsing(self):
        raise NotImplementedError("End parsing method not implemented")

    def parse_sub_stage_start(self, line):
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

    def parse_lines(self, lines):
        for line in lines:
            if self.parsing:
                if self.sub_stage_parsing:
                    if self.open_prototype:
                        self.prototype += line
                        if END_PROTOTYPE_FLAG in line:
                            self.open_prototype = False
                            self.parse_prototype(self.prototype)
                    else:
                        if END_SUB_STAGE_PARSING_FLAG in line:
                            print(f'Ending sub stage parsing for mod {self.mod_name}, in data stage {self.data_stage}')
                            self.sub_stage_parsing = False
                            self.end_sub_stage()

                        elif START_PROTOTYPE_FLAG in line:
                            self.open_prototype = True
                            self.prototype = line
                else:
                    if START_SUB_STAGE_PARSING_FLAG in line:
                        self.t_print(f'Starting sub stage parsing for line: {line}')
                        self.sub_stage_parsing = True
                        self.parse_sub_stage_start(line)
                        self.start_sub_stage()

                    elif END_MOD_PARSING_FLAG in line:
                        self.d_print('Ending parsing mod output')
                        self.parsing = False
                        self.end_parsing()
                        return

            elif START_MOD_PARSING_FLAG in line:
                self.d_print('Starting mod output parsing')
                self.parsing = True
                self.start_parsing()


class FinalDataParser(DataParser):
    def __init__(self, output_dir, **kwargs):
        DataParser.__init__(self, output_dir, **kwargs)

    def _stub(self):
        return
    start_parsing = _stub
    start_sub_stage = _stub
    end_sub_stage = _stub
    end_parsing = _stub


class DiffDataParser(DataParser):
    def __init__(self, output_dir, **kwargs):
        DataParser.__init__(self, output_dir, **kwargs)

    def _run_git(self, *args, fail_on_err=True):
        args = [str(a) for a in list(args)]
        self.d_print('Running git with args:', args)
        proc = subprocess.Popen(
            ['git'] + list(args),
            cwd=self.output_dir,
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
        print(f'Initializing git in output directory')
        self._run_git('init')
        self._run_git('config', '--local', 'user.email', 'you@example.com')
        self._run_git('config', '--local', 'user.name', 'You')
        self._run_git('add', '.')
        self._run_git(
            'commit',
            '-m', f'Empty data_raw',
            fail_on_err=False
        )

    def start_sub_stage(self):
        return

    def end_sub_stage(self):
        self._run_git('add', '.')
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

    def end_parsing(self):
        return
