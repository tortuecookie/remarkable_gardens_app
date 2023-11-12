# importing the relevant packages
import streamlit as st
import pandas as pd
import folium as fl
import geopandas as gpd
from streamlit_folium import folium_static

# setting up the page configuration
st.set_page_config(layout = "wide")

# providing a title
st.title('Gardens of France')

# making short intro
st.markdown("""
    **Using the maps below, discover the most remarkable gardens of France :deciduous_tree: :evergreen_tree: :palm_tree:!**
""")

# creating the section with the purpose of the app
st.header('Purpose', divider = 'rainbow')
github_url = "https://github.com/tortuecookie/remarkable_gardens_app"
st.markdown("""
    The purpose of this app is to illustrate the use of the *folium* Python package to visualize geospatial data using Python.
    This app was built using *streamlit*.
    The code used to build the app is provided in the last section.
    This app is also available on my GitHub page here: [app](%s).
""" % github_url)

# creating the section with the data description
st.header('Data description', divider = 'rainbow')
gardens_url = "https://www.data.gouv.fr/fr/datasets/liste-des-gardens-remarquables/"
st.markdown("""
    The data on the gardens was taken from the French gov open source platform here: [gardens](%s). 
    It provides geospatial information on the most remarkable gardens of France.
""" % gardens_url)
geojson_url = "https://france-geojson.gregoiredavid.fr/"
st.markdown("""
    The geojson data for the French departments was taken from here: [geojson](%s) (thank you very much Grégoire for making the data available!).
""" % geojson_url)

# loading the gardens data
gardens_file = "liste-des-jardins-remarquables.csv"
gardens = pd.read_csv(gardens_file, sep = ";")
gardens.rename(columns = {"nom_du_jardin": "Garden's name", "description": "Description", "departement": "Department"}, inplace = True)

# loading the geojson data
dpts_file = "departements.geojson"
dpts_data = gpd.read_file(dpts_file)
dpts_data = dpts_data[["nom", "geometry"]]

# creating the first select box in the sidebar
unique_types = [t.split("|") for t in list((gardens["types"].unique()))]
unique_types = list(set([item for sublist in unique_types for item in sublist]))
unique_types.insert(0, "All")
add_selectbox = st.sidebar.selectbox(
    'What type of garden would you like to see?',
    unique_types
)

# creating the second select box in the sidebar
unique_departements = list(gardens["Department"].unique())
unique_departements.insert(0, "All")
add_selectbox_2 = st.sidebar.selectbox(
    'Which department in particular would you like to consider?',
    unique_departements
)

# filtering the data according to the select boxes
if add_selectbox != "All":
    gardens = gardens.loc[gardens["types"].str.contains(add_selectbox)]
if add_selectbox_2 != "All":
    gardens = gardens.loc[gardens["Department"] == add_selectbox_2]

# creating the section with the maps
st.header('Maps', divider = 'rainbow')

# creating the first map
st.markdown("""
    Below a map showing the repartition of the remarkable gardens on the French territory.
""")
map_1 = fl.Map(location = [gardens["latitude"].mean(), gardens["longitude"].mean()], zoom_start = 5, control_scale = True)
fl.TileLayer('openstreetmap').add_to(map_1) # actually this is the tile option by default, but we show it as an example
clusters = fl.plugins.MarkerCluster().add_to(map_1)
for index, location_info in gardens.iterrows():
    text = f"""
    <h6> <b> Information </b> </h6>
    <i> Name </i>: {location_info["Garden's name"]}
    <br>
    <i> Location </i>: {location_info['region']}
    <br>
    <i> To know more: </i>: {location_info['site_internet_et_autres_liens']}
    """
    fl.Marker([location_info["latitude"], location_info["longitude"]], popup = fl.Popup(text, max_width = 400)).add_to(clusters)
folium_static(map_1)

# creating the second map
st.markdown("""
    Below a map showing the number of gardens by department.
""")
gardens_per_dpt = gardens.groupby(['Department'], as_index = False).size()
gardens_per_dpt.rename(columns = {"size": "Number of gardens"}, inplace = True)
gardens_per_dpt = dpts_data.merge(gardens_per_dpt, left_on = "nom", right_on = "Department")
gardens_per_dpt = gardens_per_dpt[["Department", "Number of gardens", "geometry"]]
map_2 = fl.Map(location = [gardens["latitude"].mean(), gardens["longitude"].mean()], zoom_start = 5, control_scale = True)
fl.TileLayer('cartodbpositron').add_to(map_2)
fl.Choropleth(
    columns = ['Department', 'Number of gardens'],
    data = gardens_per_dpt,
    fill_color = 'BuPu',
    fill_opacity = 0.6,
    key_on = 'feature.properties.Department',
    legend_name = 'Number of gardens by department',
    line_opacity = 0.2,
    geo_data = gardens_per_dpt,
    highlight = True,
    name = 'Remarkable gardens'
).add_to(map_2)
style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.3, 'weight': 0.1}
dpts_borders = fl.features.GeoJson(
    gardens_per_dpt,
    style_function = style_function, 
    control = False,
    highlight_function = highlight_function, 
    tooltip = fl.features.GeoJsonTooltip(
        fields = ['Department', 'Number of gardens'],
        aliases = ['Department: ', 'Number of gardens: '],
        style = ("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 5px;") 
    )
)
map_2.add_child(dpts_borders)
map_2.keep_in_front(dpts_borders)
fl.LayerControl().add_to(map_2)
folium_static(map_2)

# creating the section with the full list of gardens
st.header('Full list of gardens', divider = 'rainbow')
st.markdown("""
    The descriptions of the gardens in the table below is provide in French: this is a good occasion for you to practice it :wink:.
""")
with st.expander("Please click here to see the full list of the gardens, with detailed descriptions"):
    gardens_per_dpt = gardens[["Garden's name", "Description"]].copy()
    st.table(gardens_per_dpt.set_index(gardens_per_dpt.columns[0]))

# creating the section with the code of the app
st.header('Python code of the app', divider = 'rainbow')
with st.expander("Python code of the app with comments (click here to hide the code)", expanded = True):
    with open("remarkable_gardens.py") as f:
        code_to_display = f.read()
        st.code(code_to_display, "python")
