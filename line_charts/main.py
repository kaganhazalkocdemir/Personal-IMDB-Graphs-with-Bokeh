import pandas as pd
from tools import openfile
from bokeh.models import ColumnDataSource, Legend, LegendItem, HoverTool, RangeTool, Select, Toggle
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import viridis
from bokeh.layouts import Column, Row
# source prep
data = openfile()
data['rated_year'] = data['Date Rated'].str.split('-').apply(pd.Series).rename(columns={0: 'rated_year'})['rated_year']
data['Genres'] = data['Genres'].str.split(',')

data_gn = (data.set_index(['Your Rating', 'Const', 'Title Type', 'Year', 'rated_year'])['Genres'].apply(pd.Series)
		   .stack().reset_index().drop('level_5', axis=1).rename(columns={0: 'Genres_split'})
		   .astype({'Year': int, 'rated_year': int}))
data_gn['Genres_split'] = data_gn['Genres_split'].str.strip()

genres = data_gn.drop_duplicates('Genres_split')['Genres_split'].sort_values().tolist()
types = data_gn.drop_duplicates('Title Type')['Title Type'].sort_values().tolist()
years = sorted(data_gn['Year'].unique().tolist())
years_n = sorted(data_gn['rated_year'].unique().tolist())
colors_genres = viridis(len(genres))
colors_types = viridis(len(types))

def datacreater(gentype, year):
	'''
	gentype -> 0: Genres, 1: Types
	year    -> 0: Year, 1: rated_year
	'''
	if year == 0:
		year = 'Year'
		years_d = sorted(data_gn[year].unique().tolist())
	elif year == 1:
		year = 'rated_year'
		years_d = sorted(data_gn[year].unique().tolist())
	if gentype == 0:
		en, gen = genres, 'Genres_split'
	elif gentype == 1:
		en, gen = types, 'Title Type'
	genres_data = {'Year': data_gn.drop_duplicates(year)[year].sort_values().values.tolist()}
	for i, n in enumerate(en):
		genres_data[n] = (data_gn[data_gn[gen] == n].drop_duplicates('Const').groupby(year)['Const'].count()
						  .reindex(years_d).fillna(0).values.astype(int).tolist())
	genres_data['total'] = data_gn.drop_duplicates('Const').groupby(year)['Const'].count().apply(pd.Series).cumsum().values.tolist()
	return genres_data

def rmax(x,y):
	getmax = datacreater(x,y)
	getmax.pop('Year')
	getmax.pop('total')
	count_max = max([max(getmax[n]) for i, n in enumerate(getmax)])
	return count_max

def update_plot(attr, old, new):
	if select_xaxis.value == 'Production Year':
		genres_source.data = datacreater(0,0)
		types_source.data = datacreater(1,0)
		p.x_range.start, p.x_range.end, p.y_range.start = min(years), max(years), 0
		if select_type.value == 'Genres':
			p.y_range.end = rmax(0,0) + 2
		else:
			p.y_range.end = rmax(1,0) + 2
	else:
		genres_source.data = datacreater(0,1)
		types_source.data = datacreater(1,1)
		p.x_range.start, p.x_range.end, p.y_range.start = min(years_n), max(years_n), 0
		if select_type.value == 'Genres':
			p.y_range.end = rmax(0,1) + 2
		else:
			p.y_range.end = rmax(1,1) + 2

	if select_type.value == 'Genres':
		for i in range(len(types)):
			types_lines[i].visible = False
		for i in range(len(genres)):
			genres_lines[i].visible = True
		legend.visible, legend2.visible, legend_types.visible = True, True, False
	else:
		for i in range(len(types)):
			types_lines[i].visible = True
		for i in range(len(genres)):
			genres_lines[i].visible = False
		legend.visible, legend2.visible, legend_types.visible = False, False, True

	if add_total.active:
		if select_type.value == 'Genres':
			total_line.visible, totalselect.visible = True, True
			legendtotal.items[0].visible = True
		else:
			total_line2.visible, totalselect2.visible = True, True
			legendtotal.items[1].visible = True
	else:
		if select_type.value == 'Genres':
			total_line.visible, totalselect.visible = False, False
			legendtotal.items[0].visible = False
		else:
			total_line2.visible, totalselect2.visible = False, False
			legendtotal.items[1].visible = False

	p.xaxis.axis_label = select_xaxis.value
	p.title.text = 'Total Productions You Watched by ' + str(select_xaxis.value)

genres_source = ColumnDataSource(data=datacreater(0,0))
types_source = ColumnDataSource(data=datacreater(1,0))

# figure
p = figure(width=900, height=400, title="Total Productions You Watched by Production Year", toolbar_location='above',
		   x_range=(min(years), max(years)+0.2), x_axis_label="Production Year", y_axis_label="Total Movie",
		   y_range=(0,rmax(0,0)+2))

genres_lines, legenditems, types_lines, legendtitems = {}, [], {}, []
for i, n in enumerate(genres):
	genres_lines[i] = p.line(y=n, x='Year', color=colors_genres[i], source=genres_source, line_width=1.3,
							 hover_color=colors_genres[i], visible=True)
	legenditems.append(LegendItem(label=n, renderers=[genres_lines[i]]))

for i, n in enumerate(types):
	types_lines[i] = p.line(y=n, x='Year', color=colors_types[i], source=types_source, line_width=1.3,
							 hover_color=colors_types[i], visible=False)
	legendtitems.append(LegendItem(label=n, renderers=[types_lines[i]]))

total_line = p.line(y='total', x='Year', color='orange', source=genres_source, line_width=1.3, hover_color='orange', visible=False)
total_line2 = p.line(y='total', x='Year', color='orange', source=types_source, line_width=1.3, hover_color='orange', visible=False)

# legend
legend = Legend(items=legenditems[:round(len(legenditems)/2)], orientation='vertical', location=(0,0), click_policy='mute',
				title_standoff=1, border_line_width=1, margin=1, padding=0, spacing=9, border_line_color='white')
legend2 = Legend(items=legenditems[round(len(legenditems)/2):], orientation='vertical', location=(0,0), click_policy='mute',
				 title_standoff=1, border_line_width=1, margin=1, padding=0, spacing=9, border_line_color='white')

legendtotal = Legend(items=[LegendItem(label='Total', renderers=[total_line], visible=False),
							LegendItem(label='Total', renderers=[total_line2], visible=False)], location='top_left')

legend_types = Legend(items=legendtitems, visible=False, click_policy='mute', title_standoff=1, border_line_width=1,
					  margin=1, padding=0, spacing=9, border_line_color='white')

p.add_layout(legend2, 'left')
p.add_layout(legend, 'left')
p.add_layout(legendtotal)
p.add_layout(legend_types, 'left')

# range-select tool
select = figure(title="Select Range", height=130, width=900, y_range=p.y_range, y_axis_type=None,
				tools="", toolbar_location=None, background_fill_color="#efefef")

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

for i,n in enumerate(genres):
	select.line('Year', n, source=genres_source, color='grey')
totalselect = select.line('Year', 'total', source=genres_source, color='black', visible=False)
totalselect2 = select.line('Year', 'total', source=types_source, color='black', visible=False)

select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool

# right-side
select_type = Select(title="Graph Type", value="Genres", options=["Genres", "Types"])
select_type.on_change('value', update_plot)

select_xaxis = Select(title="X-Axis", value="Production Year", options=["Production Year", "Rated Year"])
select_xaxis.on_change('value', update_plot)

add_total = Toggle(label="Add Total Line", button_type="success")
add_total.on_change('active', update_plot)

layout=Column(Row(p, Column(select_type, select_xaxis, add_total)), select, name="linecharts")
curdoc().add_root(layout)
curdoc().title = 'Imdb Graphs - Line Charts'
