import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def initialize_movie_db():
    with open('url_movies_allocine.json', 'r') as f:
        movie_data_base = json.load(f)

    
    URL_allocine = "https://www.allocine.fr/films/"
    page = requests.get(URL_allocine)
    soup = BeautifulSoup(page.content, "html.parser")
    results_allocine = soup.find(id="content-layout")
    pagination_page = results_allocine.find_all("div", class_="pagination-item-holder")
    number_last_page = int(str(pagination_page[0]).split('</span')[-2].split('>')[-1])

    URL_allocine = "https://www.allocine.fr/films/"
    page = requests.get(URL_allocine)
    soup = BeautifulSoup(page.content, "html.parser")
    results_allocine = soup.find(id="allocine__movies_all")
    all_page = results_allocine.find_all("a", class_="meta-title-link")
    for element in all_page:
        title = element.text.strip().lower()
        if movie_data_base.get(title) and (f"https://www.allocine.fr{element['href']}" not in movie_data_base[title]):
            print(f"\tADD - {title}")
            movie_data_base[title] = movie_data_base[title] + [f"https://www.allocine.fr{element['href']}"]
        elif not movie_data_base.get(title):
            print(f"\tCREATE - {title}")
            movie_data_base[title] = [f"https://www.allocine.fr{element['href']}"]            

    # for i in tqdm(range(2,number_last_page+1)):
    for i in range(2,number_last_page+1):
        print(f"Page {i}/{number_last_page}")
        URL_allocine = f"https://www.allocine.fr/films/?page={i}"
        page = requests.get(URL_allocine)
        soup = BeautifulSoup(page.content, "html.parser")
        results_allocine = soup.find(id="allocine__movies_all")

        all_page = results_allocine.find_all("a", class_="meta-title-link")
        for element in all_page:
            title = element.text.strip().lower()

            if title == "lola e seus irmãos":
                title = "lola et ses frères"

            if movie_data_base.get(title) and (f"https://www.allocine.fr{element['href']}" not in movie_data_base[title]):
                print(f"\tADD - {title}")
                movie_data_base[title] = movie_data_base[title] + [f"https://www.allocine.fr{element['href']}"]
            elif not movie_data_base.get(title):
                print(f"\tCREATE - {title}")
                movie_data_base[title] = [f"https://www.allocine.fr{element['href']}"] 
        
        with open('url_movies_allocine.json', 'w') as fp:
            json.dump(movie_data_base, fp)

    return movie_data_base

movie_data_base = initialize_movie_db()
