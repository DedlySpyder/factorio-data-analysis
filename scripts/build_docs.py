import re, shutil
from pathlib import Path


PROJECT_ROOT_PATH = (Path(__file__).parent / '..').absolute().resolve()
DATA_RAW_DIR = PROJECT_ROOT_PATH / 'data_raw'


def read_log_file(log_file):
	content = []
	path = PROJECT_ROOT_PATH / log_file
	with path.resolve().open() as f:
		open_prototype = False
		prototype = []
		for line in f.readlines():
			if 'FactorioDataRawDump' in line:
				open_prototype = True
				if len(prototype) > 0:
					content.append("".join(prototype))
					prototype = []

			if 'DONE' in line:
				content.append(''.join(prototype))
				break

			if open_prototype:
				prototype.append(line)
	return content


def parse_prototypes(raw_prototypes):
	pattern = re.compile(r'FactorioDataRawDump\(<<(.*?)>>,<<(.*?)>>,<<(.*?)>>\)', re.MULTILINE | re.DOTALL)
	for raw in raw_prototypes:
		match = pattern.search(raw)
		print('Found %s - %s' % (match[1], match[2]))
		write_prototype(match[1], match[2], match[3])


def write_prototype(category, name, data):
	path = DATA_RAW_DIR / category / name
	print('Outputting data to ' + str(path))
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open('w') as f:
		f.write(data)


def main():
	raw_prototypes = read_log_file('factorio/factorio-current.log')

	if len(raw_prototypes) == 0:
		print('ERROR: No prototypes found in log file')
		return

	if DATA_RAW_DIR.exists():
		data = str(DATA_RAW_DIR)
		print('Deleting %s recursively' % data)
		shutil.rmtree(data)

	parse_prototypes(raw_prototypes)


if __name__ == "__main__":
	main()
