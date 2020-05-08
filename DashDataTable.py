import base64
import datetime
import io

import dash
import dash_table
import pandas as pd
import plotly
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime as dt
from dash.dependencies import Input, Output, State
from model import get_similarty
import time

# df = pd.read_csv('empty.csv')

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

markdown_text = '''
### compare field

Select which field you want to compare with it
'''


def generate_table(df, max_row=10):
	return dash_table.DataTable(
      		id='table',
      		columns=[{"name": i, "id": i} for i in df.columns],
      		data=df.to_dict('records'),
      		filter_action="native",
      		page_action="native",
      		page_current= 0,
      		page_size= max_row,
	)



# data = [go.Scatter( x=df['userId'], y=df['tag'])]

# fig = go.Figure(data)

app.layout = html.Div(children=[
#    html.H1(children='Hello Dash'),

#     html.Div(children='''
#        Dash: A web application framework for Python.
#    '''),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),


])

# must be after layout

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value')]
    )
def update_graph(xaxis_column_name, yaxis_column_name):

	print(df[xaxis_column_name])
	data = [go.Scatter( x=df[xaxis_column_name], y=df[yaxis_column_name])]

	fig = go.Figure(data)

	return fig




def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    global df
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    available_columns  = df.columns
    return html.Div([

    generate_table(df),

    dcc.Markdown(children=markdown_text),


    html.Div([


        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_columns],
                value='',
                #multi = True
            ),
        ]),


        html.Br(),
        html.Label('Your search word'),
        dcc.Input(value='', type='text', id='search_crtieria'),

        html.Br(),
        html.Label('Accuracy'),
        dcc.Slider(
            id= 'accuracy',
            min=0,
            max=9,
            marks={i: '{}'.format(i) if i == 1 else str(i) for i in range(1, 10)},
            value=5,
        ),
        html.Br(),
        html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    ], style={'columnCount': 2}),

    dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1")
        ),


    html.Div(id='output-state')

    ])



@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-state', 'children'),
              [Input('submit-button-state', 'n_clicks')],
              [State('search_crtieria', 'value'),
               State('accuracy', 'value'),
               State('xaxis-column', 'value')])
def update_output(n_clicks, input1, input2, input3):

    if n_clicks > 0 :
        dfObj = get_similarty(df, input3, input1, input2)
        # Creating a dataframe object from listoftuples
        return generate_table(dfObj)

@app.callback(Output("loading-output-1", "children"), [Input("submit-button-state", "n_clicks")])
def input_triggers_spinner(value):
    if value > 0:
        time.sleep(5)
        return ''

if __name__ == '__main__':
    app.run_server(debug=False)
