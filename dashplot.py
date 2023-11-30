import datetime, threading, time
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, callback, Input, Output
from scraper import main as scraper
from fetcher import fetch_all_repos
from utils import humanize_time

CHECK_INTERVAL_SECONDS = 3600
TITLE = "Commit Tracker"
CSV_DATA = 'commit_data.csv'
REPOS = 'urls.csv'

app = Dash(__name__)
app.css.append_css({'external_url': '/assets/custom.css'})

def get_plot_data(csv_file=CSV_DATA):
    df = pd.read_csv(csv_file).drop_duplicates()
    df.loc[:, 'datetime'] = pd.to_datetime(df['datetime'], utc=True)
    df = df.sort_values(by=['user', 'datetime']).reset_index(drop=True)
    df['commit_number'] = df.groupby('user').cumcount() + 1
    return df

def create_commit_plot(data, plot_type='line'):
    fig = getattr(px, plot_type)(data, x='datetime', y='commit_number', color='user',
                                  labels={'datetime': '', 'commit_number': 'Commit Number'},
    hover_name="user", hover_data={'user': False, 'datetime': True, 'commit_number': True, 'commit_message': True})

    return fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font_color='rgb(186,186,186)',
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        height=480)

app.layout = html.Div(
    children = [
    dcc.Markdown(f"# {TITLE}", style={'font-family': 'Arial, sans-serif', 'font-size': '18px', 'color': '#f8f8f8', 'text-align': 'center'}),
    html.Div(id='latest-commit', style={'font-family': 'Arial, sans-serif', 'margin-left': '80px', 'margin-top': '20px', 'font-size': '12px', 'color': '#ffffff'}),
    html.Div(id='stats-box', style={'font-family': 'Arial, sans-serif', 'margin-left': '80px', 'margin-top': '20px', 'font-size': '12px', 'color': '#b4b4b4'}),
    
    dcc.Graph(id='commit-graph', figure=create_commit_plot(get_plot_data(), plot_type='line')),
    
    html.Button(id='switch-button', n_clicks=0, children='Switch to Scatter', style={'width': '150px', 'margin-left': '80px'}),
    html.Code(id='run-info-display', style={'white-space': 'pre-wrap', 'margin-left': '80px'}),
    ],  id='main-content' # Hmm, this is getting messy. Should move most of it to css file probably.
)

@app.callback(Output('latest-commit', 'children'),
             [Input('commit-graph', 'figure')])
def get_latest_commit(figure):

    df = get_plot_data()
    latest_commit_index = df['datetime'].idxmax()
    latest_commit = df.loc[latest_commit_index]
    
    # AH YES, TIME, we meet again
    if latest_commit['datetime'].tzinfo is None or latest_commit['datetime'].tzinfo.utcoffset(latest_commit['datetime']) is None:
        latest_commit['datetime'] = latest_commit['datetime'].replace(tzinfo=datetime.timezone.utc)
    
    time_elapsed = datetime.datetime.now(datetime.timezone.utc) - latest_commit['datetime']
    formatted_time = humanize_time(time_elapsed)
    
    user_link = dcc.Link(latest_commit['user'], href=latest_commit['url'], target='_blank')
    
    return html.Div([html.Span(f"Latest Commit: {latest_commit['commit_message']} by "), user_link, html.Span(f" {formatted_time}")])

@app.callback(Output('stats-box', 'children'),
             [Input('commit-graph', 'figure')])
def update_stats_box(figure):
    total_commits_text = len(get_plot_data())
    return f"Total Commits: {total_commits_text}"

@app.callback([Output('commit-graph', 'figure'), Output('switch-button', 'children')],
              [Input('switch-button', 'n_clicks')])

def switch_plot(n_clicks):
    # Switch between line and scatter plots
    plot_type = 'scatter' if n_clicks % 2 == 1 else 'line'
    fig = create_commit_plot(get_plot_data(), plot_type=plot_type)
    button_text = f'Switch to {"Line" if plot_type == "scatter" else "Scatter"}'
    return fig, button_text

def git_scraper():
    global last_run, next_run, plot_data
    while True:
        last_run = (datetime.datetime.now())
        fetch_all_repos(REPOS, commit_limit=1) # Use API instead of scraping for 5k requests/hour
        next_run = datetime.datetime.now() + datetime.timedelta(seconds=CHECK_INTERVAL_SECONDS)
        print(f"Run completed. Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

        app.layout.children[-1].children = f"Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')} | Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    scraper_thread = threading.Thread(target=git_scraper)
    scraper_thread.start()
    app.run_server(debug=True)