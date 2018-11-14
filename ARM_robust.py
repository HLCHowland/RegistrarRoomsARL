#Henry Howland, Karan Erry
#eForest Scheduling Associative Rule Mining Module
#This moduleof the eForest Scheduling project takes data sets from previous semesters and seeks to mine rules from them
#that can be used to help generate semesterly class schedules.

import random, os, sys, arl_utils
import pandas as pd
from apyori import apriori
from Data import data_cleaning

''' The data cleaner is specialized to clean data only from the above datasets.
    The code in this method takes out any extraneous columns, rows and data
    from the dataframe. It also reformats info using regular expressions. '''
def clean(df):
#        print('start cleaning')
        df = data_cleaning.perform_basic_cleaning(df)
#        df.reset_index(drop=True, inplace=True)
#        df.Room = df.Room.str.extract(r'([A-Z]+ +[A-Z0-9]+)')
#        df['Dept'] = df.Course.str.extract(r'([A-Z]+)')
#        df = df[['Dept'] + df.columns.tolist()[:-1]]
#        df.Course = df.Course.str.extract(r'(?:[A-Z]+)([A-Z0-9 ]+)')
#        df = df.apply(lambda val: val.str.strip())
#        df['Title & Requirements Met'] = df['Title & Requirements Met'].str.extract(r'([^\n]+)')
#        df['Meeting Times'] = df['Meeting Times'].str.extract(
#                r'(\d\d?:\d\d? +[AP]M +- +\d\d?:\d\d? +[AP]M +[MTWRF]+)')
#        df = df.rename({'Title & Requirements Met': 'Title'})
#        df = df[df.Course != 'Course']
#        df.Room = df.Room.str.extract(r'([A-Z]+ +[A-Z]?[0-9]+)(?! - Final Exam)')
#        # df = df.drop(['Meeting Times', 'Max', 'Current', 'Avail', 'Waitlist', 'Other Attributes'], axis=1, inplace=True)
#        print('cleaned', len(df))
        return df

''' This method generates a number for the support attribute of the apriori algorithm. '''
def support_finder(df, ColumnTarget, SupportMethod):
        output = []
        if SupportMethod == 'All':
                histoMaker = (df[ColumnTarget].value_counts())
                supportVals = histoMaker / len(df)
                output.append(supportVals[int(len(supportVals) * .75)]) # The decimals correspond to the index of the
                                                                        # various IQR values of the frequency of like
                                                                        # elements within the dataset, .75 being the
                                                                        # upper limit of the inter quartile range,
                                                                        # .25 the lower, and .5 being the median frequency.
                output.append(supportVals[int(len(supportVals) * .5)])
                output.append(supportVals[int(len(supportVals) * .25)])
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
                print("Invalid support_finder(SupportMethod), mining aborted.")
                sys.exit()
                return 0
        return output

''' This method concatenates dataframes from the dfs list to get a more robust dataframe
    for rule mining. You can determine how many you want to concatenate and it will do
    so by choosing n random #s within the range of the dfs list. '''
def dataframe_appender(dfList, howMany):
        dataframes = len(dfList) -1
        MiningSet = pd.DataFrame()

        if howMany > dataframes:    # This exits the method if the # of dataframes you would like to concatinate is invalid
                print("Invalid dataframe_appender(howMany), mining aborted.")
                sys.exit()
                return 0
        else:
                randomdf = set()
                while len(randomdf) < howMany:  # Used to generate a random set of indexes that correspond to the dataframes
                                                # to be concatenated, to ensure that the rules are robust.
                        randomdf.add(random.randint(0, dataframes))
                randomdfindexes = list(randomdf)
                for i in range (0, howMany):    # Loop that concatenates the randomly selected dataframes from their list.
                        if MiningSet.empty:
                                ambiguousName = randomdfindexes[i]
                                MiningSet = dfList[ambiguousName]
                        else:
                                 randomdf = randomdfindexes[i]
                                 MiningSet = pd.concat([dfList[randomdf], MiningSet], 0, ignore_index=True)
        return MiningSet

def apyori_robust_rule_finder (dfList, howMany, robustness, supportColumnTarget, supportMethod ):
    association_results = []
    for i in range(robustness): # The robustness here dictates how many times the rule mining process will happen.
        df = (dataframe_appender(dfList, howMany))  # This function is what appends the dataframes into a larger one that
                                                    # is more suitable for rule mining.
        df = clean(df)
        support = support_finder(df, supportColumnTarget, supportMethod)    # This gets the support value for the pipeline.
        records = []    # The 'df' is the set being prepared and cleaned, derived from 'dfList' passed in at the call.
        for i in range(0, len(df)): # This line and the line below set up a dataframe that can be mined for rules.
            records.append([str(df.values[i, j]) for j in range(0, len(df.values[i]))])
        association_rules = apriori(records, min_support=support[0], min_confidence=0.2, min_lift=3, min_length=2)
        association_results.extend(list(association_rules)) # Values above define how easy it is for an association
                                                            # aka rule to be made.
    return association_results

if __name__ == '__main__':

    # Variables for the file-saving
    TEXT_TO_SAVE = ''
    MESSAGE = ''

    # Prepare data
    addressSegment = os.path.join('Data', 'originals (uncleaned)')
    dfs = [pd.read_csv(os.path.join(addressSegment, 'FA2014.csv')), # Datasets to be included in 'dfs' list for
                                                                    # processing. All of these datasets will be
                                                                    # a part of a list.
           pd.read_csv(os.path.join(addressSegment, 'FA2015.csv')),
           pd.read_csv(os.path.join(addressSegment, 'SP2015.csv')),
           pd.read_csv(os.path.join(addressSegment, 'FA2016.csv')),
           pd.read_csv(os.path.join(addressSegment, 'SP2016.csv')),
           pd.read_csv(os.path.join(addressSegment, 'FA2017.csv')),
           pd.read_csv(os.path.join(addressSegment, 'SP2017.csv')),
           pd.read_csv(os.path.join(addressSegment, 'FA2018.csv')),
           pd.read_csv(os.path.join(addressSegment, 'SP2018.csv'))]

    # Run the pipeline and store list of rules
    rules = apyori_robust_rule_finder(dfs, 8, 12, 'Room', 'Lower IQR')
    
    print(len(rules))

    # Filter rules to retain only those having a Room as the consequent
    # IMPORTANT: Using the 'all_rooms_list_maybe.xlsx' file in Data/ folder as the
    #            makeshift list of all rooms. 
    #            Check with Hill/Registrar for official list of all available rooms.
    allRooms = pd.read_excel(os.path.join('Data', 'all_rooms_list_maybe.xlsx')).iloc[:,0].values
    

    rules = pd.DataFrame({'Rules': rules})
    vc = rules['Rules'].value_counts()
#    print(type(vc))
#    print(vc)

#    TEXT_TO_SAVE += str(vc)

    # Add message and save output to file

    # ##########################################
    # ADD YOUR CUSTOM SAVE-TO-FILE MESSAGE HERE:
    # ##########################################
#    MESSAGE = 'Running (Robust) with value counts (refactored, using external clean func)'
    MESSAGE = 'List of Rooms?'

    arl_utils.save(TEXT_TO_SAVE, MESSAGE)
