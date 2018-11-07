#Henry Howland, Karan Erry
#eForest Scheduling Associative Rule Mining Module
#This moduleof the eForest Scheduling project takes data sets from previous semesters and seeks to mine rules from them
#that can be used to help generate semesterly class schedules.

import random
import pandas as pd
from apyori import apriori
from Data import data_cleaning

addressSegment = os.path.join('Data', 'originals (uncleaned)')
dfs = [pd.read_csv(os.path.join(addressSegment, 'FA2014.csv')), #Datasets to be included in 'dfs' list for
   pd.read_csv(os.path.join(addressSegment, 'FA2015.csv')),#processing. All of these datasets will be
   pd.read_csv(os.path.join(addressSegment, 'SP2015.csv')),#a part of a list.
   pd.read_csv(os.path.join(addressSegment, 'FA2016.csv')),
   pd.read_csv(os.path.join(addressSegment, 'SP2016.csv')),
   pd.read_csv(os.path.join(addressSegment, 'FA2017.csv')),
   pd.read_csv(os.path.join(addressSegment, 'SP2017.csv')),
   pd.read_csv(os.path.join(addressSegment, 'FA2018.csv')),
   pd.read_csv(os.path.join(addressSegment, 'SP2018.csv'))
  ]


def cleaner(df): #The data cleaner is specialized to clean data only from the above datasets.
                df = df.loc[df.Course != 'Course']
                df.reset_index(drop=True, inplace=True)
                df.Room = df.Room.str.extract(r'([A-Z]+ +[A-Z0-9]+)')
                df['Dept'] = df.Course.str.extract(r'([A-Z]+)')
                df = df[['Dept'] + df.columns.tolist()[:-1]]
                df.Course = df.Course.str.extract(r'(?:[A-Z]+)([A-Z0-9 ]+)')
                df = df.apply(lambda val: val.str.strip())
                df['Title & Requirements Met'] = df['Title & Requirements Met'].str.extract(r'([^\n]+)')
                df['Meeting Times'] = df['Meeting Times'].str.extract(
                        r'(\d\d?:\d\d? +[AP]M +- +\d\d?:\d\d? +[AP]M +[MTWRF]+)')
                df = df.rename({'Title & Requirements Met': 'Title'})
                df = df.drop(['Meeting Times', 'Max', 'Current', 'Avail', 'Waitlist', 'Other Attributes'], axis=1,
                             inplace=True)
                df = df[df.Course != 'Course']  # The code in this method takes out any
                df.Room = df.Room.str.extract(
                        r'([A-Z]+ +[A-Z]?[0-9]+)(?! - Final Exam)')  # extraneous columns, rows and data from
                df = df.dropna(subset=['Room'], inplace=True)  # the dataframe. It also reformats info
                return df  # using regular expressions.

def SupportFinder(df, ColumnTarget, SupportMethod): #This method generates a number for the support attribute of the
        output = []                                 #apriori algorithm.
        if SupportMethod == 'All':
                histoMaker = (df[ColumnTarget].value_counts())
                supportVals = histoMaker / len(df)
                output.append(supportVals[int(len(supportVals) * .75)]) #The decimals coorespond to the index of the various IQR values of the
                output.append(supportVals[int(len(supportVals) * .5)]) #frequency of like elemnts within the dataset, .75 being the upper limit of
                output.append(supportVals[int(len(supportVals) * .25)])#the inner quartile range, .25 the lower, and .5 being the median frequency.
        elif SupportMethod == 'Upper IQR':
                histoMaker = (df[ColumnTarget].value_counts())
                supportVals = histoMaker / len(df)
                output.append(len(supportVals)[int(len(supportVals) * 0.75)])
        elif SupportMethod == 'Median':
                histoMaker = (df[ColumnTarget].value_counts())
                supportVals = histoMaker / len(df)
                output.append(supportVals[int(len(supportVals) * 0.5)])
        elif SupportMethod == 'Lower IQR':
                histoMaker = (df[ColumnTarget].value_counts())
                supportVals = histoMaker / len(df)
                output.append(supportVals[int(len(supportVals) * 0.25)])
        else:
                print("Invalid method call.")
                return 0
        return output

def compounded_data_frames(dflist, howmany): #This method concatenates dataframes from the dfs list to get a more robust
        dataframes = len(dflist) -1          #dataframe for rule mining. You can determine how many you want to concatenate
        MiningSet = pd.DataFrame()           #and it will do so be choosing n random #s within the range of the dfs list.

        if howmany > dataframes: #This exits the method if the # of dataframes you would like to concatinate is invalid
                print("Second argument larger than number of dataframes.")
                return 0
        else:
                randomdf = set()
                while len(randomdf) < howmany: #Used to generate a random set of indexes that correspond to the dataframes
                        randomdf.add(random.randint(0, dataframes))#to be concatenated, to ensure that the rules are robust.
                randomdfindexes = list(randomdf)
                for i in range (0, howmany): #The loop that concatenates the randomly selected dataframes from their list.
                        if MiningSet.empty:
                                ambiguousName = randomdfindexes[i]
                                MiningSet = dflist[ambiguousName]
                        else:
                                 randomdf = randomdfindexes[i]
                                 MiningSet = pd.concat([dflist[randomdf], MiningSet], 0, ignore_index=True)
        return MiningSet






cdfFunctiondfSize = int(input("How many dataframes from the list of dataframes would you like to use? Please enter a number less"
                          " than the length of the list of dataframes.\n"))
sfFunctionColumnTarget = str(input("Which column in the dataframes would you like to find a support value for the apriori rule "
                               " mining algorithm? Please only enter a string that corresponds with a column in the dataframe.\n"))
sfFunctionSupportMethod = str(input('When finding the support value for the column, would you like to use the "Upper IQR"'
                                ' limit, "Lower IQR" limit, the "Median", or "All"? Please enter only one of the values '
                                ' between the quotes.\n'))

MiningSet = compounded_data_frames(dfs, cdfFunctiondfSize)
MiningSet = cleaner(MiningSet)
support = SupportFinder(MiningSet, sfFunctionColumnTarget, sfFunctionSupportMethod)

records = []
for i in range(0, len(MiningSet)):
    records.append([str(MiningSet.values[i, j]) for j in range(0, len(MiningSet.values[i]))])

association_rules = apriori(records, min_support=support[0], min_confidence=0.2, min_lift=3, min_length=2)
association_results = list(association_rules)
print(association_results)





