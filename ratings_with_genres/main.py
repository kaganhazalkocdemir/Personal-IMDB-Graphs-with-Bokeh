import pandas as pd
from bokeh.models import (ColumnDataSource, MultiChoice, Panel, Tabs, SingleIntervalTicker, Select, Dropdown,
						  Div, DataTable, TableColumn, TapTool, Button, CustomJS,
						  RadioButtonGroup, ColorPicker, Spinner)
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.layouts import Row, Column
from bokeh.io import curdoc
from bokeh.events import Tap
from os.path import dirname, join
from tools import type_change, type_change_r, curdocthemes, openfile, full_data, full_data_column

data = openfile()
# split Genres, create a new dataset includes genres_split, Conts (for comparision), your raiting
data['Genres'] = data['Genres'].str.split(',')
data_graph = (data.set_index(['Your Rating', 'Const', 'Title Type', 'Runtime (mins)'])['Genres'].apply(pd.Series)
			  .stack().reset_index().drop('level_4', axis=1).rename(columns={0: 'Genres_split'}))

data_graph['Genres_split'] = data_graph['Genres_split'].str.strip()  # delete spaces
data['Genres'] = [','.join(map(str, l)) for l in data['Genres']]  # revert to str.split for search in genres

genres_list = data_graph.drop_duplicates(subset=["Genres_split"])['Genres_split'].tolist()
types_list = type_change(data_graph.drop_duplicates(subset=["Title Type"])['Title Type'].tolist())

source_graph = ColumnDataSource(data={
	# use conts and drop same movies and count it.
	'ratings': data_graph.drop_duplicates(subset=["Your Rating"])["Your Rating"].sort_values().tolist(),
	'total': data_graph.drop_duplicates(subset=["Const"]).groupby(['Your Rating'])['Const'].count().tolist(),
	'total_lenght': data_graph.drop_duplicates(subset=["Const"]).groupby(['Your Rating'])['Runtime (mins)'].sum().tolist()
})

y_max_t = data_graph.drop_duplicates(subset=["Const"]).groupby(['Your Rating'])['Const'].count().max()
y_max = y_max_t + ((y_max_t * 10) / 100)

source_selected = ColumnDataSource(data=full_data(data, typechange=1))

def update_plot(attr, old, new):
	if multi_choice_genres.value == [] or multi_choice_types.value == []:
		updated_graph_data = {}
	else:
		data_update = (data_graph[(data_graph["Genres_split"].isin(multi_choice_genres.value))
								  & (data_graph["Title Type"].isin(type_change_r(multi_choice_types.value)))]
					   .drop_duplicates(subset=["Const"]).groupby(['Your Rating']))

		updated_graph_data = {
			'ratings': data_graph.drop_duplicates(subset=["Your Rating"])["Your Rating"].sort_values().tolist(),
			'total': data_update['Const'].count().reindex(range(10 + 1), fill_value=0).drop([0, 0]).tolist(),
			'total_lenght' : data_update['Runtime (mins)'].sum().reindex(range(10 + 1), fill_value=0).drop([0, 0]).tolist()
		}

	source_graph.data = updated_graph_data
	selection()

	if select_xaxis.value == 'Total Number':
		graph.glyph.top = 'total'
		p.yaxis.axis_label = 'Total'
		hovertool.tooltips = [("Total", "@total"), ("Score", "@ratings")]
		if multi_choice_genres.value != [] and multi_choice_types.value != []:
			y_max_n = data_update['Const'].count().max() + ((data_update['Const'].count().max() * 10) / 100)
			p.y_range.end = y_max_n  # bokeh sometimes doesnt change range (when select with pan tool), thats why added
	elif select_xaxis.value == 'Total Lenght':
		graph.glyph.top = 'total_lenght'
		p.yaxis.axis_label = 'Total Lenght (mins)'
		hovertool.tooltips = [("Total Lenght (mins)", "@total_lenght"), ("Score", "@ratings")]
		if multi_choice_genres.value != [] and multi_choice_types.value != []:
			y_max_n = data_update['Runtime (mins)'].sum().max() + ((data_update['Runtime (mins)'].sum().max() * 10) / 100)
			p.y_range.end = y_max_n

def tabchanger(dropdownevent):
	if dropdownevent.item == 'graph':
		centerlayout.children = [Column(p, div_message), Column(select_xaxis, tabs)]
		uplayout.children=[div2, dropdown]
		div2.width = 885
	elif dropdownevent.item == 'datatable':
		centerlayout.children = [Column(data_table_swg, div_message), Column(select_xaxis, tabs)]
		uplayout.children = [div2, dropdown]
		div2.width = 885
	elif dropdownevent.item == 'datatable_select':
		centerlayout.children = [data_table_selected]
		uplayout.children = [div2, button_download, dropdown]
		div2.width = 725
	elif dropdownevent.item == 'style':
		stylelayout = Column(Row(div_check, grid_button), Row(bar_color, bar_line_color), Row(bar_alpha, bar_line_alpha),
						   Row(background_color, background_alpha), Row(grid_color, grid_alpha), themeselect)
		centerlayout.children = [stylelayout]
		uplayout.children = [div2, dropdown]
		div2.width = 885

def selection():
	ratinglist = []
	for i in range(len(source_graph.selected.indices)):
		ratinglist.append(source_graph.data['ratings'][source_graph.selected.indices[i]])

	if source_graph.selected.indices:
		tapselection = data['Your Rating'].isin(ratinglist)
		selected = data[(data["Title Type"].isin(type_change_r(multi_choice_types.value))) &
						(data['Genres'].str.contains('|'.join(multi_choice_genres.value))) & (tapselection)]
		div_message.text = """<p>You can look at Selected Ratings in <u>Datatable of Selected</u> tab.</p>
		<p>For multiselect, you can use Shift (Graph, Datatable) and Ctrl (Datatable).</p>"""
	else:
		selected = data[(data["Title Type"].isin(type_change_r(multi_choice_types.value))) &
						(data['Genres'].str.contains('|'.join(multi_choice_genres.value)))]
		div_message.text = ""

	source_selected.data = full_data(selected, typechange=1)

def update_style(attr, old, new):
	if grid_button.active:
		p.xgrid.visible = False
		p.ygrid.visible = False
	else:
		p.xgrid.visible = True
		p.ygrid.visible = True

	if themeselect.value:
		curdoc().theme = themeselect.value
	else:
		p.background_fill_color = background_color.color
		p.background_fill_alpha = background_alpha.value
		p.xgrid.grid_line_color = grid_color.color
		p.ygrid.grid_line_color = grid_color.color
		p.xgrid.grid_line_alpha = grid_alpha.value
		p.ygrid.grid_line_alpha = grid_alpha.value

# plot
p = figure(title="Ratings with Genres/Types", x_axis_label="Ratings", y_axis_label="Total", plot_height=350, tools="save",
		   y_range=(0,y_max), width=650)

hovertool = HoverTool(tooltips=[("Total", "@total"), ("Your Rating", "@ratings")])
p.add_tools(hovertool,TapTool())
p.on_event(Tap, selection)

p.xaxis.ticker = SingleIntervalTicker(interval=1, num_minor_ticks=0)

graph = p.vbar(x='ratings', top='total', source=source_graph, width=0.9, bottom=0, fill_color="blue", line_color="blue",
			   fill_alpha=0.7)

# menu
dropdown_menu = [('Graph', 'graph'), ('Graph Datatable', 'datatable'), ('Datatable of Selected', 'datatable_select'),
				 None, ('Style', 'style')]
dropdown = Dropdown(label="Menu", button_type="warning", menu=dropdown_menu, max_width=150)
dropdown.on_click(tabchanger)

# right-side
select_xaxis = Select(title="X-Axis:", value='Total Number', options=['Total Number', 'Total Lenght'])
select_xaxis.on_change('value', update_plot)

multi_choice_genres = MultiChoice(value=genres_list, options=genres_list, width=400)
multi_choice_genres.on_change('value', update_plot)

multi_choice_types = MultiChoice(value=types_list, options=types_list, width=400)
multi_choice_types.on_change('value', update_plot)

clear_genres = CustomJS(args=dict(s=multi_choice_genres), code="s.value=[]")
clear_types = CustomJS(args=dict(s=multi_choice_types), code="s.value=[]")

button_clear_genres = Button(label="Clear All", button_type="success")
button_clear_genres.js_on_event('button_click', clear_genres)

button_clear_types = Button(label="Clear All", button_type="success")
button_clear_types.js_on_event('button_click', clear_types)

tab1 = Panel(child=Column(multi_choice_genres, button_clear_genres), title="Genres")
tab2 = Panel(child=Column(multi_choice_types, button_clear_types), title="Types")
tabs = Tabs(tabs=[tab1, tab2])

# datatables
columns_swg = [
		TableColumn(field="ratings", title="Ratings"),
		TableColumn(field="total", title="Total"),
		TableColumn(field="total_lenght", title="Total Lenght (mins)")]
data_table_swg = DataTable(source=source_graph, columns=columns_swg, height=240, width=640)
data_table_swg.source.selected.on_change('indices', update_plot)

data_table_selected = DataTable(source=source_selected, columns=full_data_column(), width=1050, height=400)

button_download = Button(label="Download Datatable", button_type="success", max_width=150)
button_download.js_on_click(CustomJS(args=dict(source=source_selected),
									 code=open(join(dirname(__file__), "../download.js")).read()))

div_message = Div(text="")

# style
div_check = Div(text="<p>Grids : </p>")
grid_button = RadioButtonGroup(labels=['On', 'Off'], active=0)
grid_button.on_change("active", update_style)

bar_color = ColorPicker(title="Bar Color")
bar_color.js_link('color', graph.glyph, 'fill_color')

bar_line_color = ColorPicker(title="Bar Line Color")
bar_color.js_link('color', graph.glyph, 'line_color')

bar_alpha = Spinner(title="Bar Alpha", low=0.1, high=1, step=0.1, value=0.7, width=80)
bar_alpha.js_link('value', graph.glyph, 'fill_alpha')

bar_line_alpha = Spinner(title="Bar Line Alpha", low=0.1, high=1, step=0.1, value=1, width=80)
bar_alpha.js_link('value', graph.glyph, 'line_alpha')

background_color = ColorPicker(title="Background Color")
background_color.on_change('color', update_style)

background_alpha = Spinner(title="Background Alpha", low=0.1, high=1, step=0.1, value=1, width=80)
background_alpha.on_change('value', update_style)

grid_color = ColorPicker(title="Grid Color")
grid_color.on_change('color', update_style)

grid_alpha = Spinner(title="Grid Alpha", low=0.1, high=1, step=0.1, value=1, width=80)
grid_alpha.on_change('value', update_style)

themeselect = Select(title="Themes :", value=curdocthemes[0], options=curdocthemes)
themeselect.on_change('value', update_style)

# layout
div = Div(text="", height=1)
div2 = Div(text="", width=885)

centerlayout = Row(children=[Column(p, div_message, sizing_mode='scale_width'), Column(select_xaxis, tabs)], sizing_mode='scale_width')
uplayout = Row(children=[div2, dropdown])

layout = Column(uplayout, div, centerlayout, name="score_wh_genres")

curdoc().add_root(layout)
curdoc().title = 'Imdb Graphs - Ratings with Genres'
