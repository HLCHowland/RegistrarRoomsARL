import os

def save(text_to_save, message=''):
	# Get file index
	try:
		index = int(open(os.path.join('Runs', 'index'), 'r').read().split('\n')[-2]) + 1
	except FileNotFoundError:
		# index file doesn't exist
		print('Encountered FileNotFoundError, attempting to create index file...')
		if not os.path.exists('Runs'):
			os.mkdir('Runs')
		open(os.path.join('Runs', 'index'), 'w').write('0\n')
		index = 1
		print('... Success')
	# Update index cache
	try:
		open(os.path.join('Runs', 'index'), 'a').write(f'{index}\n')
		if isinstance(text_to_save, list):
			text_to_save = '\n'.join(text_to_save)
		elif not isinstance(text_to_save, str):
			raise ValueError('Text to save must be either a list of lines, or a string')
		text_to_save = message + '\n\n' + text_to_save
		filename = f'arl_run_{index}.txt'
		open(os.path.join('Runs', filename), 'w').write(text_to_save)
		print(f"Text saved to file: '{filename}' in Runs/ folder")
	except Exception:
		raise RuntimeError('Encountered an error while saving file. Saving aborted.')