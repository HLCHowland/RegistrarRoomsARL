import pandas as pd
import os, re
from tabulate import tabulate

pd.options.mode.chained_assignment = None

global agg_total_bef, agg_total_aft
agg_total_bef, agg_total_aft = [], []

def clean(data):
    # Setup -- 'totals' variables to quanity impact of cleaning on the size of the data
    global agg_total_bef, agg_total_aft
    total_bef, total_aft = 0, 0
    total_bef = len(data)
    agg_total_bef.append(total_bef)
    # 1: Get rid of repeated column headers
    data = data.loc[data.Course != 'Course']
    data.reset_index(drop=True, inplace=True)
    # 2: Get rid of rows for which Room is missing data
    data.dropna(subset=['Room'], inplace=True)
    # 3: Standardize different fields by only retaining necessary parts...
    # ...'Room':
    data.Room = data.Room.str.extract(r'([A-Z]+ +[A-Z0-9]+)')
    # ...'Course' (split into Dept. and Course):
    data['Dept'] = data.Course.str.extract(r'([A-Z]+)')
    data = data[['Dept'] + data.columns.tolist()[:-1]]
    data.Course = data.Course.str.extract(r'(?:[A-Z]+)([A-Z0-9 ]+)')
    # ...'Meeting Times' (retain only the time slot and day):
    data['Meeting Times'] = data['Meeting Times'].str.extract(r'(\d\d?:\d\d? +[AP]M +- +\d\d?:\d\d? +[AP]M +[MTWRF]+)')
    # ...'Title & Requirements Met' (retain only the title):
    data['Title & Requirements Met'] = data['Title & Requirements Met'].str.extract(r'([^\n]+)')
    data.rename({'Title & Requirements Met':'Title'}, axis=1, inplace=True)
    # 4: Drop irrelevant columns
    data.drop(['Meeting Times', 'Max', 'Current', 'Avail', 'Waitlist', 'Other Attributes'], axis=1, inplace=True)
    # 5: Strip whitespace for better one-hot encoding
    data = data.apply(lambda val: val.str.strip())
    
    # Shutdown -- Calculate and print total rows dropped, return data
    total_aft = len(data)
    agg_total_aft.append(total_aft)
    print('For this dataset:  {:d} out of {:d} ({:.2f} %) of data was retained.'.format(total_aft, total_bef, (total_aft/total_bef) * 100))
#    print(f'For this dataset:  {total_aft} out of {total_bef} ({.2total_aft}%) of dataset retained.')
    
    return data

def writeToExcel(df, filename):
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, 'Schedule', index=False)
    writer.save()

if __name__=='__main__':
    path = 'originals (uncleaned)'
    for filename in ['FA2014.csv', 'SP2015.csv', 'FA2015.csv', 'SP2016.csv', 'FA2016.csv', 'SP2017.csv', 'FA2017.csv', 'SP2018.csv', 'FA2018.csv']:
        # Read in data
        data = pd.read_csv(os.path.join(path, filename))
        # Clean
        data = clean(data)
        # Write to file
        writeToExcel(data, filename[:-4]+'_clean.xlsx')
    
    print(f'For all datasets:\n{sum(agg_total_bef)} - {sum(agg_total_bef)-sum(agg_total_aft)} = {sum(agg_total_aft)} ({(sum(agg_total_aft)/sum(agg_total_bef))*100}% of uncleaned)')
    
    
    # Further, experimental/temporary stuff
#    print(data.Room.map(lambda room : not re.search(r'([A-Z]+ +[A-Z0-9]+)', str(room))))
#    print(data.Room.loc[data.Room.map(lambda room : not re.search(r'([A-Z]+ +[A-Z0-9]+)', str(room)))])
#    alldata = pd.concat([alldata, data.Room.loc[data.Room.map(lambda room : not re.search(r'([A-Z]+ +[A-Z0-9]+)', str(room)))]])
    
#    writerx = pd.ExcelWriter('naRooms.xlsx')
#    alldata.to_excel(writerx)
#    writerx.save()