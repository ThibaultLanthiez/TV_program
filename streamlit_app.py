import datetime
import difflib
import json
import requests
from bs4 import BeautifulSoup
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from googletrans import Translator

with open('url_movies_allocine.json', 'r') as f:
  movie_data_base = json.load(f)

st.set_page_config(page_title="Programme TV", layout="wide")

today_date = str(datetime.datetime.today().strftime('%A %d %b %Y'))
english_translator = Translator() # pip install googletrans==3.1.0a0
translation = english_translator.translate(today_date, dest="fr")
col1, col2 = st.columns(2)
st.title("Ce soir à la télé")
st.title(translation.text)

progress_bar = st.progress(0)

def get_movie_info():
    liste_cinema, liste_serieTV, liste_culture, liste_tele_film, liste_sport, liste_autre = [], [], [], [], [], []

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
            if (int(channel_number[2:]) == 4) or (int(channel_number[2:]) > 25):
                continue
            channel_info = channel_infos_element[0].find_all("a")
            channel = channel_info[0].text.strip()[len(channel_number):]

            progress_bar.progress(int(channel_number[2:])/25)

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
            title_elements = movie_element[0].find_all("h3", class_="mainBroadcastCard-title")
            title_element = title_elements[0].find_all("a")
            if movie_type_element:
                movie_type = movie_type_element[0].text.strip()
            else:
                movie_type = None  

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
            response = requests.get(url_image_movie)
            img_movie = Image.open(BytesIO(response.content))

            # Get Allocine information
            if movie_type == "Cinéma":

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
                genre = genre_element[0].find_all('span')[-1].text.strip()
                
                
                video_element = results.find_all('a', class_="trailer item")[0]['href']

                # Get movie image
                image_element = results.find_all('img', class_="thumbnail-img")
                url_img_movie_allocine = image_element[0]["src"] 
                response = requests.get(url_img_movie_allocine)
                img_movie_allocine = Image.open(BytesIO(response.content))

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
                # print(f"https://www.allocine.fr{video_element}")
                soup = BeautifulSoup(page.content, "html.parser")
                results = soup.find(id="allocine__moviepage_videos_trailer")
                trailer_element = results.find_all("div", class_="video-card-player")
                video_element = trailer_element[0].find_all("figure")
                dico_video = json.loads(video_element[0]['data-model'])
                video_link = dico_video['videos'][0]['sources']['standard'] 
                url_trailer = video_link.replace("\\","")
                
                liste_cinema.append([channel, channel_number, genre, year, url_trailer, starting_hour, title, subtitle, url, resume, img_movie_allocine, press_rate, spect_rate])
   
           
            # Show information
            else:
                if movie_type == "Série TV":
                    liste_serieTV.append([img_movie, channel, channel_number, starting_hour, title, subtitle])
                elif movie_type == "Culture Infos":
                    liste_culture.append([img_movie, channel, channel_number, starting_hour, title, subtitle])
                elif movie_type == "Téléfilm":
                    liste_tele_film.append([img_movie, channel, channel_number, starting_hour, title, subtitle])
                elif movie_type == "Sport":
                    liste_sport.append([img_movie, channel, channel_number, starting_hour, title, subtitle])
                else:
                    liste_autre.append([img_movie, channel, channel_number, starting_hour, title, subtitle])
          
    return liste_cinema, liste_serieTV, liste_culture, liste_tele_film, liste_sport, liste_autre 


liste_cinema, liste_serieTV, liste_culture, liste_tele_film, liste_sport, liste_autre = get_movie_info()

##############

# Sort movie by spectator rate
movie_ranking_initial = [(elt[-1], elt[-2], elt[4]) for elt in liste_cinema]
movie_ranking_descending = sorted(movie_ranking_initial, reverse=True) # Descending
movie_ranking = [movie_ranking_initial.index(mark) for mark in movie_ranking_descending]


st.title("Cinéma")
nb_col = 4
list_col_cinema = st.columns(nb_col)
for i, index_movie in enumerate(movie_ranking):
    movie = liste_cinema[index_movie]
    channel, channel_number, genre, year, url_trailer, starting_hour, title, subtitle, url_movie, resume, img_movie_allocine, press_rate, spect_rate = movie
    
    if press_rate == 0:
        press_rate = "aucune note"

    # if platform.uname().system == "Linux": # Mobile device
    #     column = st
    # else:
    for index_col, col in enumerate(list_col_cinema):
        if i in range(index_col, 20, nb_col):
            column = col
            break
        
    column.write("_____")
    column.image(img_movie_allocine, width=120)
    column.markdown(f"{channel} (chaîne {channel_number[2:]}) - {starting_hour}")
    column.markdown(f"**{title}** {f'({subtitle})' if (subtitle and subtitle!=title) else ''}")                     
    column.markdown(f"Spectateurs : **{spect_rate}**  |  Presse : **{press_rate}**  |  Année : **{year}**")   
    with column.expander("Informations sur le film"):
        st.video(url_trailer)
        st.markdown(f"**Année de sortie** : {year}")
        st.markdown(f"**Genre** : {genre}")
        st.markdown(f"**Résumé** : {resume}")
        st.markdown(f"[Voir sur Allociné]({url_movie})")   

##########
def show_prog(title, data):
    st.title(title)
    nb_col = 4
    list_col = st.columns(nb_col)
    for i, prog in enumerate(data):
        img_movie, channel, channel_number, starting_hour, title, subtitle = prog
        
        # if platform.uname().system == "Linux": # Mobile device
        #     column = st
        # else:
        for index_col, col in enumerate(list_col):
            if i in range(index_col, 20, nb_col):
                column = col
                break

        column.write("_____")
        column.image(img_movie, width=120)
        column.markdown(f"{channel} (chaîne {channel_number[2:]}) - {starting_hour}")
        subtitle_markdown = f"({subtitle})" if (subtitle and subtitle!=title) else ""
        column.markdown(f"**{title}** {subtitle_markdown}") 
       
show_prog(title="Culture Infos", data=liste_culture)
show_prog(title="Téléfilm", data=liste_tele_film)
show_prog(title="Sport", data=liste_sport)
show_prog(title="Série TV", data=liste_serieTV)
show_prog(title="Autre", data=liste_autre)


# Avoir note téléfilm
# Ajouter best acteur
# Ajouter durée film
# Ajouter pour tous les autres : résumé
# Ajouter résumé pour autre programme
# Mettre sur porfolio
