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
import os
import datetime  # Adicione este import no início do seu script

st.set_page_config( page_title='Visão Entregadores', page_icon='🛵', layout='wide' )

# ===================================================================================
# Funções
# ===================================================================================

def top_delivers( df1, top_asc ):
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby(['City', 'Delivery_person_ID'])
               .mean()
               .sort_values(['City', 'Time_taken(min)'], ascending=top_asc )
               .reset_index() )

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
    st.dataframe( df3 )
    
    return df3    

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

# ===================================================================================
# Import dataset
df = pd.read_csv('dataset/train.csv')

# ===================================================================================

# Limpando os dados
df1 = clean_code( df )

# ===================================================================================
# Sidebar ( Barra Lateral ) no Streamlit
# ===================================================================================

st.header('Marketplace - Visão Entregadores')

#image_path = '/Users/diogo/Documents/Comunidade-DS/ftc_programação_python/logo.png'
image=Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 6),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 13),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """___""" )
traffic_options = st.sidebar.multiselect(
    'Condições de Trânsito',
    [ 'Low', 'Medium', 'High',  'Jam' ],
    default=[ 'Low', 'Medium', 'High',  'Jam' ] )

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior de Idade', maior_idade )
        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor Idade', menor_idade )
        
        with col3:
            # A melhor condição dos veículos
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição', melhor_condicao )
            
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', pior_condicao )
    
    with st.container():
        st.markdown( """---""" )
        st.title( 'Avaliações' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliação média por entregador' )
            df_avg_ratings_per_delivery =  ( df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                               .groupby('Delivery_person_ID')
                                               .mean()
                                               .reset_index() )
            st.dataframe( df_avg_ratings_per_delivery )
            
        with col2:
            st.markdown( '##### Avaliação média por trânsito' )
            df_avg_std_rating_by_traffic = ( df1.loc[ :, [ 'Delivery_person_Ratings', 'Road_traffic_density' ] ]
                                     .groupby( 'Road_traffic_density' )
                                     .agg( { 'Delivery_person_Ratings' : [ 'mean', 'std' ] } ) )
            
            # mundança de nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_rating_by_traffic.reset_index()
            st.dataframe( df_avg_std_rating_by_traffic )

            
            st.markdown( '##### Avaliação média por clima' )
            df_avg_std_by_weather = ( df1.loc[ :, [ 'Delivery_person_Ratings', 'Weatherconditions' ] ]
                                     .groupby( 'Weatherconditions' )
                                     .agg( { 'Delivery_person_Ratings' : [ 'mean', 'std' ] } ) )
            # mundança de nome das colunas
            df_avg_std_by_weather.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_by_weather.reset_index()
            st.dataframe( df_avg_std_by_weather )
    
    with st.container():
        st.markdown( """---""" )
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Top Entregadores mais rápidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )
            
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )