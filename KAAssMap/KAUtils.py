import pandas as pd
import numpy as np
import json
import math

#The overall results dataframe
_df_ = pd.read_csv("./Data/KA_Ass_Results.csv")

#Dictionary that maps parties to their colors
with open('./Data/party_palette.json', 'r') as fp:
        _party_color_map_ = json.load(fp)

#Party wise results
_party_results_ = pd.read_csv("./Data/KAPartyResults.csv")

#The Dataframe with KA Assembly map
_mapdf_ = pd.read_pickle("./Maps/KAAssMap.pickle")

#This function removes the "(SC)" and "(ST)" tags from the constituency names
def removeSCSTFromName(AC_NAME):
    import re
    AC_NAME = re.sub("\(\s*S[CT]\s*\)","",AC_NAME.upper()).strip()
    return (AC_NAME)

# Function to get the party color map
def get_party_color_map():
    
    party_color_map = _party_color_map_
    return party_color_map

# Function to get the result for the year
def getKAResultsByYear(year):
    df = _df_.copy()
    df = df.loc[df['YEAR']==2013]
    return df

#Function returns all the general election years since (and including) 1957
def getElectionYears():
    years = _df_["YEAR"].unique()
    return years

# Returns the Dataframe of all conteststed winners for the year
# Please note that we are removing those who won unoppsed
def getContestedWinnersDFByYear(year):
    
    df = _df_.copy()
    
    #Remove those who won unopposed
    df = df.loc[(df['YEAR']==year) & (df['POSITION'] == 1) & (df['VOTES'].notnull())]
    
    #remove the POSITION column
    del df['POSITION']
    
    #rename columns
    df.rename(columns={'NAME':'WINNER',"SEX":"WINNER_SEX", \
                       "AGE":"WINNER_AGE",\
                       "CATEGORY":"WINNER_CATEGORY","PARTY":"WINNER_PARTY",\
                       "VOTES":"WINNER_VOTES"\
                      }, inplace=True)
    
    return df

# Returns the dataframe of all Runners up for the year
def getRunnersDFByYear(year):
    
    df = _df_.copy()
    
    #Remove those who won unopposed
    df = df.loc[(df['YEAR']==year) & (df['POSITION'] == 2) & (df['VOTES'].notnull())]
    
    #remove the POSITION column
    del df['POSITION']
    
    #rename columns
    df.rename(columns={'NAME':'RUNNER',"SEX":"RUNNER_SEX", "AGE":"RUNNER_AGE",\
                          "CATEGORY":"RUNNER_CATEGORY","PARTY":"RUNNER_PARTY","VOTES":"RUNNER_VOTES"\
                         }, inplace=True)
    
    return df


# Returns the dataframe of results with the winning margin for the specified year
def getMarginsDFByYear(year):
    
    winDF = getContestedWinnersDFByYear(year)
        
    runDF = getRunnersDFByYear(year)
    
    
    #merge the two dataframes by their common columns
    marginDF = pd.merge(winDF,runDF,on=["ST_NAME","YEAR","AC_NO","AC_NAME","AC_TYPE"])
    
    #We will now calculate the margin and assign it to a new column
    marginDF["WINNING_MARGIN"]= marginDF["WINNER_VOTES"]- marginDF["RUNNER_VOTES"]
    
    return marginDF
    

# Returns the dataframe of results with the pct winning margin for the specified year
def getPCTMarginsDFByYear(year):
    df = _df_.copy()
    
    #Remove those rows where there no values for VOTES
    #Get data for only the relevant year
    df = df.loc[(df['YEAR']==year) & (df['VOTES'].notnull())]
    
    totVotes = []
    counter=0
    
    #Get the Margins DF for the year
    marginDF = getMarginsDFByYear(year)
    
    for index, row in marginDF.iterrows():
        counter += 1
        ac_name=row['AC_NAME']
        subDF = df.loc[(df['YEAR'] == year) & (df['AC_NAME'] == ac_name)]
        totalVotes = subDF['VOTES'].sum()
        totVotes.append(totalVotes)
        
    marginDF['TOTAL_VOTES']=totVotes
    marginDF['PCT_MARGIN']=marginDF['WINNING_MARGIN']/marginDF['TOTAL_VOTES']*100

    return(marginDF)

# This function returns Dataframe with party results data for the year
def getKAPartyResultsByYear(year):
    
    rdf = _df_.copy()
    
    #First get the results for a specific year
    yeardf = rdf.loc[rdf['YEAR'] == year]
    
    #Now that we have the results for the year
    #Let's start gathering some information and stats
    
    #Total Votes Cast in that election
    total_votes = int(yeardf['VOTES'].sum())
    
    #Parties in that year
    parties = yeardf['PARTY'].unique()
    
    #Let us get the PCTMargins for that year
    marginsDF = getPCTMarginsDFByYear(year)
    
    #Now that we have the parties for the year,
    #Let us start gathering stats for the parties
    election_years = []
    seats_contested = []
    votes_won = []
    seats_won = []
    conversion_ratio = []
    percent_votes = []
    median_margin = []
    median_pct_margin = []
    women_cands = []
    women_winners = []
    std_margin = []
    std_pct_margin = []
    overall_median_margin = []
    overall_median_pct_margin = []
    overall_std_margin = []
    overall_std_pct_margin = []
    
    ovr_med_marg = marginsDF['WINNING_MARGIN'].median()
    ovr_med_pct_marg = marginsDF['PCT_MARGIN'].median()
    ovr_std_marg = marginsDF['WINNING_MARGIN'].std()
    ovr_std_pct_marg = marginsDF['PCT_MARGIN'].std()
    
    
    for party in parties:
        
        election_years.append(year)
        
        contested = len(yeardf.loc[yeardf['PARTY']==party].index)
        seats_contested.append(contested)
        
        votes = yeardf.loc[yeardf['PARTY']==party]['VOTES'].sum()
        votes_won.append(int(votes))

        seats = len (yeardf.loc[(yeardf['PARTY'] == party) & (yeardf['POSITION'] == 1)].index)
        seats_won.append(seats)
        
        conversion_ratio.append(seats/votes)
        percent_votes.append(votes/total_votes * 100)
        
        cands = len (yeardf.loc[(yeardf['PARTY'] == party) & (yeardf['SEX'] == 'F')].index)
        women_cands.append(cands)
        
        winners = len (yeardf.loc[(yeardf['PARTY'] == party) & (yeardf['SEX'] == 'F') & (yeardf['POSITION'] == 1)].index)
        women_winners.append(winners)
        
        #Let us calculate the medians
        med_marg = -999999
        med_pct = -9999999
        std_marg = -999999
        std_pct = -9999999
        
        #Get the subset for the party from marginsDF
        subDF = marginsDF.loc[marginsDF['WINNER_PARTY'] == party]
        
        if subDF is not None:
            med_marg = subDF['WINNING_MARGIN'].median()
            med_pct = subDF['PCT_MARGIN'].median()
            std_marg = subDF['WINNING_MARGIN'].std()
            std_pct = subDF['PCT_MARGIN'].std()
            
        median_margin.append(med_marg)
        median_pct_margin.append(med_pct)
        std_margin.append(std_marg)
        std_pct_margin.append(std_pct)
        overall_median_margin.append(ovr_med_marg)
        overall_median_pct_margin.append(ovr_med_pct_marg)
        overall_std_margin.append(ovr_std_marg)
        overall_std_pct_margin.append(ovr_std_pct_marg)
    
    #Now lets create a dataframe out of these lists
    #First create a list of tuples with column names and values
    #And the use that list of tuples to create the DF
    
    results = [('YEAR',election_years),
              ('PARTY',parties),
              ('CONTESTED',seats_contested),
              ('SEATS_WON',seats_won),
              ('VOTES_WON',votes_won),
              ('PCT_VOTES_WON',percent_votes),
              ('CONVERSION_RATIO',conversion_ratio),
              ('MEDIAN_MARGIN',median_margin),
              ('MEDIAN_PCT_MARGIN',median_pct_margin),
              ('STD_MARGIN',std_margin),
              ('STD_PCT_MARGIN',std_pct_margin),
              ('OVERALL_MEDIAN_MARGIN',overall_median_margin),
              ('OVERALL_MEDIAN_PCT_MARGIN',overall_median_pct_margin),
              ('OVERALL_STD_MARGIN',overall_std_margin),
              ('OVERALL_STD_PCT_MARGIN',overall_std_pct_margin),
              ('WOMEN_CANDS',women_cands),
              ('WOMEN_WINNERS',women_winners)
              ]
    
    results = pd.DataFrame.from_items(results)
    
    return results   
    
# This function returns the array of party results for all the years
def getKAPartyResults():
    
    import pandas as pd
    rdf = _df_.copy()
    
    years = rdf['YEAR'].unique()
    
    results = []
    
    for year in years:
        result = getKAPartyResultsByYear(year)
        results.append(result)
        
    resultsDF = pd.concat(results)
    return resultsDF

# Returns the Dataframe with all the party results for all the years
def loadKAPartyResults():
    results = _party_results_.copy()
    return results

# Returns the list of dataframes with PCT Margins for all the years
def getKAPCTMarginsDF():
    el_years = getElectionYears()
    results = []
    
    for year in el_years:
        df = getPCTMarginsDFByYear(year)
        results.append(df)
        
    marginsDF = pd.concat(results)
    
    return marginsDF

# Get a dataframe of result for a year for the specified assembly constituencies
def getResultsByYear(year,ac_names):
        
    rdf = _df_
    
    winners = []
    winnerParties = []
    winnerVotes = []
    
    runners = []
    runnerParties = []
    runnerVotes = []
    
    winDF = rdf.loc[(rdf['YEAR']==year) & (rdf['POSITION']==1)]
    runDF = rdf.loc[(rdf['YEAR']==year) & (rdf['POSITION']==2)]
    
    for ac_name in ac_names:
        ac_name = removeSCSTFromName(ac_name)
        winner = np.nan
        winnerParty = np.nan
        winnerVote = np.nan
        runner = np.nan
        runnerParty = np.nan
        runnerVote = np.nan
        
        tdf = winDF.loc[winDF['AC_NAME']==ac_name]
        if len(tdf.index) > 0:
            winner = tdf['NAME'].values[0]
            winnerParty = tdf['PARTY'].values[0]
            winnerVote = tdf['VOTES'].values[0]
            if np.isnan(winnerVote) == False:
                winnerVote = int(winnerVote)               
                    
        
        tdf = runDF.loc[runDF['AC_NAME']==ac_name]
        if len(tdf.index) > 0:
            runner = tdf['NAME'].values[0]
            runnerParty = tdf['PARTY'].values[0]
            runnerVote = tdf['VOTES'].values[0]
            if np.isnan(runnerVote) == False:
                runnerVote = int(runnerVote)
                
        
        winners.append(winner)
        winnerParties.append(winnerParty)
        winnerVotes.append(winnerVote)

        runners.append(runner)
        runnerParties.append(runnerParty)
        runnerVotes.append(runnerVote)
        
        winnerVotes = [-99999 if np.isnan(x) else x for x in winnerVotes]
        runnerVotes = [-999999 if np.isnan(x) else x for x in runnerVotes]
    
    results = {"Winners":winners,\
               "Winner Parties": winnerParties,"Winner Votes":winnerVotes, \
               "Runners":runners,"Runner Parties": runnerParties,\
               "Runner Votes":runnerVotes}
    return results

# Function that returns the MAP dataframe
def getMapDF():
    import pandas as pd
    mapdf = _mapdf_.copy()
    return mapdf

# Function that returns the list of assembly constituencies that are in the map
def getAC_Names():
    mapdf = getMapDF()
    ac_names = mapdf['AC_NAME'].unique()
    return ac_names






