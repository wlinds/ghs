import datetime, threading, time
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, callback, Input, Output, callback_context
import dash_bootstrap_components as dbc

from fetcher import fetch_all_repos
from utils import humanize_time
import stat_conf as sc

CHECK_INTERVAL_SECONDS = 3600
TITLE = 'Commit Tracker'
CSV_DATA = 'commit_data.csv'
REPOS = 'urls.csv'

external_stylesheets = ['/assets/custom.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

def get_df(csv_file=CSV_DATA):
    df = pd.read_csv(csv_file).drop_duplicates()
    df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'], utc=True)
    df = df.sort_values(by=['user', 'datetime']).reset_index(drop=True)
    df = df[~df['commit_message'].str.contains('readme', case=False)]
    df['commit_number'] = df.groupby('user').cumcount() + 1
    return df

def create_commit_plot(data, plot_type='line', cumulative=False, pred=True, pred_days=7):
    fig = getattr(px, plot_type)(data, x='datetime', y='commit_number', color='user',
                                labels={'datetime': 'Time','commit_number': 'Number','commit_message': 'Message'},
                                hover_name="user", hover_data={'user': False,
                                                               'datetime': True,
                                                               'commit_number': True,
                                                               'commit_message': True})
    if cumulative:
        total = data.groupby('datetime').size().cumsum().reset_index()
        total.columns = ['datetime', 'total']
        fig.add_scatter(x=total['datetime'], y=total['total'], mode='lines',
                        line=dict(color='#f0eac7', width=1), name='All Commits')

    return fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', height=550,
        font_color='rgb(186,186,186)', margin=dict(l=80, r=50, t=128, b=20),
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)', title=''),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)', title=''))

def generate_stat_card(title, desc, stat_function, icon, df):
    return dbc.Card(dbc.CardBody([
            html.H3(f"{icon} {title}", className='custom-fun-stats-title'),
            html.P(desc, className='custom-fun-stats-text'),
            html.P(stat_function(df), className='custom-fun-stats-text-highlight')
        ]),className='custom-fun-stats-card')

fun_cards = [generate_stat_card(df=get_df(), **config) for config in sc.stat_configs]

app.layout = html.Div(
    children = [html.Div(
        html.Div(f"{TITLE}", className='custom-title-class'), className='custom-header'),
    html.Div(children=[html.Div(id='latest-commit', className='custom-latest-commits')]),
    
    html.Div([html.Button(id='switch-plot', n_clicks=0, className='btn'),
              html.Button(id='cum-button', n_clicks=0, className='btn')],
              className='button-div'),

    html.Div([
    dcc.Graph(id='commit-graph',figure=create_commit_plot(get_df(), plot_type='line'))],
    className='plot-div'),
    
    html.Div(id='total-commits', className='custom-total-commits'),
    dcc.Interval(id='interval-component',
                 interval=CHECK_INTERVAL_SECONDS * 1000, n_intervals=0),


    dbc.Row(className='custom-fun-stats-container', children=fun_cards),

    html.Code(id='run-info-display', className='last-run'),

    ],id='main-content')

@app.callback(Output('latest-commit', 'children'), [Input('commit-graph', 'figure')])
def get_latest_commits(figure):
    df = get_df()
    df['datetime'] = pd.to_datetime(df['datetime']) # TODO fix the god damn time formatting once and for all literally half this function is just time formatting
    latest_commits_indices = df['datetime'].nlargest(3).index
    latest_commits = df.loc[latest_commits_indices]

    latest_updates = [html.H3(f"➜ LATEST UPDATES")]

    for _, commit in latest_commits.iterrows():
        if commit['datetime'].tzinfo is None or commit['datetime'].tzinfo.utcoffset(commit['datetime']) is None:
            commit['datetime'] = commit['datetime'].replace(tzinfo=datetime.timezone.utc)
        time_elapsed = datetime.datetime.now(datetime.timezone.utc) - commit['datetime']
        formatted_time = humanize_time(time_elapsed)

        user_link = dcc.Link(commit['user'], href=commit['repo_url'], target='_blank')
        commit_msg = dcc.Link(commit['commit_message'], href=commit['commit_url'], target='_blank')
        gravatar_image = html.Img(src=commit['gravatar_url'], className='custom-gravatar')

        commit_list = html.Div([gravatar_image,html.Span(" "), user_link,html.Span(": "), commit_msg,html.Span(f" {formatted_time}")])
        latest_updates.append(commit_list)

    return latest_updates

@app.callback(Output('total-commits', 'children'),
              [Input('commit-graph', 'figure'),
               Input('interval-component', 'n_intervals')])
def update_stats_box(figure, n_intervals):
    total_commits_text = len(get_df())
    return f"Total Commits: {total_commits_text}"

@app.callback([Output('commit-graph', 'figure'),
               Output('switch-plot', 'children'),
               Output('cum-button', 'children')],
              [Input('switch-plot', 'n_clicks'),
               Input('cum-button', 'n_clicks')])
def update_plot(switch_clicks, cum_clicks):
    ctx = callback_context
    if not ctx.triggered_id:
        button_id = 'switch-plot'
    else:
        button_id = ctx.triggered_id

    plot_type = 'scatter' if switch_clicks % 2 == 1 else 'line'
    cum_val = cum_clicks % 2 == 1

    fig = create_commit_plot(get_df(), plot_type=plot_type, cumulative=cum_val)
    switch_button_text = f'Switch to {"Line" if plot_type == "scatter" else "Scatter"} Plot'
    cum_button_text = f'{"Show" if not cum_val else "Hide"} total commits'
    return fig, switch_button_text, cum_button_text

def git_scraper():
    global last_run, next_run, plot_data
    while True:
        last_run = (datetime.datetime.now())
        fetch_all_repos(REPOS, commit_limit=8) # Use API instead of scraping for 5k requests/hour
        next_run = datetime.datetime.now() + datetime.timedelta(seconds=CHECK_INTERVAL_SECONDS)
        print(f"Run completed. Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

        app.layout.children[-1].children = f"Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')} | Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    scraper_thread = threading.Thread(target=git_scraper)
    scraper_thread.start()
    app.run_server(debug=True)