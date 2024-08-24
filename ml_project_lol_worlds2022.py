import requests                      # Library to make http request from web
from bs4 import BeautifulSoup        # library for web scrapping like text 
import re                            #to make regex
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np



leaderboard_path ="worlds2022_standing.csv"


tournament_urls = {
     "LEC" : "https://gol.gg/tournament/tournament-ranking/LEC%20Summer%202022/",
     "LCS" : "https://gol.gg/tournament/tournament-ranking/LCS%20Summer%202022/",
     "LPL" : "https://gol.gg/tournament/tournament-ranking/LPL%20Summer%202022/",
     "LCK" : "https://gol.gg/tournament/tournament-ranking/LCK%20Summer%202022/"
}

def scrape_league_data(url):                                 # create the function
      page = requests.get(url)                               # using request.get  to request the server to obtain data and store it in 
      html_page = BeautifulSoup(page.content, "html.parser") # analyse the html content
      
      return html_page  


def parse_teams_names(html_page): 
      pattern = re.compile(r'.* stats in .* 2022')     # create a pattern in regex to catch the name
      league_table = html_page.find_all(title=pattern) # using BS4 to find html tag 'title' which match the pattern

      teams = []                                       # initialize an emplty list to store the name of the team
      
      for team in league_table:                        # for loop to run each tag find in league table
          team_name = team.text                        # extract the texte of the html tag, which should correspond to the team name
          teams.append(team_name)                      # add the team name to the list teams

      return teams                                     # the function return the list which store the name of all the extract teams

             
def parse_teams_stats(html_page):
      team_rows = html_page.find_all('tr')[1:]         # using BS4 to find the tag tr which represent the row of a table in html. We avoided the head of the table [1:]
      teams_stats = []                                 # we initialize an empty list  to store the satst of each teams extract in the html table

      for row in team_rows:                                         # for loop to run through each row in team_rows
          data_cells = row.find_all('td', class_='text-center')     # for each row of the table, we searching cells with td which has text-center. 
          for data_cell in data_cells:                              # Another for loop that run through each cell of data
               stats = data_cell.text.strip()                       # Extract the text store in the cell with strip to delet the useless charaters
               teams_stats.append(stats)                            # Add the statistics data to the list teams_stats

      return teams_stats                                            # it return the list teams_stats which store all the stats of the team extract in the html table

def combine_data(teams, teams_stats):
    result = []                                                     # Initialize an empty list  result which will store the combine data team name and stats

    for i in range(len(teams)):                                     # For loop run through i all over the list teams with len that gives the total. And range that create a squence  of index from 0 to len -1
        name = teams[i]                                             # For each iteration we extract the team name which match in the list 'teams'
        start_index = i * 5                                         # calculate the index to extract the stats because there are 5 stattistique associate to each teams
        stats_for_name = teams_stats[start_index:start_index+5]     # extract a sub list of teams_stats . It start from start_index to start_index +5
        name_and_stats = [name] + stats_for_name                    # create a new list which store the name of the team and all the following stats of the team
        result.append(name_and_stats)                               # add the list name and stats to the list result

    return result                                                   # the function return result after go through all the teams. result is kind of a master list

def data_frame_from_list(list):                                     # transforming a list to a dataframe      
    df = pd.DataFrame(list, columns=['team_name', 'winrate', 'wins', 'loses', 'game duration', 'GPM'])

    return df

def data_frame_from_csv(path):                                       # function  with path for argument that is settle at the top
     leaderboard = pd.read_csv(path, names=['team_name', 'winrate','placement']) # pd.read_csv to read the path and I specify the columns names in the csv.

     return leaderboard

def merge_data_frames(tournament_urls):
    data_frames = []                                                # I initialize an empty list named data_frames to store de dataframes

    for league, url in tournament_urls.items():                     # for loop that run every entry of the two arguments
        html_page = scrape_league_data(url)                         # scraping of the data with the url 
        teams = parse_teams_names(html_page)                        # function parse_teaams nam are called to extract the name with the html page
        teams_stats = parse_teams_stats(html_page)                  # function parse_stats nam are called to extract the stats with the html page
        result = combine_data(teams, teams_stats)                   # function useing to associate the name with the stats

        league = data_frame_from_list(result)                       # transforming copmbined data into a dataframe with pandas. with the columuns name specify in the function
        league['standing'] = [(i + 1) for i in range(len(league))]  # adding a columns standing to the dataframe which indicate the position of the team in the rankink. Determine by the order of the team. 
        data_frames.append(league)                                  

    
    merged_data_frames = pd.concat(data_frames, ignore_index=True)
    
    return merged_data_frames


def plot_relation_GPM_worldstanding(merged_data_frames, leaderboard): 
    common_teams = list(set(merged_data_frames['team_name']).intersection(leaderboard['team_name']))

    common_teams_data_merged = merged_data_frames[merged_data_frames['team_name'].isin(common_teams)][['team_name', 'GPM']]
    common_teams_data_leaderboard = leaderboard[leaderboard['team_name'].isin(common_teams)][['team_name', 'placement']]

    result_df = pd.concat([common_teams_data_merged.set_index('team_name'), common_teams_data_leaderboard.set_index('team_name')], axis=1, join='inner').reset_index()
    result_df.columns = ['team_name', 'GPM', 'standing']
    print(result_df)

    result_df['GPM'] = pd.to_numeric(result_df['GPM'], errors='coerce')
    result_df['standing'] = pd.to_numeric(result_df['standing'], errors='coerce')

    x = result_df['GPM']
    y = result_df['standing']

    plt.scatter(x, y, color ='black')
    plt.xlabel('Gold per minute')
    plt.ylabel('Final Standing at worlds 2022')
    plt.title('Correlation between GPM and worlds standing')

    plt.gca().invert_yaxis()

def ml_algorithm_data_preparation(merged_data_frames, leaderboard):
    common_teams = list(set(merged_data_frames['team_name']).intersection(leaderboard['team_name']))

    common_teams_merged_data = merged_data_frames[merged_data_frames['team_name'].isin(common_teams)][['team_name', 'winrate', 'wins', 'loses', 'GPM', 'standing']]
    common_teams_leaderboard = leaderboard[leaderboard['team_name'].isin(common_teams)][['team_name', 'placement']]

    data_for_algorithm = pd.concat([common_teams_merged_data.set_index('team_name'), common_teams_leaderboard.set_index('team_name')], axis=1, join='inner').reset_index()

    data_for_algorithm['winrate'] = data_for_algorithm['winrate'].str.strip('%').astype(int)

    data_for_algorithm['GPM'] = pd.to_numeric(data_for_algorithm['GPM'], errors='coerce')
    data_for_algorithm['winrate'] = pd.to_numeric(data_for_algorithm['winrate'], errors='coerce')
    data_for_algorithm['wins'] = pd.to_numeric(data_for_algorithm['wins'], errors='coerce')
    data_for_algorithm['loses'] = pd.to_numeric(data_for_algorithm['loses'], errors='coerce')

    data_for_algorithm = data_for_algorithm.drop('team_name', axis=1)
    data_for_algorithm = pd.concat([pd.Series(1, index=data_for_algorithm.index, name='param0'), data_for_algorithm], axis=1)

    X = data_for_algorithm.drop(columns='placement')
    Y = data_for_algorithm.iloc[:, 6]

    X = X.apply(lambda x: x / np.max(x))

    return X, Y, data_for_algorithm
                

def gradientDescent(X, Y, theta, alpha, iterations):
    m = len(Y)
    J_history = []

    for i in range(iterations):
         hypothesis = np.dot(X, theta)
         loss = hypothesis - Y 
         gradiant = np.dot(X.T, loss) / m
         theta -= alpha * gradiant

         cost = np.sum(loss ** 2) / (2 * m)
         J_history.append(cost)

         print(J_history)

    return theta



def main():

    leaderboard = data_frame_from_csv(leaderboard_path)
    merged_data_frames = merge_data_frames(tournament_urls)

    print(merged_data_frames)
    print(leaderboard)

    plot_relation_GPM_worldstanding(merged_data_frames, leaderboard)

    X, Y, data_for_algorithm = ml_algorithm_data_preparation(merged_data_frames, leaderboard)
    print(data_for_algorithm)

    print(X)
    print(Y)


    theta = np.zeros(X.shape[1])

    theta = gradientDescent(X, Y, theta, alpha=0.01, iterations=50)
    print('optimized theta:', theta)

    theta_max =np.max(theta)
    normalized_theta = [value/theta_max for value in theta]
    print('Normalized theta: ', normalized_theta)

    # BLG, JDG, WEIBO, T1, KT, GENG, LNG, NRG
    # regular season stats 
    # theta0, winrate, wins, loses, GPM, standing
    
    result_checking_data = [
    [1, 81, 30, 7, 255, 1],
    [1, 81, 29, 7, 249, 2],
    [1, 64, 25, 14, 113, 5],
    [1, 50, 21, 21, 60, 5],
    [1, 85, 35, 6, 248, 1],
    [1, 82, 32, 7, 275, 2],
    [1, 68, 25, 12, 155, 3],
    [1, 50, 9, 9, -45, 5]
    ]

    numpy_result_checking_data = np.array(result_checking_data)

    multiplied_result = numpy_result_checking_data[:, 1:] * theta[1:]

    print("Multiplied result: ")
    print(multiplied_result)

    sum_per_row = np.sum(multiplied_result, axis=1)

    print("Sum for each row:")
    print(sum_per_row)

    # ranking manually
    # BLG = 3rd
    # JDG = 4th
    # WEIBO = 6th
    # T1 = 7th
    # KT = 2nd
    # GENG = 1st 
    # LNG = 5th
    # NRG = 8th


main()