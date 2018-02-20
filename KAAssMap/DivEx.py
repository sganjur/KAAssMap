from bokeh.io import output_notebook, show, output_file, curdoc
from bokeh.layouts import widgetbox, column
from bokeh.models.widgets import Paragraph, Slider

curdoc().clear()
output_file("div.html")
output_notebook()
def update_data(attr, old, new):
	year = year_slider.value

	if year_slider == 2013:

		p = Paragraph(text="""New Text New Text.""",
	width=200, height=100)

p = Paragraph(text="""Your text is initialized with the 'text' argument.  The
remaining Paragraph arguments are 'width' and 'height'. For this example, those values
are 200 and 100 respectively.""",
width=200, height=100)

year_slider = Slider(start=1957, end=2018, value=2008, step=1,title="Year")
year_slider.on_change('value', update_data)


master = column(p,year_slider)
curdoc().add_root(master)

show(widgetbox(p))