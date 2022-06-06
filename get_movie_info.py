import difflib
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
import requests
from io import BytesIO

with open('url_movies_allocine.json', 'r') as f:
  movie_data_base = json.load(f)

def get_info_prog(date=""):

    list_info = []

    if date:
        URL = f"https://www.programme-tv.net/programme/programme-tnt/{date}/"
    else:
        URL = "https://www.programme-tv.net/programme/programme-tnt.html"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="corps")

    all_page = results.find_all("div", class_="grid-rows")
    for movie_bloc in all_page:
        global_info = movie_bloc.find_all("div", class_="gridRow-cards")

        for info in global_info:

            # Get channel
            channel_infos_element = info.find_all("div", class_="gridRow-cardsChannel")
            channel_number_info = channel_infos_element[0].find_all("p")
            channel_number = channel_number_info[0].text.strip()
            if (int(channel_number[2:]) == 4) or (int(channel_number[2:]) > 26):
                continue
            channel_info = channel_infos_element[0].find_all("a")
            channel = channel_info[0].text.strip()[len(channel_number):]

            list_info.append([info, channel_number, channel])
    return list_info


def get_movie_info(progress_bar=None, date=""):
    liste_cinema, liste_serieTV, liste_culture, liste_tele_film, liste_sport, liste_autre = [], [], [], [], [], []
    for info, channel_number, channel in get_info_prog(date):
        if progress_bar:
            progress_bar.progress(int(channel_number[2:])/26)

        # Get movie
        film_movie_element = info.find_all("div", class_="mainBroadcastCard reverse")
        movie_element = film_movie_element[0].find_all("div", class_="mainBroadcastCard-infos")

        # Get starting hour
        starting_hour_element = movie_element[0].find_all("p", class_="mainBroadcastCard-startingHour")
        starting_hour = starting_hour_element[0].text.strip()

        # Get title
        title_elements = movie_element[0].find_all("h3", class_="mainBroadcastCard-title")
        title_element = title_elements[0].find_all("a")
        title = title_element[0].text.strip()
        link = title_element[0]["href"]

        # Get subtitle
        subtitle_element = movie_element[0].find_all("p", class_="mainBroadcastCard-subtitle")
        if subtitle_element:
            subtitle = subtitle_element[0].text.strip()
        else:
            subtitle = None

        # Get program's type
        movie_type_element = movie_element[0].find_all("p", class_="mainBroadcastCard-format")
        if movie_type_element:
            movie_type = movie_type_element[0].text.strip()
        else:
            movie_type = None  


        if (channel=="La Chaîne parlementaire") and (movie_type=="Cinéma"):
            movie_type  = "Culture Infos"

        # Get movie image
        # image_movie_element = film_movie_element[0].find_all("div", class_="pictureTagGenerator pictureTagGenerator-ratio-5-7")
        apply_ratio_lazyload = film_movie_element[0].find_all('img', class_="apply-ratio lazyload")
        apply_ratio_lazyloaded = film_movie_element[0].find_all('img', class_="apply-ratio lazyloaded")
        apply_ratio = film_movie_element[0].find_all('img', class_="apply-ratio")
        if apply_ratio_lazyload:
            url_image_movie = apply_ratio_lazyload[0]["data-src"] 
        elif apply_ratio_lazyloaded:
            url_image_movie = apply_ratio_lazyloaded[0]["data-src"]   
        elif apply_ratio:
            url_image_movie = apply_ratio[0]["src"] 


        # Get release year
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="corps")
        info_of_prog = results.find_all('div', class_="synopsis defaultStyleContentTags")
        if info_of_prog:
            resume_prog = info_of_prog[0].text.strip()
        else:
            resume_prog = None


        # Get Allocine information
        if movie_type == "Cinéma":

            try :
                # Get release year
                page = requests.get(link)
                soup = BeautifulSoup(page.content, "html.parser")
                results = soup.find(id="corps")
                info_of_movie = results.find_all('ul', class_="overview-overviewSubtitle")    
                release_year = info_of_movie[0].find_all("li")[1].text.strip()
                # print(title, release_year)

                closest_key = difflib.get_close_matches(title.lower(), movie_data_base.keys())[0]
                urls_movie = movie_data_base[closest_key]
                # print(closest_key, urls_movie)
                    

                if len(urls_movie) > 1:
                    for url in urls_movie:
                        page = requests.get(url)
                        soup = BeautifulSoup(page.content, "html.parser")
                        results = soup.find(id="allocine__moviepage")

                        year_element = results.find_all('div', class_="meta-body-item meta-body-info")
                        year_element = year_element[0].find_all('span')
                        year = year_element[0].text.strip()[-4:]

                        # print(year, release_year)
                        if int(year) in [int(release_year)-1, int(release_year), int(release_year)+1]:
                            break
                else:
                    url = urls_movie[0]
                    year = release_year

                
                page = requests.get(url)
                soup = BeautifulSoup(page.content, "html.parser")
                results = soup.find(id="allocine__moviepage")

                resume_element = soup.find_all('div', class_="content-txt")
                if resume_element:
                    resume = resume_element[0].text
                else:
                    resume = ""   

                genre_element = results.find_all('div', class_="meta-body-item meta-body-info")
                list_genre_incorrect = [g.text.strip() for g in genre_element[0].find_all('span')]
                for i_elt, elt in enumerate(reversed(list_genre_incorrect)):
                    if elt == '/':
                        break
                list_genre = list_genre_incorrect[-i_elt:]

                actors_element = results.find_all('div', class_="meta-body-item meta-body-actor")
                list_actors = [actor.text.strip() for actor in actors_element[0].find_all('span')[1:]]
                
                video_element = results.find_all('a', class_="trailer item")[0]['href']

                # Get movie image
                image_element = results.find_all('img', class_="thumbnail-img")
                url_img_movie_allocine = image_element[0]["src"] 

                ratings_element_full = results.find_all("div", class_="rating-holder rating-holder-3") 
                ratings_element_incomplet = results.find_all("div", class_="rating-holder rating-holder-2") 
                if ratings_element_full:
                    ratings = ratings_element_full[0].find_all("span", class_="stareval-note")
                    press_rate, spect_rate = [float(rate.text.strip().replace(',','.')) for rate in ratings[:2]]
                elif ratings_element_incomplet:
                    ratings = ratings_element_incomplet[0].find_all("span", class_="stareval-note")
                    press_rate, spect_rate = 0, float(ratings[0].text.strip().replace(',','.'))
                else:
                    press_rate, spect_rate = 0,0

                page = requests.get(f"https://www.allocine.fr{video_element}")
                soup = BeautifulSoup(page.content, "html.parser")
                results = soup.find(id="allocine__moviepage_videos_trailer")
                trailer_element = results.find_all("div", class_="video-card-player")
                video_element = trailer_element[0].find_all("figure")
                dico_video = json.loads(video_element[0]['data-model'])
                try:
                    video_link = dico_video['videos'][0]['sources']['high'] 
                    # print(title, 'high')
                except KeyError:
                    video_link = dico_video['videos'][0]['sources']['standard'] 
                    # print(title, 'standard')
                url_trailer = video_link.replace("\\","")
                
                liste_cinema.append([channel, channel_number, list_actors, list_genre, year, url_trailer, starting_hour, title, subtitle, url, resume, url_img_movie_allocine, press_rate, spect_rate])
            except IndexError:
                liste_cinema.append([channel, channel_number, None, None, release_year, None, starting_hour, title, subtitle, None, None, url_image_movie, 0, 0])
            except KeyError:
                liste_cinema.append([channel, channel_number, None, None, release_year, None, starting_hour, title, subtitle, None, None, url_image_movie, 0, 0])

           
        # Show information
        else:
            if movie_type == "Série TV":
                liste_serieTV.append([url_image_movie, channel, channel_number, resume_prog, starting_hour, title, subtitle])
            elif movie_type == "Culture Infos":
                liste_culture.append([url_image_movie, channel, channel_number, resume_prog, starting_hour, title, subtitle])
            elif movie_type == "Téléfilm":
                liste_tele_film.append([url_image_movie, channel, channel_number, resume_prog, starting_hour, title, subtitle])
            elif movie_type == "Sport":
                liste_sport.append([url_image_movie, channel, channel_number, resume_prog, starting_hour, title, subtitle])
            else:
                liste_autre.append([url_image_movie, channel, channel_number, resume_prog, starting_hour, title, subtitle])
    
    if progress_bar:
        progress_bar.empty()      
    return liste_cinema, liste_serieTV, liste_culture, liste_tele_film, liste_sport, liste_autre 
