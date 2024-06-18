# SET Lab Management Version V.1  3/5/2024 Location filtering  

import dash
from dash.dependencies import Input, Output, State 
from dash import dcc, html, callback
from dash.exceptions import PreventUpdate
from dash import dash_table
from datetime import date, timedelta
from datetime import datetime
from pandas.tseries.offsets import MonthBegin, MonthEnd
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import base64  
import io
import calendar
import dash_bootstrap_components as dbc
import time
import logging
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.getLogger('werkzeug').setLevel(logging.ERROR)


# Initialize the Dash app with the external stylesheet

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
    dbc.themes.BOOTSTRAP,
])

server = app.server

logging.getLogger('werkzeug').setLevel(logging.WARNING)

def Navbar():
    layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Select by Course  | ", id='course-link', href="/page1", style={"color": "white", "fontSize": 16})),
                dbc.NavItem(dbc.NavLink("Select by Location", id='location-link', href="/page2", style={"color": "white", "fontSize": 16})),
            ],
            brand="SET",
            brand_style={"fontSize": 24, "color": "white"},
            color="#262B3D",
            dark=True,
            className="custom-navbar",
            fluid=True
        ),
    ], className="d-flex justify-content-end")

    return layout

# Callback to change link color
@app.callback(
    Output('course-link', 'style'),
    Output('location-link', 'style'),
    Input('url', 'pathname')
)
def update_link_styles(pathname):
    course_link_style = {"color": "white", "fontSize": 16, "textDecoration": "none"}
    location_link_style = {"color": "white", "fontSize": 16, "textDecoration": "none"}

    if pathname == '/page1':
        course_link_style['textDecoration'] = 'underline'
        course_link_style['color'] = '#FDF480'
    elif pathname == '/page2':
        location_link_style['textDecoration'] = 'underline'
        location_link_style['color'] = '#FDF480'

    return course_link_style, location_link_style

app.layout = Navbar()

# A dictionary to map weekday abbreviations
weekday_mapping = {
    'Mo': 0,   # Monday
    'Tues': 1, # Tuesday
    'Wed': 2,  # Wednesday
    'Thurs': 3, # Thursday
    'Fri': 4   # Friday
}

# A dictionary to map tech team abbreviations
tech_team_mapping = {
    'AFW': 'Agriculture Food & Wine',
    'ASH': 'Animal Sciences & Health',
    'CAS': 'Chemical & Analytical Services',
    'DM': 'Design & Manufacturing',
    'D&M': 'Design & Manufacturing',
    'EI': 'Electronics & Instrumentation',
    'E&I': 'Electronics & Instrumentation',
    'LES': 'Life and Earth Sciences',
    'SNR': 'Structures and Natural Resources',
    'TSO': 'Technical Support Operations'
}

# Layout of the app
app.layout = html.Div(style={'backgroundColor': '#262B3D', 'color':'white'}, children=[
    Navbar(),
    # dcc.Location(id='url', refresh=False),
    html.H1("SET Lab Management Tool", style={"textAlign": "center", "background-color": "#556877", "color": "white", "fontSize": "36px"}),
    html.Hr(),

    html.Div([
        dcc.Loading(
            id="loading-upload",
            type="default",
            children=dcc.Upload(
                id='upload-data',
                children=html.Button('Upload File', style={'background-color': '#3b405c', 'color': 'white'}),
                multiple=False,
                style={'display': 'flex', 'margin-left': '60px', 'margin-bottom':'10px','fontSize': 16,}
            ),
        ),
        html.Button('Reset', id='reset-button', n_clicks=0, style={'background-color': '#3b405c', 'color': 'white', 'margin-left': '60px', 'margin-bottom': '10px', 'fontSize': 16}),
    ]),

    # Container for the term/course selection 
    html.Div(id='page-content'),
    
    # Container for buttons to show pie chart or table
    html.Div([
        dbc.ButtonGroup([
            dbc.Button('Pie Chart', id='show-pie-chart', n_clicks=0, outline=True, color="light", className="mr-3", style={'margin-right': '10px','margin-bottom': '20px', 'background-color': '#3b405c', 'color': 'white', 'fontSize': 16}),
            dbc.Tooltip("A pie chart comparing room capacity and enrollment numbers", 
                        target="show-pie-chart",
                        style={"border": "2px solid lightblue",'fontSize': 14}),
            dbc.Button('Table', id='show-table', n_clicks=0, outline=True, color="light", className="mr-3", style={'margin-right': '10px','margin-bottom': '20px', 'background-color': '#3b405c', 'color': 'white', 'fontSize': 16}),
            dbc.Tooltip("A table showing information related to classes within a selected date range", 
                        target="show-table",
                        style={"border": "2px solid lightblue",'fontSize': 14}),
            dbc.Button('Calendar', id='show-calendar',  n_clicks=0, outline=True, color="light", className="mr-3", style={'margin-right': '10px','margin-bottom': '20px', 'background-color': '#3b405c', 'color': 'white', 'fontSize': 16}),
            dbc.Tooltip("A calendar showing information related to classes within a selected date range", 
                        target="show-calendar",
                        style={"border": "2px solid lightblue",'fontSize': 14}),
            dbc.Button('Timeline', id='show-timeline',  n_clicks=0, outline=True, color="light", className="mr-3", style={'margin-right': '10px','margin-bottom': '20px', 'background-color': '#3b405c', 'color': 'white', 'fontSize': 16}),
            dbc.Tooltip("A Gantt chart showing information related to the timelines of classes within a selected date range", 
                        target="show-timeline",
                        style={"border": "2px solid lightblue",'fontSize': 14}),
        ]),
    ], style={'textAlign': 'center', 'justify-content': 'space-between', "fontSize": 16, 'background-color': '#262B3D', 'color': 'white'}),
    html.Div(id='toggle-state', children='pie', style={'display': 'none', 'background-color': '#262B3D', 'color': 'white'}),
    html.Div([
        html.Label('Select Day:'),
        dcc.Dropdown(id='day-dropdown'),  
    ], style={'display': 'none'}, id='day-dropdown-container'),  

    html.Div([
        html.Label('Select Location:'),
        dcc.Dropdown(id='location-dropdown'),  
    ], style={'display': 'none'}, id='location-dropdown-container'),  

    dcc.Loading(
        id="loading-output-div",
        type="default",
        children=html.Div(id="output-div", children=[]),
    ),
    
    dcc.Loading(
        id="loading-location-output-div",
        type="default",
        children=html.Div(id='location-output-div', children=[]),
    ),

    html.Div(id='stored-data', style={'display': 'none'}),
    html.Div([
    dcc.Store(id='current-month', storage_type='session', data={'date': datetime.now().strftime('%Y-%m-01')}),
    
    html.Div(id='calendar-view'),
    ]),
    dcc.Store(id='last-clicked-button', data={'button': None}),

    dbc.Modal(
        [
            dbc.ModalHeader(
                [
                    dbc.ModalTitle("Warning", style={'font-size': '24px'}),
                    html.Button("×", id="close-feedback-button", className="close", style={'font-size': '24px'}),
                ],
                id="modal-header",
            ),
            dbc.ModalBody("This is where feedback will be shown", id="modal-body",  style={'font-size': '18px'}),
            
        ],
        id="modal-feedback",
        is_open=False,
    ),
])

# Callback to change font color to yellow when button is clicked
@app.callback(
    [Output('show-pie-chart', 'style'),
     Output('show-table', 'style'),
     Output('show-calendar', 'style'),
     Output('show-timeline', 'style')],
    [Input('show-pie-chart', 'n_clicks'),
     Input('show-table', 'n_clicks'),
     Input('show-calendar', 'n_clicks'),
     Input('show-timeline', 'n_clicks')]
)
def update_button_styles(pie_clicks, table_clicks, calendar_clicks, timeline_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    button_styles = [{'background-color': '#3b405c', 'color': 'white', 'fontSize': 16, 'margin-bottom': '20px'}, {'background-color': '#3b405c', 'color': 'white', 'fontSize': 16, 'margin-bottom': '20px'}, 
                    {'background-color': '#3b405c', 'color': 'white', 'fontSize': 16, 'margin-bottom': '20px'}, {'background-color': '#3b405c', 'color': 'white', 'fontSize': 16, 'margin-bottom': '20px'}]

    if button_id == 'show-pie-chart':
        button_styles[0] = {'background-color': '#3b405c', 'color': '#FDF480', 'textDecoration': 'underline', 'fontSize': 16, 'margin-bottom': '20px'}
    elif button_id == 'show-table':
        button_styles[1] = {'background-color': '#3b405c', 'color': '#FDF480', 'textDecoration': 'underline', 'fontSize': 16, 'margin-bottom': '20px'}
    elif button_id == 'show-calendar':
        button_styles[2] = {'background-color': '#3b405c', 'color': '#FDF480', 'textDecoration': 'underline', 'fontSize': 16, 'margin-bottom': '20px'}
    elif button_id == 'show-timeline':
        button_styles[3] = {'background-color': '#3b405c', 'color': '#FDF480', 'textDecoration': 'underline', 'fontSize': 16, 'margin-bottom': '20px'}
    
    return button_styles

# Callback feedback alert
@app.callback(
    [
        Output("modal-feedback", "is_open"),
        Output("modal-body", "children"),
        Output("modal-header", "children"),
    ],
    [Input("upload-data", "filename")],
    [State("modal-feedback", "is_open")]
)
def file_feedback(filename, is_open):
    if not filename:
        raise PreventUpdate

    file_extension = filename.split('.')[-1]
    if file_extension.lower() in ['xlsx', 'xls']:
        return False, "", ""
    
    else:
        feedback_message = [
            "Unsupported file type.",
            html.Br(),
            "Please upload the excel spreadsheet."
        ]
        modal_header_content = html.H4("Warning", style={'font-size': '24px'})
        return True, feedback_message, modal_header_content
    
# call back for select course/location page
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page2':
        return location_selection_layout()  
    else:
        return course_selection_layout()

def course_selection_layout():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Select Term:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.Dropdown(id='term-dropdown', multi=True, placeholder="Select Term")
                ],
                style={'margin-left': '60px', 'margin-right': '30px', 'width': '20%'}
            ),
            html.Div(
                children=[
                    html.Label('Select Course:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.Dropdown(id='course-dropdown', placeholder="Select Course", multi=True)
                ],
                style={'margin-bottom': '50px', 'margin-right': '30px', 'width': '40%', 'color': 'black'}
            ),
            html.Div(
                children=[
                    html.Label('Select Date:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date_placeholder_text='Start Date',
                        end_date_placeholder_text='End Date'
                    )
                ],
                style={'width': '20%'}
            ),
            html.Div(id='output-container-date-picker-single'),
        ],
        style={'display': 'flex', 'justify-content': 'space-between', 'color': 'black'}
    )

def location_selection_layout():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Select Term:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.Dropdown(id='location-term-dropdown', multi=True, placeholder="Select Term")
                ],
                style={'margin-left': '60px', 'margin-right': '30px', 'width': '20%'}
            ),
            html.Div(
                children=[
                    html.Label('Select Technical Services Team:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.Dropdown(id='tech-team-dropdown', multi=True, placeholder="Select Technical Services Team")
                ],
                style={'margin-bottom': '50px', 'margin-right': '30px', 'width': '20%', 'color': 'black'}
            ),
            html.Div(
                children=[
                    html.Label('Select Building:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.Dropdown(id='building-dropdown', multi=True, placeholder="Select Building")
                ],
                style={'margin-bottom': '50px', 'margin-right': '30px', 'width': '20%', 'color': 'black'}
            ),
            html.Div(
                children=[
                    html.Label('Select Room:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.Dropdown(id='room-dropdown', multi=True, placeholder="Select Room")
                ],
                style={'margin-bottom': '50px', 'margin-right': '30px', 'width': '20%', 'color': 'black'}
            ),
            html.Div(
                children=[
                    html.Label('Select Date:', style={"fontSize": 16, 'color': 'white'}),
                    dcc.DatePickerRange(
                        id='location-date-range-picker',
                        start_date_placeholder_text='Start Date',
                        end_date_placeholder_text='End Date'
                    )
                ],
                style={'width': '20%'}
            ),
        ],
        style={'display': 'flex', 'justify-content': 'space-between', 'color': 'black'}
    )

# Function to parse the contents of the uploaded file.
def parse_contents(contents, filename):
   
    if contents is not None:
        content_type, content_string = contents.split(',', 1)
        decoded = base64.b64decode(content_string)
        
        # # Check the file type and read the data into a DataFrame
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xlsx' in filename or 'xls' in filename:  
                df = pd.read_excel(io.BytesIO(decoded), skiprows=1)  
            if 'Building Descr' in df.columns and 'Room' in df.columns:
                df['Location'] = df.apply(lambda row: f"{row['Building Descr']} {row['Room']}" if str(row['Room']).strip() else row['Building Descr'], axis=1)
            else:
                print("Required columns for creating 'Location' are missing")
            
            logging.info("File parsed successfully.")

            datetime_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
            for column in ['Start Date', 'End Date']:
                for format in datetime_formats:
                    try:
                        df[column] = pd.to_datetime(df[column], format=format)
                        break  
                    except ValueError:
                        pass  
            return df
        except Exception as e:
            logging.error(f"Error parsing file: {e}")
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])
    else:
        return html.Div([
            'No file uploaded.'
        ])

@app.callback(
    [
        Output('term-dropdown', 'value'),
        Output('course-dropdown', 'value'),
        Output('date-range-picker', 'start_date'),
        Output('date-range-picker', 'end_date'),
        Output('output-div', 'children', allow_duplicate=True),
    ],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call='initial_duplicate'
)
# Function to reset
def reset(n_clicks):
    if n_clicks > 0:
        return None, None, None, None, None
    return dash.no_update

@app.callback(
    [
        Output('location-term-dropdown', 'value'),
        Output('tech-team-dropdown', 'value'),
        Output('building-dropdown', 'value'),
        Output('room-dropdown', 'value'),
        Output('location-date-range-picker', 'start_date'),
        Output('location-date-range-picker', 'end_date'),
        Output('location-output-div', 'children', allow_duplicate=True),
    ],
    [Input('reset-button', 'n_clicks')],
    prevent_initial_call='initial_duplicate'
)
# Function to reset
def reset_location(n_clicks):
    if n_clicks > 0:
        return None, None, None, None, None, None, None
    return dash.no_update

# Callback function to clear the output when switching pages
@app.callback(
    [
        Output('output-div', 'children', allow_duplicate=True),
        Output('location-output-div', 'children', allow_duplicate=True),
        Output('toggle-state', 'children')  
    ],
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def clear_output(pathname):
    if pathname in ["/", "/page1", "/page2"]:
        return [], [], 'reset'  
    return dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output('stored-data', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
# Function to store the uploaded file's data.
def store_data(contents, filename):
    # First, make sure contents is not None
    if contents is not None:
        logging.info("Storing uploaded data.")
        content_type, content_string = contents.split(',', 1)
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xlsx' in filename or 'xls' in filename:  # Handle Excel file formats
                df = pd.read_excel(io.BytesIO(decoded), skiprows=1)  # Adjust skiprows as necessary

            logging.info("File loaded successfully.")

            # Convert tech team abbreviations
            if 'Tech Team' in df.columns:
                df['Tech Team'] = df['Tech Team'].map(tech_team_mapping).fillna(df['Tech Team'])

            df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
            df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')

            logging.info(f"Start Date and End Date converted. Number of records: {len(df)}")

            # Before converting to JSON:
            # Specify columns to preserve as strings:
            columns_to_preserve_as_strings = ['Class_Pat', 'Course ID', 'Catalog', 'Class Nbr', 'Building', 'Room', 'Facil ID']  # Add column names as needed
            df[columns_to_preserve_as_strings] = df[columns_to_preserve_as_strings].astype(str)
            return df.to_json(date_format='iso', orient='split')
            # return df.to_dict('records') 
        except Exception as e:
            print(e)
    raise PreventUpdate

@app.callback(
    Output('term-dropdown', 'options'),
    [Input('stored-data', 'children')],
    [State('url', 'pathname')]
)
def set_course_term_options(stored_data, pathname):
    if pathname == '/page2':
        return dash.no_update
    return generate_options(stored_data)

@app.callback(
    Output('location-term-dropdown', 'options'),
    [Input('stored-data', 'children')],
    [State('url', 'pathname')]
)
def set_location_term_options(stored_data, pathname):
    if pathname != '/page2':
        return dash.no_update
    return generate_options(stored_data)

def generate_options(stored_data):
     if stored_data:
        df = pd.read_json(stored_data, orient='split')
        unique_terms = df['Term'].unique()
        
        # Mapping from term codes to term names.
        term_mapping = {
            4410: "Semester 1",
            4420: "Semester 2",
            4405: "Summer School",
            4415: "Winter School",
            4433: "Trimester 1",
            4436: "Trimester 2",
            4439: "Trimester 3",
            4448: "Term 4"
        }
    
        options = [
            {'label': term_mapping.get(term, f'Unknown Term {term}'), 'value': term}
            for term in unique_terms
        ]
        return options
     else:
         return []

# Callback for options of Tech Team 
@app.callback(
    Output('tech-team-dropdown', 'options'),
    [Input('stored-data', 'children')]
)
def set_tech_team_options(stored_data):
    if stored_data:
        df = pd.read_json(stored_data, orient='split')
        unique_tech_teams = df['Tech Team'].dropna().unique()
        options = [{'label': 'None', 'value': ''}] + \
                  [{'label': tech_team, 'value': tech_team} for tech_team in unique_tech_teams]
        return options
    else:
        return []

# Function to update the location dropdown based on the selected day and stored data
def update_location_dropdown(selected_day, stored_data):
    if not selected_day or not stored_data:
        
        return {'display': 'none'}, [], None

    df = pd.read_json(stored_data, orient='split')
    selected_date = pd.to_datetime(selected_day).date()
    df_filtered_day = df[df['Start Date'].dt.date == selected_date]

    # Concatenate building description and room number 
    df_filtered_day['Location'] = df_filtered_day['Building Descr'] + ' ' + df_filtered_day['Room']
    
    # locations to populate the dropdown options
    unique_locations = df_filtered_day['Location'].unique()
    location_options = [{'label': location, 'value': location} for location in unique_locations]
    
    if unique_locations.size > 0:
        return {'display': 'block'}, location_options, location_options[0]['value']
    else:
        return {'display': 'none'}, [], None

def check_dates(dates, start_date, end_date):
    for d in dates:
        # print(f"Checking date: {d[0]} against range: {start_date} - {end_date}")
        if start_date <= d[0] <= end_date:
            # print("Date is within range!")
            return True
    return False

@app.callback(
    [
        Output('course-dropdown', 'options'),
        Output('output-div', 'children'),
        Output('date-range-picker', 'min_date_allowed'),
        Output('date-range-picker', 'max_date_allowed'),
    ],
    [
        Input('term-dropdown', 'value'),
        Input('course-dropdown', 'value'),
        Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date'),
        Input('show-pie-chart', 'n_clicks'),
        Input('show-table', 'n_clicks'),
        Input('show-timeline', 'n_clicks'), 
        Input('last-clicked-button', 'data'),
    ],
    [State('stored-data', 'children')]
)
# update various components based on dropdown selections
def update_course(selected_terms, selected_course, start_date, end_date, pie_n_clicks, table_n_clicks,timeline_n_clicks, last_clicked_button_data, stored_data):
    if not stored_data or not selected_terms:
        raise PreventUpdate

    df = pd.read_json(stored_data, orient='split', dtype={'Class_Pat': object})
    # df = pd.read_json(stored_data, orient='split')


    df = df[df['Term'].isin(selected_terms)]
    
    if df.empty or 'Start Date' not in df.columns or 'End Date' not in df.columns:
        return [], [html.Div("Start Date and/or End Date column not found.")], None, None
    
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')

    non_convertible_start_date = df.loc[df['Start Date'].isna(), 'Start Date']
    non_convertible_end_date = df.loc[df['End Date'].isna(), 'End Date']

    # debug lines
    if not non_convertible_start_date.empty or not non_convertible_end_date.empty:
        error_message = "Start Date and/or End Date column could not be converted to datetime."
        print("Non-convertible Start Dates:")
        print(non_convertible_start_date)
        print("Non-convertible End Dates:")
        print(non_convertible_end_date)
        print("-------------------------")
        print(df['End Date'])
        return [], [html.Div(error_message)], None, None   
    
    min_date_allowed = df['Start Date'].min().strftime('%Y-%m-%d')
    max_date_allowed = df['End Date'].max().strftime('%Y-%m-%d')

    for day in weekday_mapping:
        if day not in df.columns:
            return [], [html.Div(f"{day} column not found.")]

    # Generate options for courses
    courses = [{'label': course, 'value': course} for course in df['Course Descr'].unique()]
    children = []
    
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    children = html.Div()  

    if selected_course:
        
        df_filtered = df[df['Course Descr'].isin(selected_course)]

        if df_filtered.empty:
            return courses, [html.Div("No courses found with the selected terms and courses.", style={'fontSize': '25px'})], min_date_allowed, max_date_allowed

        df_filtered['Course Dates'] = df_filtered.apply(lambda row: generate_course_dates(row, weekday_mapping), axis=1)
        
        # debug line
        # print(df_filtered[['Course Descr', 'Course Dates']])

        if 'Course Dates' not in df_filtered.columns or not df_filtered['Course Dates'].apply(lambda x: isinstance(x, list)).any():
            return courses, [html.Div("Course Dates column could not be created.")], min_date_allowed, max_date_allowed

        # Filter the courses based on the selected date range
        if start_date and end_date:

            start_date = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0)
            end_date = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59)
            
            mask = df_filtered['Course Dates'].apply(
                lambda dates: any(start_date <= d[0] <= end_date for d in dates) if isinstance(dates, list) else False
            )
    
            # debug line
            # print("Mask for selected date range:", mask)

            if not mask.any():

                error_message = "No courses found in the selected date range."
                print(error_message)
                return courses, [html.Div(error_message, style={'fontSize': '25px'})], min_date_allowed, max_date_allowed
            
            df_filtered = df_filtered[mask]

        if 'Course Dates' in df_filtered.columns:

            df_filtered = df_filtered.explode('Course Dates')
            df_filtered['Location'] = df_filtered['Building Descr'] + ' ' + df_filtered['Room']

            last_clicked = last_clicked_button_data['button']

            if last_clicked != 'No clicks yet':
                start_date = pd.to_datetime(start_date) if start_date else None
                end_date = pd.to_datetime(end_date) if end_date else None

                if not start_date or not end_date or start_date > end_date:
                    return courses, html.Div("Please select a valid date range.", style={'fontSize': '25px'}), None , None
    
            #  Create visualizations based on the filtered data and the button clicked.
            if last_clicked == 'show-pie-chart':
                children = [create_children_for_locations(df_filtered[df_filtered['Course Descr'] == course], start_date, end_date) for course in selected_course]
            elif last_clicked == 'show-table':
                children = [create_table_for_selected_course(df_filtered[df_filtered['Course Descr'] == course], start_date, end_date, course) for course in selected_course]
            elif last_clicked == 'show-timeline':
                children = [create_timeline_for_selected_course(df_filtered[df_filtered['Course Descr'] == course], start_date, end_date,course) for course in selected_course]
        else:
            return courses, [html.Div("No valid dates for the selected courses.")], min_date_allowed, max_date_allowed
        # debug lines
        # print("Generated 'Course Dates' after date filtering:\n", df_filtered['Course Dates'])
        return courses, children, min_date_allowed, max_date_allowed
    else:
        return courses, [], min_date_allowed, max_date_allowed

# function to organize the pie charts
def create_children_for_locations(df_filtered, start_date, end_date):

    # Speed testing
    start_time_speed = time.time()

     # Concatenate building description and room number 
    df_filtered['Location'] = df_filtered['Building Descr'] + ' ' + df_filtered['Room']

    # Fill empty value for Component column 
    if 'Component' not in df_filtered.columns:
        df_filtered['Component'] = 'Unknown'  
    else:
        df_filtered['Component'] = df_filtered['Component'].fillna('Unknown')

    df_filtered['Subject / Catalogue'] = df_filtered['Subject'].astype(str) + ' ' + df_filtered['Catalog'].astype(str)    

    grouped_df = df_filtered.groupby(['Component', 'Location', 'Room Capacity', 'Enrl Capacity', 'Meeting Start', 'Meeting End', 'Subject / Catalogue'])

    start_date = pd.to_datetime(start_date).date()  
    end_date = pd.to_datetime(end_date).date()

    exploded_df = df_filtered.explode('Course Dates')
    exploded_df['Course Dates'] = pd.to_datetime(exploded_df['Course Dates']).dt.date

    filtered_dates_df = exploded_df[(exploded_df['Course Dates'] >= start_date) & 
                                    (exploded_df['Course Dates'] <= end_date)]

    all_dates = filtered_dates_df['Course Dates'].unique()
    sorted_dates = sorted(all_dates)
    dates_str = ', '.join([date.strftime('%Y-%m-%d') for date in sorted_dates])

    charts_container = html.Div(style={'display': 'flex', 'flex-wrap': 'wrap'})

    children = []
    for (component, location, room_capacity, enrl_capacity, start_time, end_time, subject_catalogue), group in grouped_df:
        fig = make_pie_chart_for_group(group)
        
        enrl_capacity = group['Enrl Capacity'].iloc[0]
        room_capacity = group['Room Capacity'].iloc[0]
        capacity_str = f"Enrol Capacity: {enrl_capacity}, Room Capacity: {room_capacity}"

        tech_team = group['Tech Team'].iloc[0] if 'Tech Team' in group.columns else None
        tech_team_info = f"Tech Team: {tech_team}" if tech_team else "Tech Team: None"
        course_descr_str = group['Course Descr'].iloc[0]
        subject_catalogue = group['Subject / Catalogue'].iloc[0]

        chart_div = html.Div([
            html.H2(course_descr_str),
            html.H4(subject_catalogue),
            html.H4(f"Location: {location}, Time: {start_time[:5]} - {end_time[:5]}"),
            html.H4(f"Dates: {dates_str}"),
            html.H4(tech_team_info),
            html.H4(capacity_str),
            dcc.Graph(figure=fig)
        ], style={'width': '48%', 'margin-left': '20px'})

        children.append(chart_div)

    charts_container.children = children

    # Speed testing 
    end_time_speed = time.time()
    processing_time = end_time_speed - start_time_speed
    print(f"Pie Chart Processing Time: {processing_time:.3f} seconds")

    return charts_container

# Function to create a table for selected course
def create_table_for_selected_course(df_filtered, start_date, end_date, course_name):

    # Speed testing
    start_time_speed = time.time()

    if df_filtered.empty or 'Course Dates' not in df_filtered.columns:
        
        return html.Div([
            html.H3(course_name, style={'textAlign': 'left'}),  # Course name as header
            html.P("No course dates available for the selected range.", style={'fontSize': '25px'}),
            html.Hr(style={'marginTop': '20px', 'marginBottom': '20px'})
        ])
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtered = df_filtered[df_filtered['Course Dates'].apply(lambda x: 
        (x[0] if x[0] is not None else pd.to_datetime('1900-01-01')) <= end_date and 
        (x[1] if x[1] is not None else pd.to_datetime('2100-01-01')) >= start_date
    )]

    if 'Course Dates' in df_filtered.columns:
        df_filtered['Course Dates'] = df_filtered['Course Dates'].apply(lambda x: f"{x[0].strftime('%Y-%m-%d %H:%M')}-{x[1].strftime('%H:%M')}" if isinstance(x, tuple) else x)
        df_filtered.sort_values(by=['Course Dates'], inplace=True, key=lambda x: pd.to_datetime(x.str.split('-').str[0]))
    else:
        return html.Div("The 'Course Dates' column could not be found.")

    df_filtered['Subject / Catalogue'] = df_filtered['Subject'].astype(str) + ' ' + df_filtered['Catalog'].astype(str)

    # Add 'Tech Team' column 
    if 'Tech Team' not in df_filtered.columns:
        df_filtered['Tech Team'] = 'None'

    table_columns = [
        {"name": "Subject / Catalogue", "id": "Subject / Catalogue"},
        {"name": "Location", "id": "Location"},
        {"name": "Time", "id": "Course Dates"},
        {"name": "Enrol Capacity", "id": "Enrl Capacity"},
        {"name": "Room Capacity", "id": "Room Capacity"},
        {"name": "Tech Team", "id": "Tech Team"},
    ]

    df_filtered.sort_values('Course Descr', inplace=True)
    
    children = []
    table_container_style = {'margin-bottom': '20px', 'overflowX': 'auto'}
    table_style = {'width': '100%', 'minWidth': '100%', 'padding': '10px', 'overflowX': 'auto', 'color': '#262B3D', 'fontSize': 14}

    for course_descr, group in df_filtered.groupby('Course Descr'):
        # Create a subheader 
        children.append(html.H3(course_descr, style={'textAlign': 'left'}))

        # Create a table for each group
        table = dash_table.DataTable(
            data=group.to_dict('records'),
            columns=table_columns,
            style_table=table_style,
            filter_action="none", 
            sort_action="native",    
            page_action="native",   
            page_size=30,
        )
        
        children.append(html.Div(table, style=table_container_style))
        children.append(html.Hr(style={'marginTop': '20px', 'marginBottom': '20px'}))
    
    # Speed testing 
    end_time_speed = time.time()
    processing_time = end_time_speed - start_time_speed
    print(f"Table Processing Time: {processing_time:.3f} seconds")

    return html.Div(children, style={'overflowX': 'auto'})

# Function to create a timeline for selected course
def create_timeline_for_selected_course(df,start_date, end_date, course):
    
    # Speed testing
    start_time_speed = time.time()

    # print(course)
    specific_columns = ['Building', 'Building Descr', 'Room', 'Course Descr', 'Course ID']
    df[specific_columns] = df[specific_columns].fillna('Unknown')
 
    charts_container = html.Div(style={'display': 'flex', 'flex-wrap': 'wrap'})

    children = []

    start_date = pd.to_datetime(start_date).date()  
    end_date = pd.to_datetime(end_date).date()

    # exploded_df = df.explode('Course Dates')
    df['Course Date'] = df['Course Dates'].apply(lambda x: pd.to_datetime(x[0]))

    df['Course Date'] = pd.to_datetime(df['Course Date']).dt.date

    df = df[(df['Course Date'] >= start_date) & 
                                    (df['Course Date'] <= end_date)]
    
    if len(df) != 0:
        df = df.drop_duplicates(subset=['Pattern Nbr', 'Course Date', 'Meeting Start'], keep='first')
        time_format = "%H:%M:%S"  # Adjust the format if necessary
        
        df['Meeting Start'] = pd.to_datetime(df['Meeting Start'].astype(str), format=time_format)
        df['Meeting End'] = pd.to_datetime(df['Meeting End'].astype(str), format=time_format)
         
        df['Location'] =   'Building: <b>' + df['Building Descr'] + ' '+df['Room'].astype(str) +  '</b>  Date: <b>' + df['Course Date'].astype(str) + '</b> <br>Class: <b>'+ df['Component'].astype(str) +', ' + df['Class_Pat'].astype(str) + '</b> Tech Team: <b>'+  df['Tech Team'].astype(str)+'</b>' 

        df['Class Time2'] = '<b>' + df['Course Descr'].astype(str)  +'</b>' +  '<br><b>Class</b>: ' + df['Component'].astype(str) +', ' +df['Class_Pat'].astype(str) +'<br><b>Date</b>: ' + df['Course Date'].astype(str)+'  <b>Time</b>: ' + df['Meeting Start'].dt.strftime('%H:%M') + ' - ' + df['Meeting End'].dt.strftime('%H:%M')
        df['Class Time'] = '  <b>Time</b>: ' + df['Meeting Start'].dt.strftime('%H:%M') + ' - ' + df['Meeting End'].dt.strftime('%H:%M')

        df = df.sort_values(by=['Course Date', 'Meeting Start'], ascending=False)                                

        tmp_df = df.drop_duplicates(subset=['Location', 'Course Date'], keep='first')                               
        if len(tmp_df['Location']) <=2:
            chart_height= 260
        elif len(tmp_df['Location']) <=4:
            chart_height= 360
        elif len(tmp_df['Location']) <=6:
            chart_height= 460
        else:
            chart_height= len(tmp_df['Location']) * 67

        course_title=df['Course Descr'].unique()[0]                               
        fig = px.timeline(df, x_start='Meeting Start', x_end='Meeting End', y='Location', color = "Class Time2", text='Class Time', height=chart_height ,title=course_title)
                                         
        fig.update_layout(showlegend=False, xaxis_title="Time", yaxis_title="Location", hovermode=False)   

        fig.update_xaxes(
                            tickformat="%H\n%M",
                            tickformatstops=[dict(dtickrange=[3600000, 86400000], value="%H:%M")],
                            dtick=3600000,  # Set dtick to 3600000 milliseconds (1 hour)
                            side ="top",
                            insiderange=['1900-01-01 07:00:00', '1900-01-01 22:00:00']  
                                        
                        )  
        style = {'display': 'block'}

        # fig.update_traces(width= 0.6 ,textposition='inside',  insidetextanchor='end',insidetextfont=dict( size=11, color='white'))
        # countLocation = len(tmp_df['Location'].unique())
        unique_location_date_counts = tmp_df.groupby(['Location', 'Course Date']).size()
        countLocation = unique_location_date_counts.sum()
        if countLocation > 1:
            fig.update_traces(width= 0.6 ,textposition='inside',  insidetextanchor='end',insidetextfont=dict( size=11, color='white'))
        elif countLocation <= 1 and chart_height == 260:
            fig.update_traces(width= 0.3 ,textposition='inside',  insidetextanchor='end',insidetextfont=dict( size=11, color='white'))
        else:
            fig.update_traces(width= 0.15 ,textposition='inside',  insidetextanchor='end',insidetextfont=dict( size=11, color='white'))    

        chart_div = html.Div([
        # html.Button('Previous', id='previous-day-button', style={'margin-left': 10}),

        dcc.Graph(id="gantt-graph", figure=fig),  # Move the graph to the left

        # html.Button('Next', id='next-day-button', n_clicks=0, style={'float': 'right'})  # Float the button right
        ], style={'display': 'block', 'width': '100%'})

        children.append(chart_div)

        charts_container.children = children

        # Speed testing 
        end_time_speed = time.time()
        processing_time = end_time_speed - start_time_speed
        print(f"Timeline Processing Time: {processing_time:3f} seconds")

        return charts_container
    else:
        
        # Speed testing 
        end_time_speed = time.time()
        processing_time = end_time_speed - start_time_speed
        print(f"Timeline Processing Time: {processing_time:.3f} seconds")

        return html.Div([
            html.H3(course, style={'textAlign': 'left'}),  # Course name as header
            html.P("No course dates available for the selected range.", style={'fontSize': '25px'})  # Larger message
        ])

# Function to generate a list of course dates
def generate_course_dates(row, weekday_mapping):
    start_date = row['Start Date']
    end_date = row['End Date']
    meeting_start_time_str = row['Meeting Start']
    meeting_end_time_str = row['Meeting End']
    dates = []
    
    for day, index in weekday_mapping.items():
        if row[day] == 'Y':
            current_date = start_date + timedelta(days=(index - start_date.weekday()) % 7)
            while current_date <= end_date:
            
                start_time = datetime.strptime(meeting_start_time_str, '%H:%M:%S').time()
                end_time = datetime.strptime(meeting_end_time_str, '%H:%M:%S').time()
                
                start_datetime = datetime.combine(current_date, start_time)
                end_datetime = datetime.combine(current_date, end_time)
                
                dates.append((start_datetime, end_datetime))
                current_date += timedelta(weeks=1)
    return dates

# Helper function to format datetime objects
def format_datetime(start_datetime, end_datetime):

    date_str = start_datetime.strftime('%Y-%m-%d')
    start_time_str = start_datetime.strftime('%H:%M')
    end_time_str = end_datetime.strftime('%H:%M')
    return f'{date_str} {start_time_str}-{end_time_str}'

# Function to create a pie chart for a selected day 
def make_pie_chart_for_selected_day(df, selected_day):

    start_datetime = None
    end_datetime = None
    
    if isinstance(selected_day, tuple):
        start_datetime, end_datetime = selected_day
    elif isinstance(selected_day, datetime):
        start_datetime = selected_day
        end_datetime = selected_day
    elif isinstance(selected_day, str):
        start_datetime = pd.to_datetime(selected_day)
        end_datetime = pd.to_datetime(selected_day)
    else:
        raise TypeError(f"selected_day must be a datetime, a tuple of datetimes, or a string, got {type(selected_day)}")

    formatted_datetime_range = format_datetime(start_datetime, end_datetime)
    selected_day_date = start_datetime.date()
    df_day = df[df['Course Dates'].apply(lambda x: x[0].date() == selected_day_date if isinstance(x, tuple) else False)]

    if df_day.empty:
        print(f"No data available for {selected_day}")
        return go.Figure() 

    enrl_capacity = 0
    room_capacity = 0

    if not df_day.empty:
        enrl_capacity = df_day['Enrl Capacity'].iloc[0] if not pd.isna(df_day['Enrl Capacity'].iloc[0]) else 0
        room_capacity = df_day['Room Capacity'].iloc[0] if not pd.isna(df_day['Room Capacity'].iloc[0]) else 0
        
        enrl_capacity = int(enrl_capacity)
        room_capacity = int(room_capacity)

    difference = enrl_capacity - room_capacity

    # Set up the pie chart values and labels based on capacity.
    if enrl_capacity > room_capacity:
        values = [room_capacity]
        names = ['Over Room Capacity']
        title = f'Capacity for {formatted_datetime_range}<br>' f'Room Capacity: {room_capacity} Enrol Capacity: {enrl_capacity}'
        color_discrete_map = {'Over Room Capacity': 'red'}
    else:
        remaining_capacity = room_capacity - enrl_capacity
        values = [enrl_capacity, remaining_capacity]
        names = ['Enrl Capacity', 'Remaining Capacity']
        title = f'Capacity for {formatted_datetime_range}<br>' f'Room Capacity: {room_capacity} Enrol Capacity: {enrl_capacity}'
        color_discrete_map = {'Enrl Capacity': 'blue', 'Remaining Capacity': 'lightgrey'}

    # Create the pie chart
    fig = px.pie(
        names=names,
        values=values,
        title=title,
        color_discrete_map=color_discrete_map
    )

    # Over Capacity case:
    if enrl_capacity > room_capacity:
        fig.update_traces(textinfo='none')  
        fig.add_annotation(
            text="Over Capacity!",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color='orange')
        )
        fig.update_layout(showlegend=False)

    return fig

# Function to create a pie chart for a group
def make_pie_chart_for_group(df_group):
    
    enrl_capacity = df_group['Enrl Capacity'].iloc[0]
    room_capacity = df_group['Room Capacity'].iloc[0]
    difference = room_capacity - enrl_capacity
    
    colors = ['darkblue', 'royalblue']
    
    # Over capacity case:
    if enrl_capacity > room_capacity:
        values = [room_capacity, enrl_capacity - room_capacity]
        names = ['Room Capacity', 'Over Capacity']
        title = "Exceed room capacity for " + abs(difference).astype(str)
        showlegend = True
    
    # Normal case:
    else:
        values = [enrl_capacity, room_capacity - enrl_capacity]
        names = ['Enrolled Capacity', 'Remaining Room Capacity']
        title = "Capacity Overview"

    # Create the pie chart.
    fig = px.pie(
        names=names,
        values=values,
        title=title,   
    )
    fig.update_traces(marker=dict(colors=colors))
  
    if enrl_capacity > room_capacity:
        fig.update_traces(textinfo='none')
        fig.add_annotation(
            text="Over Capacity!",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=25, color='Red')
        )
        
        fig.add_annotation(
            x=0.2,  
            y=1.1, 
            xref="paper",
            yref="paper",
            showarrow=False,
            text="⚠️", 
            font=dict(
                size=20,  
                color="yellow"  
            ),

        )
        fig.update_layout(showlegend=True)

    return fig

@app.callback(
    Output('last-clicked-button', 'data'),
    [Input('show-pie-chart', 'n_clicks'),
     Input('show-table', 'n_clicks'),
     Input('show-timeline', 'n_clicks'),
     Input('show-calendar', 'n_clicks')],
    [State('last-clicked-button', 'data')]
)
def update_last_clicked_button(show_pie_n_clicks, show_table_n_clicks, show_timeline_n_clicks,show_calendar_n_clicks, data):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    data['button'] = button_id
    return data

# Callback function to update the calendar view based on user inputs
@app.callback(
    Output('calendar-view', 'children'),
    [Input('last-clicked-button', 'data')],  
    [
        State('stored-data', 'children'),
        State('term-dropdown', 'value'),
        State('course-dropdown', 'value'),
        State('date-range-picker', 'start_date'),
        State('date-range-picker', 'end_date')
    ]
)
def update_calendar(last_clicked_button_data, stored_data, selected_terms, selected_course, start_date, end_date):
    
    # Speed testing
    start_time_speed = time.time()
    
    if not stored_data:
        raise PreventUpdate
    

    if last_clicked_button_data['button'] != 'show-calendar':
        return None

    start_date = pd.to_datetime(start_date) if start_date else None
    end_date = pd.to_datetime(end_date) if end_date else None

    if not start_date or not end_date or start_date > end_date:
        return html.Div("Please select a valid date range.", style={'fontSize': '25px'})

    df = pd.read_json(stored_data, orient='split')
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
    df['Location'] = df['Building Descr'] + ' ' + df['Room']
    if selected_terms:
        df = df[df['Term'].isin(selected_terms)]
    
    if selected_course:
        df = df[df['Course Descr'].isin(selected_course)]
        # df = df[df['Course Descr'] == selected_course]

    all_months_calendar = []

    # Loop through each month in the selected date range
    current_month_start = pd.to_datetime(start_date.strftime('%Y-%m-01'))
    
    while current_month_start <= end_date:
        current_month_end = current_month_start + MonthEnd(1)
        days_in_month = pd.date_range(start=current_month_start, end=current_month_end)
        month_events = {date.date(): set() for date in days_in_month}

        for _, row in df.iterrows():
            course_dates = generate_course_dates(row, weekday_mapping)
            for start_datetime, end_datetime in course_dates:
                # Check if event falls within current month
                if current_month_start.date() <= start_datetime.date() <= current_month_end.date():
                    event_key = (row['Course Descr'], row['Component'], row['Location'], start_datetime, end_datetime, row['Tech Team'], row['Class Nbr'], row['Pattern Nbr'])
                    month_events[start_datetime.date()].add(event_key)

        calendar_rows = []
        first_day_of_calendar = current_month_start - timedelta(days=current_month_start.weekday())
        
        # Style for each calendar cell
        cell_style = {
            'vertical-align': 'top',
            'border': '2px solid #ddd',
            'padding': '5px',
            'width': '200px',  
            'height': '100px'  
        }

        days_to_display = (current_month_end - first_day_of_calendar).days + 1
        for day_number in range(days_to_display):
            current_day = first_day_of_calendar + timedelta(days=day_number)
            weekday_name = calendar.day_abbr[current_day.weekday()]  
            if current_day.weekday() == 0: 
                week_cells = []
            if current_month_start <= current_day <= current_month_end:
                events_for_day = month_events.get(current_day.date(), [])
                cell_content = [html.Span(current_day.day, style={'font-weight': 'bold'})] + [format_event(event) for event in events_for_day]
            else:
                cell_content = ""
            week_cells.append(html.Td(cell_content, style=cell_style))
            if current_day.weekday() == 6:  
                calendar_rows.append(html.Tr(week_cells))
                
       
        if current_day.weekday() != 6:
            calendar_rows.append(html.Tr(week_cells))

        month_calendar_html = html.Table([
            html.Thead(html.Tr([html.Th(day) for day in calendar.day_abbr])),  
            html.Tbody(calendar_rows)
        ], style={'margin-left': 'auto', 'margin-right': 'auto', 'width': 'fit-content'})

        all_months_calendar.append(html.H2(current_month_start.strftime('%B %Y'), style={'textAlign': 'center', 'margin-top' : '20px'}))
        all_months_calendar.append(month_calendar_html)
        
        current_month_start = current_month_end + timedelta(days=1)

    # Speed testing 
    end_time_speed = time.time()
    processing_time = end_time_speed - start_time_speed
    print(f"Calendar Processing Time: {processing_time:.3f} seconds")

    return html.Div(all_months_calendar, style={'textAlign': 'center', 'fontSize': 14})

# Function to format event HTML
def format_event(event_key):
    course_descr, component, location, start_datetime, end_datetime, tech_team, class_nbr, pattern_nbr = event_key
    
    if pd.notna(class_nbr) & pd.notna(pattern_nbr):
        class_nbr_str = str(int(float(class_nbr)))
        pattern_nbr_str = str(int(float(pattern_nbr)))
        class_pattern = class_nbr_str + '_' + pattern_nbr_str
    else:
        class_pattern = "None"

    event_style = {
        'border-top': '1px solid #ccc',  
        'padding-top': '5px',  
        'margin-top': '5px',  
        'padding-bottom': '5px', 
    }

    return html.Div([
        html.Span(f"{course_descr}"),
        html.Br(),
        html.Span('🟡', style={'margin-right': '5px'}),
        html.Span(f"{component}, {class_pattern}"),
        html.Br(),
        html.Span(location),
        html.Br(),
        html.Span(f"{start_datetime.strftime('%H:%M')} - {end_datetime.strftime('%H:%M')}"),
        html.Br(),
        html.Span(f"Tech Team: {tech_team}" if tech_team else "Tech Team: None"),
    ], style=event_style)

# Function to parse time string into a time object
def parse_time(t):
    try:
        return datetime.strptime(t, '%H:%M:%S').time()
    except ValueError:
        return datetime.strptime(t, '%H:%M').time()  

# callback for select location page
@app.callback(
    [
        Output('location-output-div', 'children'),
        Output('location-date-range-picker', 'min_date_allowed'),
        Output('location-date-range-picker', 'max_date_allowed'),
    ],
    [
        Input('location-term-dropdown', 'value'),
        Input('tech-team-dropdown', 'value'),
        Input('building-dropdown', 'value'),
        Input('room-dropdown', 'value'),
        Input('location-date-range-picker', 'start_date'),
        Input('location-date-range-picker', 'end_date'),
        Input('show-pie-chart', 'n_clicks'),
        Input('last-clicked-button', 'data'),
    ],
    [State('stored-data', 'children')]
)
def update_location(selected_terms, selected_tech_teams, selected_buildings, selected_rooms, start_date, end_date, show_pie_n_clicks, last_clicked_button_data, stored_data):
    if not stored_data or not selected_terms:
        raise PreventUpdate
    
    # Load data into DataFrame 
    df = pd.read_json(stored_data, orient='split', dtype={'Class_Pat': object})
    
    df = df[df['Term'].isin(selected_terms)]
    
    if df.empty or 'Start Date' not in df.columns or 'End Date' not in df.columns:
        return [], [html.Div("Start Date and/or End Date column not found.")], None, None
    
    # Convert date strings to datetime objects
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')

    # Generate course dates
    df['Course Dates'] = df.apply(lambda row: generate_course_dates(row, weekday_mapping), axis=1)

    min_date_allowed = df['Start Date'].min().strftime('%Y-%m-%d')
    max_date_allowed = df['End Date'].max().strftime('%Y-%m-%d')

    for day in weekday_mapping:
            if day not in df.columns:
                return [html.Div(f"{day} column not found.")], None, None

    children = []
    
    # Filter by selected technical teams
    if selected_tech_teams:
        df = df[df['Tech Team'].isin(selected_tech_teams) | df['Tech Team'].isna() if '' in selected_tech_teams else df['Tech Team'].isin(selected_tech_teams)]

    # Filter by selected buildings and rooms
    if selected_buildings:
        df = df[df['Building Descr'].isin(selected_buildings)]
    
        if selected_rooms:

            df = df[df['Room'].isin(selected_rooms) | (selected_rooms == ['All'])]

            if start_date and end_date:
                start_date = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0)
                end_date = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59)
                
                mask = df['Course Dates'].apply(
                    lambda dates: any(start_date <= d[0] <= end_date for d in dates) if isinstance(dates, list) else False
                )
                if not mask.any():

                    error_message = "No courses found in the selected date range."
                    print(error_message)
                    return [html.Div(error_message, style={'fontSize': '25px'})], min_date_allowed, max_date_allowed

                df = df[mask]
            
            if 'Course Dates' in df.columns:
                df = df.explode('Course Dates')

    if df.empty:
        return [html.Div("No data available for selected criteria.")], None, None    

    last_clicked = last_clicked_button_data['button']

    # Generate visualizations 
    if last_clicked == 'show-pie-chart':
        children = create_piecharts_for_locations(df, start_date, end_date)
    elif last_clicked == 'show-table':
        children = create_table_for_locations(df, start_date, end_date)
    elif last_clicked == 'show-timeline':
        children = create_timeline_for_selected_location(df, start_date, end_date)

    return children, min_date_allowed, max_date_allowed

# callback function to set building option
@app.callback(
    Output('building-dropdown', 'options'),
    [
        Input('stored-data', 'children'),
        Input('tech-team-dropdown', 'value')
    ]
)
def set_building_options(stored_data, selected_tech_teams):
    if stored_data:
        df = pd.read_json(stored_data, orient='split')
        
        if selected_tech_teams:
            df = df[(df['Tech Team'].isin(selected_tech_teams)) | (df['Tech Team'].isna() if '' in selected_tech_teams else df['Tech Team'].isin(selected_tech_teams))]

        buildings = sorted(df['Building Descr'].dropna().unique()) 
        options = [{'label': building, 'value': building} for building in buildings]
        
        return options
    else:
        return []

# callback function to set room option
@app.callback(
    Output('room-dropdown', 'options'),
    [
        Input('building-dropdown', 'value'),
        Input('tech-team-dropdown', 'value')
    ],
    [State('stored-data', 'children')]
)
def set_room_options(selected_buildings, selected_tech_teams, stored_data):
    if not stored_data:
        return []

    df = pd.read_json(stored_data, orient='split')

    if selected_tech_teams:
        df = df[(df['Tech Team'].isin(selected_tech_teams)) | (df['Tech Team'].isna() if '' in selected_tech_teams else df['Tech Team'].isin(selected_tech_teams))]

        if selected_buildings:
            df = df[df['Building Descr'].isin(selected_buildings)]

    else:
        return [{'label': 'Select a building first', 'value': 'None'}]

    rooms = [{'label': 'All', 'value': 'All'}] + \
            [{'label': room, 'value': room} for room in df['Room'].dropna().unique()]

    return rooms

# Function to create pie charts for selected locations
def create_piecharts_for_locations(df_filtered, start_date, end_date):
    
    # Speed testing
    start_time_speed = time.time()

    if start_date is None or end_date is None:
        return html.Div("")

    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    
    #  create Location field for grouping
    df_filtered['Location'] = df_filtered['Building Descr'] + ' ' + df_filtered['Room']
    df_filtered['Subject / Catalogue'] = df_filtered['Subject'].astype(str) + ' ' + df_filtered['Catalog'].astype(str) 
    grouped_df = df_filtered.groupby(['Course Descr', 'Location', 'Room Capacity', 'Enrl Capacity', 'Meeting Start', 'Meeting End', 'Subject / Catalogue'])

    # Container to hold all the pie chart divs
    charts_container = html.Div(style={'display': 'flex', 'flex-wrap': 'wrap'})
    children = []
    
    # Iterate each data to the defined grouping
    for (course_descr, location, room_capacity, enrl_capacity, start_time, end_time, subject_catalogue), group in grouped_df:
        
        current_group_dates = group['Course Dates'].explode()
        current_group_dates = current_group_dates[current_group_dates.apply(lambda d: start_date <= d.date() <= end_date)]
        sorted_dates = sorted(current_group_dates.dt.date.unique())
        dates_str = ', '.join([date.strftime('%Y-%m-%d') for date in sorted_dates])
        
        # Generate the pie chart figure with grouped data
        fig = make_pie_chart_for_group_location(group)
        
        enrl_capacity = group['Enrl Capacity'].iloc[0]
        room_capacity = group['Room Capacity'].iloc[0]
        capacity_str = f"Enrol Capacity: {enrl_capacity}, Room Capacity: {room_capacity}"

        tech_team = group['Tech Team'].iloc[0] if 'Tech Team' in group.columns else None
        tech_team_info = f"Tech Team: {tech_team}" if tech_team else "Tech Team: None"
        course_descr_str = group['Course Descr'].iloc[0]
        subject_catalogue = group['Subject / Catalogue'].iloc[0]

        # Pie chart and the corresponding details
        chart_div = html.Div([
            html.H2(location),
            html.H4(subject_catalogue),
            html.H4(f"Course: {course_descr_str}, Time: {start_time[:5]} - {end_time[:5]}"),
            html.H4(f"Dates: {dates_str}"),
            html.H4(tech_team_info),
            html.H4(capacity_str),
            dcc.Graph(figure=fig)
        ], style={'width': '48%', 'margin-left': '20px'})

        children.append(chart_div)

    charts_container.children = children

    # Speed testing 
    end_time_speed = time.time()
    processing_time = end_time_speed - start_time_speed
    print(f"Pie Chart Processing Time: {processing_time:.3f} seconds")

    return charts_container

# Function to make pie charts for selected locations
def make_pie_chart_for_group_location(df_group):
    
    enrl_capacity = df_group['Enrl Capacity'].iloc[0]
    room_capacity = df_group['Room Capacity'].iloc[0]
    difference = room_capacity - enrl_capacity
    
    colors = ['darkblue', 'royalblue']
    
    # Over capacity case:
    if enrl_capacity > room_capacity:
        values = [room_capacity, enrl_capacity - room_capacity]
        names = ['Room Capacity', 'Over Capacity']
       
        
        title = "Exceed room capacity for " + abs(difference).astype(str)
        showlegend = True
    
    # Normal case:
    else:
        values = [enrl_capacity, room_capacity - enrl_capacity]
        names = ['Enrolled Capacity', 'Remaining Room Capacity']
        title = "Capacity Overview"

    # Create the pie chart.
    fig = px.pie(
        names=names,
        values=values,
        title=title,   
    )
    fig.update_traces(marker=dict(colors=colors))
  
    if enrl_capacity > room_capacity:
        fig.update_traces(textinfo='none')
        fig.add_annotation(
            text="Over Capacity!",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=25, color='Red')
        )
        
        fig.add_annotation(
            x=0.2,  
            y=1.1, 
            xref="paper",
            yref="paper",
            showarrow=False,
            text="⚠️", 
            font=dict(
                size=20,  
                color="yellow"  
            ),

        )
        fig.update_layout(showlegend=True)

    return fig

# Function to create table for selected locations 
def create_table_for_locations(df_filtered, start_date, end_date):
    
    # Speed testing
    start_time_speed = time.time()
    
    if df_filtered.empty:
        return html.Div("No data available for the selected range.", style={'fontSize': '16px'})

    # Convert string dates to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_filtered = df_filtered[df_filtered['Course Dates'].apply(lambda x: 
        (x[0] if x[0] is not None else pd.to_datetime('1900-01-01')) <= end_date and 
        (x[1] if x[1] is not None else pd.to_datetime('2100-01-01')) >= start_date
    )]

    # Format Course Dates for display in the table
    if 'Course Dates' in df_filtered.columns:
        df_filtered['Course Dates'] = df_filtered['Course Dates'].apply(lambda x: f"{x[0].strftime('%Y-%m-%d %H:%M')}-{x[1].strftime('%H:%M')}" if isinstance(x, tuple) else x)
    else:
        return html.Div("The 'Course Dates' column could not be found.")

    # Concatenate columns for display
    df_filtered['Subject / Catalogue'] = df_filtered['Subject'].astype(str) + ' ' + df_filtered['Catalog'].astype(str)
    df_filtered['Location'] = df_filtered['Building Descr'] + ' ' + df_filtered['Room']

    if 'Tech Team' not in df_filtered.columns:
        df_filtered['Tech Team'] = 'None'

    # Columns for the table data
    table_columns = [
        {"name": "Subject / Catalogue", "id": "Subject / Catalogue"},
        {"name": "Course Descr", "id": "Course Descr"},
        {"name": "Location", "id": "Location"},
        {"name": "Time", "id": "Course Dates"},
        {"name": "Enrol Capacity", "id": "Enrl Capacity"},
        {"name": "Room Capacity", "id": "Room Capacity"},
        {"name": "Tech Team", "id": "Tech Team"},
    ]

    df_filtered.sort_values('Course Descr', inplace=True)

    children = []
    table_container_style = {'margin-bottom': '20px', 'overflowX': 'auto'}
    table_style = {'width': '100%', 'minWidth': '100%', 'padding': '10px', 'overflowX': 'auto', 'color': '#262B3D', 'fontSize': 14}

    for course_descr, group in df_filtered.groupby('Course Descr'):
        group = group.sort_values(by='Course Dates')
        # Create a subheader 
        children.append(html.H3(course_descr, style={'textAlign': 'left'}))

        # Create a table for each group
        table = dash_table.DataTable(
            data=group.to_dict('records'),
            columns=table_columns,
            style_table=table_style,
            filter_action="none", 
            sort_action="native",    
            page_action="native",   
            page_size=30,
        )
        
        children.append(html.Div(table, style=table_container_style))
        children.append(html.Hr(style={'marginTop': '20px', 'marginBottom': '20px'}))

    # Speed testing 
    end_time_speed = time.time()
    processing_time = end_time_speed - start_time_speed
    print(f"Table Processing Time: {processing_time:.3f} seconds")

    return html.Div(children, style={'overflowX': 'auto'})


# Function to create a timeline for selected location
def create_timeline_for_selected_location(df,start_date, end_date):
    
    # Speed testing
    start_time_speed = time.time()

    if df.empty:
        return html.Div("No data available for the selected range.", style={'fontSize': '16px'})


     
    specific_columns = ['Building', 'Building Descr', 'Room', 'Course Descr', 'Course ID']
    df[specific_columns] = df[specific_columns].fillna('Unknown')
 
    charts_container = html.Div(style={'display': 'flex', 'flex-wrap': 'wrap'})

    children = []

    start_date = pd.to_datetime(start_date).date()  
    end_date = pd.to_datetime(end_date).date()

    # exploded_df = df.explode('Course Dates')
    df['Course Date'] = df['Course Dates'].apply(lambda x: pd.to_datetime(x[0]))

    df['Course Date'] = pd.to_datetime(df['Course Date']).dt.date

    df = df[(df['Course Date'] >= start_date) & 
                                    (df['Course Date'] <= end_date)]
    
    # Concatenate columns for display
    df['Subject / Catalogue'] = df['Subject'].astype(str) + ' ' + df['Catalog'].astype(str)
    df['Location'] = df['Building Descr'] + ' ' + df['Room']

    if 'Tech Team' not in df.columns:
        df['Tech Team'] = 'None'

    

    #  create Location field for grouping
    df['Location'] = df['Building Descr'] + ' ' + df['Room']
    grouped_df = df.groupby(['Course Descr', 'Location', 'Meeting Start', 'Meeting End'])


    # Container to hold all the timeline divs
    charts_container = html.Div(style={'display': 'flex', 'flex-wrap': 'wrap'})
    children = []

    # //////////////////////////////////////////////////////////////////////////
    # Iterate each data to the defined grouping
    for (course_descr, location,start_time, end_time), group in grouped_df:
        
        current_group_dates = group['Course Dates'].explode()
        current_group_dates = current_group_dates[current_group_dates.apply(lambda d: start_date <= d.date() <= end_date)]
         
        
        # Generate the Timeline figure with grouped data
        fig = make_timeline_for_group_location(group)
        
        
        tech_team = group['Tech Team'].iloc[0] if 'Tech Team' in group.columns else None
         
        # Timeline and the corresponding details
        chart_div = html.Div([
            
            dcc.Graph(id="gantt-graph",figure=fig)
        ],style={'display': 'block', 'width': '100%'})

        children.append(chart_div)

    charts_container.children = children

    # Speed testing 
    end_time_speed = time.time()
    processing_time = end_time_speed - start_time_speed
    print(f"Timeline Processing Time: {processing_time:.3f} seconds")

    return charts_container
    
  

# Function to make timelines for selected locations
def make_timeline_for_group_location(df):
    
    if len(df) != 0:
        df = df.drop_duplicates(subset=['Pattern Nbr', 'Course Date', 'Meeting Start'], keep='first')
    # ///////////////////////////////////////////////////////////////////////
        time_format = "%H:%M:%S"  # Adjust the format if necessary
        
        df['Meeting Start'] = pd.to_datetime(df['Meeting Start'].astype(str), format=time_format)
        df['Meeting End'] = pd.to_datetime(df['Meeting End'].astype(str), format=time_format)
        
         
         
        df['Location'] =   '<b>' + df['Building Descr'] + ' '+df['Room'].astype(str)  
      
        df['Class Detail'] = '<b>' + df['Course Descr'].astype(str)  +'</b>,  ' + df['Component'].astype(str) +', ' +df['Class_Pat'].astype(str) +'<br><b>Date</b>: ' + df['Course Date'].astype(str)+ '</b> Tech Team: <b>'+  df['Tech Team'].astype(str)+'</b>' 
        df['Class Time'] = '  <b>Time</b>: ' + df['Meeting Start'].dt.strftime('%H:%M') + ' - ' + df['Meeting End'].dt.strftime('%H:%M')

        df = df.sort_values(by=['Course Date', 'Meeting Start'], ascending=True)                                

        tmp_df = df.drop_duplicates(subset=['Location', 'Course Date'], keep='first')                               
        if len(tmp_df['Class Detail']) <=1:
            chart_height= 260
        elif len(tmp_df['Class Detail']) <=2:
            chart_height= 300
        elif len(tmp_df['Class Detail']) <=4:
            chart_height= 360
        elif len(tmp_df['Class Detail']) <=6:
            chart_height= 460
        else:
            chart_height= len(tmp_df['Class Detail']) * 67

        location_title=df['Location'].unique()[0]                               
        fig = px.timeline(df, x_start='Meeting Start', x_end='Meeting End', y='Class Detail', color = "Class Detail", text='Class Time', height=chart_height ,title=location_title)
                                         

        fig.update_layout(showlegend=False, xaxis_title="Time", hovermode=False)
                                        
                                         
                                        
        fig.update_xaxes(
                                        tickformat="%H\n%M",
                                        tickformatstops=[dict(dtickrange=[3600000, 86400000], value="%H:%M")],
                                        dtick=3600000,  # Set dtick to 3600000 milliseconds (1 hour)
                                        side ="top",
                                        insiderange=['1900-01-01 07:00:00', '1900-01-01 22:00:00']  
                                        
                                        )  
         
 
        unique_location_date_counts = tmp_df.groupby(['Class Detail', 'Course Date']).size()
        countLocation = unique_location_date_counts.sum()
        if countLocation > 1:
            fig.update_traces(width= 0.6 ,textposition='inside',  insidetextanchor='end',insidetextfont=dict( size=11, color='white'))
        elif countLocation <= 1 and chart_height == 260:
            fig.update_traces(width= 0.4 ,textposition='inside',  insidetextanchor='end',insidetextfont=dict( size=11, color='white'))
        else:
            fig.update_traces(width= 0.3,textposition='inside',  insidetextanchor='end',insidetextfont=dict( size=11, color='white'))
         

    return fig

# Function for display calendar: location filter 
@app.callback(
    Output('calendar-view', 'children', allow_duplicate=True),
    [
        Input('last-clicked-button', 'data'),  
        Input('location-term-dropdown', 'value'),
        Input('tech-team-dropdown', 'value'),
        Input('building-dropdown', 'value'),
        Input('room-dropdown', 'value'),
        Input('location-date-range-picker', 'start_date'),
        Input('location-date-range-picker', 'end_date'),
    ],
    [State('stored-data', 'children')],
    prevent_initial_call='initial_duplicate'
)
def update_calendar_for_location(last_clicked_button_data, selected_terms, selected_tech_teams, selected_buildings, selected_rooms, start_date, end_date, stored_data):
    
    # Speed testing
    start_time_speed = time.time()

    if not stored_data:
        raise PreventUpdate
    
    if last_clicked_button_data['button'] != 'show-calendar':
        return None

    start_date = pd.to_datetime(start_date) if start_date else None
    end_date = pd.to_datetime(end_date) if end_date else None

    if not start_date or not end_date or start_date > end_date:
        return html.Div("Please select a valid date range.", style={'fontSize': '25px'})

    df = pd.read_json(stored_data, orient='split')
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
    df['Course Dates'] = df.apply(lambda row: generate_course_dates(row, weekday_mapping), axis=1)
    df['Location'] = df['Building Descr'] + ' ' + df['Room']

    min_date_allowed = df['Start Date'].min().strftime('%Y-%m-%d')
    max_date_allowed = df['End Date'].max().strftime('%Y-%m-%d')

    # Filter data based on the location page selections
    if selected_terms:
        df = df[df['Term'].isin(selected_terms)]

    if selected_tech_teams and 'None' not in selected_tech_teams:
        df = df[df['Tech Team'].isin(selected_tech_teams) | df['Tech Team'].isna() if '' in selected_tech_teams else df['Tech Team'].isin(selected_tech_teams)]

    if selected_buildings:
        df = df[df['Building Descr'].isin(selected_buildings)]

    if selected_rooms:
        df = df[df['Room'].isin(selected_rooms) | (selected_rooms == ['All'])]
    
    if not start_date or not end_date or start_date > end_date:
        return html.Div("Please select a valid date range.", style={'fontSize': '25px'})

    if start_date and end_date:
        start_date = pd.to_datetime(start_date).replace(hour=0, minute=0, second=0)
        end_date = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59)
                
        mask = df['Course Dates'].apply(
                    lambda dates: any(start_date <= d[0] <= end_date for d in dates) if isinstance(dates, list) else False
                )
        if not mask.any():

            error_message = "No courses found in the selected date range."
            print(error_message)
            return [html.Div(error_message, style={'fontSize': '25px'})], min_date_allowed, max_date_allowed

        df = df[mask]
            
        if 'Course Dates' in df.columns:
            df = df.explode('Course Dates')

    if df.empty:
        return html.Div("No data available for selected criteria.")
    
    all_months_calendar = []

    # Loop through each month in the selected date range
    current_month_start = pd.to_datetime(start_date.strftime('%Y-%m-01'))
    while current_month_start <= end_date:
        current_month_end = current_month_start + MonthEnd(1)
        days_in_month = pd.date_range(start=current_month_start, end=current_month_end)
        month_events = {date.date(): set() for date in days_in_month}

        for _, row in df.iterrows():
            course_dates = generate_course_dates(row, weekday_mapping)
            for start_datetime, end_datetime in course_dates:
                # Check if event falls within current month
                if current_month_start.date() <= start_datetime.date() <= current_month_end.date():
                    event_key = (row['Course Descr'], row['Component'], row['Location'], start_datetime, end_datetime, row['Tech Team'], row['Class Nbr'], row['Pattern Nbr'])
                    month_events[start_datetime.date()].add(event_key)

        calendar_rows = []
        first_day_of_calendar = current_month_start - timedelta(days=current_month_start.weekday())

        # Style for each calendar cell
        cell_style = {
            'vertical-align': 'top',
            'border': '2px solid #ddd',
            'padding': '5px',
            'width': '200px',
            'height': '100px'
        }

        days_to_display = (current_month_end - first_day_of_calendar).days + 1
        for day_number in range(days_to_display):
            current_day = first_day_of_calendar + timedelta(days=day_number)
            if current_day.weekday() == 0:
                week_cells = []
            if current_month_start <= current_day <= current_month_end:
                events_for_day = month_events.get(current_day.date(), [])
                cell_content = [html.Span(current_day.day, style={'font-weight': 'bold'})] + [format_event(event) for event in events_for_day]
            else:
                cell_content = ""
            week_cells.append(html.Td(cell_content, style=cell_style))
            if current_day.weekday() == 6:
                calendar_rows.append(html.Tr(week_cells))

        if current_day.weekday() != 6:
            calendar_rows.append(html.Tr(week_cells))

        month_calendar_html = html.Table([
            html.Thead(html.Tr([html.Th(day) for day in calendar.day_abbr])),
            html.Tbody(calendar_rows)
        ], style={'margin-left': 'auto', 'margin-right': 'auto', 'width': 'fit-content'})

        all_months_calendar.append(html.H2(current_month_start.strftime('%B %Y'), style={'textAlign': 'center', 'margin-top': '20px'}))
        all_months_calendar.append(month_calendar_html)

        current_month_start = current_month_end + timedelta(days=1)

    # Speed testing 
    end_time_speed = time.time()
    processing_time = end_time_speed - start_time_speed
    print(f"Calendar Processing Time: {processing_time:.3f} seconds")

    return html.Div(all_months_calendar, style={'textAlign': 'center', 'fontSize': 14})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    # run on Cloud
    app.run_server(debug=False, host='0.0.0.0', port=port)

    # run locally
    # app.run_server(debug=False, port=8080)
   