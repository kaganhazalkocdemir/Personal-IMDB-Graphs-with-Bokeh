import pandas as pd
from os.path import dirname, join
from bokeh.models import (ColumnDataSource, Select, Slider, MultiChoice, CheckboxGroup, RangeSlider, Panel, Tabs, Div,
                          DataTable, Button, CustomJS, BasicTickFormatter,
                          DateRangeSlider, TextInput, ColorPicker, Spinner, DatetimeTickFormatter, Toggle)
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.io import curdoc
from bokeh.layouts import Row, Column
from bokeh.palettes import Category20
from datetime import datetime
from tools import openfile, full_data_column, full_data, genre_list

#source
data = openfile()
data['Date Rated'] = pd.to_datetime(data['Date Rated'])
data['Release Date'] = pd.to_datetime(data['Release Date'])
source = ColumnDataSource(data=full_data(data, typechange=1))
source.data['size'] = [x+1 for x in data['Your Rating']]
source.data['color'] = [Category20[11][x] for x in data['Your Rating']]

axisselected = {'Year': 'Year', 'User Rating': 'Your Rating', 'Imdb Rating': 'IMDb Rating',
                'Number Of Votes': 'Num Votes', 'Release Date': 'Release Date', 'Runtime (mins)': 'Runtime (mins)'}

types = ['movie', 'tvMovie', 'tvSeries', 'tvMiniSeries', 'tvEpisode', 'short', 'video', 'tvSpecial']
def update_plot(attr, old, new):
	selectedtypes = []
	for i in range(4):
		if i in select_type.active:
			selectedtypes.append(types[i])
		if i in select_type2.active:
			selectedtypes.append(types[i+4])
	type_part = (data['Title Type'].isin(selectedtypes))

	# slider - imdb raiting - part 1
	if round(imdb_rating.value[0]) == round(imdb_rating.value[1]):
		slider_part1 = (data['IMDb Rating'] == round(imdb_rating.value[0]))
	else:
		slider_part1 = ((data['IMDb Rating'] >= round(imdb_rating.value[0])) & (
					data['IMDb Rating'] <= imdb_rating.value[1]))

	# slider - user raiting - part 2
	if round(user_rating.value[1]) == round(user_rating.value[0]):
		slider_part2 = (data['Your Rating'] == round(user_rating.value[0]))
	else:
		slider_part2 = ((data['Your Rating'] >= round(user_rating.value[0])) & (
					data['Your Rating'] <= user_rating.value[1]))

	# slider - release year - part 3
	if movie_year_slider.value[0] == movie_year_slider.value[1]:
		slider_part3 = (data['Year'] == movie_year_slider.value[0])
	else:
		slider_part3 = ((data['Year'] >= movie_year_slider.value[0]) & (data['Year'] <= movie_year_slider.value[1]))

	# slider - date rated - part 4
	date_rated_first = datetime.strftime(datetime.fromtimestamp(date_rated_slider.value[0] / 1000), "%Y-%m-%d")
	date_rated_second = datetime.strftime(datetime.fromtimestamp(date_rated_slider.value[1] / 1000), "%Y-%m-%d")

	if date_rated_first == date_rated_second:
		slider_part4 = (data['Date Rated'] == date_rated_first)
	else:
		slider_part4 = ((data['Date Rated'] >= date_rated_first) & (data['Date Rated'] <= date_rated_second))

	# slider - num votes - part 5
	slider_part5 = (data['Num Votes'] <= num_votes_slider.value)

	# genres selection - genres_part
	'''nonselect_genres = []
	for i in range(len(genre_list)):
		if genre_list[i] not in genre_choise.value:
			nonselect_genres.append(genre_list[i])'''
	base = r'^{}'
	expr = '(?=.*{})'
	exprr = '(?!.*{})'  # for non selection but not using in this app. I used first, but dont want to use it.
	genres_part = (data['Genres'].str.contains(base.format(''.join(expr.format(w) for w in genre_choise.value))))

	# all parts in together
	if director_search.value=='':
		updated_last = data[(type_part) & (slider_part1) & (slider_part2) & (slider_part3) & (slider_part4) & (slider_part5) & (genres_part)]
	else:
		dir_part = (data['Directors'].str.contains(director_search.value, case=False))
		updated_last = data[(type_part) & (slider_part1) & (slider_part2) & (slider_part3) & (slider_part4) & (slider_part5) & (genres_part) & (dir_part)]

	# axis x / axis y change
	for i, n in axisselected.items():
		if selectx.value == i:
			circles.glyph.x = n
			p.xaxis.formatter = BasicTickFormatter(use_scientific=False)
		elif selectx.value == 'Release Date':
			circles.glyph.x = 'Release Date'
			p.xaxis.formatter = DatetimeTickFormatter(days=["%d %B %Y"], months=["%d %B %Y"], years=["%d %B %Y"])

	for i, n in axisselected.items():
		if selecty.value == i:
			circles.glyph.y = n
			p.yaxis.formatter = BasicTickFormatter(use_scientific=False)
		elif selecty.value == 'Release Date':
			circles.glyph.y = 'Release Date'
			p.yaxis.formatter = DatetimeTickFormatter(days=["%d %B %Y"], months=["%d %B %Y"], years=["%d %B %Y"])

	# different sizes and colors for circles
	if radselect.value == 'Your Rating':
		size = [x+1 for x in updated_last['Your Rating']]
	elif radselect.value == 'Imdb Rating':
		size = [x+1 for x in updated_last['IMDb Rating']]
	elif radselect.value == 'Number of Votes':
		sized = []
		for i, n in enumerate(updated_last['Num Votes']):
			if n < 10000:
				sized.append(2)
			elif 10000 <= n < 50000:
				sized.append(3)
			elif 50000 <= n < 100000:
				sized.append(4)
			elif 100000 <= n < 300000:
				sized.append(5)
			elif 300000 <= n < 500000:
				sized.append(6)
			elif 500000 <= n < 750000:
				sized.append(7)
			elif 750000 <= n < 1000000:
				sized.append(8)
			elif 1000000 <= n < 1500000:
				sized.append(9)
			elif 1500000 <= n < 2000000:
				sized.append(10)
			elif n > 2000000:
				sized.append(11)
		size = sized
	elif radselect.value == 'Runtime (mins)':
		sized = []
		for i, n in enumerate(updated_last['Runtime (mins)'].tolist()):
			if not isinstance(n, float) or n == None:
				sized.append(2)
			elif n < 20:
				sized.append(3)
			elif 20 <= n < 40:
				sized.append(4)
			elif 40 <= n < 90:
				sized.append(5)
			elif 90 <= n < 120:
				sized.append(6)
			elif 120 <= n < 150:
				sized.append(7)
			elif 150 <= n < 180:
				sized.append(8)
			elif 180 <= n < 200:
				sized.append(9)
			elif 200 <= n < 240:
				sized.append(10)
		size = sized

	# colors
	if colorselect.value == 'Your Rating':
		color = [Category20[11][x] for x in updated_last['Your Rating']]
	elif colorselect.value == 'Imdb Rating':
		color = [Category20[11][round(x)] for x in updated_last['IMDb Rating']]
	elif colorselect.value == 'Number of Votes':
		colord = []
		for i, n in enumerate(updated_last['Num Votes'].tolist()):
			if n < 10000:
				colord.append(Category20[11][0])
			elif 10000 <= n < 50000:
				colord.append(Category20[11][1])
			elif 50000 <= n < 100000:
				colord.append(Category20[11][2])
			elif 100000 <= n < 300000:
				colord.append(Category20[11][3])
			elif 300000 <= n < 500000:
				colord.append(Category20[11][4])
			elif 500000 <= n < 750000:
				colord.append(Category20[11][5])
			elif 750000 <= n < 1000000:
				colord.append(Category20[11][6])
			elif 1000000 <= n < 1500000:
				colord.append(Category20[11][7])
			elif 1500000 <= n < 2000000:
				colord.append(Category20[11][8])
			elif n > 2000000:
				colord.append(Category20[11][9])
		color = colord
	elif colorselect.value == 'Runtime (mins)':
		colord = []
		for i, n in enumerate(updated_last['Runtime (mins)'].tolist()):
			if not isinstance(n, float) or n == None:
				colord.append(Category20[11][0])
			elif n < 20:
				colord.append(Category20[11][1])
			elif 20 <= n < 40:
				colord.append(Category20[11][2])
			elif 40 <= n < 90:
				colord.append(Category20[11][3])
			elif 90 <= n < 120:
				colord.append(Category20[11][4])
			elif 120 <= n < 150:
				colord.append(Category20[11][5])
			elif 150 <= n < 180:
				colord.append(Category20[11][6])
			elif 180 <= n < 200:
				colord.append(Category20[11][7])
			elif 200 <= n < 240:
				colord.append(Category20[11][8])
		color = colord
	elif colorselect.value == 'Types':
		colord = []
		for i, n in enumerate(updated_last['Title Type']):
			if n == 'movie':
				colord.append(Category20[11][0])
			elif n == 'tvMiniSeries':
				colord.append(Category20[11][1])
			elif n == 'tvMovie':
				colord.append(Category20[11][2])
			elif n == 'tvSeries':
				colord.append(Category20[11][3])
			elif n == 'tvEpisode':
				colord.append(Category20[11][4])
			elif n == 'short':
				colord.append(Category20[11][5])
			elif n == 'video':
				colord.append(Category20[11][6])
			elif n == 'tvSpecial':
				colord.append(Category20[11][7])
			else:
				colord.append(Category20[11][8])
		color = colord

	# update source
	uptd_data = full_data(updated_last, typechange=1)
	uptd_data['size'] = size
	uptd_data['color'] = color
	source.data = uptd_data
	p.xaxis.axis_label = selectx.value
	p.yaxis.axis_label = selecty.value

	totaldiv.text = "<font color=red>(Selected)</font> Number Of Movies : " + str(len(source.data['Const']))

	if radtoggle.active:
		circles.glyph.size = 'size'
	else:
		circles.glyph.size = 4
	if colortoggle.active:
		circles.glyph.fill_color = 'color'
	else:
		circles.glyph.fill_color = 'grey'

	curdoc().theme = graph_style.value

def reset_selection():
	source.selected.indices = []

# graph
p = figure(width=800, height=520, x_axis_label="Years", y_axis_label="Number of Votes", title="All Movies You Watched")
circles = p.circle(x="Year", y="Num Votes", source=source, color="color", line_color=None, fill_alpha=0.7,
                   hover_color='orange', size='size')
p.y_range.start = 1

p.yaxis.formatter = BasicTickFormatter(use_scientific=False)  # because no one wanna see e1+16851 :)
p.xaxis.formatter = BasicTickFormatter(use_scientific=False)

p.add_tools(
	HoverTool(tooltips=[("Title", "@Title"), ("Release Date", "@{Release Date}{%d/%m/%Y}"), ("Type", "@Type"),
						("Genres", "@Genres"),
						("Runtime (mins)", "@{Runtime (mins)}"), ("User Raiting", "@{Your Rating}"),
						("Imdb Raiting", "@{IMDb Rating}")], formatters={"@{Release Date}": 'datetime'}))

# right-menu
selectx = Select(title="X-Axis:", value="Years", options=[x for x in axisselected])
selecty = Select(title="Y-Axis:", value="Number Of Votes", options=[x for x in axisselected])
selectx.on_change('value', update_plot)
selecty.on_change('value', update_plot)

# selection of type. two group to fit in screen.
select_type = CheckboxGroup(labels=["Movie", "TV Movie", "TV Series", "TV Mini-Series"], active=[0, 1, 2, 3],
                            width=150)
select_type2 = CheckboxGroup(labels=["TV Episode", "Short", "Video", "TV Special"], active=[0, 1, 2, 3], width=150)
select_type.on_change("active", update_plot)
select_type2.on_change("active", update_plot)

imdb_rating = RangeSlider(start=1, end=10, value=(1, 10), step=1, title="Imdb Raiting")
user_rating = RangeSlider(start=1, end=10, value=(1, 10), step=1, title="User Raiting")
imdb_rating.on_change('value', update_plot)
user_rating.on_change('value', update_plot)

data_table = DataTable(source=source, columns=full_data_column(dateformatter=True), width=880, height=400)
button_reset = Button(label="Reset Selection", button_type="success")
button_download = Button(label="Download Selection", button_type="success")
button_reset.on_click(reset_selection)
button_download.js_on_click(CustomJS(args=dict(source=source),
                                     code=open(join(dirname(__file__), "../download.js")).read()))

totaldiv = Div(text="Number Of Movies : " + str(len(data)), height=2)

genre_choise = MultiChoice(value=[], options=genre_list, height=50, title="Genres")
genre_choise.on_change('value', update_plot)

director_search = TextInput(value="", title="Director(s):")
director_search.on_change('value', update_plot)

minyear = data["Year"].min()
maxyear = data["Year"].max()
minyear_rated = data["Date Rated"].min()
maxyear_rated = data["Date Rated"].max()
max_numvotes = data["Num Votes"].max()

movie_year_slider = RangeSlider(start=minyear, end=maxyear, value=(minyear, maxyear), step=1, title="Release Years")
date_rated_slider = DateRangeSlider(value=(minyear_rated, maxyear_rated), start=minyear_rated, end=maxyear_rated,
                                    title="Date Rated")
num_votes_slider = Slider(start=0, end=max_numvotes, value=max_numvotes, step=1000, title="Number of Votes")
movie_year_slider.on_change('value', update_plot)
date_rated_slider.on_change('value', update_plot)
num_votes_slider.on_change('value', update_plot)

div = Div(text="""""", height=1)  #without empty div right tabs touch above tabs

# sizes & colors tab
radtoggle = Toggle(label="Different Sizes", button_type="success", active=True)
radtoggle.on_change('active', update_plot)

radselect = Select(title="by:", value="Your Rating", options=['Your Rating', 'Imdb Rating', 'Number of Votes', 'Runtime (mins)'])
radselect.on_change('value', update_plot)

colortoggle = Toggle(label="Different Colors", button_type="success", active=True)
colortoggle.on_change('active', update_plot)

colorselect = Select(title="by:", value="Your Rating", options=['Your Rating', 'Imdb Rating', 'Number of Votes', 'Runtime (mins)', 'Types'])
colorselect.on_change('value', update_plot)

# style-tab
graph_style = Select(title="Graph Style:", value="Years",
                     options=["", "caliber", "dark_minimal", "light_minimal", "night_sky", "contrast"])
graph_style.on_change('value', update_plot)

point_color = ColorPicker(title="Point Color")
point_color.js_link('color', circles.glyph, 'fill_alpha')

circle_size = Spinner(title="Circle size", low=1, high=40, step=0.5, value=4, width=100)
circle_size.js_link('value', circles.glyph, 'size')

circle_alpha = Spinner(title="Circle Alpha", low=0.1, high=1, step=0.1, value=0.7, width=100)
circle_alpha.js_link('value', circles.glyph, 'fill_alpha')

circle_line_color = ColorPicker(title="Circle Line Color")
circle_line_color.js_link('color', circles.glyph, 'line_color')

circle_line_alpha = Spinner(title="Circle Line Alpha", low=0.1, high=1, step=0.1, value=1, width=100)
circle_line_alpha.js_link('value', circles.glyph, 'line_alpha')

circle_line_width = Spinner(title="Circle Line Width", low=1, high=40, step=1, value=1, width=100)
circle_line_width.js_link('value', circles.glyph, 'line_width')

title_input = TextInput(value="", title="Title:")
title_input.js_link('value', p.title, 'text')

title_color = ColorPicker(title="Title Color")
title_color.js_link('color', p.title, 'text_color')

title_height = TextInput(value="13px", title="Title Size:")
title_height.js_link('value', p.title, 'text_font_size')

title_background = ColorPicker(title="Title Background Color")
title_background.js_link('color', p.title, 'background_fill_color')

stylediv = Div(text="""<p>Circle color and size options make all circles same. If you want to go back, please refresh the page</p>""")

# layout
layout_right_1 = Column(selectx, selecty, Row(select_type, select_type2), imdb_rating, user_rating, movie_year_slider,
                        date_rated_slider, num_votes_slider)

tab_r1 = Panel(child=layout_right_1, title="Others")
tab_r2 = Panel(child=Column(genre_choise, director_search), title="Genres & Search")
tab_r3 = Panel(child=Column(radtoggle, radselect, colortoggle, colorselect), title="Sizes & Colors")

layout1 = Column(div, Row(p, Tabs(tabs=[tab_r1, tab_r3, tab_r2])), sizing_mode="stretch_height")
layout2 = Row(data_table, Column(button_reset, button_download, totaldiv))
layout3 = Row(Column(graph_style, point_color, Row(circle_size, circle_alpha), circle_line_color, Row(circle_line_alpha,
					 circle_line_width)), Column(title_input, title_color, title_height, title_background), stylediv)

tab1 = Panel(child=layout1, title="Graphs")
tab2 = Panel(child=layout2, title="Datatable")
tab3 = Panel(child=layout3, title="Style")

curdoc().add_root(Tabs(tabs=[tab1, tab2, tab3], name="all_movies"))
curdoc().title = 'Imdb Graphs - All Movies'
