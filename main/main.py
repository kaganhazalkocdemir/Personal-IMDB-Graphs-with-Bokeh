from bokeh.io import curdoc
from bokeh.models import FileInput, Div
from pybase64 import b64decode
import pandas as pd
import io

columns = ['Const', 'Your Rating', 'Date Rated', 'Title', 'URL', 'Title Type', 'IMDb Rating', 'Runtime (mins)', 'Year',
		   'Genres', 'Num Votes', 'Release Date', 'Directors']

def upload_file(attr, old, new):
	file = io.BytesIO(b64decode(new))
	try:
		new_data = pd.read_csv(file, encoding='latin1')
		if all(e in new_data.columns for e in columns):
			new_data.to_csv('ratings.csv', index=False)
			error_div.text = """<font color="green"><b>Your file <u>successfully</u> uploaded.
			 Now, you can check Personal Imdb Graphs from right-menu</b></font>"""
		else:
			error_div.text = """<font color="red"><b>This is not IMDB Ratings File!</b></font>"""
	except:
		error_div.text = """<font color="red"><b>This is not .csv file!</b></font>"""

file_input = FileInput(name="fileinput", accept="<.csv>")
file_input.on_change('value', upload_file)

error_div = Div(text="", name="error_div")

curdoc().title = 'Imdb Graphs'
curdoc().add_root(file_input)
curdoc().add_root(error_div)
