import argparse
import re
import shutil
import subprocess
import sys

from pathlib import Path


PROJECT_ROOT_PATH = (Path(__file__).parent / '..').absolute().resolve()
DATA_RAW_DIR = PROJECT_ROOT_PATH / 'data_raw'

FACTORIO_EXE = PROJECT_ROOT_PATH / 'factorio/bin/x64/factorio'
FACTORIO_LOG_FILE = PROJECT_ROOT_PATH / 'factorio/factorio-current.log'
TMP_DIR = PROJECT_ROOT_PATH / '_tmp'


vprint = lambda *_, **__: None


def create_tmp():
	if not TMP_DIR.exists():
		print('Creating temp directory: ' + str(TMP_DIR))
		TMP_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_tmp():
	if TMP_DIR.exists():
		print('Cleaning up temp directory: ' + str(TMP_DIR))
		shutil.rmtree(str(TMP_DIR))


def read_log_file_lines(path):
	path = path or FACTORIO_LOG_FILE
	print('Reading log file: ' + str(path))
	with path.resolve().open() as f:
		return f.readlines()


def parse_log_lines_to_raw_prototypes(log_file_lines):
	content = []
	prototype = []
	open_prototype = False
	for line in log_file_lines:
		if 'FactorioDataRawDump' in line:
			open_prototype = True
			if len(prototype) > 0:
				content.append(''.join(prototype))
				prototype = []

		if 'DONE' in line:
			content.append(''.join(prototype))
			break

		if open_prototype:
			prototype.append(line)
	return content


def parse_prototypes(raw_prototypes):
	print('Parsing %d prototypes' % len(raw_prototypes))
	pattern = re.compile(r'FactorioDataRawDump\(<<(.*?)>>,<<(.*?)>>,<<(.*?)>>\)', re.MULTILINE | re.DOTALL)
	for raw in raw_prototypes:
		match = pattern.search(raw)
		vprint('Found %s - %s' % (match[1], match[2]))
		write_prototype(match[1], match[2], match[3])


def write_prototype(category, name, data):
	path = DATA_RAW_DIR / category / name
	vprint('Outputting data to ' + str(path))
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open('w') as f:
		f.write(data)


def run_factorio():
	print('Running local Factorio to generate fresh logs')
	completed = subprocess.run(
		[FACTORIO_EXE, '--create', str(TMP_DIR / 'dummy_map')],
		stderr=subprocess.PIPE,
		stdout=subprocess.PIPE
	)

	if completed.returncode > 0:
		print('ERROR: Factorio failed to run:')
		print(completed.stderr)

	print('Factorio ran successfully')


def upgrade_factorio(version): #TODO - test this
	print('Upgrading Factorio to ' + version)
	completed = subprocess.run(
		[FACTORIO_EXE, '--apply-update', version],
		stderr=subprocess.PIPE
	)

	if completed.returncode > 0:
		print('ERROR: Failed to upgrade Factorio:')
		print(completed.stderr)
		sys.exit(completed.returncode)
	print('Successfully upgraded Factorio')


def main(log_lines):
	create_tmp()

	raw_prototypes = parse_log_lines_to_raw_prototypes(log_lines)
	if len(raw_prototypes) == 0:
		print('ERROR: No prototypes found in log file')
		return

	if DATA_RAW_DIR.exists():
		data = str(DATA_RAW_DIR)
		print('Deleting data directory %s recursively' % data)
		shutil.rmtree(data)

	parse_prototypes(raw_prototypes)
	cleanup_tmp()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description="""Builds the data_raw directory with all prototype data from the local Factorio instance"""
	)

	parser.add_argument('-f', '--file', action='store', help='Log file to read, instead of launching local Factorio install')
	parser.add_argument('-u', '--upgrade', action='store', help='Upgrade local Factorio before running, to provided version')
	parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

	args = parser.parse_args()

	if args.verbose:
		vprint = print

	if args.upgrade:
		upgrade_factorio(args.upgrade)

	create_tmp()

	log_file = None
	if args.file:
		log_file = Path(args.file)
	else:
		run_factorio()

	lines = read_log_file_lines(log_file)

	main(lines)
