from bokeh.models import (ColumnDataSource, RangeSlider, Select, ColorPicker, MultiChoice, DataTable, TableColumn,
                          Button, CustomJS, Div)
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.layouts import Column, Row
from bokeh.palettes import Inferno256, Magma256, Plasma256, Viridis256, Cividis256, Turbo256, Greys256
from bokeh.io import curdoc
from bokeh.models import Panel, Tabs, TapTool
from bokeh.events import Tap
from tools import openfile, full_data, full_data_column, type_change, type_change_r
from os.path import dirname, join
data = openfile()

Colorpallettes = ["Inferno", "Magma", "Plasma", "Viridis", "Cividis", "Turbo", "Greys"]
Colorpallettesdict = dict(Inferno=Inferno256, Magma=Magma256, Plasma=Plasma256, Viridis=Viridis256, Cividis=Cividis256,
                          Turbo=Turbo256, Greys=Greys256)

source = ColumnDataSource(data={
	'years': data[data["Title Type"].isin(["movie"])].drop_duplicates(subset=["Year"])["Year"].sort_values().tolist(),
	'mean_by_years' : data[data["Title Type"].isin(["movie"])].groupby('Year')['Your Rating'].mean().round(2),
	'total_by_years' : data[data["Title Type"].isin(["movie"])].groupby('Year')['Your Rating'].count(),
	'lenght_mean' : data[data["Title Type"].isin(["movie"])].groupby('Year')['Runtime (mins)'].mean().values.round(2),
	'lenght_total' : data[data["Title Type"].isin(["movie"])].groupby('Year')['Runtime (mins)'].sum().values,
	'color': Colorpallettesdict["Inferno"][:len(data[data["Title Type"].isin(["movie"])].drop_duplicates(subset=["Year"])["Year"].sort_values())],
})

selected_source = ColumnDataSource(data=full_data(data[data["Title Type"].isin(["movie"])], typechange=1))

minyear = data["Year"].min()
maxyear = data["Year"].max()

y_axis_options = {"Average Score" : "mean_by_years",
                  "Number Of Watched Movies" : "total_by_years",
                  "Average Lenght (mins)" : "lenght_mean",
                  "Total Lenght (mins)": "lenght_total"}

types_list = type_change(data.drop_duplicates(subset=["Title Type"])["Title Type"].tolist())

datatable_years = [
        TableColumn(field="years", title="Years"),
        TableColumn(field="mean_by_years", title="Average Score"),
        TableColumn(field="total_by_years", title="Number Of Watched Movies")]

datatable_lenght = [
			TableColumn(field="years", title="Years"),
			TableColumn(field="lenght_mean", title="Average Lenght (mins)"),
			TableColumn(field="lenght_total", title="Total Lenght (mins)")]

def update_plot(attr, old, new):
	start_year = range_slider.value[0] - 1
	end_year = range_slider.value[1] + 1

	# y-axis changer
	for i, y in enumerate(y_axis_options):
		if select_y_axis.value == y:
			yearsbar.glyph.top = y_axis_options[y]
			p.yaxis.axis_label = y

	# hover-tool/datatable changer
	if select_y_axis.value == [k for k, v in y_axis_options.items()][0] or select_y_axis.value == [k for k, v in y_axis_options.items()][1]:
		changablehover.tooltips = [("Year", "@years"), ("Average Score", "@mean_by_years"), ("Total Production", "@total_by_years")]
		datatable_min.columns = datatable_years
		button_dwn_min.label = "Download Rating Datatable"
	elif select_y_axis.value == [k for k, v in y_axis_options.items()][2] or select_y_axis.value == [k for k, v in y_axis_options.items()][3]:
		changablehover.tooltips = [("Year", "@years"), ("Average Lenght (mins)", "@lenght_mean"), ("Total Lenght (mins)", "@lenght_total")]
		datatable_min.columns = datatable_lenght
		button_dwn_min.label = "Download Lenght Datatable"

	# updated data
	selection_drop = (data[data["Title Type"].isin(type_change_r(types_multi.value))].drop_duplicates(subset=["Year"]).
					  query('Year>' + str(start_year) + ' and Year<' + str(end_year) + ''))
	selection_ = (data[data["Title Type"].isin(type_change_r(types_multi.value))]
				  .query('Year>' + str(start_year) + ' and Year<' + str(end_year) + '').groupby('Year'))
	new_data = {
		'years': selection_drop['Year'].sort_values().tolist(),
		'mean_by_years': selection_['Your Rating'].mean().round(2),
		'total_by_years': selection_['Your Rating'].count(),
		'lenght_mean' : selection_['Runtime (mins)'].mean().values.round(2),
		'lenght_total' : selection_['Runtime (mins)'].sum().values,
		'color': (Colorpallettesdict[select.value][:len(selection_drop['Year'])])
	}

	source.data = new_data

	p.x_range.start = range_slider.value[0] - 1
	p.x_range.end = range_slider.value[1] + 1
	tabselect()


# bar-graph
p = figure(title="Scores with Years", x_axis_label="Years", y_axis_label="Average Score", plot_height=350, width=700)
yearsbar = p.vbar(x='years', top='mean_by_years', source=source, width=0.9, bottom=0, fill_color="color",
                  line_color="color", fill_alpha=0.7)

changablehover = HoverTool(tooltips=[("Year", "@years"), ("Average Score", "@mean_by_years"),
									 ("Total Production", "@total_by_years")])
p.add_tools(changablehover, TapTool())

def tabselect():
	yearlist=[]
	start_year = range_slider.value[0] - 1
	end_year = range_slider.value[1] + 1

	for i in range(len(source.selected.indices)):
		yearlist.append(source.data['years'][source.selected.indices[i]])

	updated_table_data = full_data(data[(data['Year'].isin(yearlist)) & (data['Title Type'].isin(type_change_r(types_multi.value)))])

	updated_table_data_wtap_s = (data[data['Title Type'].isin(type_change_r(types_multi.value))]
								 .query('Year>' + str(start_year) + ' and Year<' + str(end_year) + ''))
	updated_table_data_wtap = full_data(updated_table_data_wtap_s)

	selected_source.data = updated_table_data

	if source.selected.indices:
		selected_source.data = updated_table_data
		div_message.text = """<p>You can look at Selected Years in second datatable at <u>Datatable</u> tab.</p>
		<p>For multiselect, you can use Shift (Graph, Datatable) and Ctrl (Datatable).</p>"""
	else:
		selected_source.data = updated_table_data_wtap
		div_message.text=""

p.on_event(Tap, tabselect)
p.y_range.start = 0
p.x_range.start = minyear - 1
p.x_range.end = maxyear + 1

# right-side : slider, y-axis, multichoice
range_slider = RangeSlider(start=minyear, end=maxyear, value=(minyear, maxyear), step=1, title="Years")
range_slider.on_change('value', update_plot)

select_y_axis = Select(title="Y-Axis:",
                       value=[k for k, v in y_axis_options.items()][0], options=[k for k, v in y_axis_options.items()])
select_y_axis.on_change('value', update_plot)

types_multi = MultiChoice(title="Types", value=["Movie"], options=types_list)
types_multi.on_change('value', update_plot)

# datatable
clearall = CustomJS(args=dict(s=types_multi), code="s.value=[]")

datatable_min = DataTable(source=source, columns=datatable_years, width=700, height=300)
datatable_min.source.selected.on_change('indices', update_plot)

button_reset = Button(label="Clear Selection", button_type="success")
button_reset.js_on_event('button_click', clearall)

button_dwn_min = Button(label="Download Rating Datatable", button_type="success")
button_dwn_selected = Button(label="Download Selected Movies Datatable", button_type="success")

button_dwn_min.js_on_click(CustomJS(args=dict(source=source),
                                     code=open(join(dirname(__file__), "../download.js")).read()))
button_dwn_selected.js_on_click(CustomJS(args=dict(source=selected_source),
                                     code=open(join(dirname(__file__), "../download.js")).read()))

selected_datatable = DataTable(source=selected_source, columns=full_data_column(), width=1025, height=280)

div_message = Div(text="")

# style
select = Select(title="Color Pallette:", value=Colorpallettes[0], options=Colorpallettes)
select.on_change('value', update_plot)

picker = ColorPicker(title="Line Color")
picker.js_link('color', yearsbar.glyph, 'line_color')

# tabs and layout
tab1 = Panel(child=Row(Column(p, range_slider), Column(select_y_axis, types_multi, button_reset, div_message)), title="Graph")
tab2 = Panel(child=Column(select, picker), title="Style")
tab3 = Panel(child=Column(Row(datatable_min, Column(button_reset, types_multi, button_dwn_min, button_dwn_selected, div_message)), selected_datatable), title="Datatable")

curdoc().add_root(Tabs(tabs=[tab1, tab3, tab2], name="scores_wh_years"))
curdoc().title = 'Imdb Graphs - Scores with Years'
