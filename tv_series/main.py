import pandas as pd
from bokeh.models import (ColumnDataSource, DataTable, Div, Button, CustomJS, Panel, Tabs, DatetimeTickFormatter,
                          SingleIntervalTicker, Legend, LegendItem, Select)
from bokeh.io import curdoc
from bokeh.layouts import Column, Row
from bokeh.plotting import figure
from bokeh.palettes import Category20
from bokeh.models.tools import HoverTool
from tools import full_data_column, full_data, openfile
from collections import defaultdict
from os.path import dirname, join

data = openfile()

data[['title_split', 'episode_name']] = data[data['Title Type'] == 'tvEpisode']['Title'].str.split(':', 1, expand=True)
data['Date Rated'] = pd.to_datetime(data['Date Rated'])
data['Release Date'] = pd.to_datetime(data['Release Date'])

series_names = (data[(data['Title Type'] == 'tvEpisode')].drop_duplicates(subset='title_split')['title_split']
                .sort_values().values.tolist())

sd_columns = ['Const', 'Your Rating', 'Date Rated', 'Title Type', 'URL', 'IMDb Rating', 'Runtime (mins)', 'Year',
              'Genres', 'Num Votes', 'Release Date', 'Directors']

series_data = defaultdict(list)
for i, d in enumerate(series_names):
    try:
        for x, y in enumerate(sd_columns):
            series_data[y].append(data[data['Title'] == d][y].values[0])
    except IndexError:  # some of episodes without rated main tv series
        for x, y in enumerate(sd_columns):
            series_data[y].append(None)

series_data['series_name'] = (data[data['Title Type'] == 'tvEpisode']
                              .groupby(['title_split'])['episode_name'].count().index)
series_data['episode_number'] = (data[data['Title Type'] == 'tvEpisode']
                                 .groupby(['title_split'])['episode_name'].count().values)

tvseries_source = ColumnDataSource(data=series_data)
tvepisodes_source = ColumnDataSource(data={})


def update_plot(attr, old, new):
    selected_series = []
    if tvseries_source.selected.indices:
        tvepisodes_datatable.visible, divselection.visible = True, True

        for i in range(len(tvseries_source.selected.indices)):
            selected_series.append(tvseries_source.data['series_name'][tvseries_source.selected.indices[i]])

        divselection.text = "Selected TV Series : "+' , '.join([str(e) for e in selected_series])

        # update episodes of selected tv series
        selected_data = data[(data['Title Type'] == 'tvEpisode') & (data['title_split'].isin(selected_series))]
        tvepisodes_source.data = full_data(selected_data, newdata=[['Episode Title', 'episode_name']], nonlist=[9])

        # update plot, legend, div-message
        for i, n in enumerate(series_data['series_name']):
            if n in selected_series:
                lineplotdict[n].visible = True
                circleplotdict[n].visible = True
                div_message.text = """<p>You can look at Selected TV Series in <u>Graph</u> tab.</p>
                <p>For multiselect, you can use Shift (Graph, Datatable) and Ctrl (Datatable).</p>"""
            else:
                lineplotdict[n].visible = False
                circleplotdict[n].visible = False
                div_message.text = ""
        legenditems = []
        for i, n in enumerate(selected_series):
            legenditems.append(LegendItem(label=n, renderers=[lineplotdict[n], circleplotdict[n]]))
        plot_legend.items = legenditems

        for a, b in enumerate(series_data['series_name']):
            updated_select = data[(data['Title Type'] == 'tvEpisode') & (data['title_split'].isin([b]))].sort_values(by=select_yaxis.value)
            updated_data = full_data(updated_select, nonlist=[0, 3, 4, 8, 10, 11, 7, 9, 12, 5],
                                     newdata=[['Release Date', select_yaxis.value], ['Episode Title', 'episode_name']])
            plotdatadict[b].data = updated_data
        p.xaxis.axis_label = select_yaxis.value

        yrmin = lambda x: 1 if x == 1 else x-1
        yrmax = lambda x: 10+0.2 if x == 10 else x+1
        p.y_range.start = yrmin(selected_data['Your Rating'].min())
        p.y_range.end = yrmax(selected_data['Your Rating'].max())
        p.x_range.start = selected_data[select_yaxis.value].min() - pd.DateOffset(months=5)
        p.x_range.end = selected_data[select_yaxis.value].max() + pd.DateOffset(months=5)

tvseries_columns = full_data_column(addnew=[['series_name', 'Title', 0], ['episode_number', '(Rated) Episode Number', 1]],
                                    nonlist=[0, 2, 8], dateformatter=True)

tvepisodes_columns = full_data_column(nonlist=[2, 0, 10],
                                      addnew=[['Episode Title', 'Episode Title', 0]], dateformatter=True)

tvseries_datatable = DataTable(source=tvseries_source, columns=tvseries_columns, width=900, height=400)
tvseries_datatable.source.selected.on_change('indices', update_plot)

divselection = Div(text="", visible=False)

tvepisodes_datatable = DataTable(source=tvepisodes_source, columns=tvepisodes_columns, width=900, height=400,
                                 visible=False)

# buttons-datatable tab
download_button1 = Button(label="Download TV Series Datatable", button_type="success")
download_button2 = Button(label="Download TV Episodes Datatable", button_type="success")

download_button1.js_on_click(CustomJS(args=dict(source=tvseries_source),
                                      code=open(join(dirname(__file__), "../download.js")).read()))

download_button2.js_on_click(CustomJS(args=dict(source=tvepisodes_source),
                                      code=open(join(dirname(__file__), "../download.js")).read()))

buttons = Column(download_button1, download_button2)

# graph
lineplotdict, plotdatadict, circleplotdict = {}, {}, {}
x_max = data[data['Title Type'] == 'tvEpisode']['Release Date'].max() + pd.DateOffset(months=5)
x_min = data[data['Title Type'] == 'tvEpisode']['Release Date'].min() - pd.DateOffset(months=5)

p = figure(title="Selected Tv Series", x_axis_label="Release Date", y_axis_label="Your Rating",
           toolbar_location="above", y_range=(0, 10), x_range=(x_max, x_min), width=600, height=500)

if len(series_data['series_name']) == 1:
    color_graph = Category20[3][:1]
elif len(series_data['series_name']) == 2:
    color_graph = Category20[3][:2]
else:
    color_graph = Category20[len(series_data['series_name'])]

for a, b in enumerate(series_data['series_name']):
    graph_select = data[(data['Title Type'] == 'tvEpisode') & (data['title_split'].isin([b]))].sort_values(by='Release Date')
    plotdatadict[b] = ColumnDataSource(data=full_data(graph_select, nonlist=[0, 3, 4, 8, 10, 7, 9, 12, 5],
                                                      newdata=[['Episode Title', 'episode_name']]))

    lineplotdict[b] = p.line('Release Date', 'Your Rating', line_width=2, source=plotdatadict[b],
                             color=color_graph[a], muted_color=color_graph[a], muted_alpha=0.2, visible=False)
    circleplotdict[b] = p.circle('Release Date', 'Your Rating', line_width=2, source=plotdatadict[b],
                                 color=color_graph[a], muted_color=color_graph[a], muted_alpha=0.2, visible=False)


plot_legend = Legend(click_policy="mute")
p.add_layout(plot_legend, 'right')

hovertooltips = [("Episode", "@{Episode Title}"), ("Your Rating", "@{Your Rating}"), ("Release Date", "@{Release Date}{%d/%m/%Y}"),
                 ("Date Rated", "@{Date Rated}{%d/%m/%Y}"), ("Imdb Rating", "@{IMDb Rating}")]
hoverformatters = {"@{Release Date}": 'datetime', "@{Date Rated}": "datetime"}


p.add_tools(HoverTool(renderers=[circleplotdict[b] for a, b in enumerate(circleplotdict)], tooltips=hovertooltips,
                      formatters=hoverformatters))
p.xaxis.formatter = DatetimeTickFormatter(days=["%d %B %Y"], months=["%d %B %Y"], years=["%d %B %Y"])
p.yaxis.ticker = SingleIntervalTicker(interval=1, num_minor_ticks=0)
p.xaxis.major_label_orientation = 0.66

select_yaxis = Select(title="Y-Axis:", value="Release Date", options=["Release Date", "Date Rated"])
select_yaxis.on_change('value', update_plot)

div_message = Div(text="")

# layout
layout_tab1 = Column(Row(tvseries_datatable, buttons, div_message), divselection, tvepisodes_datatable)

tab1 = Panel(child=layout_tab1, title="Datatables")
tab2 = Panel(child=Row(p, select_yaxis), title="Graph")

tabs = Tabs(tabs=[tab1, tab2], name='tv_series')

curdoc().add_root(tabs)
curdoc().title = 'Imdb Graphs - TV Series'
