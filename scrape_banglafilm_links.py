import requests
from bs4 import BeautifulSoup
import csv

url = "https://oldnothi.bfa.gov.bd/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

films = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/film-details/" in href:
        films.append(href)


# Remove duplicates
films = sorted(set(films), key=lambda x: int(x.split('/')[-1]))


with open("bangla_films.csv", "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["url"])
    for link in films:
        writer.writerow([link])

print(f"Saved {len(films)} film links to bangla_films.csv")