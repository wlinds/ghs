import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, callback, Input, Output
app = Dash(__name__)

plot_data = pd.read_csv('data.csv').drop_duplicates()
plot_data.loc[:, 'datetime'] = pd.to_datetime(plot_data['datetime'], utc=True)
plot_data = plot_data.sort_values(by=['user', 'datetime']).reset_index(drop=True)
plot_data['commit_number'] = plot_data.groupby('user').cumcount() + 1

def create_commit_plot(data, plot_type='line'):
    return getattr(px, plot_type)(data, x='datetime', y='commit_number', color='user',
                                  labels={'datetime': '', 'commit_number': 'Commit Number'},
                                  hover_data={'commit_message': True})

app.layout = html.Div([
    dcc.Graph(id='commit-graph', figure=create_commit_plot(plot_data, plot_type='line')),
    html.Button(id='switch-button', n_clicks=0, children='Switch to Scatter',
                style={'width': '150px', 'margin-left': '80px'})
])

# Switch between line and scatter
@app.callback([Output('commit-graph', 'figure'), Output('switch-button', 'children')],
              [Input('switch-button', 'n_clicks')])

def switch_plot(n_clicks):
    plot_type = 'scatter' if n_clicks % 2 == 1 else 'line'
    fig = create_commit_plot(plot_data, plot_type=plot_type)
    button_text = f'Switch to {"Line" if plot_type == "scatter" else "Scatter"}'
    return fig, button_text

if __name__ == '__main__':
    app.run_server(debug=True)