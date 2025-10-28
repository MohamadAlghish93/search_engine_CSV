import base64
import io
import time
from datetime import datetime as dt

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback_context
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from model import get_similarty  # your custom function


app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Global dataframe storage
df = None

# Enhanced color scheme
COLORS = {
    'primary': '#3b82f6',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'danger': '#ef4444',
    'background': '#f8fafc',
    'card': '#ffffff',
    'border': '#e2e8f0',
    'text': '#334155'
}

# App Layout with enhanced UI
app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'}, children=[
    # Header
    html.Div(style={'textAlign': 'center', 'marginBottom': '30px'}, children=[
        html.H1('📊 Smart Data Similarity Search', 
                style={'color': COLORS['text'], 'marginBottom': '10px', 'fontSize': '2.5rem'}),
        html.P('Upload your data, select a field, and find similar records with AI-powered search',
               style={'color': '#64748b', 'fontSize': '1.1rem'})
    ]),
    
    # Main Container
    html.Div(style={'maxWidth': '1400px', 'margin': '0 auto'}, children=[
        
        # Upload Section
        html.Div(style={
            'backgroundColor': COLORS['card'],
            'padding': '30px',
            'borderRadius': '12px',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }, children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.Div('📁', style={'fontSize': '3rem', 'marginBottom': '10px'}),
                    html.Div('Drag and Drop or ', style={'display': 'inline'}),
                    html.A('Select Files', style={'color': COLORS['primary'], 'fontWeight': 'bold'}),
                    html.Div('Supported formats: CSV, Excel (.xls, .xlsx)', 
                            style={'fontSize': '0.9rem', 'color': '#64748b', 'marginTop': '10px'})
                ]),
                style={
                    'width': '100%',
                    'minHeight': '150px',
                    'lineHeight': '60px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'borderColor': COLORS['border'],
                    'backgroundColor': '#f1f5f9',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s'
                },
                multiple=False
            ),
            html.Div(id='upload-status', style={'marginTop': '15px', 'textAlign': 'center'})
        ]),
        
        # Main Content Area
        html.Div(id='output-data-upload'),
    ])
])


def generate_table(df, max_row=15, table_id='table'):
    """Generate an enhanced data table"""
    return dash_table.DataTable(
        id=table_id,
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        filter_action="native",
        sort_action="native",
        page_action="native",
        page_current=0,
        page_size=max_row,
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': COLORS['primary'],
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'left',
            'padding': '12px',
            'border': 'none'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'system-ui, -apple-system, sans-serif',
            'fontSize': '14px',
            'border': '1px solid #e2e8f0'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8fafc'
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': '#dbeafe',
                'border': f'1px solid {COLORS["primary"]}'
            }
        ],
        export_format='xlsx',
        export_headers='display'
    )


def parse_contents(contents, filename, date):
    """Parse uploaded file contents"""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    global df
    
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return html.Div([
                html.Div('⚠️ Unsupported file format', 
                        style={'color': COLORS['danger'], 'fontSize': '1.1rem', 'textAlign': 'center'})
            ])
    except Exception as e:
        print(e)
        return html.Div([
            html.Div('❌ Error processing file', 
                    style={'color': COLORS['danger'], 'fontSize': '1.1rem', 'textAlign': 'center'}),
            html.Div(str(e), style={'fontSize': '0.9rem', 'color': '#64748b', 'marginTop': '10px'})
        ])

    available_columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    return html.Div([
        # Data Overview Cards
        html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 
                       'gap': '20px', 'marginBottom': '25px'}, children=[
            # Card 1: Rows
            html.Div(style={
                'backgroundColor': COLORS['card'],
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'borderLeft': f'4px solid {COLORS["primary"]}'
            }, children=[
                html.Div('📋 Total Rows', style={'color': '#64748b', 'fontSize': '0.9rem', 'marginBottom': '8px'}),
                html.Div(f'{len(df):,}', style={'fontSize': '2rem', 'fontWeight': 'bold', 'color': COLORS['text']})
            ]),
            
            # Card 2: Columns
            html.Div(style={
                'backgroundColor': COLORS['card'],
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'borderLeft': f'4px solid {COLORS["secondary"]}'
            }, children=[
                html.Div('📊 Total Columns', style={'color': '#64748b', 'fontSize': '0.9rem', 'marginBottom': '8px'}),
                html.Div(f'{len(df.columns)}', style={'fontSize': '2rem', 'fontWeight': 'bold', 'color': COLORS['text']})
            ]),
            
            # Card 3: File Info
            html.Div(style={
                'backgroundColor': COLORS['card'],
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'borderLeft': f'4px solid {COLORS["success"]}'
            }, children=[
                html.Div('📁 File Name', style={'color': '#64748b', 'fontSize': '0.9rem', 'marginBottom': '8px'}),
                html.Div(filename, style={'fontSize': '1rem', 'fontWeight': 'bold', 'color': COLORS['text'], 
                                         'overflow': 'hidden', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'})
            ]),
        ]),
        
        # Data Table Section
        html.Div(style={
            'backgroundColor': COLORS['card'],
            'padding': '25px',
            'borderRadius': '12px',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
            'marginBottom': '25px'
        }, children=[
            html.H3('📑 Data Preview', style={'color': COLORS['text'], 'marginBottom': '20px'}),
            generate_table(df),
        ]),
        
        # Search Configuration Section
        html.Div(style={
            'backgroundColor': COLORS['card'],
            'padding': '30px',
            'borderRadius': '12px',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
            'marginBottom': '25px'
        }, children=[
            html.H3('🔍 Similarity Search Configuration', 
                   style={'color': COLORS['text'], 'marginBottom': '25px'}),
            
            # Search Controls Grid
            html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '25px'}, children=[
                # Column Selection
                html.Div(children=[
                    html.Label('Select Field to Search', 
                              style={'fontWeight': 'bold', 'color': COLORS['text'], 
                                    'marginBottom': '10px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='xaxis-column',
                        options=[{'label': col, 'value': col} for col in available_columns],
                        value=available_columns[0] if available_columns else '',
                        placeholder="Choose a column...",
                        style={'marginBottom': '10px'}
                    ),
                    html.Small('Select which column to perform similarity search on', 
                              style={'color': '#64748b'})
                ]),
                
                # Search Criteria
                html.Div(children=[
                    html.Label('Search Keywords', 
                              style={'fontWeight': 'bold', 'color': COLORS['text'], 
                                    'marginBottom': '10px', 'display': 'block'}),
                    dcc.Input(
                        id='search_crtieria',
                        type='text',
                        value='',
                        placeholder='Enter your search term...',
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'borderRadius': '6px',
                            'border': f'1px solid {COLORS["border"]}',
                            'fontSize': '14px',
                            'marginBottom': '10px'
                        }
                    ),
                    html.Small('Enter the text you want to find similar matches for', 
                              style={'color': '#64748b'})
                ]),
            ]),
            
            # Accuracy Slider
            html.Div(style={'marginTop': '25px'}, children=[
                html.Label('Similarity Threshold', 
                          style={'fontWeight': 'bold', 'color': COLORS['text'], 
                                'marginBottom': '15px', 'display': 'block'}),
                dcc.Slider(
                    id='accuracy',
                    min=0,
                    max=9,
                    marks={i: {'label': str(i), 'style': {'color': COLORS['text']}} 
                          for i in range(10)},
                    value=5,
                    tooltip={"placement": "bottom", "always_visible": False}
                ),
                html.Small('Adjust the similarity threshold (higher = more strict matching)', 
                          style={'color': '#64748b', 'display': 'block', 'marginTop': '10px'})
            ]),
            
            # Submit Button
            html.Div(style={'textAlign': 'center', 'marginTop': '30px'}, children=[
                html.Button(
                    '🔍 Search for Similar Records',
                    id='submit-button-state',
                    n_clicks=0,
                    style={
                        'backgroundColor': COLORS['primary'],
                        'color': 'white',
                        'border': 'none',
                        'padding': '15px 40px',
                        'fontSize': '1.1rem',
                        'fontWeight': 'bold',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'boxShadow': '0 4px 6px rgba(59, 130, 246, 0.3)',
                        'transition': 'all 0.3s'
                    }
                ),
            ]),
        ]),
        
        # Loading Indicator
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1"),
            color=COLORS['primary']
        ),
        
        # Results Section
        html.Div(id='output-state'),
        
        # Visualization Section
        html.Div(id='visualization-section', style={'marginTop': '25px'}),
    ])


@app.callback(
    Output('upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_upload_status(contents, filename):
    """Display upload status"""
    if contents is not None:
        return html.Div([
            html.Span('✅ ', style={'fontSize': '1.2rem'}),
            html.Span(f'File uploaded successfully: {filename}', 
                     style={'color': COLORS['success'], 'fontWeight': 'bold'})
        ])
    return ''


@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified')
)
def update_output(contents, filename, date):
    """Handle file upload"""
    if contents is not None:
        return parse_contents(contents, filename, date)
    return html.Div()


@app.callback(
    Output('output-state', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('search_crtieria', 'value'),
    State('accuracy', 'value'),
    State('xaxis-column', 'value')
)
def update_output_table(n_clicks, search_term, accuracy, column):
    """Update results table based on similarity search"""
    if n_clicks > 0 and df is not None:
        if not search_term:
            return html.Div(style={
                'backgroundColor': '#fef2f2',
                'padding': '20px',
                'borderRadius': '8px',
                'textAlign': 'center',
                'color': COLORS['danger']
            }, children=[
                html.Div('⚠️ Please enter a search term', style={'fontSize': '1.1rem', 'fontWeight': 'bold'})
            ])
        
        try:
            result_df = get_similarty(df, column, search_term, accuracy)
            
            return html.Div(style={
                'backgroundColor': COLORS['card'],
                'padding': '25px',
                'borderRadius': '12px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
            }, children=[
                html.Div(style={'marginBottom': '20px'}, children=[
                    html.H3('✨ Search Results', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                    html.Div([
                        html.Span(f'Found {len(result_df)} similar records ', 
                                 style={'color': '#64748b', 'fontSize': '1rem'}),
                        html.Span(f'(searching for "{search_term}" in "{column}")', 
                                 style={'color': '#64748b', 'fontSize': '0.9rem', 'fontStyle': 'italic'})
                    ])
                ]),
                generate_table(result_df, table_id='results-table') if not result_df.empty else 
                html.Div('No matching records found. Try adjusting the similarity threshold.', 
                        style={'textAlign': 'center', 'color': '#64748b', 'padding': '40px'})
            ])
        except Exception as e:
            return html.Div(style={
                'backgroundColor': '#fef2f2',
                'padding': '20px',
                'borderRadius': '8px',
                'textAlign': 'center',
                'color': COLORS['danger']
            }, children=[
                html.Div('❌ Error performing search', style={'fontSize': '1.1rem', 'fontWeight': 'bold'}),
                html.Div(str(e), style={'fontSize': '0.9rem', 'marginTop': '10px'})
            ])
    return html.Div()


@app.callback(
    Output("loading-output-1", "children"),
    Input("submit-button-state", "n_clicks")
)
def input_triggers_spinner(n_clicks):
    """Show loading spinner during search"""
    if n_clicks > 0:
        time.sleep(1)  # Simulate processing time
    return ''


@app.callback(
    Output('visualization-section', 'children'),
    Input('output-state', 'children'),
    State('xaxis-column', 'value')
)
def update_visualization(results, column):
    """Add visualization for numeric columns"""
    if results and df is not None:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            return html.Div(style={
                'backgroundColor': COLORS['card'],
                'padding': '25px',
                'borderRadius': '12px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
            }, children=[
                html.H3('📈 Data Distribution', style={'color': COLORS['text'], 'marginBottom': '20px'}),
                html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(400px, 1fr))', 
                               'gap': '20px'}, children=[
                    dcc.Graph(
                        figure=px.histogram(
                            df, 
                            x=col, 
                            title=f'Distribution of {col}',
                            color_discrete_sequence=[COLORS['primary']]
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': 'system-ui'}
                        )
                    ) for col in numeric_cols[:2]  # Show first 2 numeric columns
                ])
            ])
    return html.Div()


if __name__ == '__main__':
    app.run(debug=True)
