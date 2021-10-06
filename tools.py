from bokeh.models import TableColumn, HTMLTemplateFormatter, DateFormatter
import pandas as pd

def type_change(type_list):
    def t_list_change(tlist):
        new = []
        for i, type_name in enumerate(tlist):
            if type_name == 'movie':
                new.append("Movie")
            elif type_name == 'tvMiniSeries':
                new.append("TV Mini Series")
            elif type_name == 'tvMovie':
                new.append("TV Movie")
            elif type_name == 'tvSeries':
                new.append("TV Series")
            elif type_name == 'tvEpisode':
                new.append("TV Episode")
            elif type_name == 'short':
                new.append("Short")
            elif type_name == 'video':
                new.append("Video")
            elif type_name == 'tvSpecial':
                new.append("TV Special")
            else:
                new.append(type_name)
        return new
    if not isinstance(type_list, list):
        x = []
        x.append(type_list)
        return t_list_change(x)[0]
    else:
        return t_list_change(type_list)


def type_change_r(type_list):
    def t_list_change(tlist):
        new = []
        for i, type_name in enumerate(tlist):
            if type_name == 'Movie':
                new.append("movie")
            elif type_name == 'TV Mini Series':
                new.append("tvMiniSeries")
            elif type_name == 'TV Movie':
                new.append("tvMovie")
            elif type_name == 'TV Series':
                new.append("tvSeries")
            elif type_name == 'TV Episode':
                new.append("tvEpisode")
            elif type_name == 'Short':
                new.append("short")
            elif type_name == 'Video':
                new.append("video")
            elif type_name == 'TV Special':
                new.append("tvSpecial")
            else:
                new.append(type_name)
        return new
    if not isinstance(type_list, list):
        x = []
        x.append(type_list)
        return t_list_change(x)[0]
    else:
        return t_list_change(type_list)

curdocthemes = ['caliber', 'dark_minimal', 'light_minimal', 'night_sky', 'contrast']

def full_data(datavar, typechange=0, nonlist=[], newdata=[]):
    '''
    creates full data generally for data-tables
    :param typechange : create type to good looking version. ex. tvSeries -> TV Series
    :param nonlist : removes unwanted TableColumn numbers. should be a list like [6,0,3, ...]
    :param newdata : adds new data.[[name, datakey], [name2, datakey2], ...]
    '''
    data_dict = {'Const': datavar['Const'],  # 0
                 'Your Rating': datavar['Your Rating'],  # 1
                 'Date Rated': datavar['Date Rated'],  # 2
                 'Title': datavar['Title']}  # 3
    if typechange:   # 4
        data_dict.update({'Type': type_change(datavar['Title Type'].tolist())})
    else:
        data_dict.update({'Type': datavar['Title Type'].tolist()})
    data_dict.update({'URL': datavar['URL'],   # 5
                      'IMDb Rating': datavar['IMDb Rating'],  # 6
                      'Runtime (mins)': datavar['Runtime (mins)'],  # 7
                      'Year': datavar['Year'],  # 8
                      'Genres': datavar['Genres'],  # 9
                      'Num Votes': datavar['Num Votes'],  # 10
                      'Release Date': datavar['Release Date'],  # 11
                      'Directors': datavar['Directors']})  # 12

    columnlist = ['Const', 'Your Rating', 'Date Rated', 'Title', 'Type', 'URL', 'IMDb Rating', 'Runtime (mins)', 'Year',
                  'Genres', 'Num Votes', 'Release Date', 'Directors']

    # delete unwanted items and add new items
    for i in sorted(nonlist, reverse=True):
        data_dict.pop(columnlist[i])

    for i, n in enumerate(newdata):
        data_dict[n[0]] = datavar[n[1]]

    return data_dict


def full_data_column(nonlist=[], addnew=[], dateformatter=False):
    '''
    creates a data columns for datatables
    :param nonlist : removes unwanted TableColumn numbers. should be a list like [6,0,3, ...]
    :param addnew : adds new TableColumn. [[field1, title1, index1], [field2, number2, index2], ...]. uses datavar
    :param dateformatter : add dateformatter to datatable column
    '''
    formatter = DateFormatter(format="%m/%d/%Y")
    datacolumns = [
    TableColumn(field="Title", title="Title"),  # 0
    TableColumn(field="Year", title="Year"),  # 1
    TableColumn(field="Type", title="Type"),  # 2
    TableColumn(field="Your Rating", title="User Raiting")]  # 3
    if dateformatter:
        datacolumns.append(TableColumn(field="Date Rated", title="Date Rated", formatter=formatter))  # 4
    else:
        datacolumns.append(TableColumn(field="Date Rated", title="Date Rated"))  # 4
    datacolumns.extend((
    TableColumn(field="IMDb Rating", title="Imdb Raiting"),  # 5
    TableColumn(field="Num Votes", title="Number of Votes"),  # 6
    TableColumn(field="Runtime (mins)", title="Runtime (mins)"),  # 7
    TableColumn(field="Directors", title="Director(s)")))  # 8
    if dateformatter:
        datacolumns.append(TableColumn(field="Release Date", title="Release Date", formatter=formatter))  # 9
    else:
        datacolumns.append(TableColumn(field="Release Date", title="Release Date"))  # 9
    datacolumns.extend((
    TableColumn(field="Genres", title="Genres"),  # 10
    TableColumn(field="URL", title="URL",  # 11
                formatter=HTMLTemplateFormatter(template='<a href="<%=value%>"><%=value%></a>'))))

    # delete unwanted items and add new items
    for i in sorted(nonlist, reverse=True):
        datacolumns.pop(i)
    for i, n in enumerate(sorted(addnew, key=lambda item: item[2])):
        datacolumns = datacolumns[:n[2]] + [TableColumn(field=n[0], title=n[1])] + datacolumns[n[2]:]

    return datacolumns

def openfile():
    filename = 'ratings.csv'
    data = pd.read_csv(filename, encoding='latin1')
    return data

def list_join(l):
    # list to str with ','
    try:
        return ','.join(map(str, l))
    except TypeError:
        return None

def getlistof(listname):
    data = openfile()
    types = data['Title Type'].unique()
    data['Genres'] = data['Genres'].str.split(',')
    data = (data.set_index(['Your Rating', 'Const', 'Title Type', 'Runtime (mins)'])['Genres'].apply(pd.Series)
                  .stack().reset_index().drop('level_4', axis=1).rename(columns={0: 'Genres_split'}))
    data['Genres_split'] = data['Genres_split'].str.strip()
    genres = data.drop_duplicates(subset=["Genres_split"])['Genres_split'].sort_values().tolist()
    if listname == 'types':
        return types
    elif listname == 'genres':
        return genres

genre_list = ['Comedy', 'Drama', 'Romance', 'Action', 'Sci-Fi', 'Thriller', 'Fantasy', 'Biography', 'Adventure',
              'Family', 'Crime', 'Mystery', 'Horror', 'Music', 'Animation', 'Short', 'Documentary', 'History',
              'Western', 'Musical', 'War', 'Sport', 'Reality-TV', 'News']