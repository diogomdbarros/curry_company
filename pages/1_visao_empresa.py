
# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import re
from datetime import time
from PIL import Image
import folium
from streamlit_folium import folium_static

# Import Dataset
import os

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

# ===================================================================================
# Funções
# ===================================================================================

def clean_code( df1 ):
    
    """ Está função tem a responsabilidade de limpar o DataFrame
    
        Tipos de Limpeza:
        1. Remoção dos dados NaN
        2. Mudança de tipo das colunas de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Imput: Dataframe
        Output: Dataframe
    """

    # 1. Convertendo o tipo da coluna Delivery_person_Age de texto para inteiro e removendo os valores nulos
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # Removendo os valores nulos
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 2. Convertendo o tipo da coluna Delivery_person_Ratings de texto para float

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. Convertendo o tipo da coluna Delivery_person_Ratings de texto para float
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4. Convertendo o tipo da coluna multiple_deliveries de texto para inteiro
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5. Removendo os espaços dentro de strings/texto/object
    # df1 = df1.reset_index(drop=True)
    # for i in range(len( df1 )):
    #     df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

    # 6. Removendo os espaços dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split ( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1 

def order_metric( df1 ):
    cols = ['ID', 'Order_Date']
    # selecao de linhas
    df_aux = df1.loc[:, cols].groupby( 'Order_Date' ).count().reset_index()
    # desenhar o grafico de linhas
    fig = px.bar( df_aux, x='Order_Date', y='ID')
    
    return fig
    
def traffic_order_share( df1 ):
    df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density']]
                  .groupby('Road_traffic_density')
                  .count()
                  .reset_index() )
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    fig = px.pie( df_aux, values='ID',names='Road_traffic_density')
    
    return fig

def traffic_order_city( df1 ):
    df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density', 'City']]
              .groupby(['City', 'Road_traffic_density'])
              .count()
              .reset_index() )
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID')
    
    return fig
    
def order_by_week( df1 ):
    # Cria a coluna semana
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime( '%U')
    df_aux = ( df1.loc[:, ['ID', 'Week_of_year']]
              .groupby( 'Week_of_year' )
              .count()
              .reset_index() )
    fig = px.line( df_aux, x='Week_of_year', y='ID' )

    return fig

def order_share_by_week( df1 ):        
    # Quantidade de pedidos por semana / Número único de entregadores por semana
    df_aux01 = ( df1.loc[:, ['ID', 'Week_of_year']]
                    .groupby('Week_of_year')
                    .count()
                    .reset_index() )
    df_aux02 = ( df1.loc[:, ['Delivery_person_ID', 'Week_of_year']]
                    .groupby('Week_of_year')
                    .nunique()
                    .reset_index() )

    df_aux = pd.merge( df_aux01, df_aux02, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_of_year', y='order_by_deliver')

    return fig

def coutry_maps( df1 ):
            
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = ( df1.loc[:, cols]
                  .groupby(['City', 'Road_traffic_density'])
                  .median()
                  .reset_index() )
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info [['City', 'Road_traffic_density']]).add_to(map)
    folium_static( map, width=1024, height=600 )


# ===================================================================================
# Início da Estrutura lógica do código
# ===================================================================================    

# Import dataset

df = pd.read_csv('dataset/train.csv')

# ===================================================================================

# Limpando os dados
df1 = clean_code( df )

# ===================================================================================
# Sidebar ( Barra Lateral ) no Streamlit
# ===================================================================================

st.header('Marketplace - Visão Cliente')

#image_path = '/Users/diogo/Documents/Comunidade-DS/ftc_programação_python/logo.png'
image=Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.sidebar.markdown( '## Selecione uma data limite' )

import datetime  # Adicione este import no início do seu script

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 6),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 13),
    format='DD-MM-YYYY')

st.sidebar.markdown( """___""" )
traffic_options = st.sidebar.multiselect(
    ' Quais as condições de trânsito ',
    ['Low', 'Medium', 'High',  'Jam'],
    default=['Low', 'Medium', 'High',  'Jam'] )

st.sidebar.markdown( """___""" )
conditions_options = st.sidebar.multiselect( 
    'Condições Climáticas',
    [ 'Cloudy', 'Fog', 'Sandstorms', 'Storm', 'Sunny', 'Wind' ],
    default=[ 'Cloudy', 'Fog', 'Sandstorms', 'Storm', 'Sunny', 'Wind' ] )

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '##### Powerd By Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# ===================================================================================
# Layout no Streamlit
# ===================================================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric( df1 )
        st.header( 'Orders by Day' )
        st.plotly_chart ( fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_width=True )             

        with col2:
            fig = traffic_order_city( df1 )
            st.header( 'Traffic Order City' )
            st.plotly_chart( fig, use_container_width=True )           

with tab2:
    with st.container():
        fig = order_by_week( df1 )
        st.header( "Order by Week" )
        st.plotly_chart( fig, use_container_width=True )
            
    with st.container():
        fig = order_share_by_week( df1 )
        st.header( "Order Share by Week" )
        st.plotly_chart( fig, use_container_width=True )
                
        
    with tab3:
        st.header( "Country Maps" )
        coutry_maps( df1 )