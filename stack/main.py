from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.palettes import Category20, viridis, cividis
from bokeh.layouts import Row, Column
from bokeh.models import (ColumnDataSource, FactorRange, RangeSlider, Legend, MultiChoice, Select, Legend, LegendItem,
						  Div, Button)
import pandas as pd
from tools import openfile, type_change, type_change_r

# data preperation
data = openfile()

# dp - types selection
data_yt = (data.groupby(['Year', 'Title Type'])['Title Type'].count().apply(pd.Series).rename(columns={0: 'total'})
		   .unstack(fill_value=0).stack().reset_index())

# dp - genres
data['Genres'] = data['Genres'].str.split(',')
data_gn = (data.set_index(['Const', 'Year'])['Genres'].apply(pd.Series).stack().reset_index().drop('level_2', axis=1)
		   .rename(columns={0: 'Genres_split'}))
data_gn['Genres_split'] = data_gn['Genres_split'].str.strip()
data_gn = (data_gn.groupby(['Year', 'Genres_split'])['Genres_split'].count().apply(pd.Series)
		   .rename(columns={0: 'total'}).unstack(fill_value=0).stack().reset_index())

ymax_yt = data_yt.groupby('Year')['total'].sum().max() + 40
y_max_gn = data_gn.groupby('Year')['total'].sum().max() + 40

# source
years_int = data_yt.drop_duplicates(subset='Year')['Year']
y_min, y_max = years_int.min(), years_int.max()
years = years_int.apply(str).tolist()
types = type_change(data_yt.drop_duplicates(subset='Title Type')['Title Type'].tolist())
colors_years = Category20[len(types)]

genres = data_gn.drop_duplicates(subset='Genres_split')['Genres_split'].tolist()
colors_genres = viridis(len(genres))

types_data = {'years': years}
for i, n in enumerate(data_yt.drop_duplicates('Title Type')['Title Type']):
	types_data[type_change(n)] = data_yt[data_yt['Title Type'] == n]['total'].tolist()
types_source = ColumnDataSource(data=types_data)

genres_data = {'years': years}
for i, n in enumerate(data_gn.drop_duplicates('Genres_split')['Genres_split']):
	genres_data[n] = data_gn[data_gn['Genres_split'] == n]['total'].tolist()
genres_source = ColumnDataSource(data=genres_data)

def update_plot(attr, old, new):
	global g_value
	g_value = g_select.value
	# range update
	y_min, y_max = slider_years.value[0], slider_years.value[1]
	new_range = [str(x) for x in years_int.tolist() if y_min <= x <= y_max]
	xr_factors.factors = new_range

	# update data
	if g_select.value == 'Genres':
		# update visibility
		for i in range(len(stack_genres_names)):
			stack_genres_names[i].visible = True
		for i in range(len(stack_types_names)):
			stack_types_names[i].visible = False
		genres_choice.visible = True
		type_choice.visible = False
		type_legend.visible = False
		text.visible = True
		p.y_range.end = y_max_gn

		# update the genres data
		updated_data = {'years': years}
		for i, n in enumerate(genres_choice.value):
			updated_data[n] = data_gn[data_gn['Genres_split'] == n]['total'].tolist()
		genres_source.data = updated_data
	else:
		# update visibility
		for i in range(len(stack_genres_names)):
			stack_genres_names[i].visible = False
		for i in range(len(stack_types_names)):
			stack_types_names[i].visible = True
		genres_choice.visible = False
		type_choice.visible = True
		type_legend.visible = True
		text.visible = False
		p.y_range.end = ymax_yt

		# update type data
		updated_data = {'years': years}
		for i, n in enumerate(type_choice.value):
			updated_data[n] = data_yt[data_yt['Title Type'] == type_change_r(n)]['total'].tolist()
			type_legend.items[types.index(n)].visible = True
		types_source.data = updated_data

		# update type legend
		nontypes = list(set(types) - set(type_choice.value))
		for i, n in enumerate(nontypes):
			type_legend.items[types.index(n)].visible = False

def clearall():
	try:
		if g_value == 'Genres':
			genres_choice.value = []
		else:
			type_choice.value = []
	except NameError:
		type_choice.value = []


# figure
xr_factors = FactorRange(factors=years)
p = figure(x_range=xr_factors, width=800, height=400, title="Productions by Year",
		   toolbar_location=None, tools="hover", tooltips="$name @years: @$name", y_range=(0, ymax_yt))

stack_types = p.vbar_stack(types, x='years', width=0.9, color=colors_years, source=types_source)
stack_genres = p.vbar_stack(genres, x='years', width=0.9, color=colors_genres, source=genres_source, visible=False)

stack_genres_names, stack_types_names = {}, {}
for i, n in enumerate(stack_genres):
	stack_genres_names[i] = n
for i, n in enumerate(stack_types):
	stack_types_names[i] = n

type_legend_i = []
for i, n in enumerate(types):
	type_legend_i.append(LegendItem(label=n, renderers=[stack_types_names[i]]))
'''for i, n in enumerate(genres):
	genres_legend_i.append(LegendItem(label=n, renderers=[stack_genres_names[i]]))'''

type_legend = Legend(items=type_legend_i, click_policy="mute", orientation='horizontal', location='top_left',
					 visible=True)
'''genres_legend = Legend(items=genres_legend_i, click_policy="mute", visible=True, orientation='vertical',
					   glyph_height=5, label_height=5, location=(0,-60))'''

p.add_layout(type_legend)

p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.xaxis.major_label_orientation = 0.92

# right-side
g_select = Select(value="Types", options=["Types", "Genres"], title="Graph Type")
g_select.on_change('value', update_plot)

slider_years = RangeSlider(start=y_min, end=y_max, value=(y_min, y_max), step=1, title="Years")
slider_years.on_change('value', update_plot)

type_choice = MultiChoice(value=types, options=types, title='Types :', visible=True)
type_choice.on_change('value', update_plot)

genres_choice = MultiChoice(value=genres, options=genres, title='Genres :', visible=False)
genres_choice.on_change('value', update_plot)

text = Div(text="""Looks like there are way more productions here. This is because one production includes more than one
genres.""", visible=False)

button_clear = Button(label="Clear All", button_type="success")
button_clear.on_click(clearall)

curdoc().add_root(Row(p, Column(slider_years, g_select, type_choice, genres_choice, button_clear, text), name="stack"))
curdoc().title = 'Imdb Graphs - Stack'
