import pandas as pd
import os, re
from tabulate import tabulate

path = 'originals (uncleaned)'
totalbef, totalaft = [], []
#alldata = pd.Series()
for filename in ['2015-FA.csv', '2015-SP.csv', '2016-FA.csv', '2016-SP.csv', '2017-FA.csv', '2017-SP.csv', '2018-FA.csv', '2018-SP.csv']:
    # Setup -- Read in data and set up writer
    data = pd.read_csv(os.path.join(path, filename))
    writer = pd.ExcelWriter(filename[:-4]+'_clean.xlsx')
    totalbef.append(len(data))
    # Begin cleaning
    # Step 1: Get rid of repeated column headers
    data = data.loc[data.Course != 'Course']
    # (OR) data.drop(data.loc[data.Course == 'Course'].index, inplace=True)
    data.reset_index(drop=True, inplace=True)
    # Step 2: Standardize 'room' field, by deleting unnecessary parts
    data.Room = data.Room.str.extract(r'([A-Z]+ +[A-Z0-9]+)')
#    data.Room = data.Room.str.extract(r'([A-Z]+ +[A-Z]?[0-9]+)(?! - Final Exam)')
    # Step 3: Get rid of rows for which Room is missing data
    data.dropna(subset=['Room'], inplace=True)
    # Shutdown -- Write modifications to new excel files
    data.to_excel(writer, 'Schedule', index=False)
    writer.save()
    totalaft.append(len(data))
    # Further, experimental/temporary stuff
#    print(data.Room.map(lambda room : not re.search(r'([A-Z]+ +[A-Z0-9]+)', str(room))))
#    print(data.Room.loc[data.Room.map(lambda room : not re.search(r'([A-Z]+ +[A-Z0-9]+)', str(room)))])
#    alldata = pd.concat([alldata, data.Room.loc[data.Room.map(lambda room : not re.search(r'([A-Z]+ +[A-Z0-9]+)', str(room)))]])

#writerx = pd.ExcelWriter('naRooms.xlsx')
#alldata.to_excel(writerx)
#writerx.save()

print(f'{sum(totalbef)} - {sum(totalbef)-sum(totalaft)} = {sum(totalaft)} ({(sum(totalaft)/sum(totalbef))*100}% of uncleaned)')
#print(tabulate([totalbef+[sum(totalbef)], totalaft+[sum(totalaft)], list(map(lambda x,y :x-y, totalbef+[sum(totalbef)], totalaft+[sum(totalaft)]))]))

