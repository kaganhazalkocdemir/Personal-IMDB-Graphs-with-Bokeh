import pandas as pd
from bokeh.models import ColumnDataSource, DataTable, TableColumn, Button, Toggle, Panel, Tabs, Select, Dropdown, Div
from bokeh.layouts import Row, Column
from bokeh.io import curdoc
from bokeh.palettes import viridis, magma, inferno, grey, cividis, Turbo256
from bokeh.plotting import figure
from bokeh.transform import cumsum
from math import pi
from tools import openfile, type_change

data = openfile()
# split genres
data['Genres'] = data['Genres'].str.split(',')
data = (data.set_index(['Your Rating', 'Const', 'Year', 'Title Type'])['Genres'].apply(pd.Series).stack().reset_index()
        .drop('level_4', axis=1).rename(columns={0: 'Genres_split'}))
data['Genres_split'] = data['Genres_split'].str.strip()
data['Title Type'] = data['Title Type'].apply(type_change)

def datacreater(datatag, dataname, pallette, *passnumber):
        '''
        creates data and updated data for pie charts and data tables
        passnumber: if it was a pass number, creates a updated data source that skip more than this number
        '''
        variabledictionary = {}
        first = datatag
        second = datatag + '_mean'
        third = 'total_by_' + datatag
        sourcename = 'source_top_' + datatag + '_data'
        sourcenameupdated = 'source_top_' + datatag + 'updated_data'

        if passnumber:
                selection = (data[data.groupby([dataname])["Your Rating"].transform('count') > passnumber[0]]
                        .groupby([dataname])["Your Rating"])
                variabledictionary[sourcenameupdated] = {
                        first: selection.mean().index,
                        second: selection.mean().sort_values(ascending=False).values.round(2),
                        third: selection.count().values,
                        'angle': selection.count().values / selection.count().values.sum()*2*pi,
                        'angle_by_mean': selection.mean() / selection.mean().sum() * 2 * pi,
                        'color': pallette(len(selection.mean().index))
                }
                return variabledictionary[sourcenameupdated]
        else:
                selection = data.groupby([dataname])["Your Rating"]
                variabledictionary[sourcename] = {
                        first: selection.mean().index,
                        second: selection.mean().sort_values(ascending=False).values.round(2),
                        third: selection.count().values,
                        'angle': selection.count().values / selection.count().values.sum() * 2 * pi,
                        'angle_by_mean': selection.mean() / selection.mean().sum() * 2 * pi,
                        'color': pallette(len(selection.mean().index))
                }
                return variabledictionary[sourcename]


def update_all(attr, old, new):

        Colorpallettesdict = dict(viridis=viridis, magma=magma, inferno=inferno, grey=grey, cividis=cividis, Turbo256=Turbo256)

        if skipbutton.active:
                source_top_genres.data = datacreater('genres', 'Genres_split', Colorpallettesdict[genres_style.value],50)
        else:
                source_top_genres.data = datacreater('genres', 'Genres_split', Colorpallettesdict[genres_style.value])

        if skipbutton2.active:
                source_top_years.data = datacreater('years', 'Year', Colorpallettesdict[years_style.value],10)
        else:
                source_top_years.data = datacreater('years', 'Year', Colorpallettesdict[years_style.value])

        if skipbutton3.active:
                source_top_types.data = datacreater('types', 'Title Type', Colorpallettesdict[types_style.value],10)
        else:
                source_top_types.data = datacreater('types', 'Title Type', Colorpallettesdict[types_style.value])

        if select.value == "Total Movie":
                genres_pie.glyph.start_angle = cumsum('angle', include_zero=True)
                genres_pie.glyph.end_angle = cumsum('angle')
                p.title.text = "Pie Chart of Genres by Total Movie"
        elif select.value == "Mean":
                genres_pie.glyph.start_angle = cumsum('angle_by_mean', include_zero=True)
                genres_pie.glyph.end_angle = cumsum('angle_by_mean')
                p.title.text="Pie Chart of Genres by Mean"

        if select2.value == "Total Movie":
                years_pie.glyph.start_angle = cumsum('angle', include_zero=True)
                years_pie.glyph.end_angle = cumsum('angle')
                p2.title.text="Pie Chart of Years by Total Movie"
        elif select2.value == "Mean":
                years_pie.glyph.start_angle = cumsum('angle_by_mean', include_zero=True)
                years_pie.glyph.end_angle = cumsum('angle_by_mean')
                p2.title.text="Pie Chart of Years by Mean"

        if select3.value == "Total Movie":
                types_pie.glyph.start_angle = cumsum('angle', include_zero=True)
                types_pie.glyph.end_angle = cumsum('angle')
                p3.title.text="Pie Chart of Types by Total Movie"
        elif select3.value == "Mean":
                types_pie.glyph.start_angle = cumsum('angle_by_mean', include_zero=True)
                types_pie.glyph.end_angle = cumsum('angle_by_mean')
                p3.title.text="Pie Chart of Types by Mean"

source_top_years = ColumnDataSource(data=datacreater('years', 'Year', viridis))
source_top_genres = ColumnDataSource(data=datacreater('genres', 'Genres_split', magma))
source_top_types = ColumnDataSource(data=datacreater('types', 'Title Type', magma))

# data-tables and charts
columns_genres = [
        TableColumn(field="genres", title="Genres"),
        TableColumn(field="genres_mean", title="Mean"),
        TableColumn(field="total_by_genres", title="Total")]
columns_years = [
        TableColumn(field="years", title="Years"),
        TableColumn(field="years_mean", title="Mean"),
        TableColumn(field="total_by_years", title="Total")]
columns_types = [
        TableColumn(field="types", title="Types"),
        TableColumn(field="types_mean", title="Mean"),
        TableColumn(field="total_by_types", title="Total")]

data_table_genres = DataTable(source=source_top_genres, columns=columns_genres, width=550, height=240)
data_table_years = DataTable(source=source_top_years, columns=columns_years, width=550, height=240)
data_table_types = DataTable(source=source_top_types, columns=columns_types, width=550, height=240)

p = figure(plot_height=350, width=550,  title="Pie Chart of Genres by Total Movie", toolbar_location=None, x_range=(-1,1),
           sizing_mode="scale_both",  tools="hover",
           tooltips=[("Genre", "@genres"), ("Mean", "@genres_mean"), ("Total Movie", "@total_by_genres")])

p2 = figure(plot_height=350, width=550, title="Pie Chart of Years by Total Movie", toolbar_location=None, x_range=(-1,1),
            sizing_mode="scale_both", tools="hover",
            tooltips=[("Year", "@years"), ("Mean", "@years_mean"), ("Total Movie", "@total_by_years")])

p3 = figure(plot_height=350, width=550, title="Pie Chart of Types by Total Movie", toolbar_location=None, x_range=(-1,1),
            sizing_mode="scale_both", tools="hover",
            tooltips=[("Types", "@types"), ("Mean", "@types_mean"), ("Total Movie", "@total_by_types")])

genres_pie = p.wedge(x=0, y=2, radius=0.5,
                     start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                     line_color="white", fill_color='color', source=source_top_genres)

years_pie = p2.wedge(x=0, y=2, radius=0.5,
                     start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                     line_color="white", fill_color='color', source=source_top_years)

types_pie = p3.wedge(x=0, y=2, radius=0.5,
                     start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                     line_color="white", fill_color='color', source=source_top_types)

p.axis.axis_label, p2.axis.axis_label, p3.axis.axis_label = None, None, None
p.axis.visible, p2.axis.visible, p3.axis.visible = False, False, False
p.grid.grid_line_color, p2.grid.grid_line_color, p3.grid.grid_line_color = None, None, None

# reset functions
def callback():
    source_top_genres.selected.indices = []

def callback2():
    source_top_years.selected.indices = []

def callback3():
    source_top_types.selected.indices = []

# buttons, selects
button1 = Button(label="Clear Selection", button_type="success")
button2 = Button(label="Clear Selection", button_type="success")
button3 = Button(label="Clear Selection", button_type="success")

button1.on_click(callback)
button2.on_click(callback2)
button3.on_click(callback3)

skipbutton = Toggle(label="Less than 50 movies", button_type="success")
skipbutton2 = Toggle(label="Less than 10 movies", button_type="success")
skipbutton3 = Toggle(label="Less than 10 movies", button_type="success")

skipbutton.on_change('active', update_all)
skipbutton2.on_change('active', update_all)
skipbutton3.on_change('active', update_all)

select = Select(value="Total Movie", options=["Total Movie", "Mean"])
select2 = Select(value="Total Movie", options=["Total Movie", "Mean"])
select3 = Select(value="Total Movie", options=["Total Movie", "Mean"])

select.on_change('value', update_all)
select2.on_change('value', update_all)
select3.on_change('value', update_all)

def taballtypes(mode):
        # changes label/title of buttons and selections
        if mode:
                button1.label = "Clear Selection of Genres"
                button2.label = "Clear Selection of Years"
                button3.label = "Clear Selection of Types"
                skipbutton.label = "Less than 50 movies of Genres"
                skipbutton2.label = "Less than 50 movies of Years"
                skipbutton3.label = "Less than 50 movies of Types"
                select.title="Genres :"
                select2.title="Years :"
                select3.title="Types :"
        else:
                button1.label = "Clear Selection"
                button2.label = "Clear Selection"
                button3.label = "Clear Selection"
                skipbutton.label = "Less than 50 movies"
                skipbutton2.label = "Less than 50 movies"
                skipbutton3.label = "Less than 50 movies"
                select.title = ""
                select2.title = ""
                select3.title = ""

def tabchanger(dropdownevent):
        #  changes tabs according to dropdown menu
        if dropdownevent.item == 'genres_years':
                tablayout.tabs = [tab_genres_years_data, tab_genres_years_charts]
                taballtypes(False)
        elif dropdownevent.item == 'genres_types':
                tablayout.tabs = [tab_genres_types_data, tab_genres_types_charts]
                taballtypes(False)
        elif dropdownevent.item == 'years_types':
                tablayout.tabs = [tab_years_types_data, tab_years_types_charts]
                taballtypes(False)
        elif dropdownevent.item == 'all':
                tablayout.tabs = [tab_all_data, tab_all_charts]
                taballtypes(True)
        elif dropdownevent.item == 'onebyone':
                tablayout.tabs = [tab_genres, tab_years, tab_types]
                taballtypes(False)
        elif dropdownevent.item == 'style':
                tablayout.tabs = [tab_style]
                taballtypes(False)
                tablayout.active = 0

# dropbox menu
menu = [("Genres - Years", "genres_years"), ("Genres - Types", "genres_types"), ("Years - Types", "years_types"),
        None,
        ("All Together","all"),
        ("One by One","onebyone"),
        None,
        ("Style","style")]

dropdown = Dropdown(label="Chart Types", button_type="warning", menu=menu, max_width=250)
dropdown.on_click(tabchanger)

# tabs
tab_genres_years_data = Panel(child=Row(Column(data_table_genres,button1,skipbutton,select),
                                        Column(data_table_years,button2,skipbutton2,select2)), title="Data Tables")
tab_genres_years_charts = Panel(child=Row(p, p2, sizing_mode="fixed"), title="Pie Charts")

tab_genres_types_data = Panel(child=Row(Column(data_table_genres,button1,skipbutton,select),
                                        Column(data_table_types,button3,skipbutton3,select3)), title="Data Tables")
tab_genres_types_charts = Panel(child=Row(p, p3, sizing_mode="fixed"), title="Pie Charts")

tab_years_types_data = Panel(child=Row(Column(data_table_years,button2,skipbutton2,select2),
                                       Column(data_table_types,button3,skipbutton3,select3)), title="Data Tables")
tab_years_types_charts = Panel(child=Row(p2, p3, sizing_mode="fixed"), title="Pie Charts")

tab_all_data = Panel(child=Column(Row(data_table_genres,data_table_years),
                                  Row(data_table_types, Column(button1, button2, button3, skipbutton, skipbutton2, skipbutton3))), title="Data Tables")
tab_all_charts = Panel(child=Column(Row(p,p2, sizing_mode="fixed"),
                                    Row(p3, Column(select, select2, select3, skipbutton, skipbutton2, skipbutton3), sizing_mode="fixed")), title="Pie Charts")

tab_genres = Panel(child=Row(p, Column(data_table_genres, button1, skipbutton, select), sizing_mode="fixed"), title="Genres")
tab_years = Panel(child=Row(p2, Column(data_table_years, button2, skipbutton2, select2), sizing_mode="fixed"), title="Years")
tab_types = Panel(child=Row(p3, Column(data_table_types, button3, skipbutton3, select3), sizing_mode="fixed"), title="Types")

# style-tab
styles_option = ['viridis', 'magma', 'inferno', 'grey', 'cividis', 'Turbo256']

genres_style = Select(value="viridis", title="Genres :", options=styles_option)
years_style = Select(value="magma", title="Years :", options=styles_option)
types_style = Select(value="cividis", title="Types :", options=styles_option)
genres_style.on_change('value', update_all)
years_style.on_change('value', update_all)
types_style.on_change('value', update_all)

tab_style = Panel(child=Column(genres_style, years_style, types_style), title="Style")

dropdiv = Div(text="", width=850)
# final layout
tablayout = Tabs(tabs=[tab_genres_years_data, tab_genres_years_charts])
layout = Column(Row(dropdiv, dropdown), tablayout, name="piechartslayout")

curdoc().add_root(layout)
curdoc().title = 'Imdb Graphs - Pie Charts'
