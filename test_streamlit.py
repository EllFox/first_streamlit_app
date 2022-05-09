import streamlit as st
import altair as alt
import sqlalchemy
import pymysql
import pandas as pd



page = st.sidebar.radio('Page', ['Testing', 'Super Graf'])



if page == 'Testing':

    st.write('Ahoj :)')
    st.write('Jak je?')
    st.write('Ale tak jde to. Imphotep.')

    student_conn_string = "mysql+pymysql://data-student:u9AB6hWGsNkNcRDm@data.engeto.com/data_academy_02_2022"
    engeto_data_conn = sqlalchemy.create_engine(student_conn_string)

    query1 = """
                SELECT yearly_average_temperature, north FROM countries c
                WHERE 1=1
                    AND yearly_average_temperature IS NOT NULL
                    AND north IS NOT NULL
            """
    df_temps = pd.read_sql(query1, engeto_data_conn)

    st.write(df_temps)

    ## graf 1
    chart1 = alt.Chart(df_temps).mark_circle(size=60).encode(
                x='north',
                y='yearly_average_temperature',
                tooltip=['north', 'yearly_average_temperature']
            ).interactive()
    chart1


    query_test = """
            SELECT
                *
            FROM covid19_tests
            WHERE 1=1
                AND country IN ('Czech Republic', 'Austria', 'Slovakia')
                """

    df_tests = pd.read_sql(query_test, engeto_data_conn)
    st.write(df_tests)

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

    chart2

    c1, c2 = st.columns((1,1))
    c1.altair_chart(chart1)
    c2.altair_chart(chart2)

elif page == 'Super Graf':

    student_conn_string = "mysql+pymysql://data-student:u9AB6hWGsNkNcRDm@data.engeto.com/data_academy_02_2022"
    engeto_data_conn = sqlalchemy.create_engine(student_conn_string)  

    query = """
        SELECT 
            DATE(a.date_from) as date,
            a.value,
            b.name as product,
            c.name as location
        FROM
            czechia_price a 
        LEFT JOIN czechia_price_category b
            ON a.category_code = b.code
        LEFT JOIN czechia_region c 
            ON a.region_code = c.code
        WHERE c.name is not NULL
        """
    
    df = pd.read_sql(query, engeto_data_conn)

    df = df[(df['product'] == 'Šunkový salám') & (df['location'] == 'Jihomoravský kraj')]

    st.write(df)

    chart = alt.Chart(df).mark_line().encode(
        x = 'date:T',
        y = 'value:Q'
    )

    chart