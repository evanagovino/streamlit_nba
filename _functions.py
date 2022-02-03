import streamlit as st
import plotly.express as px
import streamlit.components.v1 as components
from jinja2 import Template

metric_map = {
'vorp': 'VORP',
'bpm': 'BPM',
'obpm': 'OBPM',
'dbpm': 'DBPM',
'ts_pct': 'TS%',
'trb_pct': 'TRB%',
'tov_pct': 'TOV%',
'usg_pct': 'USG%',
'fg3_pct': '3P%',
'fg2_pct': '2P%',
'ft_pct': 'FT%',
'fg_pct': 'FG%',
'fg3a_per_fga_pct': '3PAr',
'fta_per_fga_pct': 'FTr',
'off_rtg': 'Offensive Rating',
'def_rtg': 'Defensive Rating',
'mov': 'Margin of Victory',
'sos': 'Schedule Strength',
'win_pct': 'Winning Percentage',
'ast_pct': 'AST%',
'efg_pct': 'EFG%',
'orb_pct': 'ORB%',
'ft_rate': 'FTr',
'opp_efg_pct': 'Opp. EFG%',
'opp_tov_pct': 'Opp. TOV%',
'drb_pct': 'DRB%',
'opp_ft_rate': 'Opp. FTr',
'stl_pct': 'STL%',
'blk_pct': 'BLK%'
}

def _build_metric(label, value, percentile):
    html_text = """
    <style>
    .metric {
       font-family: sans-serif;
       text-align: center;
    }
    .metric .value {
       font-size: 30px;
       line-height: 1.6;
    }
    .metric .label {
       letter-spacing: 2px;
       font-size: 14px;
       text-transform: uppercase;
    }
    </style>
    <div class="metric">
       <div class="label">
          {{ label }}
       </div>
       <div class="value">
          {{ value }}
       </div>
       <div class="label">
          {{ percentile }}
       </div>
    </div>
    """
    html = Template(html_text)
    return html.render(label=label, value=value, percentile=percentile)

def metric_row(data):
    columns = st.columns(len(data))
    for i, (label, value) in enumerate(data.items()):
        with columns[i]:
            components.html(_build_metric(label, value, percentile))

def metric(label, value, percentile):
    components.html(_build_metric(label, value, percentile), height=100)

def get_values(annual_league_df, column, comp_type='team_comparison'):
    #print('comp_type', comp_type, column)
    if comp_type in ('team_comparison', 'team'):
        position = annual_league_df[annual_league_df['team'] == st.session_state.team].index.values[0]
    elif comp_type in ('year', 'season_comparison'):
        position = annual_league_df[annual_league_df['year'] == st.session_state.year].index.values[0]
    else:
        #print('triggered')
        position = annual_league_df[annual_league_df['player'] == st.session_state.player].index.values[0]
    value = annual_league_df[column][position]
    rank = annual_league_df[column].rank(ascending=False).astype('int').values[position]
    for percentile in range(100):
        if annual_league_df[column].astype('float').quantile(q=percentile/100) > value:
            break
    percentile -= 1
    #value, percentile = return_value(annual_df, st.session_state.player, column)
    if column in (['def_rtg', 'tov_pct', 'opp_ft_rate', 'opp_efg_pct']):
        rank = annual_league_df[column].rank().astype('int').values[position]
    if column == 'win_pct':
        wins = annual_league_df['wins'][position]
        losses = annual_league_df['losses'][position]
        if comp_type in (['team', 'team_comparison']):
            metric('Record', f'{wins}-{losses}', f'{rank} / {len(annual_league_df)} Teams')
        elif comp_type in (['team_player_comparison']):
            #print('triggered')
            metric('Record', f'{wins}-{losses}', f'{rank} / {len(annual_league_df)} Players')
        elif comp_type in (['season_comparison', 'year']):
            metric('Record', f'{wins}-{losses}', f'{rank} / {len(annual_league_df)} Seasons')
        elif comp_type in (['player','league_comparison']):
            metric(metric_map[column], value, f'{percentile} % League')
    else:
        if comp_type in (['team', 'team_comparison']):
            metric(metric_map[column], value, f'{rank} / {len(annual_league_df)} Teams')
        elif comp_type in (['team_player_comparison']):
            #print('triggered')
            metric(metric_map[column], value, f'{rank} / {len(annual_league_df)} Players')
        elif comp_type in (['season_comparison', 'year']):
            metric(metric_map[column], value, f'{rank} / {len(annual_league_df)} Seasons')
        elif comp_type in (['player', 'league_comparison']):
            #print('triggered')
            metric(metric_map[column], value, f'{percentile} % League')

def show_scatterplot(df, x_axis='off_rtg', y_axis='def_rtg', hover_name='team'):
    if hover_name == 'team_player_comparison':
        hover_name = 'player'
    fig = px.scatter(
        data_frame=df,
        #x=x_axis,
        #y=y_axis,
        x= x_axis,
        y= y_axis,
        color='color',
        hover_name=hover_name,
        labels={x_axis: metric_map[x_axis],
                y_axis: metric_map[y_axis]})
    fig.update(layout_coloraxis_showscale=False)
    fig.update_traces(marker=dict(size=20))
    if y_axis == 'def_rtg':
        fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

def show_stripplot(df, hover_name='team'):
    if hover_name == 'team_player_comparison':
        hover_name = 'player'
    fig = px.strip(
        data_frame=df,
        #x=x_axis,
        #y=y_axis,
        y='metric',
        x='value',
        color='color',
        hover_name=hover_name,
        stripmode='overlay',
        orientation='h'
        #labels={x_axis: metric_map[x_axis],
        #        y_axis: metric_map[y_axis]}
                )
    fig.update(layout_coloraxis_showscale=False)
    fig.update(layout_showlegend=False)
    fig.update_layout(yaxis=None)
    fig.update_traces(marker=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)

def show_metrics(df, cols, comp_type='team'):
    width = min(len(cols), 4)
    col_ = st.columns(width)
    for position, col in enumerate(cols):
        column = position % width
        with col_[column]:
            #print(col, column)
            get_values(df, col, comp_type=comp_type)

def league_comparison(df, level, cols=['win_pct', 'off_rtg', 'def_rtg', 'mov'], x_axis='off_rtg', y_axis='def_rtg', team=None, year=None, player=None):
    #print(cols, level)
    if level == 'team':
        df['color'] = [2 if i == team else 1 for i in df['team']]
    elif level == 'year':
        df['color'] = [2 if i == year else 1 for i in df['year']]
    elif level in (['player', 'team_player_comparison']):
        df['color'] = [2 if i == player else 1 for i in df['player']]
    show_scatterplot(df, x_axis=x_axis, y_axis=y_axis, hover_name=level)
    show_metrics(df, cols=cols, comp_type=level)

def metric_comparison(df, level='team', cols=['fg_pct', 'fg3_pct', 'ft_pct', 'fta_per_fga_pct', 'fg3a_per_fga_pct', 'ts_pct'], team=None, year=None, player=None):
    temp_df = df.copy()
    if level == 'team_player_comparison':
        temp_df.index = temp_df['player']
    else:
        temp_df.index = temp_df[level]
    temp_df = temp_df[cols].stack().reset_index()
    if level == 'team':
        temp_df.columns = ['team', 'metric', 'value']
        temp_df['metric'] = [metric_map[i] for i in temp_df['metric']]
        temp_df['color'] = [2 if i == team else 1 for i in temp_df['team']]
    elif level == 'year':
        temp_df.columns = ['year', 'metric', 'value']
        temp_df['metric'] = [metric_map[i] for i in temp_df['metric']]
        temp_df['color'] = [2 if i == year else 1 for i in temp_df['year']]
    elif level in (['player', 'team_player_comparison']):
        temp_df.columns = ['player', 'metric', 'value']
        temp_df['metric'] = [metric_map[i] for i in temp_df['metric']]
        temp_df['color'] = [2 if i == player else 1 for i in temp_df['player']]
    show_stripplot(temp_df, hover_name=level)
    show_metrics(df, cols=cols, comp_type=level)


