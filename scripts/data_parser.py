import re

START_MOD_PARSING_FLAG = '<<START - FactorioDataRawDump>>'
END_MOD_PARSING_FLAG = '<<DONE - FactorioDataRawDump>>'
START_SUB_STAGE_PARSING_FLAG = '<<START>>'
END_SUB_STAGE_PARSING_FLAG = '<<DONE>>'

SUB_STAGE_PATTERN = re.compile(r'.*<<START>><<(.*)>><<(.*)>>')
PROTOTYPE_PATTERN = re.compile(r'.*FactorioDataRawDump\(<<(.*?)>>,<<(.*?)>>,<<(.*?)>>\)', re.MULTILINE | re.DOTALL)


# TODO - perf - future - parse while Factorio is running
class Data_Parser:
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

    def start_parsing(self):
        self.d_print('Starting parsing mod output')
        self.parsing = True

    def start_sub_stage(self, line):
        self.t_print('Starting parsing sub stage for line:', line)
        self.sub_stage_parsing = True
        matches = SUB_STAGE_PATTERN.match(line)
        if not matches:
            raise RuntimeError('Line is invalid for sub stage start: ' + line)
        
        self.mod_name = matches[1]
        self.data_stage = matches[2]
        
        print('Sub stage started for mod', self.mod_name, ', in data stage', self.data_stage)

    def parse_prototype(self, prototype):
        self.t_print('Parsing prototype for line:', prototype)
        matches = PROTOTYPE_PATTERN.match(prototype)
        if not matches:
            raise RuntimeError('Line is invalid for prototype: ' + prototype)

        category, name, prototype = matches[1], matches[2], matches[3]
        self.t_print('Parsed prototype:', category, ' - ', name)
        self.write_prototype(category, name, prototype)

    def write_prototype(self, category, name, prototype):
        path = self.output_dir / category / name
        self.t_print('Writing prototype to ', path, ':', category, ' - ', name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w') as f:
            f.write(prototype)

    def end_sub_stage(self):
        print('Ending parsing sub stage for mod', self.mod_name, ', in data stage', self.data_stage)
        self.sub_stage_parsing = False
        # pack up current prototype (ship and git commit?)

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
