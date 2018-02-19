#### Function to remove the Constistuency category from name
#### For example "AURAD (SC)" will become "AURAD" with this function

def removeSCSTFromName(AC_NAME):
    import re
    AC_NAME = re.sub("\(\s*S[CT]\s*\)","",AC_NAME.upper()).strip()
    return (AC_NAME)

############ Function to get the results of all constistuencies in the
############ the ac_names list for a given year 
def getResultsByYear(year,ac_names):
    import pandas as pd
    import numpy as np
    import math
    
    rdf = pd.read_csv("./Data/KA_Ass_Results.csv")
    
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
    
    results = {"Winners":winners,"Winner Parties": winnerParties,"Winner Votes":winnerVotes, \
              "Runners":runners,"Runner Parties": runnerParties,"Runner Votes":runnerVotes}
    return results
 
####### This function returns the dictionary mapping a political party to a color
def get_party_color_map():
    import json
    with open('./Data/party_palette.json', 'r') as fp:
        party_color_map = json.load(fp)
    return party_color_map


##### Function that returns the years the elections were held
###### returns a list
def getElectionYears():
    rdf = pd.read_csv("./Data/KA_Ass_Results.csv")
    years = rdf["YEAR"].unique()
    return years
    
######### This function returns the list of resutls of all the elections held in Karnataka
######### Note that the list is a list of lists
######### Further the results are for those constituencies listed in 2008 and 2013
def getAllResults():
    years = getElectionYears()
    
    #I am getting the constituency names of the current map here
    mdf = pd.read_pickle("./Maps/KAAssMap.pickle")
    ac_names = list(mdf['AC_NAME'])
    
    allResults = {}
    
    for year in years:
        results = getResultsByYear(year,ac_names)
        allResults[year]=results
    return allResults


############### The main section of the program
import pandas as pd

from bokeh.io import show
from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper,
    CategoricalColorMapper,
    Slider,
    CustomJS
)
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure, output_file

# fetch and clear the document
from bokeh.io import curdoc
curdoc().clear()

#output_file("callback.html")

mdf = pd.read_pickle("./Maps/KAAssMap.pickle")
#ac_names = list(mdf['AC_NAME'])
#results = getResultsByYear(2013,ac_names)

allResults = getAllResults()
results = allResults[2008]

palette.reverse()


ac_xs = [row["LATS"] for index, row in mdf.iterrows()]
ac_ys = [row["LONGS"] for index, row in mdf.iterrows()]

ac_names = [row['AC_NAME'] for index, row in mdf.iterrows() ]
ac_rates = [row['AC_NO'] for index, row in mdf.iterrows()]
color_mapper = LogColorMapper(palette=palette)


party_color_map = get_party_color_map()

parties = []
colors = []

for key,val in party_color_map.items():
    parties.append(key)
    colors.append(val)
    
cc_mapper = CategoricalColorMapper(factors=parties,palette=colors)


source = ColumnDataSource(data=dict(
    x=ac_xs,
    y=ac_ys,
    name=ac_names,
    winner = results["Winners"],
    winnerParty = results["Winner Parties"],
    runner = results["Runners"],
    runnerParty = results["Runner Parties"],
    winnerVotes = results["Winner Votes"],
    runnerVotes = results["Runner Votes"]

))

TOOLS = "pan,box_zoom,reset,hover,save"

p = figure(
    title="Karnataka Assembly Constituencies", 
    tools=TOOLS, toolbar_location="left",
    x_axis_location=None, y_axis_location=None,width=500,height=780,
)
p.grid.grid_line_color = None

p.patches('x', 'y', source=source,
          fill_color={'field': 'winnerParty', 'transform': cc_mapper},
          fill_alpha=0.7, line_color="black", line_width=0.5, \
          legend = 'winnerParty')

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Name", "@name"),
    ("Winner", "@winner"),
    ("Votes","@winnerVotes"),
    ("Party", "@winnerParty"),
    ("Runner Up", "@runner"),
    ("Runner Up Party", "@runnerParty"),
    ("Votes 2","@runnerVotes"),    
    
]

##### The function called by the slider to update the data
def update_data(attrname, old, new):

    # Get the current slider values
    year = slider.value
    global allResults


    if year in allResults.keys():
        results = allResults[year]
   
    # update source with new data
    global source
    source.data = dict(
    x=ac_xs,
    y=ac_ys,
    name=ac_names,
    winner = results["Winners"],
    winnerParty = results["Winner Parties"],
    runner = results["Runners"],
    runnerParty = results["Runner Parties"],
    winnerVotes = results["Winner Votes"],
    runnerVotes = results["Runner Votes"]
    )

slider = Slider(title="YEAR", value=2008, start=1957, end=2013, step=1)
slider.on_change('value', update_data)


#layout = column(slider, p)

#show(layout)
curdoc().add_root(column(slider, p, width=800))
curdoc().title = "Karnataka Assembly Maps"


