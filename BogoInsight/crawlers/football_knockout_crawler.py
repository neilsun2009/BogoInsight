import requests
import json
import sys
import os
from io import BytesIO
import pandas as pd
import numpy as np
import shutil
from bs4 import BeautifulSoup, NavigableString
import unicodedata
from datetime import datetime
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class FootballKnockoutCrawler(BaseCrawler):
    
    TOURNAMENT_CONFIG = {
        "FIFA World Cup": {
            "games": [
                {
                    "year": 2022,
                    "game_name": "Qatar 2022",
                    "data_url": "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup"
                },
                {
                    "year": 2018,
                    "game_name": "Russia 2018",
                    "data_url": "https://en.wikipedia.org/wiki/2018_FIFA_World_Cup"
                },
                {
                    "year": 2014,
                    "game_name": "Brazil 2014",
                    "data_url": "https://en.wikipedia.org/wiki/2014_FIFA_World_Cup"
                },
                {
                    "year": 2010,
                    "game_name": "South Africa 2010",
                    "data_url": "https://en.wikipedia.org/wiki/2010_FIFA_World_Cup"
                },
                {
                    "year": 2006,
                    "game_name": "Germany 2006",
                    "data_url": "https://en.wikipedia.org/wiki/2006_FIFA_World_Cup"
                },
                {
                    "year": 2002,
                    "game_name": "Korea/Japan 2002",
                    "data_url": "https://en.wikipedia.org/wiki/2002_FIFA_World_Cup"
                },
                {
                    "year": 1998,
                    "game_name": "France 1998",
                    "data_url": "https://en.wikipedia.org/wiki/1998_FIFA_World_Cup"
                }
            ]
        },
        "UEFA Euro": {
            "games": [
                {
                    "year": 2021,
                    "game_name": "Euro 2020",
                    "data_url": "https://en.wikipedia.org/wiki/UEFA_Euro_2020"
                },
                {
                    "year": 2016,
                    "game_name": "France 2016",
                    "data_url": "https://en.wikipedia.org/wiki/UEFA_Euro_2016"
                },
                {
                    "year": 2012,
                    "game_name": "Poland/Ukraine 2012",
                    "data_url": "https://en.wikipedia.org/wiki/UEFA_Euro_2012"
                },
                {
                    "year": 2008,
                    "game_name": "Austria/Switzerland 2008",
                    "data_url": "https://en.wikipedia.org/wiki/UEFA_Euro_2008"
                },
                {
                    "year": 2004,
                    "game_name": "Portugal 2004",
                    "data_url": "https://en.wikipedia.org/wiki/UEFA_Euro_2004"
                },
                {
                    "year": 2000,
                    "game_name": "Netherlands/Belgium 2000",
                    "data_url": "https://en.wikipedia.org/wiki/UEFA_Euro_2000"
                },
            ]
        }
    }
   
    
    def __init__(self):
        super().__init__(
            topic='Football Knockout Matches',
            desc="""
                Match results for knockout stages of major football tournaments.
            """,
            tags=['sports', 'football'],
            source_desc="""
                Wikipedia pages on various football tournaments
            """
        )


    def crawl(self):
        match_data = pd.DataFrame()
        
        for tournament, tournament_data in self.TOURNAMENT_CONFIG.items():
            for game in tournament_data['games']:
                print(f'Crawling data for {tournament} - {game["game_name"]}...')
                r = requests.get(game['data_url'], timeout=20)
                if r.status_code != 200:
                    self._handle_crawl_failure(r)
                soup = BeautifulSoup(r.text, 'html.parser')
                # Remove all reference link anchors
                for sup in soup.find_all('sup'):
                    sup.extract()
                # Find the section by title
                section = soup.find('span', {'class': 'mw-headline', 'id': 'Knockout_stage'})
                if section is None:
                    section = soup.find('span', {'class': 'mw-headline', 'id': 'Knockout_phase'})
                section = section.parent           
                # Initialize an empty list to hold the filtered h3 elements
                sub_sections = []
                # Iterate over all next siblings of the section
                for sibling in section.find_next_siblings():
                    # If the sibling is an h2, break the loop
                    if sibling.name == 'h2':
                        break
                    # If the sibling is an h3 and does not contain 'Bracket', add it to the list
                    elif sibling.name == 'h3' and 'Bracket' not in sibling.text:
                        sub_sections.append(sibling)

                # Collect match details
                for sub_section in sub_sections:
                    match_details = self._extract_match_details(sub_section)
                    for match_detail in match_details:
                        match_detail['tournament'] = tournament
                        match_detail['year'] = game['year']
                        match_detail['game'] = game['game_name']
                    new_data = pd.DataFrame(match_details)
                    match_data = pd.concat([match_data, new_data], ignore_index=True)

        self.raw_data = match_data
        logger.info(f"Successfully crawled data for {self.topic}, {len(self.raw_data)} records found.")
       
        
    def process(self):
        assert isinstance(self.raw_data, pd.DataFrame), "Raw data is not of type pd.DataFrame."

        df = pd.DataFrame(self.raw_data)
        # Reorder the columns
        # new_order = ['period', 'usage', 'series', 'architecture', 'fab (nm)'] + [c for c in df.columns if c not in ['period', 'usage', 'series', 'architecture', 'fab (nm)']]
        # df = df.reindex(new_order, axis=1)
        # df = df.sort_values('period')

        self.processed_data = df
    
    def _extract_match_details(self, sub_section):
        match_details_list = []
    
        # Extract match round from the current subsection
        match_round = sub_section.find('span', class_='mw-headline').text.strip()
    
        # Find all subsequent siblings until the next h3
        for sibling in sub_section.next_siblings:
            if sibling.name in ['h3', 'h2']:
                break
    
            if isinstance(sibling, NavigableString):
                continue
    
            if sibling.get('class') == ['footballbox']:
                match_details = {}
    
                # Extract date
                date_div = sibling.find('div', class_='fdate')
                hidden_span = date_div.find('span', style="display:none")
                if hidden_span:
                    hidden_span.decompose()  # Remove the hidden span
                date_string = date_div.get_text(strip=True, separator=' ')
                date = datetime.strptime(date_string, '%d %B %Y')
                match_details['date'] = date
    
                # Extract home team
                home_team = sibling.find('th', class_='fhome').text.strip()
                match_details['home_team'] = home_team
    
                # Extract away team
                away_team = sibling.find('th', class_='faway').text.strip()
                match_details['away_team'] = away_team
    
                # Extract home and away scores
                score = sibling.find('th', class_='fscore').text.strip()
                if '(' in score:
                    match_details['has_extra_time'] = True
                    score = score.split(' (')[0]
                else:
                    match_details['has_extra_time'] = False
                home_score, away_score = score.split('–')
                match_details['home_score'] = int(home_score)
                match_details['away_score'] = int(away_score)
                
                # Get match report link
                report = sibling.find('td', string=lambda t: t and 'Report' in t)
                match_details['report_link'] = report.find('a')['href']# if report else None
                
                # Check for penalties
                penalties = sibling.find('th', string=lambda t: t and 'Penalties' in t)
                if penalties:
                    penalties = penalties.parent
                    match_details['has_penalties'] = True
                    pen_score = penalties.find_next_sibling('tr').find('th').text.strip()
                    pen_home_score, pen_away_score = pen_score.split('–')
                    match_details['pen_home_score'] = pen_home_score
                    match_details['pen_away_score'] = pen_away_score
                else:
                    match_details['has_penalties'] = False
    
                # Add the match round to the match details
                match_details['round'] = match_round
    
                # Add the match details to the list
                match_details_list.append(match_details)
    
        return match_details_list
     
      
if __name__ == "__main__":
    crawler = FootballKnockoutCrawler()
    crawler.crawl()
    print(crawler.raw_data.head())
    crawler.process()
    print(crawler.processed_data.head())
    # delete previously output files
    output_base = f"../data/{crawler.topic.replace(' ', '_').lower()}"
    if os.path.exists(output_base):
        shutil.rmtree(output_base)
    # output
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')