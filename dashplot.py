import datetime, threading, time
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, callback, Input, Output
from main import main # TODO Rename to scraper or something

CHECK_INTERVAL_SECONDS = 3600
TITLE = "Commit Tracker"

app = Dash(__name__)
app.css.append_css({'external_url': '/assets/custom.css'})

def get_plot_data(csv_file='data.csv'):
    plot_data = pd.read_csv(csv_file).drop_duplicates()
    plot_data.loc[:, 'datetime'] = pd.to_datetime(plot_data['datetime'], utc=True)
    plot_data = plot_data.sort_values(by=['user', 'datetime']).reset_index(drop=True)
    plot_data['commit_number'] = plot_data.groupby('user').cumcount() + 1
    return plot_data

plot_data = get_plot_data()

def create_commit_plot(data, plot_type='line'):
    fig = getattr(px, plot_type)(data, x='datetime', y='commit_number', color='user',
                                  labels={'datetime': '', 'commit_number': 'Commit Number'},
                                  hover_data={'commit_message': True})
    return fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font_color='rgb(186,186,186)',
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
    )

app.layout = html.Div(
    children = [
    dcc.Markdown(f"# {TITLE}", style={'font-family': 'Arial, sans-serif', 'font-size': '18px', 'color': '#f8f8f8', 'text-align': 'center'}),
    dcc.Graph(id='commit-graph', figure=create_commit_plot(plot_data, plot_type='line')),
    html.Button(id='switch-button', n_clicks=0, children='Switch to Scatter',
                style={'width': '150px', 'margin-left': '80px'}),

    html.Code(id='run-info-display', style={'white-space': 'pre-wrap', 'margin-left': '80px'}),
    ],  id='main-content'
)

@app.callback([Output('commit-graph', 'figure'), Output('switch-button', 'children')],
              [Input('switch-button', 'n_clicks')])

def switch_plot(n_clicks):
    plot_type = 'scatter' if n_clicks % 2 == 1 else 'line'
    fig = create_commit_plot(plot_data, plot_type=plot_type)
    button_text = f'Switch to {"Line" if plot_type == "scatter" else "Scatter"}'
    return fig, button_text

def git_scraper():
    global last_run, next_run, plot_data
    while True:
        last_run = (datetime.datetime.now())
        print(f"{last_run} | [+] Running scraper.")

        n_commits = main()

        if n_commits == 0:
            print(f"No new updates.")
        else:
            print(f"{n_commits} new update(s).\n")
            plot_data = get_plot_data()

        next_run = datetime.datetime.now() + datetime.timedelta(seconds=CHECK_INTERVAL_SECONDS)
        print(f"Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

        app.layout.children[-1].children = f"Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')} | Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}"
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    scraper_thread = threading.Thread(target=git_scraper)
    scraper_thread.start()
    app.run_server(debug=True)