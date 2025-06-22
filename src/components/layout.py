from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from components.charts import (
    make_all_qbs_epa_adj_chart, 
    make_all_qbs_yards_chart,
    make_all_qbs_td_int_chart,
    make_all_qbs_mean_cpoe_chart
)
from data.data_processing import fetch_all_qb_season_totals

def make_layout():
    """Creates the layout for the Dash app."""
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col(
                    html.H1("Quarterback Qualities"),
                    className="text-center mb-4"
                )
            ]),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            options=[{'label': str(year), 'value': year} for year in range(2010, 2024)],
                            value=2023,
                            id='season-select',
                            className='mb-3',
                            placeholder="Select a season"
                        ),
                        width=4
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id='qb-select',
                            options=[],
                            value=None,
                            placeholder="Select a quarterback",
                            clearable=True,
                            className='mb-3'
                        ),
                        width=4
                    )
                ],
                justify="center",
                className="mb-4"
            ),
            dbc.Row([
                dbc.Col(
                    [
                        dcc.Loading(
                            id='loading-epa-chart',
                            children=dcc.Graph(id='all-qb-epa-chart'),
                            type="circle"
                        ),
                        html.P("EPA (Expected Points Added) measures the impact of a quarterback's plays on the team's expected score.")
                    ],
                    className='mb-4',
                    width=3
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id='loading-yards-chart',
                            children=dcc.Graph(id='all-qb-yards-chart'),
                            type="circle"
                        ),
                        html.P("Total yards gained by the quarterback during the season.")
                    ],
                    className='mb-4',
                    width=3
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id='loading-td-int-chart',
                            children=dcc.Graph(id='all-qb-td-int-chart'),
                            type="circle"
                        ),
                        html.P("Touchdowns and interceptions thrown by the quarterback, sorted by TD:INT ratio.")
                    ],
                    className='mb-4',
                    width=3
                ),
                dbc.Col(
                    [
                        dcc.Loading(
                            id='loading-mean-cpoe-chart',
                            children=dcc.Graph(id='all-qb-mean-cpoe-chart'),
                            type="circle"
                        ),
                        html.P("Mean CPOE (Completion Percentage Over Expected) measures the quarterback's accuracy relative to expectations.")
                    ],
                    className='mb-4',
                    width=3
                ),
            ])
        ],
        fluid=True,
        className="mt-4"
    )


@callback(
    Output('all-qb-epa-chart', 'figure'),
    Output('all-qb-yards-chart', 'figure'),
    Output('all-qb-td-int-chart', 'figure'),
    Output('all-qb-mean-cpoe-chart', 'figure'),
    Input('season-select', 'value'),
    Input('qb-select', 'value')
)
def update_all_qb_charts(season, qb_name):
    """Updates the all qb charts based on the selected season."""
    
    epa_chart = make_all_qbs_epa_adj_chart(season, qb_name=qb_name).figure
    yards_chart = make_all_qbs_yards_chart(season, qb_name=qb_name).figure
    td_int_chart = make_all_qbs_td_int_chart(season, qb_name=qb_name).figure
    cpoe_chart = make_all_qbs_mean_cpoe_chart(season, qb_name=qb_name).figure
    
    return epa_chart, yards_chart, td_int_chart, cpoe_chart

@callback(
    Output('qb-select', 'options'),
    Input('season-select', 'value')
)
def update_qb_dropdown(season):
    """Updates the quarterback dropdown based on the selected season."""
    if not season:
        return []
    
    # Fetch all quarterbacks for the selected season
    qb_options = fetch_all_qb_season_totals(season)['passer_player_name'].unique()
    
    return [qb for qb in qb_options]
