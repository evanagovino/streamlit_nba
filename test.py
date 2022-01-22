import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from jinja2 import Template

#Functions

def return_value(temp_annual_df, player, column='ws'):
    value = temp_annual_df[temp_annual_df['player'] == player][column].values[0]
    for i in range(100):
        if temp_annual_df[column].astype('float').quantile(q=i/100) > value:
            break
    return value, i-1

def create_player_df(df, player, player_columns):
    average_columns_key = ['bpm', 'obpm', 'dbpm', 'age', 'ts_pct', 'trb_pct', 'tov_pct', 'usg_pct', 'fg3_pct', 'fg2_pct', 'ft_pct', 'fg3a_per_fga_pct', 'fta_per_fga_pct']
    total_columns_key = ['vorp', 'mp']
    average_columns = [i for i in player_columns if i in average_columns_key]
    total_columns = [i for i in player_columns if i in total_columns_key]
    d = {}
    for i in total_columns:
        d[i] = 'sum'
    for i in average_columns:
        d[i] = 'mean'
    d['team'] = ['first', 'count']
    test = df[df['player'] == player][player_columns].groupby(['player','year']).agg(d).reset_index()
    test.columns  = [value[0] if position < test.shape[1] - 1  else value[1] for position, value in enumerate(test.columns)]
    if test['count'].max() > 1:
        mask = test[test['count'] > 1].index[0]
        test['team'][mask] = 'TOT'
    return test.sort_values('year', ascending=False).reset_index(drop=True)

# def evaluate_percentile(p):
#     if p >= 95:
#         return 'Elite'
#     elif p >= 90:
#         return 'All Star'
#     elif p >= 70:
#         return 'Above Average'
#     elif p >= 40:
#         return 'Average'
#     elif p >= 20:
#         return 'Below Average'
#     else:
#         return 'Poor'

def team_value(temp_annual_df, columns):
    annual_league_df = temp_annual_df.merge(temp_annual_df.groupby('team')[['mp']].sum().reset_index(), on='team')
    for column in columns:
        annual_league_df[column] = (annual_league_df[column] * annual_league_df['mp_x']) / annual_league_df['mp_y']
    annual_league_df = annual_league_df.groupby('team')[columns].sum().reset_index()
    return annual_league_df

def highlight_col_player(x, player):
    return ['background-color: red']*len(x) if x.player == player else ['']*len(x)

def highlight_col_year(x, year):
    return ['background-color: red']*len(x) if x.year == year else ['']*len(x)

def highlight_col_team(x, team):
    return ['background-color: red']*len(x) if x.team == team else ['']*len(x)

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
    components.html(_build_metric(label, value, percentile), height=90)


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

#Metric Names
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
'fg3a_per_fga_pct': '3PAr',
'fta_per_fga_pct': 'FTr',
'off_rtg': 'Offensive Rating',
'def_rtg': 'Defensive Rating',
'mov': 'Margin of Victory',
'sos': 'Schedule Strength',
'win_pct': 'Winning Percentage'
}

#df = pd.read_csv('/Users/evanagovino/Downloads/test_df.csv')

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
st.session_state.keep_player = False
team = st.sidebar.selectbox('Which team?', st.session_state.team_list, key='team', on_change=update_from_team)
year = st.sidebar.selectbox('Which year?', st.session_state.year_list, key='year', on_change=update_from_year)
print(team, year)
team_df = st.session_state.df[(st.session_state.df['team'] == team) & (st.session_state.df['year'] == year)].sort_values('mp', ascending=False).reset_index(drop=True)
annual_df = st.session_state.df[(st.session_state.df['year'] == year)].sort_values('mp', ascending=False).reset_index(drop=True)
player_list = team_df['player'].unique()
player = st.sidebar.selectbox('Which player?', team_df['player'].unique(), on_change=update_from_player)
print('keep player status', st.session_state.keep_player)
if 'player' in st.session_state:
    pass
    #print('Session State Player', st.session_state['player'])
else:
    print('No player')
if 'player' not in st.session_state:
    st.session_state['player'] = player
    print('Session State Initiated', st.session_state['player'])
#else:
#    st.session_state['player'] = player
#    print('Session State Changed', st.session_state['player'])

hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """

title_alignment = """
<style>
#atlanta-hawks {
  text-align: center
}

#league-comparisons {
  text-align: center
}

#historical-comparisons {
  text-align: center
}

#team-comparisons {
  text-align: center
}

#basic-metrics {
  text-align: center
}

#advanced-metrics {
  text-align: center
}

#shooting-metrics {
  text-align: center
}

#trae-young {
  text-align: center
}
</style>
"""

st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
st.markdown(title_alignment, unsafe_allow_html=True)

#team_df = df[(df['team'] == team) & (df['year'] == year)].sort_values('mp', ascending=False).reset_index(drop=True)
#annual_df = df[(df['year'] == year)].sort_values('mp', ascending=False).reset_index(drop=True)
#player = st.sidebar.selectbox('Which player?', team_df['player'].unique())
#player_two = st.sidebar.selectbox('Which player?', st.session_state.player_list, key='xxx')

advanced_data = st.sidebar.checkbox('Show Advanced Metrics', value=True)
shooting_data = st.sidebar.checkbox('Show Shooting Metrics', value=True)
st.title(team_map[team])
st.header('League Comparisons')

original_columns = ['vorp', 'bpm','obpm', 'dbpm']
original_columns_league = ['win_pct','off_rtg', 'def_rtg', 'mov']
advanced_columns = ['ts_pct', 'trb_pct', 'tov_pct', 'usg_pct']
advanced_columns_league = ['ts_pct', 'tov_pct', 'sos']
shooting_columns = ['fg3_pct', 'fg2_pct', 'ft_pct', 'fg3a_per_fga_pct', 'fta_per_fga_pct']
shooting_columns_league = ['fg3_pct', 'ft_pct', 'fg3a_per_fga_pct', 'fta_per_fga_pct']
global_columns = original_columns.copy()
if advanced_data:
    for column in advanced_columns:
        global_columns.append(column)
if shooting_data:
    for column in shooting_columns:
        global_columns.append(column)

annual_league_df = st.session_state.league_df[st.session_state.league_df['year'] == year].sort_values('win_pct', ascending=False).reset_index(drop=True)

with st.expander('Show league table'):
    st.dataframe(annual_league_df.style.apply(highlight_col_team, team=team, axis=1))

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Basic Metrics')
    for column in original_columns_league:
        position = annual_league_df[annual_league_df['team'] == team].index.values[0]
        value = annual_league_df[column][position]
        rank = annual_league_df[column].rank(ascending=False).astype('int').values[position]
        if column == 'def_rtg':
            rank = annual_league_df[column].rank().astype('int').values[position]
        #st.write(f'**{metric_map[column]}**:',annual_league_df[column].rank(ascending=False).astype('int').values[position], 'of 30 in league')
        if column == 'win_pct':
            wins = annual_league_df['wins'][position]
            losses = annual_league_df['losses'][position]
            metric('Record', f'{wins}-{losses}', f'{rank} / {len(annual_league_df)} Teams')
        else:
            metric(metric_map[column], value, f'{rank} / {len(annual_league_df)} Teams')
if advanced_data:
    with col2:
        st.subheader('Advanced Metrics')
        for column in advanced_columns_league:
            position = annual_league_df[annual_league_df['team'] == team].index.values[0]
            value = annual_league_df[column][position]
            rank = annual_league_df[column].rank(ascending=False).astype('int').values[position]
            if column == 'tov_pct':
                rank = annual_league_df[column].rank().astype('int').values[position]
            #st.write(f'{metric_map[column]}:',annual_league_df[column].rank(ascending=False).astype('int').values[position], 'of 30 in league')
            metric(metric_map[column], value, f'{rank} / {len(annual_league_df)} Teams')
if shooting_data:
    with col3:
        st.subheader('Shooting Metrics')
        for column in shooting_columns_league:
            position = annual_league_df[annual_league_df['team'] == team].index.values[0]
            value = annual_league_df[column][position]
            rank = annual_league_df[column].rank(ascending=False).astype('int').values[position]
            #st.write(f'{metric_map[column]}:',annual_league_df[column].rank(ascending=False).astype('int').values[position], 'of 30 in league')
            metric(metric_map[column], value, f'{rank} / {len(annual_league_df)} Teams')

player_columns = ['player', 'team','year','age', 'mp'] + global_columns

st.title(st.session_state.player)

st.header('League Comparisons')

with st.expander('Show league table'):
    st.dataframe(annual_df[player_columns].style.apply(highlight_col_player, player=st.session_state.player, axis=1))

#player_df = st.session_state.df[(st.session_state.df['player'] == st.session_state.player)][player_columns].sort_values('year', ascending=False).reset_index(drop=True)
player_df = create_player_df(st.session_state.df, st.session_state.player, player_columns)
#st.session_state.df[(st.session_state.df['player'] == st.session_state.player)][player_columns].sort_values('year', ascending=False).reset_index(drop=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Basic Metrics')
    for column in original_columns:
            value, percentile = return_value(annual_df, st.session_state.player, column)
            #status = evaluate_percentile(percentile)
            metric(metric_map[column], value, f'{percentile} % League')
    
if advanced_data:
    with col2:
        st.subheader('Advanced Metrics')
        for column in advanced_columns:
            value, percentile = return_value(annual_df, st.session_state.player, column)
            #status = evaluate_percentile(percentile)
            metric(metric_map[column], value, f'{percentile} % League')
            #st.write(f'{metric_map[column]}:',return_value(annual_df, player, column), 'percentile')

if shooting_data:
    with col3:
        st.subheader('Shooting Metrics')
        for column in shooting_columns:
            value, percentile = return_value(annual_df, st.session_state.player, column)
            #status = evaluate_percentile(percentile)
            metric(metric_map[column], value, f'{percentile} % League')
            #st.write(f'{metric_map[column]}:',return_value(annual_df, player, column), 'percentile')

with st.expander('Show visualizations'):
    col1, col2, col3 = st.columns(3)
    with col1:
        fig, ax = plt.subplots(len(original_columns), 1)
        for position, column in enumerate(original_columns):
            ax[position].hist(annual_df[column], bins=20)
            ax[position].axvline(annual_df[annual_df['player'] == st.session_state.player][column].values[0], color='k', linestyle='dashed', linewidth=1)
            ax[position].title.set_text(metric_map[column])
            ax[position].get_yaxis().set_visible(False)
        fig.tight_layout()
        col1.pyplot(fig)
    if advanced_data:
        with col2:
            fig, ax = plt.subplots(len(advanced_columns), 1)
            for position, column in enumerate(advanced_columns):
                ax[position].hist(annual_df[column], bins=20)
                ax[position].axvline(annual_df[annual_df['player'] == st.session_state.player][column].values[0], color='k', linestyle='dashed', linewidth=1)
                ax[position].title.set_text(metric_map[column])
                ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col2.pyplot(fig)
    if shooting_data:
        with col3:
            fig, ax = plt.subplots(len(shooting_columns), 1)
            for position, column in enumerate(shooting_columns):
                ax[position].hist(annual_df[column], bins=20)
                ax[position].axvline(annual_df[annual_df['player'] == st.session_state.player][column].values[0], color='k', linestyle='dashed', linewidth=1)
                ax[position].title.set_text(metric_map[column])
                ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col3.pyplot(fig)

st.header('Historical Comparisons')

with st.expander('Show historical table'):
    st.dataframe(player_df.style.apply(highlight_col_year, year=year, axis=1))

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Basic Metrics')
    for column in original_columns:
        position = player_df[player_df['year'] == year].index.values[0]
        value = player_df[column][position]
        rank = player_df[column].rank(ascending=False).astype('int').values[position]
        #st.write(f'{metric_map[column]}:',player_df[column].rank(ascending=False).astype('int').values[position], f'of {len(player_df)} in career')
        metric(metric_map[column], value, f'{rank} / {len(player_df)} Seasons')
if advanced_data:
    with col2:
        st.subheader('Advanced Metrics')
        for column in advanced_columns:
            position = player_df[player_df['year'] == year].index.values[0]
            value = player_df[column][position]
            rank = player_df[column].rank(ascending=False).astype('int').values[position]
            metric(metric_map[column], value, f'{rank} / {len(player_df)} Seasons')
            #st.write(f'{metric_map[column]}:', player_df[column].rank(ascending=False).astype('int').values[position], f'of {len(player_df)} in career')
if shooting_data:
    with col3:
        st.subheader('Shooting Metrics')
        for column in shooting_columns:
            position = player_df[player_df['year'] == year].index.values[0]
            value = player_df[column][position]
            rank = player_df[column].rank(ascending=False).astype('int').values[position]
            metric(metric_map[column], value, f'{rank} / {len(player_df)} Seasons')
            #st.write(f'{metric_map[column]}:', player_df[column].rank(ascending=False).astype('int').values[position], f'of {len(player_df)} in career')

with st.expander('Show visualizations'):
    col1, col2, col3 = st.columns(3)
    with col1:
        fig, ax = plt.subplots(len(original_columns), 1)
        for position, column in enumerate(original_columns):
            ax[position].bar(player_df['year'], player_df[column], color= 'blue')
            ax[position].bar(player_df[player_df['year'] == year]['year'], player_df[player_df['year'] == year][column], color = 'red')
            ax[position].set_title(metric_map[column])
            #ax[position].get_yaxis().set_visible(False)
        fig.tight_layout()
        col1.pyplot(fig)
        fig, ax = plt.subplots(len(original_columns), 1)
        for position, column in enumerate(original_columns):
            ax[position].boxplot(player_df[column], vert=False)
            ax[position].axvline(player_df[player_df['year'] == year][column].values[0], color='k', linestyle='dashed', linewidth=1)
            ax[position].set_title(metric_map[column])
            ax[position].get_yaxis().set_visible(False)
        fig.tight_layout()
        col1.pyplot(fig)
    if advanced_data:
        with col2:
            fig, ax = plt.subplots(len(advanced_columns), 1)
            for position, column in enumerate(advanced_columns):
                ax[position].bar(player_df['year'], player_df[column], color= 'blue')
                ax[position].bar(player_df[player_df['year'] == year]['year'], player_df[player_df['year'] == year][column], color = 'red')
                ax[position].set_title(metric_map[column])
                #ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col2.pyplot(fig)
            fig, ax = plt.subplots(len(advanced_columns), 1)
            for position, column in enumerate(advanced_columns):
                ax[position].boxplot(player_df[column], vert=False)
                ax[position].axvline(player_df[player_df['year'] == year][column].values[0], color='k', linestyle='dashed', linewidth=1)
                ax[position].set_title(metric_map[column])
                ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col2.pyplot(fig)
    if shooting_data:
        with col3:
            fig, ax = plt.subplots(len(shooting_columns), 1)
            for position, column in enumerate(shooting_columns):
                ax[position].bar(player_df['year'], player_df[column], color= 'blue')
                ax[position].bar(player_df[player_df['year'] == year]['year'], player_df[player_df['year'] == year][column], color = 'red')
                ax[position].set_title(metric_map[column])
                #ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col3.pyplot(fig)
            fig, ax = plt.subplots(len(shooting_columns), 1)
            for position, column in enumerate(shooting_columns):
                ax[position].boxplot(player_df[column], vert=False)
                ax[position].axvline(player_df[player_df['year'] == year][column].values[0], color='k', linestyle='dashed', linewidth=1)
                ax[position].set_title(metric_map[column])
                ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col3.pyplot(fig)

st.header('Team Comparisons')

with st.expander('Show team table'):
    st.dataframe(team_df[player_columns].style.apply(highlight_col_player, player=st.session_state.player, axis=1))

col1, col2, col3 = st.columns(3)

position = team_df[team_df['player'] == st.session_state.player].index.values[0]

with col1:
    st.subheader('Basic Metrics')
    for column in original_columns:
        position = team_df[team_df['player'] == st.session_state.player].index.values[0]
        value = team_df[column][position]
        rank = team_df[column].rank(ascending=False).astype('int').values[position]
        metric(metric_map[column], value, f'{rank} / {len(team_df)} Players')
        #st.write(f'{metric_map[column]}:',team_df[column].rank(ascending=False).astype('int').values[position], f'of {len(team_df)} on team')
    
if advanced_data:
    with col2:
        st.subheader('Advanced Metrics')
        for column in advanced_columns:
            position = team_df[team_df['player'] == st.session_state.player].index.values[0]
            value = team_df[column][position]
            rank = team_df[column].rank(ascending=False).astype('int').values[position]
            metric(metric_map[column], value, f'{rank} / {len(team_df)} Players')
            #st.write(f'{metric_map[column]}:',team_df[column].rank(ascending=False).astype('int').values[position], f'of {len(team_df)} on team')

if shooting_data:
    with col3:
        st.subheader('Shooting Metrics')
        for column in shooting_columns:
            position = team_df[team_df['player'] == st.session_state.player].index.values[0]
            value = team_df[column][position]
            rank = team_df[column].rank(ascending=False).astype('int').values[position]
            metric(metric_map[column], value, f'{rank} / {len(team_df)} Players')
            #st.write(f'{metric_map[column]}:',team_df[column].rank(ascending=False).astype('int').values[position], f'of {len(team_df)} on team')

with st.expander('Show visualizations'):
    col1, col2, col3 = st.columns(3)
    with col1:
        fig, ax = plt.subplots(len(original_columns), 1)
        for position, column in enumerate(original_columns):
            ax[position].hist(team_df[column], bins=20)
            ax[position].axvline(team_df[team_df['player'] == st.session_state.player][column].values[0], color='k', linestyle='dashed', linewidth=1)
            ax[position].title.set_text(metric_map[column])
            ax[position].get_yaxis().set_visible(False)
        fig.tight_layout()
        col1.pyplot(fig)
    if advanced_data:
        with col2:
            fig, ax = plt.subplots(len(advanced_columns), 1)
            for position, column in enumerate(advanced_columns):
                ax[position].hist(team_df[column], bins=20)
                ax[position].axvline(team_df[team_df['player'] == st.session_state.player][column].values[0], color='k', linestyle='dashed', linewidth=1)
                ax[position].title.set_text(metric_map[column])
                ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col2.pyplot(fig)
    if shooting_data:
        with col3:
            fig, ax = plt.subplots(len(shooting_columns), 1)
            for position, column in enumerate(shooting_columns):
                ax[position].hist(team_df[column], bins=20)
                ax[position].axvline(team_df[team_df['player'] == st.session_state.player][column].values[0], color='k', linestyle='dashed', linewidth=1)
                ax[position].title.set_text(metric_map[column])
                ax[position].get_yaxis().set_visible(False)
            fig.tight_layout()
            col3.pyplot(fig)

