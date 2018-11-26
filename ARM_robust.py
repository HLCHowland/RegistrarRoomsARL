#    (c) 2018  Karan Erry, Henry Howland
# eForest Scheduling Associative Rule Mining Module
# This module of the eForest Scheduling project takes data sets from previous semesters and seeks to mine rules from them
# that can be used to help generate semesterly class schedules.

import random, os, sys, arl_utils, time, pandas as pd
from apyori import apriori
from Data import data_cleaning

global allDFs

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
def calculate_viable_support (df, ColumnTarget, SupportMethod):
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
            print("Invalid calculate_viable_support (SupportMethod), mining aborted.")
            sys.exit()
            return 0
    return output


''' This method concatenates dataframes from the dfs list to get a more robust dataframe
    for rule mining. You can determine how many you want to concatenate and it will do
    so by choosing n random #s within the range of the dfs list. '''
def concat_multiple_DFs(howMany):
    if howMany == 0:
        # append all together
        return pd.concat(allDFs, axis=0, ignore_index=True)
    else:
        # append only some together
        dataframes = len(allDFs) -1
        MiningSet = pd.DataFrame()

        if howMany > dataframes:    # This exits the method if the # of dataframes you would like to concatinate is invalid
                print("Invalid concat_multiple_DFs(howMany), mining aborted.")
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
                                MiningSet = allDFs[ambiguousName]
                        else:
                                 randomdf = randomdfindexes[i]
                                 MiningSet = pd.concat([allDFs[randomdf], MiningSet], 0, ignore_index=True)
        return MiningSet
        
        
def drop_duplicate_rules(rulesDf):
    # Drop duplicates (classified by duplication in the rule-antecedent column)
    # Method: Sort rule-antecdent duplicates by descending order of itemset-support, then drop the dupes
    rulesDf.sort_values(by=['Rule Antecedent', 'Itemset Support'], ascending=False, inplace=True)
    rulesDf.drop_duplicates(subset='Rule Antecedent', inplace=True)
    rulesDf.reset_index(drop=True, inplace=True)
    return rulesDf
        

''' This function filters rules to retain only those having a Room as the consequent.
    IMPORTANT: Using the 'all_rooms_list_maybe.xlsx' file in Data/ folder as the
               makeshift list of all rooms. 
               Check with Hill/Registrar for official list of all available rooms.
'''
def filter_apyori_results(rules):
    allRooms = pd.read_excel(os.path.join('Data', 'all_rooms_list_maybe.xlsx')).iloc[:,0].values
    filteredRules = []
    for relationRecord in rules:
        for orderedStats in relationRecord[2]:
            if list(orderedStats[1])[0] in allRooms:    # the rule consequent is orderedStats[1], and
                                                        # it will always only have one element -- hence
                                                        # the [0] access.
                filteredRules.append(relationRecord[0:2] + orderedStats[:])
    filteredRulesDf = pd.DataFrame(filteredRules, columns=['Itemset', 'Itemset Support', 'Rule Antecedent', 'Rule Consequent', 'Rule Confidence', 'Rule Lift'])
    filteredRulesDf = drop_duplicate_rules(filteredRulesDf)
    return filteredRulesDf
    

def run_non_robust_pipeline (howMany, supportColumnTarget, supportMethod):
    # 1 Concatenate desired number of DFs into one aggregate DF
    data = concat_multiple_DFs(howMany)
    # 2 Calculate viable minimum support by desired method
    vmSupport = calculate_viable_support(data, supportColumnTarget, supportMethod)
    # 3 Convert data to list of lists as required by the apyori algorithm
    data = data.applymap(lambda elem: str(elem)).values.tolist()
    # 4 Run the apriori algorithm, with chosen minimum values, storing results in 'rules'
    rules = apriori(data, min_support=vmSupport[0], min_confidence=0.2, min_lift=3, min_length=2)
    # 5 Filter and and clean the rules
    filtered_rules = filter_apyori_results(rules)
    # return
    return filtered_rules


def run_robust_pipeline (robustness, howMany, supportColumnTarget, supportMethod ):
    association_results = []
    for x in range(robustness): # The robustness here dictates how many times the rule mining process will happen.
        df = (concat_multiple_DFs(howMany))  # This function is what appends the dataframes into a larger one that
                                             # is more suitable for rule mining.
        support = calculate_viable_support (df, supportColumnTarget, supportMethod)    # This gets the support value for the pipeline.
#        print(support[0])
        records = []    # The 'df' is the set being prepared, derived from 'allDFs' passed in at the call.
        for i in range(0, len(df)): # This line and the line below set up a dataframe that can be mined for rules.
            records.append([str(df.values[i, j]) for j in range(0, len(df.values[i]))])
        association_rules = list(apriori(records, min_support=support[0], min_confidence=0.2, min_lift=3, min_length=2))
        association_results.extend(list(association_rules)) # Values above define how easy it is for an association
                                                            # aka rule to be made.
    return association_results

def run_robust_with_given_support (robustness, howMany, support):
    association_results = []
    for x in range(robustness): # The robustness here dictates how many times the rule mining process will happen.
        df = (concat_multiple_DFs(howMany))  # This function is what appends the dataframes into a larger one that
                                            # is more suitable for rule mining.
        records = []    # The 'df' is the set being prepared, derived from 'allDFs' passed in at the call.
        for i in range(0, len(df)): # This line and the line below set up a dataframe that can be mined for rules.
            records.append([str(df.values[i, j]) for j in range(0, len(df.values[i]))])
        association_rules = apriori(records, min_support=support, min_confidence=0.2, min_lift=3, min_length=2)
        association_results.extend(list(association_rules)) # Values above define how easy it is for an association
                                                            # aka rule to be made.
    return association_results
    
    
''' This function runs the apyori algorithm NON-ROBUSTLY on ever-decreasing values for the minimum
    support, thus over time gradually getting more and more rules. 
'''
def run_indefinitely():
    JUMP = 0.0005    # as a starting point
    data = concat_multiple_DFs(0)    # concatenate all DFs
    data_as_list = data.applymap(lambda elem: str(elem)).values.tolist()
    runsDir = 'Indef_Runs'
    cachePath = os.path.join(runsDir, 'indefinite_run_cache.txt')
    try:
        while (True):
            # 1 Get min support, either from past run or fresh
            try:
                cacheLines = open(cachePath, 'r').read().split('\n')
                if cacheLines[-1].startswith('INIT_MIN_SUPP'):
                    vmSupport = float(cacheLines[-1].split('\t')[1])
                elif cacheLines[-1].startswith('SUCCESS'):
                    lastSupport = float(cacheLines[-1].split('\t')[1])
                    if lastSupport - JUMP < 0:
                        JUMP /= 10
                    vmSupport = lastSupport - JUMP
                elif cacheLines[-1].startswith('INCOMPLETE'):
                    vmSupport = float(cacheLines[-1].split('\t')[1])
                allRules = pd.read_csv(os.path.join(runsDir, 'all_runs_rules.csv'))
            except FileNotFoundError:
                # cache doesn't exist, no it's never been run
                vmSupport = calculate_viable_support(data, 'Room', 'Lower IQR')[0]
                open(cachePath, 'w').write(f'INIT_MIN_SUPP\t{vmSupport}')
                allRules = None
            # 2 Record time
            startTime = time.time()
            # FUTURE: Execute a run-time function as a separate process that
            #         prints an updated run-time every n seconds that the alg runs
            # 3 Run algorithm and filter rules
#            rules = apriori(data_as_list, min_support=vmSupport, min_confidence=0.2, min_lift=3, min_length=2)
            robust_rules = run_robust_with_given_support(12, 8, vmSupport)
            thisRun_rules = filter_apyori_results(robust_rules)
            # 4 Extend rules lists and save to files
            if allRules is None:
                # first successful run
                allRules = thisRun_rules
            else:
                allRules = pd.concat([allRules, thisRun_rules], axis=0, ignore_index=True)
                allRules = drop_duplicate_rules(allRules)
            allRules.to_csv(os.path.join(runsDir, 'all_runs_rules.csv'))
            thisRun_rules.to_csv(os.path.join(runsDir, f'supp_{vmSupport}.csv'))
            # 5 Get run_time and record support and run_time as a successful
            runTime = time.time() - startTime
            open(cachePath, 'a').write(f'\nSUCCESS\t{vmSupport}\t{runTime}')
            print(f'SUCCESSFUL RUN. Ran with {vmSupport} support over {runTime} seconds.')
    except (KeyboardInterrupt, EOFError):
        # manual interrupt
        runTime = time.time() - startTime
        open(cachePath, 'a').write(f'\nINCOMPLETE\t{vmSupport}\t{runTime}')
        print(f'\tINCOMPLETE RUN. Ran with {vmSupport} support for {runTime} seconds.')
    
    
    # 1 Get last successful run's min support
    # 2 Record Current Time
    # Future Improvement: If ran before, calculate time estimate from previous runs
    # 3 Run Apyori and wrapper (time-printing) function
    #    If KeyboardInterrupt:
    #    4 Save Run time as an incomplete
    #    5 Output basic info
    # 4 Extend the list of rules with these rules
    # 5 Record support as a successful, along with time of the run

#def run_asymptotically():
#    min_supp = open('continuous_run_cache', 'r')

if __name__ == '__main__':

    # Variables for the file-saving
    TEXT_TO_SAVE = ''
    MESSAGE = ''

    # Prepare data
    addressSegment = os.path.join('Data', 'originals (uncleaned)')
    # Parse all datasets into dataframes, clean once and for all, and put them in a list for easy access
    global allDFs
    allDFs = [clean(pd.read_csv(os.path.join(addressSegment, 'FA2014.csv'))),   # Datasets to be included in 'dfs' list for
                                                                                # processing. All of these datasets will be
                                                                                # a part of a list.
              clean(pd.read_csv(os.path.join(addressSegment, 'FA2015.csv'))),
              clean(pd.read_csv(os.path.join(addressSegment, 'SP2015.csv'))),
              clean(pd.read_csv(os.path.join(addressSegment, 'FA2016.csv'))),
              clean(pd.read_csv(os.path.join(addressSegment, 'SP2016.csv'))),
              clean(pd.read_csv(os.path.join(addressSegment, 'FA2017.csv'))),
              clean(pd.read_csv(os.path.join(addressSegment, 'SP2017.csv'))),
              clean(pd.read_csv(os.path.join(addressSegment, 'FA2018.csv'))),
              clean(pd.read_csv(os.path.join(addressSegment, 'SP2018.csv')))]
        
    # RUN INDEFINITELY
    run_indefinitely()

    # Run the ROBUST pipeline and save list of rules
#    rules = run_robust_pipeline (12, 8, 'Room', 'Lower IQR')
#    filtered_rules = filter_apyori_results(rules)
#    filtered_rules.to_csv('filteredRules.csv')

#    rules = pd.DataFrame({'Rules': rules})
#    vc = rules['Rules'].value_counts()
#    print(type(vc))
#    print(vc)

#    TEXT_TO_SAVE += str(vc)

    # Add message and save output to file

    # ##########################################
    # ADD YOUR CUSTOM SAVE-TO-FILE MESSAGE HERE:
    # ##########################################
#    MESSAGE = 'Running (Robust) with value counts (refactored, using external clean func)'
    MESSAGE = 'List of Rooms?'

#    arl_utils.save(TEXT_TO_SAVE, MESSAGE)