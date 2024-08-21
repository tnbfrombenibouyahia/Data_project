import requests                      # Library to make http request from web
from bs4 import BeautifulSoup        # library for web scrapping like text 
import re                            #to make regex
import pandas as pd

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

def data_frame_from_list(list):                                            
    df = pd.DataFrame(list, columns=['team_name', 'winrate', 'wins', 'loses', 'game duration', 'GPM'])

    return df

def data_frame_from_csv(path): 
     leaderboard = pd.read_csv(path, names=['team_name', 'winrate','placement'])

     return leaderboard

def merge_data_frames(tournament_urls):
    data_frames = []

    for league, url in tournament_urls.items():
        html_page = scrape_league_data(url)
        teams = parse_teams_names(html_page)
        teams_stats = parse_teams_stats(html_page)
        result = combine_data(teams, teams_stats)

        league = data_frame_from_list(result)
        league['standing'] = [(i + 1) for i in range(len(league))]
        data_frames.append(league)

    
    merged_data_frames = pd.concat(data_frames, ignore_index=True)
    
    return merged_data_frames
   

def main():
    merged_data_frames = merge_data_frames(tournament_urls)
    leaderboard = data_frame_from_csv(leaderboard_path)

    print(merged_data_frames)
    print(leaderboard)

main()