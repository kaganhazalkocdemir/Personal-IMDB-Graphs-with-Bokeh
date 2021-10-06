# Personal IMDB Graphs with Bokeh
Do you like watching movies and also rate all of them in IMDB? Would you like to look at your IMDB stats based on your rated movie data? And also would like to see a bunch of graphs and tables. Come in then, this little script is for you!

## Usage
Just start `main.py`. Also you could start manually (start separetly):

```
    bokeh serve --show main/ --port 5001
```
```
    bokeh serve all_movies/ circles/ directors/ heatmaps/ line_charts/ piecharts/ ratings_with_years/ ratings_with_genres/ stack/ tv_series/ --port 5002
```
Also, you could start separetly :
`bokeh serve --show line_charts/`

## Dependencies
* Bokeh 3.4
* Pandas
* pybase64 (only for reading your .csv file in `main/` folder)

## _Any error? New Ideas?_
Please feel free to pull request, If you found any problem. Also you could contact me with `angelsdemos@gmail.com`

## Screenshots

![All Movies](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs.png)
![Line Charts](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs6.png)
![Directors](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs8.png)
![Datatable](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs4.png)
![Pie Chart](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs2.png)
![Heatmap](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs10.png)
![Heatmap](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs3.png)
![Stack](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs7.png)
![Circles](/blob/9eee83499e2da13d18bc67f04c7a983e46f6b68f\Screenshots\imdbgraphs11.png)

For more screenshots, look at `Screenshots/` folder.
