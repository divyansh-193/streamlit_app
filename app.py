import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from datetime import datetime, timedelta

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')

    import pandas as pd
    import matplotlib.pyplot as plt
    import altair as alt
    from scipy.stats import pearsonr

    st.title("GIS Data analysis")

    df = pd.read_csv("180 days.csv")
        
    st.header('Dataframe with Filters')

    # Filter options
    project_options = ['All'] + list(df['Project'].unique())
    checklistname_options = ['All'] + list(df['checklistname'].unique())
    module_options = ['All'] + list(df['Module'].unique())
    workstation_options = ['All'] + list(df['Workstation'].unique())
    projecttype_options = ['All'] + list(df['ProjectType'].unique())
    projectstatus_options = ['All'] + list(df['ProjectStatus'].unique())
    bay_options = ['All'] + list(df['Bay'].unique())
    position_options = ['All'] + list(df['Position'].unique())

    col1, col2 = st.columns(2)

    with col1:
        selected_project = st.selectbox('Project', project_options)
        selected_module = st.selectbox('Module', module_options)
        selected_projecttype = st.selectbox('Project Type', projecttype_options)
        selected_bay = st.selectbox('Bay', bay_options)

    with col2:
        selected_checklistname = st.selectbox('Checklist Name', checklistname_options)
        selected_workstation = st.selectbox('Workstation', workstation_options)
        selected_projectstatus = st.selectbox('Project Status', projectstatus_options)
        selected_position = st.selectbox('Position', position_options)

    filtered_df = df.copy()
    if selected_project != 'All':
        filtered_df = filtered_df[filtered_df['Project'] == selected_project]
    if selected_checklistname != 'All':
        filtered_df = filtered_df[filtered_df['checklistname'] == selected_checklistname]
    if selected_module != 'All':
        filtered_df = filtered_df[filtered_df['Module'] == selected_module]
    if selected_workstation != 'All':
        filtered_df = filtered_df[filtered_df['Workstation'] == selected_workstation]
    if selected_projecttype != 'All':
        filtered_df = filtered_df[filtered_df['ProjectType'] == selected_projecttype]
    if selected_projectstatus != 'All':
        filtered_df = filtered_df[filtered_df['ProjectStatus'] == selected_projectstatus]
    if selected_bay != 'All':
        filtered_df = filtered_df[filtered_df['Bay'] == selected_bay]
    if selected_position != 'All':
        filtered_df = filtered_df[filtered_df['Position'] == selected_position]

    # Display filtered dataframe
    st.dataframe(filtered_df)

    #--------------------------------------#

    aggregated_df = filtered_df.groupby('Project').agg({
        'Module': 'nunique',
        'checklistname': 'nunique',
        'durationmin': 'sum',
        'Workstation': 'nunique'
    }).reset_index()

    aggregated_df.columns = ['Project', 'Module_Count', 'Checklistname_Count', 'Total_Duration_Min', 'Workstation_Count']

    # Streamlit app
    st.header('Correlation finder')

    # Axis options
    axis_options = {
        'Count of Module per Project': 'Module_Count',
        'Count of Checklistname per Project': 'Checklistname_Count',
        'Duration (min) per Project': 'Total_Duration_Min',
        'Count of Workstation per Project': 'Workstation_Count'
    }

    # Dropdowns to select x and y axes
    col3, col4 = st.columns(2)

    with col3:
        x_axis_label = st.selectbox('Select X-axis', list(axis_options.keys()))

    with col4:
        y_axis_label = st.selectbox('Select Y-axis', list(axis_options.keys()))

    x_axis = axis_options[x_axis_label]
    y_axis = axis_options[y_axis_label]

    # Calculate correlation factor
    corr, _ = pearsonr(aggregated_df[x_axis], aggregated_df[y_axis])

    # Create scatterplot with regression line
    scatterplot = alt.Chart(aggregated_df).mark_circle(size=100).encode(
        x=alt.X(x_axis, title=x_axis_label),
        y=alt.Y(y_axis, title=y_axis_label),
        tooltip=['Project', x_axis, y_axis]
    ).interactive()

    regression_line = scatterplot.transform_regression(
        x_axis, y_axis, method='linear'
    ).mark_line()

    chart = scatterplot + regression_line

    # Display scatterplot with regression line
    st.altair_chart(chart, use_container_width=True)

    # Display correlation factor
    st.write(f'Correlation factor (Pearson correlation coefficient): {corr:.2f}')


    #---------------------------------------------------------#

    st.header('Bar Graphs')

    # Define axis options
    categorical_options = ['Project', 'Workstation', 'Module', 'checklistname', 'ProjectType', 'Bay', 'Position']
    continuous_options = {
        'Count of Module': 'Module',
        'Count of Checklistname': 'checklistname',
        'Duration (min)': 'durationmin',
        'Count of Workstation': 'Workstation',
        'Count of Project': 'Project'
    }

    col5, col6 = st.columns(2)

    # Dropdowns to select x and y axes
    with col5:
        x_axis = st.selectbox('Select X-axis (Categorical)', categorical_options)

    with col6:
        y_axis_label = st.selectbox('Select Y-axis (Continuous)', list(continuous_options.keys()))
    y_axis = continuous_options[y_axis_label]

    # Aggregate data for the bar graph
    if y_axis == 'Project':
        aggregated_df1 = filtered_df.groupby(x_axis).size().reset_index(name='Count of Project')
        y_axis = 'Count of Project'
    else:
        aggregated_df1 = filtered_df.groupby(x_axis).agg({y_axis: 'nunique' if 'Count' in y_axis_label else 'sum'}).reset_index()

    # Create bar graph
    bar_graph = alt.Chart(aggregated_df1).mark_bar().encode(
        x=alt.X(x_axis, title=x_axis),
        y=alt.Y(y_axis, title=y_axis_label),
        tooltip=[x_axis, y_axis]
    ).interactive()

    # Display bar graph
    st.altair_chart(bar_graph, use_container_width=True)

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')