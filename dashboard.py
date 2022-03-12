import dash
from dash import Dash, html, dcc, dash_table
from dash.dependencies import ClientsideFunction, Input, Output
from concurrent.futures import ThreadPoolExecutor

from utils import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

UPDATE_INTERVAL = 1*60*60*5

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


#Dataframes
cands_df = create_cands_df()
jobs_df = create_jobs_df()
hiring_speed_df = create_hiring_speed_df(jobs_df)
create_hiring_average_dep_graph(hiring_speed_df)
tth_df = create_tth_df(jobs_df)
ccs_df = create_ccs_df(jobs_df, cands_df)
SOURCES_COLOR_MAP = create_color_dictionary(cands_df)
source_quarterly = create_source_quarterly(cands_df)

#Pretty column names for tables
hiring_speed_names = ['Name', 'Department Name', 'Opened At', 'Closed At', 'Days Open', 'Location']
tth_names = ['Name', 'Department Name', 'Opened At', 'Days Open', 'Location']
ccs_names = ['Last Name', 'First Name', 'Job', 'Current Stage', 'Department Name', 'Location']

#Static Graphs
dep_speed_graph = create_hiring_average_dep_graph(hiring_speed_df)
loc_speed_graph = create_hiring_average_loc_graph(hiring_speed_df)
dep_open_graph = create_tth_average_dep_graph(tth_df)
loc_open_graph = create_tth_average_loc_graph(tth_df)
all_sources_graph = create_all_sources_graph(cands_df, SOURCES_COLOR_MAP)
sources_graph = create_sources_graph(cands_df, SOURCES_COLOR_MAP)


def update_data_live(period=UPDADE_INTERVAL):
    global cands_df, jobs_df, hiring_speed_df, tth_df, ccs_df, SOURCES_COLOR_MAP, all_sources_graph, sources_graph, source_quarterly  
    while True:
        time.sleep(period)
        print('start updating')
        cands_df = create_cands_df()
        jobs_df = create_jobs_df()
        hiring_speed_df = create_hiring_speed_df(jobs_df)
        tth_df = create_tth_df(jobs_df)
        ccs_df = create_ccs_df(jobs_df, cands_df)
        SOURCES_COLOR_MAP = create_color_dictionary(cands_df)
        all_sources_graph = create_all_sources_graph(cands_df, SOURCES_COLOR_MAP)
        sources_graph = create_sources_graph(cands_df, SOURCES_COLOR_MAP)
        source_quarterly = create_source_quarterly(cands_df)
        print('end updating')

def make_layout():

    layout = html.Div(className='row', children=[
    
    html.H1(id='title', children='Recruitment Dashboard'),
        
        
    dcc.Tabs([
        
        dcc.Tab(label="Candidates' Current Stage", children=[

            html.H4(id='title_css', children="Select to View Candidates' Current Stage by Department"),

            dcc.Dropdown(
                id='ccs_dropdown',
                options=get_dropdown_dep(ccs_df),
                clearable=False,
                value=get_dropdown_dep(ccs_df)[0]['label'],
                style=dict(width='50%')
            ),
            
            dcc.Graph(id = 'ccs_graph'),

            dash_table.DataTable(
                id='ccs_table',
                columns=[{"name": i[0], "id": i[1]} for i in zip(ccs_names, ccs_df.columns)],
                style_cell={'textAlign': 'left'},
            )
            

        ]),  # close Candidates' Current Stage Tab
        
        dcc.Tab(label='Open Roles', children=[

            html.H4(id='title_tth', children='Average Duration of Open Roles by Department and Location'),

            html.Div([
                html.Div(
                dcc.Graph(id="hire_dep_graph", figure=dep_open_graph),
                className='six columns'),
            html.Div(
                dcc.Graph(id="hire_loc_graph", figure=loc_open_graph),
                className='six columns')],
                className='row'),       
                
                
            html.H4(id='title_hired', children='Select to View Open Roles by Department'),

            dcc.Dropdown(
                id='tth_dropdown',
                options=get_dropdown_dep(tth_df),
                clearable=False,
                value=get_dropdown_dep(tth_df)[0]['label'],
                style=dict(width='50%')
            ),

            html.Div(style={'height': '20px'}),

            dash_table.DataTable(
                id='tth_table',
                columns=[{"name": i[0], "id": i[1]} for i in zip(tth_names, tth_df.columns)],
                style_cell={'textAlign': 'left'},
            ),
            
        ]),  # close Open Roles Tab

        
        dcc.Tab(label='Filled Roles - Hiring Speed', children=[

            html.H4(id='title_graph', children='Hiring Speed by Department and Location'),
            
            
            html.Div([
                html.Div(
                dcc.Graph(id="speed_dep_graph", figure=dep_speed_graph),
                className='six columns'),
            html.Div(
                dcc.Graph(id="speed_loc_graph", figure=loc_speed_graph),
                className='six columns')],
                className='row'),                   
            
                        
            html.H4(id='title_speed', children='Select to View Hiring Speed by Department'),

                        dcc.Dropdown(
                id='speed_dropdown',
                options=get_dropdown_dep(hiring_speed_df),
                clearable=False,
                value=get_dropdown_dep(hiring_speed_df)[0]['label'],
                style=dict(width='50%')
            ),

            html.Div(style={'height': '20px'}),
            
            dash_table.DataTable(
                id='speed_table',
                columns=[{"name": i[0], "id": i[1]} for i in zip(hiring_speed_names, hiring_speed_df.columns)],
                style_cell={'textAlign': 'left'},
            ),
            
        ]),  # close Filled Roles - Hiring Speed Tab

        dcc.Tab(label='Candidate Source Statistics', children=[

            html.H4(id='title_sources', children='Hover over graph for more information'),

            html.Div(
                dcc.Graph(figure=all_sources_graph, id="a_s_graph", style={'display': 'inline-block'})
                , style={'width': '49%', 'display': 'inline-block'}),
            html.Div(
                dcc.Graph(figure=sources_graph, id="s_graph", style={'display': 'inline-block'})
                , style={'width': '49%', 'display': 'inline-block'}),

            html.H4(id='title_quarterly', children='Select Source and Year to View Total vs Hired Candidates'),


            html.Div(
                className='row', children=[
                    html.Div(className='two columns', children=[
                        dcc.Dropdown(
                        id='source_dropdown',
                        options=get_dropdown_sources(source_quarterly),
                        clearable=False,
                        value=get_dropdown_sources(source_quarterly)[0]['label']
                        )], style=dict(width='50%')),
                    html.Div(className='two columns', children=[
                        dcc.Dropdown(
                        id='year_dropdown',
                        options=get_dropdown_year(source_quarterly),
                        clearable=False,
                        value=get_dropdown_year(source_quarterly)[0]['label']
                        )], style=dict(width='50%'))],
                style=dict(display='flex')),

            
            html.Div([
                html.Div(
                dcc.Graph(id="total_graph"),
                className='six columns'),
            html.Div(
                dcc.Graph(id="hired_graph"),
                className='six columns')],
                className='row'),

        ]),  # close sources tab

    ]),
    ])

    return layout
 
    
app.layout = make_layout

executor = ThreadPoolExecutor(max_workers=1)
executor.submit(update_data_live)
 


@app.callback(
    dash.dependencies.Output('speed_table', 'data'),
    [dash.dependencies.Input('speed_dropdown', 'value')])
def update_output(value):
    speed_drop_df = create_speed_by_dep(hiring_speed_df, value)
    speed_dict = speed_drop_df.to_dict('records')
    return speed_dict


@app.callback(
    dash.dependencies.Output('speed_dep_graph', 'figure'),
    [dash.dependencies.Input('graph_speed_dropdown', 'value')])
def update_output(value):
    return create_hiring_average_dep_graph(hiring_speed_df, value)


@app.callback(
    dash.dependencies.Output('speed_loc_graph', 'figure'),
    dash.dependencies.Output(component_id='speed_loc_graph', component_property='style'),
    [dash.dependencies.Input('graph_speed_dropdown', 'value')])
def update_output(value):
    if value == 'Horizen Labs':
        return create_hiring_average_loc_graph(hiring_speed_df, value), {'display': 'inline-block'}
    else:
        return create_hiring_average_loc_graph(hiring_speed_df, value), {'display': 'none'}


@app.callback(
    dash.dependencies.Output('tth_table', 'data'),
    [dash.dependencies.Input('tth_dropdown', 'value')])
def update_output(value):
    tth_drop_df = create_tth_by_dep(tth_df, value)
    tth_dict = tth_drop_df.to_dict('records')
    return tth_dict


@app.callback(
    dash.dependencies.Output('hire_dep_graph', 'figure'),
    [dash.dependencies.Input('graph_hire_dropdown', 'value')])
def update_output(value):
    return create_tth_average_dep_graph(tth_df, value)


@app.callback(
    dash.dependencies.Output('hire_loc_graph', 'figure'),
    dash.dependencies.Output(component_id='hire_loc_graph', component_property='style'),
    [dash.dependencies.Input('graph_hire_dropdown', 'value')])
def update_output(value):
    if value == 'Horizen Labs':
        return create_tth_average_loc_graph(tth_df, value), {'display': 'inline-block'}
    else:
        return create_tth_average_loc_graph(tth_df, value), {'display': 'none'}


@app.callback(
    dash.dependencies.Output('ccs_table', 'data'),
    [dash.dependencies.Input('ccs_dropdown', 'value')])
def update_output(value):
    ccs_drop_df = create_ccs_by_dep(ccs_df, value)
    ccs_dict = ccs_drop_df.to_dict('records')
    return ccs_dict

@app.callback(
    dash.dependencies.Output('ccs_graph', 'figure'),
    [dash.dependencies.Input('ccs_dropdown', 'value')])
def update_output(value):
    return create_ccs_graph(ccs_df,value)

@app.callback(
    dash.dependencies.Output('total_graph', 'figure'),
    [dash.dependencies.Input('source_dropdown', 'value'),
     dash.dependencies.Input('year_dropdown', 'value')])
def update_output(source,year):
    return create_total_cands_graph(source_quarterly, source, year)

@app.callback(
    dash.dependencies.Output('hired_graph', 'figure'),
    [dash.dependencies.Input('source_dropdown', 'value'),
     dash.dependencies.Input('year_dropdown', 'value')])
def update_output(source,year):
    return create_hired_cands_graph(source_quarterly, source, year)



if __name__ == '__main__':
    app.run_server(port=8051, debug=False)