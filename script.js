const apiKey = '101f5c57';  // Replace 'YOUR_API_KEY' with your actual API key from OMDb

function searchMovies() {
    const searchInput = document.getElementById('searchInput').value;
    const resultsContainer = document.getElementById('results');

    // Clear previous results
    resultsContainer.innerHTML = "";

    // Make a request to OMDb API for movie search
    fetch(`http://www.omdbapi.com/?apikey=${apiKey}&t=${encodeURIComponent(searchInput)}`)
        .then(response => response.json())
        .then(movie => {
            // Check if the response contains movie details
            if (movie.Response === 'True') {
                // Display the movie details
                resultsContainer.innerHTML = `
                    <h2>${movie.Title} (${movie.Year})</h2>
                    <p>${movie.Plot}</p>
                    <p>Director: ${movie.Director}</p>
                    <p>Actors: ${movie.Actors}</p>
                    <p>Genre: ${movie.Genre}</p>
                    <p>IMDb Rating: ${movie.imdbRating}</p>
                    <img src="${movie.Poster}" alt="${movie.Title} Poster">
                `;
            } else {
                resultsContainer.innerHTML = "<p>Film non trouvé.</p>";
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            resultsContainer.innerHTML = "<p>Erreur lors de la recherche. Veuillez réessayer.</p>";
        });
}
