import os
import platform

if __name__ == '__main__':
    if platform.system() == 'Windows':
        os.system("start cmd /K py -m bokeh serve --show main/ --port 5001")
        os.system("start cmd /K py -m bokeh serve all_movies/ circles/ directors/ heatmaps/ line_charts/ piecharts/ ratings_with_years/ ratings_with_genres/ stack/ tv_series/ --port 5002")
    else:
        os.system("bokeh serve --show main/ --port 5001")
        os.system("bokeh serve all_movies/ circles/ directors/ heatmaps/ line_charts/ piecharts/ ratings_with_years/ ratings_with_genres/ stack/ tv_series/ --port 5002")