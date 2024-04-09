import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static
import json
import ast

@st.cache
def load_data():
    df = pd.read_csv('country_chlor_df.csv')
    return df

@st.cache
def load_geojson():
    with open('world-countries.json') as f:
        geo_data = json.load(f)
    return geo_data
    
def find_pairs(countries, target_country):
    countries = ast.literal_eval(countries)
    entering_pairs = []
    leaving_pairs = []
    for i in range(1, len(countries)):
        if countries[i] == target_country and countries[i-1] != target_country:
            entering_pairs.append(countries[i-1])
        elif countries[i-1] == target_country and countries[i] != target_country:
            leaving_pairs.append(countries[i])
    return entering_pairs, leaving_pairs

def process_data(df, target_country):
    entering = []
    leaving = []
    for _, row in df.iterrows():
        e, l = find_pairs(row['country'], target_country)
        entering.extend(e)
        leaving.extend(l)

    entering_freq = pd.Series(entering).value_counts().reset_index(name='entering_frequency')
    leaving_freq = pd.Series(leaving).value_counts().reset_index(name='leaving_frequency')
    entering_freq = entering_freq.dropna(subset=['entering_frequency'])
    leaving_freq = leaving_freq.dropna(subset=['leaving_frequency'])
    merged_df = pd.merge(
        entering_freq.rename(columns={'index': 'country'}),
        leaving_freq.rename(columns={'index': 'country'}),
        on='country',
        how='outer'
    ).fillna(0)
    merged_df['entering_frequency'] = merged_df['entering_frequency'].astype(float)
    merged_df['leaving_frequency'] = merged_df['leaving_frequency'].astype(float)
    merged_df['net_frequency'] = merged_df['entering_frequency'] - merged_df['leaving_frequency']
    merged_df['net_frequency'] = merged_df['net_frequency'].astype(float)

    merged_df = merged_df.fillna(0)

    return merged_df

def plot_choropleth(geojson_data, data, target_country):
    
    data = data.fillna(0)
    data['entering_frequency'] = pd.to_numeric(data['entering_frequency'], errors='coerce').fillna(0)
    data['leaving_frequency'] = pd.to_numeric(data['leaving_frequency'], errors='coerce').fillna(0)
    data['net_frequency'] = pd.to_numeric(data['net_frequency'], errors='coerce').fillna(0)

    m = folium.Map(location=[20, 0], zoom_start=2)

    folium.Choropleth(
        geo_data=geojson_data,
        name=f'Entering {target_country}',
        data= data,
        columns=['country', 'entering_frequency'],
        key_on='feature.properties.name',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Entering {target_country}'
    ).add_to(m)

    folium.Choropleth(
        geo_data=geojson_data,
        name=f'Leaving {target_country}',
        data=data,
        columns=['country', 'leaving_frequency'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Leaving {target_country}'
    ).add_to(m)

    folium.Choropleth(
        geo_data=geojson_data,
        name=f'Net Movement in relation to {target_country}',
        data=data,
        columns=['country', 'net_frequency'],
        key_on='feature.properties.name',
        fill_color='PiYG',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Net Movement in relation to {target_country}'
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

def main():
    st.title('Choropleth Map for Research Migration')
    
    df = load_data()
    geojson_data = load_geojson()
    
    countries = ['Portugal', 'United States of America', 'United Kingdom', 'France',
       'South Africa', 'Italy', 'Japan', 'Denmark', 'Taiwan', 'Russia',
       'China', 'Canada', 'Argentina', 'Germany', 'Ireland', 'Belgium',
       'Norway', 'Spain', 'Slovakia', 'Poland', 'Finland', 'Australia',
       'Switzerland', 'Saudi Arabia', 'Mexico', 'Algeria', 'Brazil',
       'Netherlands', 'Czechia', 'Armenia', 'Greece', 'Egypt', 'India',
       'South Korea', 'Sweden', 'Malaysia', 'Iran', 'Iceland', 'Austria',
       'Chile', 'Ukraine', 'Hungary', 'Serbia', 'Israel', 'Estonia',
       'Romania', 'Croatia', 'Pakistan', 'Bangladesh', 'Belarus',
       'Morocco', 'Venezuela', 'Bulgaria', 'Lebanon', 'Vietnam', 'Turkey',
       'Uzbekistan', 'Puerto Rico', 'Costa Rica', 'Palestine',
       'New Zealand', 'Libya', 'Colombia', 'Ghana', 'Azerbaijan',
       'Lithuania', 'Cuba', 'Indonesia', 'Ecuador', 'Slovenia',
       'Paraguay', 'Cameroon', 'Tunisia', 'Ethiopia', 'Kazakhstan',
       'North Macedonia', 'Moldova', 'Peru', 'Latvia', 'Botswana',
       'Georgia', 'Zimbabwe', 'Thailand', 'Nigeria', 'Iraq', 'N. Cyprus',
       'United Arab Emirates', 'Senegal', 'Philippines', 'Luxembourg',
       'Jordan', 'Trinidad and Tobago', 'Kyrgyzstan', 'Kenya', 'Cyprus',
       'Sri Lanka', 'Haiti', 'Dominican Rep.', 'Panama', 'Kuwait',
       'Somalia', 'Madagascar', 'Uganda', 'Gambia', 'Mongolia', 'Angola',
       'Uruguay', 'Bosnia and Herz.', 'Albania', 'Nicaragua', 'Yemen']
    
    target_country = st.selectbox('Select a Country', countries)
    
    if target_country:
        data = process_data(df, target_country)
        if data is not None:
            m = plot_choropleth(geojson_data, data, target_country)
            if m is not None:
                folium_static(m)

if __name__ == '__main__':
    main()
