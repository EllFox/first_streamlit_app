import streamlit as st
import altair as alt
import sqlalchemy
import pymysql
import pandas as pd
import plotly.express as px
page = st.sidebar.radio('Page', ['Testing', 'Super Graf', 'bonus'])
if page == 'Testing':
    st.write('ahoj')
    st.write('jak je ?')
    st.write('dost dobry !')
    student_conn_string = "mysql+pymysql://data-student:u9AB6hWGsNkNcRDm@data.engeto.com/data_academy_02_2022"
    engeto_data_conn = sqlalchemy.create_engine(student_conn_string)
    query1 = """
            SELECT yearly_average_temperature, north FROM countries c
            WHERE 1=1
                AND yearly_average_temperature IS NOT NULL
                AND north IS NOT NULL
        """
    df_temps = pd.read_sql(query1, engeto_data_conn)
    ## graf 1
    chart1 = alt.Chart(df_temps).mark_circle(size=60).encode(
            x='north',
            y='yearly_average_temperature',
            tooltip=['north', 'yearly_average_temperature']
        ).interactive()
    query_test= """
        SELECT
            *
        FROM covid19_tests
        WHERE 1=1
            AND country IN ('Czech Republic', 'Austria', 'Slovakia')
    """
    ## nacteni a uprava dataframu
    df_tests = pd.read_sql(query_test, engeto_data_conn)
    df_tests.dropna(inplace=True)
    df_tests['date'] = pd.to_datetime(df_tests['date'])
    ## graf 2
    selection = alt.selection_multi(fields=['country'], bind='legend')
    chart2 = alt.Chart(df_tests).mark_line().encode(
        x=alt.X(
            'date',
            axis=alt.Axis(
                format=('%Y-%m-%d'),
                labelAngle=-45
            )
        ),
        y='tests_performed',
        color='country',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).properties(
        width=650
    ).add_selection(selection).interactive()
    c1, c2 = st.columns((1,1))
    c1.altair_chart(chart1)
    c2.altair_chart(chart2)
elif page == 'Super Graf':
    student_conn_string = "mysql+pymysql://data-student:u9AB6hWGsNkNcRDm@data.engeto.com/data_academy_02_2022"
    engeto_data_conn = sqlalchemy.create_engine(student_conn_string)
    query = """
        SELECT
            DATE(a.date_from) AS date,
            a.value,
            b.name AS product,
            c.name AS location
        FROM czechia_price a
        LEFT JOIN czechia_price_category b
            ON a.category_code = b.code
        LEFT JOIN czechia_region c
            ON a.region_code = c.code
        WHERE c.name IS NOT NULL
    """
    df = pd.read_sql(query, engeto_data_conn)
    product_options_query = """
        SELECT
            DISTINCT name
        FROM czechia_price_category
    """
    product_options_df = pd.read_sql(product_options_query, engeto_data_conn)
    product_options_list = product_options_df['name'].to_list()
    product_choice = st.sidebar.selectbox('Product', product_options_list)
    region_options_query = """
    SELECT
        DISTINCT name
    FROM czechia_region
    """
    region_options_df = pd.read_sql(region_options_query, engeto_data_conn)
    region_options_list = region_options_df['name'].to_list()
    region_choice = st.sidebar.multiselect('Location', region_options_list, default=['Hlavní město Praha'])
    df = df[(df['product'] == product_choice) & (df['location'].isin(region_choice))]
    brush = alt.selection(type='interval', encodings=['x'])
    selection = alt.selection_multi(fields=['location'], bind='legend')
    base = alt.Chart(df).mark_line().encode(
        x='date',
        y='value',
        color='location',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        selection
    )
    upper = base.encode(
        alt.X('date', scale=alt.Scale(domain=brush)),
    ).properties(width=700)
    lower = base.properties(height=60, width=700).add_selection(brush)
    c1, c2, c3 = st.columns((1,5,1))
    c2.markdown('# Product prices by regions')
    st.altair_chart(upper & lower, use_container_width=True)

if page == 'bonus':

    query = """
        WITH base AS (
            SELECT
                DATE_ADD(cbd.date, INTERVAL(-WEEKDAY(cbd.date)) DAY) week_monday,
                country,
                confirmed,
                deaths,
                recovered
            FROM covid19_basic_differences cbd
            WHERE cbd.date >= '2021-01-01'
            GROUP BY
                1,2
        )
        SELECT
            b.week_monday,
            b.country,
            b.confirmed,
            b.deaths,
            b.recovered,
            c.iso3
        FROM base b
        LEFT JOIN countries c
            ON c.country = b.country
        WHERE 1=1
            AND c.continent = 'Europe'
"""
    student_conn_string = "mysql+pymysql://data-student:u9AB6hWGsNkNcRDm@data.engeto.com/data_academy_02_2022"
    engeto_data_conn = sqlalchemy.create_engine(student_conn_string)
    df_plotly = pd.read_sql(query, engeto_data_conn)
    df_plotly.week_monday = df_plotly.week_monday.astype(str)
    df_plotly = df_plotly[(df_plotly['confirmed'] >= 0) & (df_plotly['deaths'] >= 0) & (df_plotly['recovered'] >= 0)]
    fig = px.scatter_geo(
    df_plotly,
    locations='iso3',
    color='country',
    hover_name='country',
    size=f'confirmed',
    projection='orthographic',
    animation_frame='week_monday'
    )
    st.plotly_chart(fig)