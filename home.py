from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import nfl_data_py as nfl
import plotly.graph_objects as go

# Register page for Dash app



def fetch_qb_adj_data(season: int) -> pd.DataFrame:
    """Fetches and processes quarterback adjusted EPA data for a given season.

    Args:
        season (int): The NFL season year (e.g., 2023).
    Returns:
        pd.DataFrame: Processed DataFrame with quarterback adjusted EPA metrics.
    """
    pbp = nfl.import_pbp_data([season])

    # Filter to dropbacks only
    dropbacks = pbp[pbp['qb_dropback'] == 1].copy()

    # Calculate defensive skill metrics per defense per season
    def_metrics = (
        dropbacks.groupby(['season', 'defteam'])
        .agg(
            def_epa_per_dropback=('epa', 'mean'),
            def_success_rate_allowed=('success', 'mean'),
            def_pressure_rate=('qb_hit', 'sum'),
            def_dropbacks=('qb_dropback', 'count'),
        )
        .assign(def_pressure_rate=lambda df: df.def_pressure_rate / df.def_dropbacks)
        .reset_index()
    )

    # Calculate OL proxy metrics per offense per season
    ol_metrics = (
        dropbacks.groupby(['season', 'posteam'])
        .agg(
            pressures_allowed=('qb_hit', 'sum'),
            sacks_allowed=('sack', 'sum'),
            dropbacks=('qb_dropback', 'count'),
        )
        .assign(
            pressure_rate=lambda df: df.pressures_allowed / df.dropbacks,
            sack_rate=lambda df: df.sacks_allowed / df.dropbacks
        )
        .reset_index()
    )

    # Merge defensive and OL metrics onto dropbacks
    dropbacks = dropbacks.merge(def_metrics, on=['season', 'defteam'], how='left')
    dropbacks = dropbacks.merge(ol_metrics, on=['season', 'posteam'], how='left')

    # Filter for true QBs with min dropbacks threshold
    min_dropbacks = 150
    qb_counts = dropbacks.groupby(['season', 'passer_player_name']).size().reset_index(name='dropbacks')
    true_qbs = qb_counts[qb_counts['dropbacks'] >= min_dropbacks]['passer_player_name'].unique()
    dropbacks_true_qbs = dropbacks[dropbacks['passer_player_name'].isin(true_qbs)].copy()

    # Define clutch situations: 3rd/4th and long, last 5 minutes, close game (within 7 points)
    dropbacks_true_qbs['clutch_situation'] = (
        (dropbacks_true_qbs['down'].isin([3, 4])) &
        (dropbacks_true_qbs['ydstogo'] >= 7) &
        (dropbacks_true_qbs['game_seconds_remaining'] <= 300) &
        (dropbacks_true_qbs['score_differential'].abs() <= 7)
    )

    # Add play-level adjusted EPA
    dropbacks_true_qbs['adj_epa'] = (
        dropbacks_true_qbs['epa'] - dropbacks_true_qbs['def_epa_per_dropback']
    ) / (1 + dropbacks_true_qbs['pressure_rate'])

    # Aggregate clutch adjusted EPA stats per QB
    clutch_stats = (
        dropbacks_true_qbs[dropbacks_true_qbs['clutch_situation']]
        .groupby('passer_player_name')['adj_epa']
        .agg(['mean', 'sum', 'count'])
        .rename(columns={
            'mean': 'clutch_avg_adj_epa',
            'sum': 'clutch_total_adj_epa',
            'count': 'clutch_plays'
        })
        .reset_index()
    )

    # Aggregate non-clutch adjusted EPA stats per QB
    non_clutch_stats = (
        dropbacks_true_qbs[~dropbacks_true_qbs['clutch_situation']]
        .groupby('passer_player_name')['adj_epa']
        .agg(['mean', 'sum', 'count'])
        .rename(columns={
            'mean': 'non_clutch_avg_adj_epa',
            'sum': 'non_clutch_total_adj_epa',
            'count': 'non_clutch_plays'
        })
        .reset_index()
    )

    # Aggregate overall QB metrics normalized by defense and OL skill
    qb_adj = (
        dropbacks_true_qbs.groupby(['season', 'passer_player_name'])
        .agg(
            dropbacks=('qb_dropback', 'count'),
            total_epa=('epa', 'sum'),
            avg_epa_per_dropback=('epa', 'mean'),
            avg_def_epa_allowed=('def_epa_per_dropback', 'mean'),
            avg_def_success_rate_allowed=('def_success_rate_allowed', 'mean'),
            avg_def_pressure_rate=('def_pressure_rate', 'mean'),
            avg_ol_pressure_rate_allowed=('pressure_rate', 'mean'),
            avg_ol_sack_rate_allowed=('sack_rate', 'mean'),
        )
        .reset_index()
    )

    # Merge clutch stats with overall QB summary
    qb_adj = qb_adj.merge(clutch_stats, on='passer_player_name', how='left')
    qb_adj = qb_adj.merge(non_clutch_stats, on='passer_player_name', how='left')

    # Calculate adjusted EPA metrics
    qb_adj['epa_vs_expectation'] = qb_adj['avg_epa_per_dropback'] - qb_adj['avg_def_epa_allowed']
    qb_adj['epa_vs_def_and_ol'] = qb_adj['epa_vs_expectation'] / (1 + qb_adj['avg_ol_pressure_rate_allowed'])

    # Calculate clutch vs non-clutch adjusted EPA difference
    qb_adj['clutch_vs_non_clutch_adj_diff'] = qb_adj['clutch_avg_adj_epa'] - qb_adj['non_clutch_avg_adj_epa']

    # Filter to just QBs with over 200 dropbacks
    qb_adj = qb_adj[qb_adj['dropbacks'] >= 200].copy()

    return qb_adj

def make_qb_epa_adj_chart(season: int = 2023) -> dcc.Graph:
    """Creates the chart for EPA adjusted quarterback metrics.
    Returns:
        dcc.Graph: A Dash Graph component with the quarterback adjusted EPA chart.
    """
    qb_adj = fetch_qb_adj_data(season)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=qb_adj['passer_player_name'],
        y=qb_adj['epa_vs_expectation'],
        name='EPA vs Expectation',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=qb_adj['passer_player_name'],
        y=qb_adj['epa_vs_def_and_ol'],
        name='EPA vs Defense and OL',
        marker_color='orange'
    ))
    fig.add_trace(go.Bar(
        x=qb_adj['passer_player_name'],
        y=qb_adj['clutch_vs_non_clutch_adj_diff'],
        name='Clutch vs Non-Clutch Adjusted EPA Diff',
        marker_color='green'
    ))
    fig.update_layout(
        title='Quarterback Adjusted EPA Metrics (2023)',
        xaxis_title='Quarterback',
        yaxis_title='Adjusted EPA',
        barmode='group',
        height=600,
        template='plotly_white'
    )
    fig.update_xaxes(tickangle=-45, tickmode='array', tickvals=qb_adj['passer_player_name'])
    fig.update_yaxes(tickformat='.2f')
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_layout(legend_title_text='Metrics', legend=dict(x=0, y=1.0, orientation='h'))
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    fig.update_layout(
        xaxis=dict(tickangle=-45, tickmode='array', tickvals=qb_adj['passer_player_name']),
        yaxis=dict(tickformat='.2f')
    )
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    fig.update_layout(
        legend_title_text='Metrics',
        legend=dict(x=0, y=1.0, orientation='h'),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return dcc.Graph(figure=fig)

def make_home_layout():
    """Creates the layout for the home page of the Dash app.
    Returns:
        html.Div: The layout for the home page containing the chart.
    """
    return html.Div(
        [
            dbc.Row([
                dbc.Col(
                    html.H1("Quarterback Qualities"),
                    className="text-center mb-4"
                )
            ]),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options=[
                            year for year in range(2010, 2024)
                        ],
                        value=2023,
                        id='season-select',
                        className='mb-3',
                        placeholder="Select a season"
                    )
                )
            ]),
            dbc.Row([
                dbc.Col(
                    id='qb-epa-chart',
                    className='mb-4',
                    children=[make_qb_epa_adj_chart()]
                )
            ])
        ],
        className="container mt-4"
    )


@callback(
    Output('qb-epa-chart', 'children'),
    Input('season-select', 'value')
)
def update_qb_epa_chart(season: int):
    """Updates the quarterback adjusted EPA chart based on selected season."""
    if season is None:
        return []

    return make_qb_epa_adj_chart(season)
