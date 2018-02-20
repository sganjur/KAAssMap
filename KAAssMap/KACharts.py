import KAUtils as KAU
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource, CategoricalColorMapper, Slider, Legend, LegendItem
from bokeh.plotting import figure
from bokeh.layouts import column, gridplot, row,layout
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.io import curdoc


pc_map = KAU.get_party_color_map()

def getPartyColors(parties_list):
    
    colors = []
    for party in parties_list:
        colors.append(pc_map[party])
    
    return colors

def getStartsEnds(value_list):
    import math
    
    val_sum = sum(value_list)
    starts = []
    ends = []
    
    sa=0
    ea=0

    for val in value_list:
        sa = ea 
        ea = sa+val * 2 * math.pi / val_sum
        starts.append(sa)
        ends.append(ea)
    return starts,ends


def DonutChart(lab_dic,amt_dic,title):

    from bokeh.layouts import layout 
    from bokeh.models import ( 
      HoverTool, ColumnDataSource, Legend, LegendItem, Text
    ) 
    from bokeh.plotting import figure 
    from bokeh.palettes import brewer 
    from numpy import pi  
    
    for key,val in lab_dic.items():
        hv1 = key
        labels = val
        
    for key,val in amt_dic.items():
        hv2 = key
        amounts = val
    
    sangles,eangles = getStartsEnds(amounts)
    
    colors = getPartyColors(labels)    
     
    source=ColumnDataSource(dict(starts=sangles, ends=eangles,\
                                 labels=labels, amounts=amounts,colors=colors)) 

    plot =  figure(toolbar_location="right") 

    hover = HoverTool( 
            tooltips=[ 
              (hv1, '@labels'), 
              (hv2,'@amounts') 
            ] 
        ) 
    plot.add_tools(hover) 
    
    glyph=Text(text=[title],\
               text_align="center",text_baseline="middle",\
               text_color="#774422",text_font_style="bold",text_font_size="10pt")
    
    plot.add_glyph(glyph)

    r = plot.annular_wedge(0, 0, start_angle='starts', end_angle='ends',\
                           color='colors', inner_radius=0.7, outer_radius=0.8,\
                           source=source) 
       
    plot.axis.visible = False
    plot.grid.visible = False

    
    return plot, source



def DonutChartWithLegend(lab_dic,amt_dic,title):

    from bokeh.layouts import layout 
    from bokeh.models import ( 
      HoverTool, ColumnDataSource, Legend, LegendItem, Text
    ) 
    from bokeh.plotting import figure 
    from bokeh.palettes import brewer 
    from numpy import pi  
    
    for key,val in lab_dic.items():
        hv1 = key
        labels = val
        
    for key,val in amt_dic.items():
        hv2 = key
        amounts = val
    
    sangles,eangles = getStartsEnds(amounts)
    
    colors = getPartyColors(labels)    
     
    source=ColumnDataSource(dict(starts=sangles, ends=eangles,\
                                 labels=labels, amounts=amounts,colors=colors)) 

    plot =  figure(toolbar_location="right") 

    hover = HoverTool( 
            tooltips=[ 
              (hv1, '@labels'), 
              (hv2,'@amounts') 
            ] 
        ) 
    plot.add_tools(hover) 
    
    glyph=Text(text=[title],\
               text_align="center",text_baseline="middle",\
               text_color="#774422",text_font_style="bold",text_font_size="10pt")
    
    plot.add_glyph(glyph)

    r = plot.annular_wedge(0, 0, start_angle='starts', end_angle='ends',\
                           color='colors', inner_radius=0.7, outer_radius=0.8,\
                           source=source) 
  
    legend = Legend(items=[LegendItem(label=dict(field="labels"), \
                                      renderers=[r])], location=(0, 0)) 
    plot.add_layout(legend, 'right') 
    
    plot.axis.visible = False
    plot.grid.visible = False

    
    return plot, source

def KAAssMap(mapdf,results):
    import pandas as pd
    import KAUtils as KAU

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
    
    from bokeh.plotting import figure
    
    mdf = mapdf
    results = results


    ac_xs = [row["LATS"] for index, row in mdf.iterrows()]
    ac_ys = [row["LONGS"] for index, row in mdf.iterrows()]

    ac_names = [row['AC_NAME'] for index, row in mdf.iterrows() ]
    ac_rates = [row['AC_NO'] for index, row in mdf.iterrows()]


    party_color_map = KAU.get_party_color_map()

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

    # The tool bar
    TOOLS = "pan,box_zoom,reset,hover,save,tap"
    
    # Let us actually instantiate the figure
    plot = figure(
        title="Karnataka Assembly Constituencies", tools=TOOLS,toolbar_location="left",width=500, height=675,
        x_axis_location=None, y_axis_location=None
    )

    #We are not interested in the grids
    plot.grid.grid_line_color = None
    plot.grid.visible = False

    #Now is the time to actually draw the map
    plot.patches('x', 'y', source=source,
              fill_color={'field': 'winnerParty', 'transform': cc_mapper},
              fill_alpha=0.7, line_color="black", line_width=0.5,legend = 'winnerParty')
    
    # Set up the tooltip items for hover display
    hover = plot.select_one(HoverTool)
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

    return plot, source


    
###################################
###################################################
###### Boxplot stufff
####################################
####################################################
def buildBoxPlotData(rdf):
    col_names = list(rdf)
    cat_name = col_names[0]

    #First let us sort the dataframe by values in the first column
    rdf = rdf.sort_values(by=[cat_name])

    value_name = col_names[1]
    cats = rdf[cat_name].unique().tolist()
    
    # find the quartiles and IQR for each category
    groups = rdf.groupby(cat_name)
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr

    # find the outliers for each category
    def outliers(group):
        category = group.name
        return group[(group[value_name] > upper.loc[category][value_name]) | (group[value_name] < lower.loc[category][value_name])][value_name]

    out = groups.apply(outliers).dropna()

    outx = []
    outy = []

    if not out.empty:
        for cat in cats:
            # only add outliers if they exist
            if not out.loc[cat].empty:
                for value in out[cat]:
                    outx.append(cat)
                    outy.append(value)
                    
    #Now let us fix the length of the outliers to match with length of cats
    #This is needed because it seems to impact the rendering of chart
    #Specifically while rendering via bokeh serve
    
    diff = len(cats) - len(out)
    
    if diff > 0:
        #print("OUT is lesser")
        #We need to add dummys to out
        i=0
        while i < diff:
            outx.append(np.nan)
            outy.append(np.nan)
            i +=1
    elif diff < 0:   
        #We need to remove the rows from out
        print("OUT is higher")
        i=0
        while i > diff:
            del (outx[-1])
            del (outy[-1])
            i -= 1
    
    #Now let us fix the upper and lower values
    # They can't be more than 100 or less than 0
    
    
    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper[value_name] = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,value_name]),upper[value_name])]
    lower[value_name] = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,value_name]),lower[value_name])]


    box_stuff =dict(
        x=cats, 
        upper = upper[value_name],
        lower = lower[value_name],
        upper_bottom=q2[value_name],
        upper_top=q3[value_name],
        lower_bottom=q1[value_name],
        lower_top=q2[value_name],
        outx = outx,
        outy = outy
    )
    
    return box_stuff




############# The Boxplot

def Boxplot(bx_source,title,x_label, y_label):
    
    party_color_map = KAU.get_party_color_map()

    prts = []
    clrs = []

    for key,val in party_color_map.items():
        prts.append(key)
        clrs.append(val)
    
    source = ColumnDataSource(data=bx_source)
    title = title
    x_label = x_label
    y_label = y_label
    
    cc_mapper = CategoricalColorMapper(factors=prts,palette=clrs)
   
    p = figure(tools="save", title="",width=500,height=300,x_range=[])
    p.x_range.factors = source.data['x']
    p.segment(source=source, x0 ='x', y0='upper', x1='x', y1='upper_top', line_color="black")
    p.segment(source=source, x0='x',y0='lower', x1='x', y1='lower_bottom', line_color="black")


    # Add the upper and lower quartiles
    l=p.vbar(source = source, x='x', width=0.7, bottom='upper_bottom', top='upper_top', \
             fill_color={'field': 'x','transform': cc_mapper}, line_color="black")
    p.vbar(source = source, x='x', width=0.7, bottom='lower_bottom', top='lower_top', \
           fill_color={'field': 'x','transform': cc_mapper}, line_color="black")
    
    # whiskers (almost-0 height rects simpler than segments)
    p.rect(source = source, x='x', y='lower', width=0.2, height=0.01, line_color="black")
    p.rect(source = source, x='x', y='upper', width=0.2, height=0.01, line_color="black")

    # outliers
    p.circle(source = source, x='outx', y='outy', size=6, color={'field': 'outx','transform': cc_mapper}, fill_alpha=0.6)

    #legend = Legend(items=[LegendItem(label=dict(field="x"), renderers=[l])])
    #p.add_layout(legend, 'below')
    #p.legend.location = (100,10)

    # Setup plot titles and such.
    p.title.text = title
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="8pt"
    p.xaxis.major_label_orientation = np.pi/4
    p.xaxis.axis_label=x_label
    p.yaxis.axis_label=y_label
    
    return p, source



###################################################################
##################################################
####### TableDisplay related functions
########
#### This function generates the TblStuff for displaying KA Party results for a particular year
#### We will display PARTY, SEATS_WON and PCT_VOTES_WON fields from the given DataFrame
def getKAPartyTblStuff(df):
    
    pdf = df.copy()
    pdf = pdf.loc[pdf['SEATS_WON'] > 0]
    pdf = pdf.sort_values(by=['SEATS_WON','PARTY'],ascending=[False,True])
    
    data = dict (
        labels=pdf['PARTY'].tolist(),
        values1=pdf['SEATS_WON'],
        values2=pdf['PCT_VOTES_WON']
    )
  
    source = ColumnDataSource(data)

    columns = [
        TableColumn(field="labels", title="Party"),
        TableColumn(field="values1", title="Seats Won"),
        TableColumn(field="values2", title="% Vote Share"),
    ]
    
    tblStuff = {"source":source, "columns":columns}
    
     
    return tblStuff

def TableDisplay(tblStuff):
    source = tblStuff['source']
    columns = tblStuff['columns']
    data_table = DataTable(source=source, columns=columns, width=400, height=200)
    return data_table, source


