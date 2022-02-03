import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit.components.v1 as components
from jinja2 import Template
import _functions as functions

st.set_page_config(layout="wide")

#Team Names
team_map = {
'ATL': 'Atlanta Hawks',
'BOS': 'Boston Celtics',
'BRK': 'Brooklyn Nets',
'CHI': 'Chicago Bulls',
'CHO': 'Charlotte Hornets',
'CLE': 'Cleveland Cavaliers',
'DAL': 'Dallas Mavericks',
'DEN': 'Denver Nuggets',
'DET': 'Detroit Pistons',
'IND': 'Indiana Pacers',
'GSW': 'Golden State Warriors',
'HOU': 'Houston Rockets',
'LAC': 'Los Angeles Clippers',
'LAL': 'Los Angeles Lakers',
'MEM': 'Memphis Grizzlies',
'MIA': 'Miami Heat',
'MIL': 'Milwaukee Bucks',
'MIN': 'Minnesota Timberwolves',
'NOP': 'New Orleans Pelicans',
'OKC': 'Oklahoma City Thunder',
'ORL': 'Orlando Magic',
'NYK': 'New York Knicks',
'PHI': 'Philadelphia 76ers',
'PHO': 'Phoenix Suns',
'POR': 'Portland Trailblazers',
'SAC': 'Sacramento Kings',
'SAS': 'San Antonio Spurs',
'TOR': 'Toronto Raptors',
'UTA': 'Utah Jazz',
'WAS': 'Washington Wizards'
}

#Process Data
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv('team_df.csv')
    st.session_state.league_df = pd.read_csv('league_df.csv')
    st.session_state.team_list = sorted(st.session_state.df['team'].unique())
    st.session_state.year_list = sorted(st.session_state.df['year'].unique(), reverse=True)

def update_from_team():
    if 'player' in st.session_state:
        del st.session_state['player']
    #pass
    #del st.session_state['team_df']
    #del st.session_state['player_list']
    #st.session_state.team_df = st.session_state.df[(st.session_state.df['team'] == st.session_state.team) & (st.session_state.df['year'] == st.session_state.year)].sort_values('mp', ascending=False).reset_index(drop=True)
    #st.session_state.player_list = st.session_state.team_df['player'].unique()
    #st.session_state.player = st.session_state.player_list[0]
    #st.sidebar.selectbox('Which player?', st.session_state.player_list, key='player')

def update_from_year():
    team_df = st.session_state.df[(st.session_state.df['team'] == st.session_state.team) & (st.session_state.df['year'] == st.session_state.year)].sort_values('mp', ascending=False).reset_index(drop=True)
    player_list = team_df['player'].unique()
    print('Player', st.session_state.player)
    if st.session_state.player not in player_list:
        print('Player not in player list, callback triggered')
        del st.session_state['player']
    else:
        print(f'{st.session_state.player} in player list and will remain consistent')

def update_from_player():
    if 'player' in st.session_state:
        del st.session_state['player']




#CSS
#st.session_state.keep_player = False
team = st.sidebar.selectbox('Which team?', st.session_state.team_list, key='team', on_change=update_from_team)
year = st.sidebar.selectbox('Which year?', st.session_state.year_list, key='year', on_change=update_from_year)
print(team, year)
team_df = st.session_state.df[(st.session_state.df['team'] == team) & (st.session_state.df['year'] == year)].sort_values('mp', ascending=False).reset_index(drop=True)
annual_df = st.session_state.df[(st.session_state.df['year'] == year)].sort_values('mp', ascending=False).reset_index(drop=True)
player_list = team_df['player'].unique()
player = st.sidebar.selectbox('Which player?', team_df['player'].unique(), on_change=update_from_player)
st.session_state.view = st.sidebar.selectbox('Which view?', ['Team', 'Player'])
annual_league_df = st.session_state.league_df[st.session_state.league_df['year'] == year].sort_values('win_pct', ascending=False).reset_index(drop=True)
historical_league_df = st.session_state.league_df[st.session_state.league_df['team'] == team].sort_values('win_pct', ascending=False).reset_index(drop=True)
#print('keep player status', st.session_state.keep_player)
if 'player' in st.session_state:
    pass
    #print('Session State Player', st.session_state['player'])
else:
    print('No player')
if 'player' not in st.session_state:
    st.session_state['player'] = player
    print('Session State Initiated', st.session_state['player'])
player_df = st.session_state.df[(st.session_state.df['player'] == st.session_state.player)].sort_values('year', ascending=False).reset_index(drop=True)
league_comparison = st.sidebar.checkbox('League Comparison', value=True)
if st.session_state.view == 'Player':
    team_comparison = st.sidebar.checkbox('Team Comparison', value=True)
historical_comparison = st.sidebar.checkbox('Historical Comparison', value=True)

title_alignment = """
<style>
.row_heading.level0 {display:none}
            .blank {display:none}
#atlanta-hawks {
  text-align: center
}

#trae-young {
  text-align: center
}

#league-comparison {
  text-align: center
}

#historical-comparison {
  text-align: center
}

#team-comparison {
  text-align: center
}

#player-rating {
  text-align: center
}

#shooting-comparison {
  text-align: center
}

#offensive-metrics {
  text-align: center
}

#defensive-metrics {
  text-align: center
}

#team-rating {
  text-align: center
}

#offensive-four-factors {
  text-align: center
}

#defensive-four-factors {
  text-align: center
}

</style>
"""

st.markdown(title_alignment, unsafe_allow_html=True)

if st.session_state.view == 'Team':

    st.title(team_map[team])
    if league_comparison:
        st.header('League Comparison')
        st.subheader('Team Rating')
        functions.league_comparison(annual_league_df, level='team', cols=['win_pct', 'off_rtg', 'def_rtg', 'mov'], team=team)
        st.subheader('Shooting Comparison')
        functions.metric_comparison(annual_league_df, level='team', cols=['fg_pct', 'fg3_pct', 'ft_pct', 'fta_per_fga_pct', 'fg3a_per_fga_pct', 'ts_pct'], team=team)
        st.subheader('Offensive Four Factors')
        functions.metric_comparison(annual_league_df, level='team', cols=['efg_pct', 'orb_pct', 'tov_pct', 'ft_rate'], team=team)
        st.subheader('Defensive Four Factors')
        functions.metric_comparison(annual_league_df, level='team', cols=['opp_efg_pct', 'opp_tov_pct', 'drb_pct', 'opp_ft_rate'], team=team)
    if historical_comparison:
        st.header('Historical Comparison')
        st.subheader('Team Rating')
        functions.league_comparison(historical_league_df, level='year', cols=['win_pct', 'off_rtg', 'def_rtg', 'mov'], year=year)
        st.subheader('Shooting Comparison')
        functions.metric_comparison(historical_league_df, level='year', cols=['fg_pct', 'fg3_pct', 'ft_pct', 'fta_per_fga_pct', 'fg3a_per_fga_pct', 'ts_pct'], year=year)
        st.subheader('Offensive Four Factors')
        functions.metric_comparison(historical_league_df, level='year', cols=['efg_pct', 'orb_pct', 'tov_pct', 'ft_rate'], year=year)
        st.subheader('Defensive Four Factors')
        functions.metric_comparison(historical_league_df, level='year', cols=['opp_efg_pct', 'opp_tov_pct', 'drb_pct', 'opp_ft_rate'], year=year)

elif st.session_state.view == 'Player':

    st.title(st.session_state.player)
    if league_comparison:
        st.header('League Comparison')
        st.subheader('Player Rating')
        temp_df = annual_df[annual_df['mp'] >= annual_df['mp'].quantile(0.3)]
        functions.league_comparison(temp_df, level='player', cols=['vorp', 'bpm', 'obpm', 'dbpm'], player=player, x_axis='obpm', y_axis='dbpm')
        st.subheader('Shooting Comparison')
        functions.metric_comparison(temp_df, level='player', cols=['fg2_pct', 'fg3_pct', 'ft_pct', 'fta_per_fga_pct', 'fg3a_per_fga_pct', 'ts_pct'], player=player)
        st.subheader('Offensive Metrics')
        functions.metric_comparison(temp_df, level='player', cols=['usg_pct', 'ast_pct', 'tov_pct', 'orb_pct'], player=player)
        st.subheader('Defensive Metrics')
        functions.metric_comparison(temp_df, level='player', cols=['drb_pct', 'stl_pct', 'blk_pct'], player=player)
    if team_comparison:
        st.header('Team Comparison')
        st.subheader('Player Rating')
        temp_df = team_df[team_df['mp'] >= annual_df['mp'].quantile(0.3)]
        functions.league_comparison(temp_df, level='team_player_comparison', cols=['vorp', 'bpm', 'obpm', 'dbpm'], player=player, x_axis='obpm', y_axis='dbpm')
        st.subheader('Shooting Comparison')
        functions.metric_comparison(temp_df, level='team_player_comparison', cols=['fg3_pct', 'ft_pct', 'fta_per_fga_pct', 'fg3a_per_fga_pct', 'ts_pct'], player=player)
        st.subheader('Offensive Metrics')
        functions.metric_comparison(temp_df, level='team_player_comparison', cols=['usg_pct', 'ast_pct', 'tov_pct', 'orb_pct'], player=player)
        st.subheader('Defensive Metrics')
        functions.metric_comparison(temp_df, level='team_player_comparison', cols=['drb_pct', 'stl_pct', 'blk_pct'], player=player)
    if historical_comparison:
        st.header('Historical Comparison')
        st.subheader('Player Rating')
        functions.metric_comparison(player_df, level='year', cols=['vorp', 'bpm', 'obpm', 'dbpm'], year=year)
        st.subheader('Shooting Comparison')
        functions.metric_comparison(player_df, level='year', cols=['fg2_pct','fg3_pct', 'ft_pct', 'fta_per_fga_pct', 'fg3a_per_fga_pct', 'ts_pct'], year=year)
        st.subheader('Offensive Metrics')
        functions.metric_comparison(player_df, level='year', cols=['usg_pct', 'ast_pct', 'tov_pct', 'orb_pct'], year=year)
        st.subheader('Defensive Metrics')
        functions.metric_comparison(player_df, level='year', cols=['drb_pct', 'stl_pct', 'blk_pct'], year=year)

