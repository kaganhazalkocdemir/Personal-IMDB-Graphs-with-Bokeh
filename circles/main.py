import pandas as pd
from bokeh.io import curdoc, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Slider, HoverTool, Select, HoverTool, Legend, LegendItem, Button
from bokeh.layouts import Row, Column
from bokeh.palettes import Spectral, viridis
from tools import openfile, type_change
data = openfile()
'''
There are group of circle gylphs instead of CategorialMapper feature. It's because when we use CategorialMapper, we could create groups,
however legend looks like one piece if you want to use "mute". So, you have to create different legend groups if you want to use this function.
'''
# source prep
data['rated_year'] = data['Date Rated'].str.split('-').apply(pd.Series).rename(columns={0: 'rated_year'})['rated_year']
data['Genres'] = data['Genres'].str.split(',')

data_yt = (data.groupby(['rated_year', 'Title Type'])['Title Type'].count().apply(pd.Series).rename(columns={0: 'count'})
		   .unstack(fill_value=0).stack().reset_index().astype({'rated_year': int}))

data_gn_raw = (data.set_index(['Title Type', 'Const', 'rated_year', 'Your Rating'])['Genres'].apply(pd.Series)
		   .stack().reset_index().drop('level_4', axis=1).rename(columns={0: 'Genres_split'})
		   .astype({'rated_year': int}))
data_gn_raw['Genres_split'] = data_gn_raw['Genres_split'].str.strip()

data_gn = (data_gn_raw.groupby(['rated_year', 'Genres_split'])['Genres_split'].count().apply(pd.Series).rename(columns={0: 'count'})
		   .unstack(fill_value=0).stack().reset_index())

data_yt['mean'] = (data.groupby(['rated_year', 'Title Type'])['Your Rating'].mean().apply(pd.Series).rename(columns={0: 'mean'})
						.unstack(fill_value=0).stack().reset_index()['mean'])

data_gn['mean'] = (data_gn_raw.groupby(['rated_year', 'Genres_split'])['Your Rating'].mean().apply(pd.Series).rename(columns={0: 'mean'})
					.unstack(fill_value=0).stack().reset_index()['mean'])


data_yt['Title Type'] = data_yt['Title Type'].apply(type_change)
years = sorted(data_yt['rated_year'].unique())
types = data_yt.drop_duplicates('Title Type')['Title Type'].tolist()
genres = sorted(data_gn_raw['Genres_split'].unique().tolist())

yrange_min = data_yt[data_yt['rated_year'] == years[0]]['mean'].min()
yrange_max = data_yt[data_yt['rated_year'] == years[0]]['mean'].max()*2
colors = Spectral[len(types)]
colors_g = viridis(len(genres))

def datacreater(data, year, size):
	'''
	data -> 0: Types, 1:Genres
	year -> 0: min,   1:slider
	size -> 0: mean   1:size
	'''
	if data==0:
		datavar, datahead, datains = types, data_yt, 'Title Type'
	elif data==1:
		datavar, datahead, datains = genres, data_gn, 'Genres_split'
	if year==0:
		yearin = years[0]
	elif year==1:
		yearin = slider_years.value
	datadict={}
	for i, n in enumerate(datavar):
		if size == 0:
			size_s = datahead[(datahead[datains] == n) & (datahead['rated_year'] == yearin)]['mean'] * 3
		elif size == 1:
			size_s = datahead[(datahead[datains] == n) & (datahead['rated_year'] == yearin)]['count']
		datadict[n] = {
			'mean': datahead[(datahead[datains] == n) & (datahead['rated_year'] == yearin)]['mean'],
			'count': datahead[(datahead[datains] == n) & (datahead['rated_year'] == yearin)]['count'],
			'type': datahead[(datahead[datains] == n) & (datahead['rated_year'] == yearin)][datains],
			'size': size_s}
	return datadict

def update_plot(attr, old, new):
	if select_size.value == 'Mean':
		yr = data_yt[data_yt['rated_year'] == slider_years.value]['count']
		yr_min = yr.min()-10
		yr_max = yr.max()+50
		p.y_range.start, p.y_range.end = yr_min, yr_max
	else:
		yr = data_yt[data_yt['rated_year'] == slider_years.value]['count']
		yr_min = yr.min()-10
		yr_max = yr.max()+(yr.max()/2)
		p.y_range.start, p.y_range.end = yr_min, yr_max

	if select_type.value == 'Types':
		data_t1, data_t2 = datacreater(0, 1, 0), datacreater(0, 1, 1)
		for i, n in enumerate(types):
			circles[n].visible = True
			if select_size.value == 'Mean':
				source_types[n].data = data_t1[n]
			else:
				source_types[n].data = data_t2[n]
		for i, n in enumerate(genres):
			circles_g[n].visible = False
		p.title.text = 'Movies You Watched by Types'
		legend.visible, legend2.visible, legend3.visible = True, False, False
	else:
		data_g1, data_g2 = datacreater(1, 1, 0), datacreater(1, 1, 1)  # function come out of loop bc of performance
		for i, n in enumerate(genres):
			circles_g[n].visible = True
			if select_size.value == 'Mean':
				source_genres[n].data = data_g1[n]
			else:
				source_genres[n].data = data_g2[n]
		for i, n in enumerate(types):
			circles[n].visible = False
		p.title.text = 'Movies You Watched by Genres'
		legend.visible, legend2.visible, legend3.visible = False, True, True

def animate_update():
    year = slider_years.value + 1
    if year > years[-1]:
        year = years[0]
    slider_years.value = year

def animate():
    global callback_id
    if button_play.label == '► Play':
        button_play.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 500)
    else:
        button_play.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)

p = figure(title='Movies You Watched by Types', plot_height=400, plot_width=700, y_range=(yrange_min, yrange_max),
		   x_axis_label="Mean", y_axis_label="Total Movie")

circles, source_types, legenditems = {}, {}, []
circles_g, source_genres, legenditems_g = {}, {}, []
data_t = datacreater(0,0,0)
for i, n in enumerate(types):
	source_types[n] = ColumnDataSource(data=data_t[n])
	circles[n] = p.circle(x='mean', y='count', fill_alpha=0.8, source=source_types[n], size='size', color=colors[i], visible=True)
	legenditems.append(LegendItem(label=n, renderers=[circles[n]]))

data_g=datacreater(1,0,0)
for i, n in enumerate(genres):
	source_genres[n] = ColumnDataSource(data=data_g[n])
	circles_g[n] = p.circle(x='mean', y='count', fill_alpha=0.8, source=source_genres[n], size='size', color=colors_g[i], visible=False)
	legenditems_g.append(LegendItem(label=n, renderers=[circles_g[n]]))

# tools
hoverrenderers=[circles[b] for a, b in enumerate(types)] + [circles_g[b] for a, b in enumerate(genres)]
hovertool = HoverTool(renderers=hoverrenderers, tooltips=[('Type', '@type'), ('Mean', '@mean'), ('Count', '@count')])
p.add_tools(hovertool)

legend = Legend(items=legenditems, click_policy='mute')

legend2 = Legend(items=legenditems_g[:round(len(legenditems_g)/2)], orientation='vertical', location=(0,0),
				click_policy='mute', title_standoff=1, border_line_width=1, margin=1, padding=0, spacing=9, visible=False)
legend3 = Legend(items=legenditems_g[round(len(legenditems_g)/2):], orientation='vertical', location=(0,0),
				 click_policy='mute', title_standoff=1, border_line_width=1, margin=1, padding=0, spacing=9, visible=False)

p.add_layout(legend, 'left')
p.add_layout(legend3, 'left')
p.add_layout(legend2, 'left')

# right-side
slider_years = Slider(start=years[0], end=years[-1], step=1, value=years[0], title='Year')
slider_years.on_change('value', update_plot)

select_size = Select(title="Size of Circles by", value="Mean", options=["Count", "Mean"])
select_size.on_change('value', update_plot)

select_type = Select(title="Graph Type", value="Types", options=["Types", "Genres"])
select_type.on_change('value', update_plot)

button_play = Button(label='► Play')
button_play.on_click(animate)

callback_id = None  # for play animation

curdoc().add_root(Row(p, Column(slider_years, select_size, select_type, button_play), name='circles'))
curdoc().title = 'Imdb Graphs - Scatter with Genres and Types'