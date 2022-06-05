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

from get_movie_info import get_movie_info

with open('url_movies_allocine.json', 'r') as f:
  movie_data_base = json.load(f)

st.set_page_config(page_title="Programme TV", 
                   layout="wide",
                   initial_sidebar_state="collapsed")

choice_date = st.sidebar.selectbox(
     "Choix de la date :",
     ('Hier', 'Ce soir', 'Demain', "Après demain"),
     index=1)

if choice_date == "Ce soir":
    date = ""
elif choice_date == "Demain":
    currentTimeDate = datetime.datetime.now() + datetime.timedelta(days=1)
    date = currentTimeDate.strftime('%Y-%m-%d')
elif choice_date == "Après demain":
    currentTimeDate = datetime.datetime.now() + datetime.timedelta(days=2)
    date = currentTimeDate.strftime('%Y-%m-%d')
elif choice_date == "Hier":
    currentTimeDate = datetime.datetime.now() - datetime.timedelta(days=1)
    date = currentTimeDate.strftime('%Y-%m-%d')  

change_date = date if date else datetime.datetime.today().strftime('%Y-%m-%d')
date_format = datetime.datetime.strptime(change_date, '%Y-%m-%d')
date_correct = str(date_format.strftime('%A %d %b %Y'))
english_translator = Translator() # pip install googletrans==3.1.0a0
translation = english_translator.translate(date_correct, dest="fr")
col1, col2 = st.columns(2)
st.title(f"{choice_date} à la télé ({translation.text})")

progress_bar = st.progress(0)
liste_cinema, liste_serieTV, liste_culture, liste_tele_film, liste_sport, liste_autre = get_movie_info(date=date, progress_bar=progress_bar)
st.write("_____")

##############

def show_prog(title, data):
    if data:
        st.title(title)
        nb_col = 4
        list_col = st.columns(nb_col)
        
        if title == "Cinéma":
            # Sort movie by spectator rate
            movie_ranking_initial = [(elt[-1], elt[-2], elt[4]) for elt in data]
            movie_ranking_descending = sorted(movie_ranking_initial, reverse=True) # Descending
            movie_ranking = [movie_ranking_initial.index(mark) for mark in movie_ranking_descending]
            for i, index_movie in enumerate(movie_ranking):
                movie = data[index_movie]
                channel, channel_number, list_actors, list_genre, year, url_trailer, starting_hour, title, subtitle, url_movie, resume, url_img_movie_allocine, press_rate, spect_rate = movie
                
                if press_rate == 0:
                    press_rate = "aucune note"
                if spect_rate == 0:
                    spect_rate = "aucune note"

                # if platform.uname().system == "Linux": # Mobile device
                #     column = st
                # else:
                for index_col, col in enumerate(list_col):
                    if i in range(index_col, 20, nb_col):
                        column = col
                        break
                
                response = requests.get(url_img_movie_allocine)
                img_movie_allocine = Image.open(BytesIO(response.content))
                    
                column.write("_____")
                column.image(img_movie_allocine, width=150)
                column.markdown(f"{channel} (chaîne {channel_number[2:]}) - {starting_hour}")
                column.markdown(f"**{title}** {f'({subtitle})' if (subtitle and subtitle!=title) else ''}")                     
                column.markdown(f"Spectateurs : **{spect_rate}**  |  Presse : **{press_rate}**  |  Année : **{year}**")   
                if url_trailer:
                    with column.expander("Informations sur le film"):
                        st.video(url_trailer)
                        st.markdown(f"**Genre** : {', '.join(list_genre)}")
                        st.markdown(f"**Avec** : {', '.join(list_actors)}")
                        st.markdown(f"**Résumé** : {resume}")
                        st.markdown(f"[Voir sur Allociné]({url_movie})") 
                else:
                    column.markdown(":warning: Film non trouvé sur Allocine")  
        else:
            for i, prog in enumerate(data):
                url_image_movie, channel, channel_number, resume_prog, starting_hour, title, subtitle = prog
                
                response = requests.get(url_image_movie)
                img_movie = Image.open(BytesIO(response.content))

                # if platform.uname().system == "Linux": # Mobile device
                #     column = st
                # else:
                for index_col, col in enumerate(list_col):
                    if i in range(index_col, 20, nb_col):
                        column = col
                        break

                column.write("_____")
                column.image(img_movie, width=150)
                column.markdown(f"{channel} (chaîne {channel_number[2:]}) - {starting_hour}")
                subtitle_markdown = f"({subtitle})" if (subtitle and subtitle!=title) else ""
                column.markdown(f"**{title}** {subtitle_markdown}") 
                if resume_prog:
                    with column.expander("Informations sur le programme"):
                        st.markdown(f"**Résumé** : {resume_prog}")
       
show_prog(title="Cinéma", data=liste_cinema)
show_prog(title="Culture Infos", data=liste_culture)
show_prog(title="Téléfilm", data=liste_tele_film)
show_prog(title="Sport", data=liste_sport)
show_prog(title="Série TV", data=liste_serieTV)
show_prog(title="Autre", data=liste_autre)


# Avoir note téléfilm
# Ajouter durée film
# Mettre sur porfolio
# Gérer ordre portable
