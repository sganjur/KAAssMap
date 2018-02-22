import KAUtils as KAU
import KACharts as KAC
import pandas as pd
from bokeh.plotting import output_notebook, show
from bokeh.layouts import column, gridplot, row

from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    CategoricalColorMapper,
    Slider,
    CustomJS
)

def update_party_data(year):

    if year == 2018:
        return

    df = party_results[year]

    parties = df.loc[df['SEATS_WON']>0]['PARTY'].tolist()
    seats = df.loc[df['SEATS_WON']>0]['SEATS_WON'].tolist()
    votes = df.loc[df['SEATS_WON']>0]['VOTES_WON'].tolist()
    votes_pct = df.loc[df['SEATS_WON']>0]['PCT_VOTES_WON'].tolist()
    sangles,eangles = KAC.getStartsEnds(seats)
    colors = KAC.getPartyColors(parties)

    dnsource1.data['labels']=parties
    dnsource1.data['amounts']=seats
    dnsource1.data['starts']=sangles
    dnsource1.data['ends']=eangles
    dnsource1.data['colors']=colors
    sangles,eangles = KAC.getStartsEnds(votes)

    dnsource2.data['labels']=parties
    dnsource2.data['amounts']=votes_pct
    dnsource2.data['starts']=sangles
    dnsource2.data['ends']=eangles
    dnsource2.data['colors']=colors
    sangles,eangles = KAC.getStartsEnds(votes_pct)


def update_maps_data(year):
    if year == 2018:
        return

    results = map_results[year]
    MapSource.data["winner"] = results["Winners"]
    MapSource.data["winnerParty"] = results["Winner Parties"]
    MapSource.data["runner"] = results["Runners"]
    MapSource.data["runnerParty"] = results["Runner Parties"]
    MapSource.data["winnerVotes"] = results["Winner Votes"]
    MapSource.data["runnerVotes"] = results["Runner Votes"]


def update_box_data(year):

    if year == 2018:
        return

    box_source.data = box_dic[year]
    box_plot.x_range.factors = box_source.data['x']



def update_2018_data():



    #First let's get the full results dataframe for 2018
    df2018 = KAU.getKAResultsByYear(2018)



    #Get the value from modi_slider and set it as modi_pct
    modi_pct = float(modi_slider.value)

    #Transfer votes from various parties to BJP based on modi_pct
    if modi_pct > 0.0:
        df2018 = KAU.inc2bjp(df2018,modi_pct)
        df2018 = KAU.jds2bjp(df2018,modi_pct)
        #df2018 = KAU.ind2bjp(df2018,modi_pct)


    #Get the value from anti_inc_slider and set it as anti_inc_pct
    anti_inc_pct = float(anti_inc_slider.value)
    if anti_inc_pct > 0.0:
        df2018 = KAU.inc2bjp(df2018,anti_inc_pct * 2/3)
        df2018 = KAU.inc2jds(df2018,anti_inc_pct * 1/3)

    

    #Reassign positions based on the votes
    try:
        df2018 = KAU.reassignPositions(df2018)
    except Exception :
        print("Exception in reassignPositions")
    else:
        pass
    finally:
        pass
    
    #Table display stuff
    rdf2018 = KAU.get2018KAPartyResults(df2018)

    party_results2018=rdf2018
    tblStuff2018 = KAC.getKAPartyTblStuff(rdf2018)
    tbl_dic2018 = tblStuff2018

    tblSource.data = tbl_dic2018['source'].data

    #Map Stuff
    results2018 = KAU.get2018Results(df2018)
    
    MapSource.data["winner"] = results2018["Winners"]
    MapSource.data["winnerParty"] = results2018["Winner Parties"]
    MapSource.data["runner"] = results2018["Runners"]
    MapSource.data["runnerParty"] = results2018["Runner Parties"]
    MapSource.data["winnerVotes"] = results2018["Winner Votes"]
    MapSource.data["runnerVotes"] = results2018["Runner Votes"]


    #Box Plot Stuff
    bdf2018 = KAU.get2018PCTMarginsDF(df2018)
    rdf2018 = bdf2018[['WINNER_PARTY',"PCT_MARGIN"]]
    box_data2018 = KAC.buildBoxPlotData(rdf2018)
    box_plot.x_range.factors = box_data2018['x']
    box_source.data = box_data2018


    #Donut chart
    tmpdf = party_results2018
    parties2018 = tmpdf.loc[tmpdf['SEATS_WON']>0]['PARTY'].tolist()
    party_dic2018 = {"Party":parties}
    seats = tmpdf.loc[tmpdf['SEATS_WON']>0]['SEATS_WON'].tolist()
    seats_dic = {"Seats":seats}

    sangles,eangles = KAC.getStartsEnds(seats)
    colors = KAC.getPartyColors(parties)

    dnsource1.data['labels']=parties
    dnsource1.data['amounts']=seats
    dnsource1.data['starts']=sangles
    dnsource1.data['ends']=eangles
    dnsource1.data['colors']=colors
    
    

    
    return


def update_data(attrname, old, new):

    # Get the current slider values
    year = year_slider.value

    if year == 2018:
        update_2018_data()
        return

    if year in party_results.keys():
        update_party_data(year)
        tblSource.data = tbl_dic[year]['source'].data

    if year in map_results.keys():
        update_maps_data(year)

    if year in box_dic:
        update_box_data(year)
    	





#######################################
#######################################
############ Main Stuff Begins
##################################

# fetch and clear the document
from bokeh.io import curdoc
curdoc().clear()

MapDF = KAU.getMapDF()

el_years = KAU.getElectionYears()

ac_names = KAU.getAC_Names()

map_results = {}
party_results = {}
box_dic = {}

for year in el_years:
    bdf = KAU.getPCTMarginsDFByYear(year)
    rdf = bdf[['WINNER_PARTY',"PCT_MARGIN"]]
    box_data = KAC.buildBoxPlotData(rdf)
    box_dic[year]=box_data

box_plot,box_source = KAC.Boxplot(box_dic[2008],"Spread of Victory Margins","Parties","Victor Margin(%)")

for year in el_years:
    result = KAU.getResultsByYear(year,ac_names)
    map_results[year] = result

MapPlot, MapSource = KAC.KAAssMap(MapDF,map_results[2008])

party_results = {}
tbl_dic = {}

for year in el_years:
    rdf = KAU.getKAPartyResultsByYear(year)
    party_results[year]=rdf
    tblStuff = KAC.getKAPartyTblStuff(rdf)
    tbl_dic[year] = tblStuff

df = party_results[2008]

tblPlt, tblSource = KAC.TableDisplay(tbl_dic[2008])

parties = df.loc[df['SEATS_WON']>0]['PARTY'].tolist()
party_dic = {"Party":parties}
seats = df.loc[df['SEATS_WON']>0]['SEATS_WON'].tolist()
seats_dic = {"Seats":seats}

dnplt1, dnsource1 = KAC.DonutChart(party_dic,seats_dic,"Seat Shares")

parties = df.loc[df['SEATS_WON']>0]['PARTY'].tolist()
party_dic = {"Party":parties}
votes_pct = df.loc[df['SEATS_WON']>0]['PCT_VOTES_WON'].tolist()
votes_pct_dic = {"Votes Pct":votes_pct}


dnplt2, dnsource2 = KAC.DonutChart(party_dic,votes_pct_dic,"% Votes Shares")

year_slider = Slider(start=1957, end=2018, value=2008, step=1,title="Year")
year_slider.on_change('value', update_data)

modi_slider = Slider(start=0.0, end=5.0, value=0.0, step=1,title="Modi Factor")
modi_slider.on_change('value', update_data)

anti_inc_slider = Slider(start=0.0, end=3.0, value=0.0, step=1,title="Anti Incumbency Factor")
anti_inc_slider.on_change('value', update_data)

sliders = column([year_slider,modi_slider,anti_inc_slider])
from bokeh.layouts import gridplot

donuts = gridplot([tblPlt,dnplt1],ncols=2,plot_width=275, plot_height=275,toolbar_location="right")
donuts_box = column(donuts, box_plot)
map_plus_sliders = column([MapPlot, sliders])


master = row([map_plus_sliders,donuts_box])
curdoc().add_root(master)
#curdoc().add_root(column(MapPlot,donuts_plus_slider))
curdoc().title = "Karnataka Election Results"

