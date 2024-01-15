import time
import streamlit as st
import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

# Configuration de la page Streamlit
st.set_page_config(
    page_title="CinéFlix 🎬",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Personnalisation du style Streamlit
st.markdown(
    """
    <style>
        body {
            text-align: center;
            color: white;
        }
        .stMarkdown {
            text-align: center;
        }
        .search-card, .recommendation-card {
            padding: 10px;
            background-color: #1f2c38;
            border-radius: 10px;
            margin-top: 10px;
        }
        img {
            max-width: 100%;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Pop-up d'ouverture de page
if "content_displayed" not in st.session_state:
    with st.empty():
        for seconds in range(3):
            st.image("https://hips.hearstapps.com/hmg-prod/images/netflix-1597403529.gif", use_column_width=True, width=600)
            time.sleep(1)
        st.empty()
    st.session_state.content_displayed = True

# En-tête
st.markdown('<h1 style="color: red;">Bienvenue sur CinéFlix 🎥 🍿</h1>', unsafe_allow_html=True)

# Charger les données à partir du fichier JSON
with open('movies.json', 'r') as file:
    movies_data = json.load(file)

DEFAULT_DIRECTOR_ENCODED = -1
DEFAULT_GENRE_ENCODED = 0

def get_recommendations(movie, movies_list, nn_model, label_encoder_director, label_encoder_genre):
    # Vérifier si le réalisateur est dans l'ensemble d'entraînement
    if movie["director"] in label_encoder_director.classes_:
        director_encoded = label_encoder_director.transform([movie["director"]])[0]
    else:
        # Gérer la valeur inconnue (par exemple, en remplaçant par une valeur par défaut)
        director_encoded = DEFAULT_DIRECTOR_ENCODED

    # Vérifier si le genre est dans l'ensemble d'entraînement
    if movie["genre"] in label_encoder_genre.classes_:
        genre_encoded = label_encoder_genre.transform([movie["genre"]])[0]
    else:
        # Gérer la valeur inconnue (par exemple, en remplaçant par une valeur par défaut)
        genre_encoded = DEFAULT_GENRE_ENCODED

    # Encodage de la recherche pour NearestNeighbors
    search_encoded = [genre_encoded, director_encoded, *movie["actors_encoded"]]

    # Trouver les indices des films les plus similaires
    _, indices = nn_model.kneighbors([search_encoded], n_neighbors=6)

    # Retirer le film de recherche des résultats
    indices = indices[0][1:]

    # Récupérer les recommandations
    recommendations = [movies_list[index] for index in indices]

    return recommendations

# Convertir les données en une liste de dictionnaires
movies_list = [
    {
        "title": str(movie["Series_Title"]),
        "release_date": movie["Released_Year"],
        "genre": movie["Genre"],
        "vote_average": movie["IMDB_Rating"],
        "poster_path": movie["Poster_Link"],
        "director": movie["Director"],
        "actors": [movie["Star1"], movie["Star2"], movie["Star3"], movie["Star4"]]
    }
    for movie in movies_data
]

# Collecter toutes les données distinctes pour les réalisateurs, le genre et les acteurs
all_director_data = [movie["Director"] for movie in movies_data]
all_genre_data = [movie["Genre"] for movie in movies_data]
all_actors_data = [movie["Star1"] for movie in movies_data] + \
                  [movie["Star2"] for movie in movies_data] + \
                  [movie["Star3"] for movie in movies_data] + \
                  [movie["Star4"] for movie in movies_data]

# Utiliser LabelEncoder pour les caractéristiques catégorielles
label_encoder_director = LabelEncoder()
label_encoder_genre = LabelEncoder()
label_encoder_actors = LabelEncoder()

# Entraîner les encodeurs avec les bonnes données
label_encoder_director.fit(all_director_data)
label_encoder_genre.fit(all_genre_data)
label_encoder_actors.fit(all_actors_data)

for movie in movies_list:
    movie["director"] = label_encoder_director.transform([movie["director"]])[0]
    movie["actors_encoded"] = label_encoder_actors.transform(movie["actors"])
    movie["genre"] = label_encoder_genre.transform([movie["genre"]])[0]

# Créer une matrice de caractéristiques pour NearestNeighbors
features_matrix = np.array([
    [movie["genre"], movie["director"], *movie["actors_encoded"]]
    for movie in movies_list
])

# Entraîner le modèle NearestNeighbors
nn_model = NearestNeighbors(metric='minkowski', algorithm='brute', p=2, n_neighbors=6, n_jobs=-1)
nn_model.fit(features_matrix)

# Entrée de recherche
search_options = ['Titre', 'Réalisateur', 'Acteur']
selected_search_option = st.selectbox('Choisissez le type de recherche :', search_options, index=0)

if selected_search_option == 'Titre':
    selected_query = st.text_input('Recherchez un film par titre :', key='film_input')
elif selected_search_option == 'Réalisateur':
    selected_query = st.text_input('Recherchez un film par réalisateur :', key='director_input')
elif selected_search_option == 'Acteur':
    selected_query = st.text_input('Recherchez un film par acteur :', key='actor_input')

# Bouton de recherche
if st.button('Rechercher'):
    if selected_search_option == 'Titre':
        # Filtrer les films qui correspondent à la recherche par titre
        results = [movie for movie in movies_list if selected_query.lower() in movie['title'].lower()]
    elif selected_search_option == 'Réalisateur':
        # Filtrer les films qui correspondent à la recherche par réalisateur
        results = [movie for movie in movies_list if selected_query.lower() in movie['director'].lower()]
    elif selected_search_option == 'Acteur':
        # Filtrer les films qui correspondent à la recherche par acteur
        results = [movie for movie in movies_list if selected_query.lower() in [actor.lower() for actor in movie['actors']]]

    # Affichage des résultats de la recherche
    st.markdown(f'<h2>Résultats pour <span style="color: red;">{selected_query}</span></h2>', unsafe_allow_html=True)
    if results:
        for result in results:
            st.markdown(
                f"""
                <div class="search-card">
                    <h3>{result['title']}</h3>
                    <p>Date de sortie: {result['release_date']}</p>
                    <p>Note moyenne: {result['vote_average']}</p>
                    <p>Réalisateur: {label_encoder_director.inverse_transform([result['director']])[0]}</p>
                    <p>Acteurs: {', '.join(result['actors'])}</p>
                    <p>Genre: {', '.join(label_encoder_genre.inverse_transform([result['genre']]))}</p>
                    <img src="{result['poster_path']}" alt="Poster">
                </div>
                """,
                unsafe_allow_html=True
            )

        # Créer une matrice de caractéristiques mise à jour pour NearestNeighbors
        features_matrix = np.array([
            [movie["genre"], movie["director"], *movie["actors_encoded"]]
            for movie in movies_list
        ])

        nn_model.fit(features_matrix)

        # Obtenez les recommandations basées sur le réalisateur et le genre
        recommendations = get_recommendations(results[0], movies_list, nn_model, label_encoder_director, label_encoder_genre)

        # Afficher les recommandations
        st.markdown('<h2>Recommandations</h2>', unsafe_allow_html=True)
        for i, recommendation in enumerate(recommendations):
            st.markdown(
                f"""
                <div class="recommendation-card">
                    <h4>#{i+1} Recommandation</h4>
                    <p>{recommendation['title']}</p>
                    <p>Date de sortie: {recommendation['release_date']}</p>
                    <p>Note moyenne: {recommendation['vote_average']}</p>
                    <p>Réalisateur: {label_encoder_director.inverse_transform([recommendation['director']])[0]}</p>
                    <p>Acteurs: {', '.join(recommendation['actors'])}</p>
                    <p>Genre: {', '.join(label_encoder_genre.inverse_transform([recommendation['genre']]))}</p>
                    <img src="{recommendation['poster_path']}" alt="Poster" style="max-width:100%; border-radius: 10px;">
                </div>
                """,
                unsafe_allow_html=True
            )