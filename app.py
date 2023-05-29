import streamlit as st
import plotly.express as px
import pandas as pd
import json 
import requests
from streamlit_lottie import st_lottie
from numerize import numerize

# Utilise tout l'espace disponible
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Chargement des données
def load_data():
    return pd.read_csv('data/bapenda-od_15832_jml_kndrn_tidak_daftar_ulang__jenis_kndrn_fungsi_kndrn_data.csv', sep=',', index_col=0)

df_kendaraan = load_data()
df_kendaraan['fungsi_kendaraan'] = df_kendaraan['fungsi_kendaraan'].str.strip()
df_kendaraan['nama_kabupaten_kota'] = df_kendaraan['nama_kabupaten_kota'].str.strip()
df_kendaraan['cabang_pelayanan'] = df_kendaraan['cabang_pelayanan'].str.strip()

# data for metric


# Titre du Dashboard
def load_url(url: str):
    animation = requests.get(url)
    if animation.status_code != 200:
        return None 
    return animation.json()

animation = load_url('https://assets10.lottiefiles.com/packages/lf20_ymyikn6l.json')
# Organisation du dashboard
met1, met2, met3 = st.columns(3)
left_tab1, left_tab2, right_tab1, right_tab2 = st.tabs(['Visual 1', 'Visual 2', 'Visual 3', 'Visual 4'])
# Ajout d'un formulaire de filtre
with st.sidebar:
    st_lottie(animation)
    st.title("Dashboard Kendaraan Yang Tidak Terdaftar Ulang di Provinsi Jabar 2013 - 2022")

    with st.expander('Klik untuk membuka parameter pencarian'):
        st.write("""Pilih parameter yang sesuai dibawah ini untuk memfilter data yang ditampilkan dalam bentuk grafik: """)

        dates = df_kendaraan['tahun']
        categories = df_kendaraan['jenis_kendaraan'].unique()
        segments = df_kendaraan['fungsi_kendaraan'].unique()
        regions = df_kendaraan['nama_kabupaten_kota'].unique()
        

        date_range = st.select_slider('Pilih tahun :',
            options = [x for x in range(2013, 2023)],
            value = (2013, 2015)
        
        )
        start_date, end_date = date_range

        selected_categories = st.multiselect(
            label = 'Pilih kategori kendaraan :',
            options = categories,
            default = categories
        )

        selected_segments = st.multiselect(
            label = 'Pilih segment kendaraan :',
            options = segments,
            default = segments
        )

       
        selected_regions = st.selectbox(
            label = 'Pilih Kota/Kabupaten :',
            options = list(regions) + ['Semua'],
        )
        
        if selected_regions != 'Semua':
            df_kendaraan = df_kendaraan.query('tahun >= @start_date \
                and tahun <= @end_date \
                and jenis_kendaraan in @selected_categories \
                and fungsi_kendaraan in @selected_segments \
                and nama_kabupaten_kota in @selected_regions \
            ')
        else:
            df_kendaraan = df_kendaraan.query('tahun >= @start_date \
                and tahun <= @end_date \
                and jenis_kendaraan in @selected_categories \
                and fungsi_kendaraan in @selected_segments \
            ')
        
        pivot_kabupaten_kota = df_kendaraan.pivot_table(index=['nama_kabupaten_kota'], values='jumlah_kendaraan', aggfunc='sum').reset_index()
        pivot_cabang_pelayanan = df_kendaraan.pivot_table(index=['nama_kabupaten_kota', 'cabang_pelayanan'], values='jumlah_kendaraan', aggfunc='sum').reset_index()
        pivot_kabupaten_kota_kendaraan = df_kendaraan.pivot_table(index=['nama_kabupaten_kota', 'fungsi_kendaraan'], values='jumlah_kendaraan', aggfunc='sum').reset_index()
        pivot_total_kendaraan = df_kendaraan.pivot_table(index=['jenis_kendaraan', 'tahun'], values='jumlah_kendaraan', aggfunc='sum').reset_index()
        pivot_fungsi_kendaraan = df_kendaraan.pivot_table(index=['fungsi_kendaraan', 'tahun'], values='jumlah_kendaraan', aggfunc='sum').reset_index()
        
        if df_kendaraan.empty:
            st.error('Tidak ada data untuk pilihan ini: pilih parameter lain.')
            st.stop()

with met1:
    summary = df_kendaraan['jumlah_kendaraan'].sum().astype(float)
    st.metric(label='Total kendaraan', value=numerize.numerize(summary))
    
with met2:
    minimal = df_kendaraan['jumlah_kendaraan'].min().astype(float)
    st.metric(label='Minimal jumlah kendaraan', value=numerize.numerize(minimal))

with met3:
    maximal = df_kendaraan['jumlah_kendaraan'].max().astype(float)
    st.metric(label='Maximal jumlah kendaraan', value=numerize.numerize(maximal))

with left_tab1:
    if selected_regions == 'Semua':
        st.subheader('Total kendaraan dari setiap kota/kabupaten')
        # products_sold_per_category_container = st.container()
        # with products_sold_per_category_container:
            
        figbar2 = px.bar(pivot_kabupaten_kota, x='jumlah_kendaraan', y='nama_kabupaten_kota', color='nama_kabupaten_kota', orientation='h')
        st.plotly_chart(figbar2, use_container_width=True, config={'displayModeBar': True}, theme='streamlit')
    else:
        st.subheader('Total kendaraan dari setiap kota/kabupaten')
        # total_kendaraan_per_kota = st.container()
        # with total_kendaraan_per_kota:
        figbar2 = px.bar(pivot_cabang_pelayanan, y='jumlah_kendaraan', x='cabang_pelayanan', color='cabang_pelayanan')
        st.plotly_chart(figbar2, use_container_width=True, config={'displayModeBar': True})

with left_tab2:
    if selected_regions != 'Semua':
        st.subheader('Jumlah kendaraan berdasarkan fungsi kendaraan')
        figline3 = px.pie(pivot_kabupaten_kota_kendaraan, values='jumlah_kendaraan', names='fungsi_kendaraan')
        st.plotly_chart(figline3, use_container_width=True, config={'displayModeBar': True})
    else:
        st.subheader('Jumlah kendaraan berdasarkan fungsi kendaraan')
        figline3 = px.bar(pivot_kabupaten_kota_kendaraan, x='jumlah_kendaraan', y='nama_kabupaten_kota', color='fungsi_kendaraan', orientation='h')
        st.plotly_chart(figline3, use_container_width=True, config={'displayModeBar': True})

with right_tab1:
    st.subheader(f'Total kendaraan dari {start_date} sampai {end_date}')
    figline = px.line(pivot_total_kendaraan, x='tahun', y='jumlah_kendaraan', color='jenis_kendaraan')
    st.plotly_chart(figline, use_container_width=True, config={'displayModeBar': True})
        

with right_tab2:
    st.subheader(f'Distribusi jumlah kendaraan dari tahun {start_date} sampai {end_date}')
    figbox = px.box(pivot_fungsi_kendaraan, x="fungsi_kendaraan", y="jumlah_kendaraan")
    st.plotly_chart(figbox, use_container_width=True, config={'displayModeBar': True})
