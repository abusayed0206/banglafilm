# -*- coding: utf-8 -*-
"""
scraper_bengali.py

This script scrapes movie details in BENGALI from the Bangladesh Film Archive website.
It reads a list of URLs from a 'links.csv' file and saves the scraped data
into 'data/bengali_movies.csv'.
"""

import csv
import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://oldnothi.bfa.gov.bd"
CHANGE_LANGUAGE_PATH = "/change-language"
LANGUAGE_TO_SCRAPE = 'bn'

LABELS = {
    'bn': {
        'মুক্তির তারিখ:': 'release_date',
        'পরিচালক:': 'director',
        'প্রযোজক:': 'producer',
        'অভিনয়:': 'starring',
        'ভাষা:': 'language',
    }
}

def get_movie_data(session, url):
    """
    Fetches and parses movie data for the Bengali language.
    """
    print(f"--- Processing URL for Bengali: {url} ---")
    movie_data = {
        'title': '', 'release_date': '', 'director': '',
        'producer': '', 'starring': '', 'language': '',
    }

    try:
        initial_response = session.get(url)
        initial_response.raise_for_status()
        initial_soup = BeautifulSoup(initial_response.content, 'html.parser')

        token_tag = initial_soup.find('input', {'name': '_token'})
        if not token_tag or not token_tag.get('value'):
            print("Error: Could not find CSRF token.")
            return movie_data
        
        csrf_token = token_tag.get('value')

        lang_change_url = BASE_URL + CHANGE_LANGUAGE_PATH
        payload = {'_token': csrf_token, 'lantype': LANGUAGE_TO_SCRAPE}
        headers = {'Referer': url}
        
        session.post(lang_change_url, data=payload, headers=headers)
        
        final_response = session.get(url)
        final_response.raise_for_status()
        soup = BeautifulSoup(final_response.content, 'html.parser')

        title_tag = soup.find('h1', class_='page-title')
        if title_tag:
            movie_data['title'] = title_tag.get_text(strip=True)

        details_div = soup.find('div', class_='col-lg-6 col-md-6')
        if details_div:
            p_tags = details_div.find_all('p')
            lang_labels = LABELS[LANGUAGE_TO_SCRAPE]

            for p in p_tags:
                strong_tag = p.find('strong')
                if strong_tag:
                    label = strong_tag.get_text(strip=True)
                    full_text = p.get_text(strip=True)
                    value = full_text.replace(label, '', 1).strip()

                    if label in lang_labels:
                        key = lang_labels[label]
                        movie_data[key] = value
        
        print(f"Successfully parsed Bengali data. Title: {movie_data.get('title')}")
        return movie_data

    except requests.exceptions.RequestException as e:
        print(f"Error during network request for {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for {url}: {e}")

    return movie_data

def main():
    """ Main function to run the Bengali scraper. """
    input_csv_file = 'links.csv'
    output_folder = 'data'
    output_csv_file = os.path.join(output_folder, 'bengali_movies.csv')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.exists(input_csv_file):
        print(f"'{input_csv_file}' not found. Please create it with a 'url' column.")
        return

    with open(output_csv_file, 'w', newline='', encoding='utf-8') as f_out:
        fieldnames = ['url', 'title', 'release_date', 'director', 'producer', 'starring', 'language']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        with open(input_csv_file, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                url = row['url'].strip()
                if not url:
                    continue
                
                url = url.replace('/./', '/')

                with requests.Session() as session:
                    session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    
                    bengali_data = get_movie_data(session, url)
                    
                    # Add the URL to the data dictionary before writing
                    bengali_data['url'] = url
                    writer.writerow(bengali_data)
                    print("-" * 20)
                    time.sleep(1) 

    print(f"Bengali scraping complete. Data saved to '{output_csv_file}'.")

if __name__ == '__main__':
    main()
