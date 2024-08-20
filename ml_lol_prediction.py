import requests # Library to make http request from web
from bs4 import BeautifulSoup # library for web scrapping like text 
import re

url_lec ="https://gol.gg/tournament/tournament-ranking/LEC%20Summer%20Season%202024/" # variable which has URL

def scrape_league_data(url): # create the function
      page = requests.get(url) # using request.get  to request the server to obtain data and store it in 
      html_page = BeautifulSoup(page.content, "html.parser")
      
      return html_page

def parse_teams_names(html_page): 
      pattern = re.compile(r'.* stats in .* 2022')
      league_table = html_page.find_all(title=pattern)


def main():  # function main get the url_lec and storie in into page
      html_page = scrape_league_data(url_lec)
      print(html_page)

main()