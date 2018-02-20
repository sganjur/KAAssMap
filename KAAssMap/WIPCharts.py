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

    results = map_results[year]
    MapSource.data["winner"] = results["Winners"]
    MapSource.data["winnerParty"] = results["Winner Parties"]
    MapSource.data["runner"] = results["Runners"]
    MapSource.data["runnerParty"] = results["Runner Parties"]
    MapSource.data["winnerVotes"] = results["Winner Votes"]
    MapSource.data["runnerVotes"] = results["Runner Votes"]


def update_box_data(year):
    box_source.data = box_dic[year]
    box_plot.x_range.factors = box_source.data['x']


def update_data(attrname, old, new):

    # Get the current slider values
    year = year_slider.value

    if year in party_results.keys():
        update_party_data(year)
        tblSource.data = tbl_dic[year]['source'].data

    if year in map_results.keys():
        update_maps_data(year)

    if year in box_dic:
        update_box_data(year)
    	

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

from bokeh.layouts import gridplot

donuts = gridplot([dnplt1,dnplt2],ncols=2,plot_width=250, plot_height=250,toolbar_location="right")
donuts_box = column(donuts,tblPlt, box_plot)
map_plus_slider = column([MapPlot, year_slider])


master = row([map_plus_slider,donuts_box])
curdoc().add_root(master)
#curdoc().add_root(column(MapPlot,donuts_plus_slider))
curdoc().title = "Karnataka Election Results"

