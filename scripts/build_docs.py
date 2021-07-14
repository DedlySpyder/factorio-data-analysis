import argparse
import re
import requests
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
		vprint(f'Found {match[1]} - {match[2]}')
		write_prototype(match[1], match[2], match[3])


def write_prototype(category, name, data):
	path = DATA_RAW_DIR / category / name
	vprint('Outputting data to ' + str(path))
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open('w') as f:
		f.write(data)


def run_factorio():
	_run_factorio('--create', str(TMP_DIR / 'dummy_map'))


def upgrade_factorio():
	version = get_current_version()
	upgrade_path = get_upgrade_path(get_upgrade_versions(), version)

	upgrade_count = len(upgrade_path)
	if upgrade_count == 0:
		print("Factorio fully updated")
		return

	print(f'Upgrading Factorio in {len(upgrade_path)} steps')
	for upgrade in upgrade_path:
		base_version = upgrade["from"]
		to = upgrade["to"]
		print(f'Upgrading from {base_version} to {to}')

		upgrade_link = get_upgrade_link(base_version, to)
		vprint(f'Upgrade link: {upgrade_link}')

		upgrade_file = download_upgrade_zip(upgrade_link, to)
		vprint(f'Upgrade file: {upgrade_file}')

		print('Applying update to Factorio')
		_run_factorio('--apply-update', upgrade_file)
		print(f'Successfully updated to {to}')
		print()


def get_current_version():
	lines = _run_factorio('--version')
	for line in lines:
		match = re.match('Version: ([\d\.]*) .*', line)
		if match:
			return match.group(1)
	raise RuntimeError('Failed to get current version of Factorio')


def download_upgrade_zip(url, to):
	file = TMP_DIR / f'{to}.zip'
	r = _run_get(url)
	open(file, 'wb').write(r.content)
	return str(file)


def get_upgrade_link(base_version, to):
	links = _run_get('https://updater.factorio.com/get-download-link', {
		'package': 'core-linux_headless64',
		'from': base_version,
		'to': to
	}).json()
	if len(links) < 1:
		raise RuntimeError(f'Failed to get upgrade links: {links}')
	return links[0]


def get_upgrade_versions():
	return _run_get('https://updater.factorio.com/get-available-versions').json()


def _run_get(url, params={}):
	try:
		r = requests.get(url, params=params)
		r.raise_for_status()
		return r
	except Exception as e:
		print('Error: Could not get list of updates for updater')
		raise SystemExit(e)


def get_upgrade_path(versions, from_version):
	print('Calculating upgrade path')
	upgrade_path = []
	latest_upgrade = from_version
	while True:
		upgrade = highest_single_upgrade(versions, latest_upgrade)
		if upgrade is None:
			break
		upgrade_path.append(upgrade)
		latest_upgrade = upgrade['to']
	return upgrade_path


def highest_single_upgrade(versions, from_version):
	highest = None
	for v in versions['core-linux_headless64']:
		if 'from' in v and v['from'] == from_version:
			vprint(f'Found possible upgrade from {from_version} to {v["to"]}')
			if highest is None or version_is_higher(v['to'], highest):
				highest = v

	return highest


def version_is_higher(version, test):
	v1, v2, v3 = [int(n) for n in version.split('.')]
	t1, t2, t3 = [int(n) for n in test.split('.')]
	if t1 > v1 or (t1 == v1 and t2 > v2) or (t1 == v1 and t2 == v2 and t3 > v3):
		print(f'{test} is higher than {version}')
		return True
	return False


def _run_factorio(*args):
	args = list(args)
	vprint(f'Running Factorio from {FACTORIO_EXE} with args: {args}')
	proc = subprocess.Popen(
		[FACTORIO_EXE] + args,
		stderr=subprocess.PIPE,
		stdout=subprocess.PIPE,
		bufsize=1
	)

	lines = []
	for line in iter(proc.stdout.readline, None):
		if not line:
			break
		line = line.decode('utf-8')
		lines.append(line)
		vprint(line, end='')
	vprint('End of output')
	vprint()
	proc.stdout.close()
	proc.wait()

	if proc.returncode > 0:
		print('ERROR: Factorio failed to run:')
		print(proc.stderr.read().decode('utf-8'))
		return proc.returncode
	else:
		print('Factorio ran successfully')
		return lines


def main(log_lines):
	create_tmp()

	raw_prototypes = parse_log_lines_to_raw_prototypes(log_lines)
	if len(raw_prototypes) == 0:
		print('ERROR: No prototypes found in log file')
		return

	if DATA_RAW_DIR.exists():
		data = str(DATA_RAW_DIR)
		print(f'Deleting data directory {data} recursively')
		shutil.rmtree(data)

	parse_prototypes(raw_prototypes)
	cleanup_tmp()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description="""Builds the data_raw directory with all prototype data from the local Factorio instance"""
	)

	parser.add_argument('-e', '--exe', action='store', help=f'Factorio exe file to use instead of {FACTORIO_EXE}')
	parser.add_argument('-f', '--file', action='store', help='Log file to read, instead of launching local Factorio install')
	parser.add_argument('-u', '--upgrade', action='store_true', help='Upgrade local Factorio before running, to provided version')
	parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')

	args = parser.parse_args()

	if args.verbose:
		vprint = print

	if args.exe:
		FACTORIO_EXE = Path(args.exe)
		if not args.file:
			FACTORIO_LOG_FILE = (FACTORIO_EXE.parent / '../../factorio-current.log').absolute().resolve()

	create_tmp()

	if args.upgrade:
		upgrade_factorio()

	log_file = None
	if args.file:
		log_file = Path(args.file)
	else:
		run_factorio()

	lines = read_log_file_lines(log_file)

	main(lines)
