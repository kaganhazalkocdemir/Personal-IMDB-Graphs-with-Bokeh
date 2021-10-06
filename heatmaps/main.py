import pandas as pd
import calendar
from bokeh.io import curdoc
from bokeh.models import (BasicTicker, ColorBar, ColumnDataSource,
                          LinearColorMapper, PrintfTickFormatter, Select)
from bokeh.plotting import figure
from bokeh.models.tools import HoverTool
from bokeh.layouts import Column, Row
from bokeh.palettes import Inferno256, Magma256, Plasma256, Viridis256, Cividis256, Turbo256, Greys256, BrBG10
from tools import openfile

# source prep.
data = openfile()
data['month_rated'] = pd.to_datetime(data['Date Rated']).dt.month
data['year_rated'] = pd.to_datetime(data['Date Rated']).dt.year
new_data = pd.DataFrame({'count': data.groupby(['year_rated', 'month_rated'], dropna=False)['month_rated'].count()}).reset_index()

new_data['month_rating'] = data.groupby(['year_rated', 'month_rated'], dropna=False)['Your Rating'].mean().values

x_range = new_data.drop_duplicates(subset=["year_rated"])["year_rated"].sort_values().values.astype(str)
y_range = new_data.drop_duplicates(subset=["month_rated"])["month_rated"].sort_values().values.astype(str)

new_data.year_rated = new_data.year_rated.astype(str)
new_data.month_rated = new_data.month_rated.astype(str)

source = ColumnDataSource(data={
    'month': new_data['month_rated'],
    'year': new_data['year_rated'],
    'count': new_data['count'],
    'month_rating' : new_data['month_rating']
})

defaultcolors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d", "#550b2d"]

Colorpallettes = ["Default","Inferno", "Magma", "Plasma", "Viridis", "Cividis", "Turbo", "Greys", 'Inferno Reverse',
                  'Magma Reverse','Plasma Reverse','Viridis Reverse','Cividis Reverse','Turbo Reverse','Greys Reverse',
                  'BrBG', 'BrBG Reverse']

Colorpallettesdict = {'Inferno': Inferno256, 'Magma':Magma256, 'Plasma':Plasma256, 'Viridis':Viridis256,
                      'Cividis':Cividis256,'Turbo':Turbo256, 'Greys':Greys256, 'Inferno Reverse':Inferno256[::-1],
                      'Magma Reverse':Magma256[::-1], 'Plasma Reverse':Plasma256[::-1], 'Viridis Reverse':Viridis256[::-1],
                      'Cividis Reverse':Cividis256[::-1], 'Turbo Reverse':Turbo256[::-1], 'Greys Reverse':Greys256[::-1],
                      'BrBG':BrBG10,'BrBG Reverse':BrBG10[::-1], "Default": defaultcolors}


def update_plot(attr, old, new):
    mapper.palette = Colorpallettesdict[select_color.value]

    if select_heatmap.value == select_heatmap_l[0]:
        mapper.low = source.data['count'].min()
        mapper.high = source.data['count'].max()
        rects.glyph.fill_color = {'field': 'count', 'transform': mapper}
        p.title.text = "Number of Productions You Watched by Years"
        color_bar.title = "Number of Rated Productions"
        hovertool.tooltips = [("Year", "@year"), ("Month", "@month"), ("Total", "@count")]
    elif select_heatmap.value == select_heatmap_l[1]:
        mapper.low = 1
        mapper.high = 10
        rects.glyph.fill_color = {'field': 'month_rating', 'transform': mapper}
        p.title.text = "Average Rating You Watched by Years"
        color_bar.title = "Your Average Rating"

        hovertool.tooltips = [("Year", "@year"), ("Month", "@month"), ("Average Rating", "@month_rating")]


mapper = LinearColorMapper(palette=defaultcolors, low=source.data['count'].min(), high=source.data['count'].max())

p = figure(plot_width=900, plot_height=450, title="Number of Productions You Watched by Years",
           x_range=x_range, y_range=y_range, x_axis_location="above", tools="")

rects = p.rect(x="year", y="month", width=1, height=1, source=source,
               line_color=None, fill_color={'field': 'count', 'transform': mapper})

color_bar = ColorBar(color_mapper=mapper, title="Number of Rated Productions", title_text_font_style='normal',
                     ticker=BasicTicker(desired_num_ticks=10),
                     formatter=PrintfTickFormatter(format='%.1d'))

hovertool = HoverTool(tooltips=[("Year", "@year"), ("Month", "@month"), ("Total", "@count")])


p.add_tools(hovertool)
p.add_layout(color_bar, 'right')

p.axis.axis_line_color = None
p.axis.major_tick_line_color = None

p.axis.major_label_text_font_size = "12px"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = 1.0

select_heatmap_l = ['Production Numbers', 'Your Rating']

select_heatmap = Select(title="Heatmaps by:", value=select_heatmap_l[0], options=select_heatmap_l)
select_heatmap.on_change('value', update_plot)


select_color = Select(title="Color Pallette:", value=Colorpallettes[0], options=Colorpallettes)
select_color.on_change('value', update_plot)

layout = Row(p,Column(select_heatmap,select_color), name='heatmaps')

curdoc().add_root(layout)
curdoc().title = 'Imdb Graphs - Heatmaps'
