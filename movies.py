import streamlit as st
import requests

st.set_page_config(
    page_title="CinéFlix 🎬",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Bienvenue sur CinéFlix 🎥 🍿")
st.write("Recherchez un film et découvrez-en d'autres similaires.")
selected_film = st.text_input('Recherchez un film par titre', key='film_input')


# Function to fetch movie details from OMDb API
def get_movie_details(title, api_key):
    base_url = "http://www.omdbapi.com/"
    params = {"apikey": api_key, "t": title}
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data from OMDb API. Status Code: {response.status_code}")
        return None

# OMDb API key
omdb_api_key = "101f5c57"  

if selected_film:
    # Fetch movie details from OMDb API
    movie_details = get_movie_details(selected_film, omdb_api_key)

    if movie_details:
        # Display the details of the chosen movie
        st.write("Détails du film:")
        st.write(f"Titre: {movie_details['Title']}")
        st.write(f"Année de sortie: {movie_details['Year']}")
        st.write(f"Genre: {movie_details['Genre']}")
        st.write(f"Réalisateur: {movie_details['Director']}")
        st.write(f"Acteurs: {movie_details['Actors']}")
        st.image(movie_details['Poster'], caption=f"Affiche de {movie_details['Title']}", use_column_width=True)

        def get_similar_movies(genre):
            base_url = "http://www.omdbapi.com/"
            params = {"apikey": omdb_api_key, "type": "movie", "r": "json", "s": genre}
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                return response.json().get('Search', [])
            else:
                st.error(f"Error fetching similar movies from OMDb API. Status Code: {response.status_code}")
                return []

        similar_movies = get_similar_movies(movie_details['Genre'])
        if similar_movies:
            st.write("Films similaires:")
            for movie in similar_movies:
                st.write(f"Titre: {movie['Title']}")
                st.write(f"Année de sortie: {movie['Year']}")
                st.write("---")
        else:
            st.write("Aucun film similaire trouvé.")
    else:
        st.warning("Les détails du film n'ont pas pu être récupérés.")
else:
    st.info("Veuillez entrer un titre de film pour commencer la recherche.")
