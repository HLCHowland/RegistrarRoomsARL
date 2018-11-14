import os, pandas as pd
from Data import data_cleaning

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
	
''' Generate an excel sheet with rooms found in all datasets. '''	
def generate_all_rooms_list():
	# Prepare the datasets
	addressSegment = os.path.join('Data', 'originals (uncleaned)')
	dfList = [pd.read_csv(os.path.join(addressSegment, 'FA2014.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'FA2015.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'SP2015.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'FA2016.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'SP2016.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'FA2017.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'SP2017.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'FA2018.csv')),
		   pd.read_csv(os.path.join(addressSegment, 'SP2018.csv'))]
	# Generate unique list of rooms
	allRooms = set()
	for df in dfList:
		df = data_cleaning.perform_basic_cleaning(df)
		for room in df.loc[:,'Room']:
			allRooms.add(str(room))
	# Sort alphabetically
	allRooms = sorted(allRooms)
	# Save list to an Excel file in Data/ folder
	writer = pd.ExcelWriter(os.path.join('Data','all_rooms_list_maybe.xlsx'))
	pd.DataFrame(allRooms).to_excel(writer, index=False)
	writer.save()
	# Inform user
	print("List of rooms saved as an Excel file 'all_rooms_list_MAYBE.xlsx' in Data/ folder.\nWARNING: This list of rooms may not be comprehensive.\n\t Check with Prof. Hill/the registrar to obtain an official list of all available rooms.")