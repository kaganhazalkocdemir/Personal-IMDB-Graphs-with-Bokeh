import pandas as pd
from bokeh.models import (ColumnDataSource, DataTable, TableColumn, SingleIntervalTicker, Slider, CheckboxButtonGroup,
                          Select, FactorRange, HoverTool, Toggle)
from bokeh.plotting import figure
from bokeh.layouts import Row, Column
from bokeh.io import curdoc
from tools import openfile, type_change_r, full_data, list_join, full_data_column

# source
data = openfile()
data['Directors'] = data['Directors'].str.split(',')
data_director = (data.set_index(['Your Rating', 'Const', 'Title Type',])['Directors'].apply(pd.Series)
                 .stack().reset_index().drop('level_3', axis=1).rename(columns={0: 'directors_split'}))
data_director['directors_split'] = data_director['directors_split'].str.lstrip()
data['Directors'] = [list_join(l) for l in data['Directors']]

dirselect_ = (data_director[data_director['Title Type'] == 'movie'].groupby(['directors_split'])['directors_split']
             .count().sort_values(ascending=False).head(10))
dirselect = data_director[data_director['Title Type'] == 'movie'].groupby(['directors_split'])
directors_source = ColumnDataSource(data={
    'directors': dirselect_.index.tolist(),
    'movie_nums': dirselect_.values.tolist(),
    'mean_by_dir': [data_director[data_director['directors_split'] == n]['Your Rating'].mean().round(2) for i, n in
                    enumerate(dirselect_.index.tolist())]
})

selected_dir_source = ColumnDataSource(data=full_data(data[(data['Directors'].isin(['Tim Burton']) & (data['Title Type'] == 'movie'))]))

def update_plot(attr, old, new):
    selected_types = []
    for i in range(len(typecheckbutton.active)):
        selected_types.append(typelabels[typecheckbutton.active[i]])
    dirselect_uptd = (data_director[data_director['Title Type'].isin(type_change_r(selected_types))]
                      .groupby(['directors_split'])['directors_split'].count().sort_values(ascending=False))

    updated_dirsdata = {
        'directors': dirselect_uptd.head(slider_nums.value).index.tolist(),
        'movie_nums': dirselect_uptd.head(slider_nums.value).values.tolist(),
        'mean_by_dir': [data_director[data_director['directors_split'] == n]['Your Rating'].mean().round(2) for i, n in
                        enumerate(dirselect['directors_split'].count().sort_values(ascending=False).head(slider_nums.value).index.tolist())]
    }

    directors_source.data = updated_dirsdata
    x_range_f.factors = dirselect_uptd.head(slider_nums.value).index.tolist()
    p.title.text = "Top " + str(slider_nums.value) + " Directors You Watched"

    if graphtoggle.active:
        dirline.visible, dircircle.visible = True, True
    else:
        dirline.visible, dircircle.visible = False, False

    if select_yaxis.value == 'Mean of Rating':
        dirbar.glyph.top = 'mean_by_dir'
        p.yaxis.axis_label = "Mean Of Your Rating"
    else:
        dirbar.glyph.top = 'movie_nums'
        p.yaxis.axis_label = "Total Movie You Watched"

    if select_yaxis_l.value == 'Mean of Rating':
        dirline.glyph.y = 'mean_by_dir'
        dircircle.glyph.y = 'mean_by_dir'
    else:
        dirline.glyph.y = 'movie_nums'
        dircircle.glyph.y = 'movie_nums'

    selected_dirs=[]
    if directors_source.selected.indices:
        for i in range(len(directors_source.selected.indices)):
            selected_dirs.append(directors_source.data['directors'][directors_source.selected.indices[i]])
        sdir_datatable.visible = True
        selected_dir_source_updt = full_data(data[(data['Directors'].str.contains('|'.join(selected_dirs), na=False))
                                                   & (data['Title Type'].isin(type_change_r(selected_types)))])
        selected_dir_source.data = selected_dir_source_updt

# plot
x_range_f = FactorRange(factors=directors_source.data['directors'])
p = figure(title="Top 10 Directors You Watched", x_axis_label="Directors", y_axis_label="Total Movie You Watched",
           x_range=x_range_f, width=600, height=450)
dirbar = p.vbar(x='directors', top='movie_nums', source=directors_source, width=0.9)
dirline = p.line(x='directors', y='mean_by_dir', line_width=2, source=directors_source, color='orange', visible=False)
dircircle = p.circle(x='directors', y='mean_by_dir', line_width=2, source=directors_source, color='orange', visible=False)

p.yaxis.ticker = SingleIntervalTicker(interval=1, num_minor_ticks=0)
p.y_range.start = 0
p.xaxis.major_label_orientation = 0.66
p.toolbar.active_drag = None

p.add_tools(HoverTool(renderers=[dircircle], tooltips=[('Mean of Rating', '@mean_by_dir')]))

# right-side
dirscolumns = [
    TableColumn(field="directors", title="Director Name"),
    TableColumn(field="movie_nums", title="Number Of Movies"),
    TableColumn(field="mean_by_dir", title="Mean")]
dir_datatable = DataTable(source=directors_source, columns=dirscolumns, width=670, height=300)
dir_datatable.source.selected.on_change('indices', update_plot)

slider_nums = Slider(start=3, end=50, value=10, step=1, title="Number of Directors", width=670)
slider_nums.on_change('value', update_plot)

typelabels = ["Movie", "TV Series", "TV Movie", "Short", "TV Mini Series", "TV Episode", "TV Special", "Video"]
typecheckbutton = CheckboxButtonGroup(labels=typelabels, active=[0], width=670)
typecheckbutton.on_change('active', update_plot)

select_yaxis = Select(title="Y-Axis of Bar Chart:", value="Total Movie", options=["Total Movie", "Mean of Rating"], width=220)
select_yaxis.on_change('value', update_plot)

select_yaxis_l = Select(title="Y-Axis of Line Chart:", value="Mean of Rating", options=["Total Movie", "Mean of Rating"], width=220)
select_yaxis_l.on_change('value', update_plot)

graphtoggle = Toggle(label="Display Line Chart", button_type="success", width=220)
graphtoggle.on_change('active', update_plot)

#selected-directors datatable
sdir_datatable = DataTable(source=selected_dir_source, columns=full_data_column(), height=300, width=1270, visible=False)

# layout
rightside = Column(dir_datatable, slider_nums, typecheckbutton, Row(graphtoggle, select_yaxis, select_yaxis_l,
                                                                    sizing_mode='scale_width'), sizing_mode='scale_width')
layout = Column(Row(p,rightside, sizing_mode='scale_width'), sdir_datatable, sizing_mode='scale_width', name='directors')

curdoc().add_root(layout)
curdoc().title = 'Imdb Graphs - Directors'
