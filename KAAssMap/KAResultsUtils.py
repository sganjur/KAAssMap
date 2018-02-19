import pandas as pd

def getKAPartyResultsByYear(year):
    
    import pandas as pd
    rdf = pd.read_csv("./Data/KA_Ass_Results.csv")
    
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
        
        #Get the subset for the party from marginsDF
        subDF = marginsDF.loc[marginsDF['WINNER_PARTY'] == party]
        
        if subDF is not None:
            med_marg = subDF['WINNING_MARGIN'].median()
            med_pct = subDF['PCT_MARGIN'].median()
            
        median_margin.append(med_marg)
        median_pct_margin.append(med_pct)
    
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
              ('WOMEN_CANDS',women_cands),
              ('WOMEN_WINNERS',women_winners)
              ]
    
    results = pd.DataFrame.from_items(results)
    
    return results   
    

def getKAPartyResults():
    
    import pandas as pd
    rdf = pd.read_csv("./Data/KA_Ass_Results.csv")
    
    years = rdf['YEAR'].unique()
    
    results = []
    
    for year in years:
        result = getKAPartyResultsByYear(year)
        results.append(result)
        
    resultsDF = pd.concat(results)
    return resultsDF


def loadKAPartyResults():
    
    results = pd.read_csv("./Data/KAPartyResults.csv")
    return results





def getContestedWinnersDFByYear(year):
    import pandas as pd
    df = pd.read_csv("./Data/KA_Ass_Results.csv")
    
    #Remove those who won unopposed
    df = df.loc[(df['YEAR']==year) & (df['POSITION'] == 1) & (df['VOTES'].notnull())]
    
    #remove the POSITION column
    del df['POSITION']
    
    #rename columns
    df.rename(columns={'NAME':'WINNER',"SEX":"WINNER_SEX", "AGE":"WINNER_AGE",\
                          "CATEGORY":"WINNER_CATEGORY","PARTY":"WINNER_PARTY","VOTES":"WINNER_VOTES"\
                         }, inplace=True)
    
    return df

def getRunnersDFByYear(year):
    import pandas as pd
    df = pd.read_csv("./Data/KA_Ass_Results.csv")
    
    #Remove those who won unopposed
    df = df.loc[(df['YEAR']==year) & (df['POSITION'] == 2) & (df['VOTES'].notnull())]
    
    #remove the POSITION column
    del df['POSITION']
    
    #rename columns
    df.rename(columns={'NAME':'RUNNER',"SEX":"RUNNER_SEX", "AGE":"RUNNER_AGE",\
                          "CATEGORY":"RUNNER_CATEGORY","PARTY":"RUNNER_PARTY","VOTES":"RUNNER_VOTES"\
                         }, inplace=True)
    
    return df


def getMarginsDFByYear(year):
    
    winDF = getContestedWinnersDFByYear(year)
        
    runDF = getRunnersDFByYear(year)
    
    
    #merge the two dataframes by their common columns
    marginDF = pd.merge(winDF,runDF,on=["ST_NAME","YEAR","AC_NO","AC_NAME","AC_TYPE"])
    
    #We will now calculate the margin and assign it to a new column
    marginDF["WINNING_MARGIN"]= marginDF["WINNER_VOTES"]- marginDF["RUNNER_VOTES"]
    
    return marginDF
    

def getPCTMarginsDFByYear(year):
    df = pd.read_csv("./Data/KA_Ass_Results.csv")
    
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


def removeSCSTFromName(AC_NAME):
    import re
    AC_NAME = re.sub("\(\s*S[CT]\s*\)","",AC_NAME.upper()).strip()
    return (AC_NAME)


def get_party_color_map():
    import json
    with open('./Data/party_palette.json', 'r') as fp:
        party_color_map = json.load(fp)
    return party_color_map


def getElectionYears():
    rdf = pd.read_csv("./Data/KA_Ass_Results.csv")
    years = rdf["YEAR"].unique()
    return years

    

def getKAPCTMarginsDF():
    import pandas as pd
    el_years = getElectionYears()
    results = []
    
    for year in el_years:
        df = getPCTMarginsDFByYear(year)
        results.append(df)
        
    marginsDF = pd.concat(results)
    
    return marginsDF



