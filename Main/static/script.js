document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded');
    setupNavigationHandlers();
    setupSelectionHandlers();
});


// Global variables to store user selections
let userSelections = {
    favoriteGenres: [],
    dislikedGenres: [],
    characteristics: [],
    turnoffs: [],
    moods: [],
    bookLength: null,
    minRating: null,
    searchQuery: ''
};

function setupNavigationHandlers() {
    console.log('Setting up navigation handlers');
    document.querySelectorAll('button[data-action]').forEach(button => {
        button.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            const currentPage = document.querySelector('.page:not([style*="display: none"])');
            const currentPageId = currentPage.id;
            
            console.log(`Navigation action: ${action} from page ${currentPageId}`);

            if (action === 'next') {
                const nextPageNum = parseInt(currentPageId.replace('page', '')) + 1;
                const nextPage = document.getElementById(`page${nextPageNum}`);
                if (nextPage) {
                    currentPage.style.display = 'none';
                    nextPage.style.display = 'block';
                }
            } else if (action === 'back') {
                const prevPageNum = parseInt(currentPageId.replace('page', '')) - 1;
                const prevPage = document.getElementById(`page${prevPageNum}`);
                if (prevPage) {
                    currentPage.style.display = 'none';
                    prevPage.style.display = 'block';
                }
            }
        });
    });
}

function setupSelectionHandlers() {
    console.log('Setting up selection handlers');
    
    // Favorite Genres
    const favoriteGenresSelect = document.getElementById('favoriteGenres');
    if (favoriteGenresSelect) {
        favoriteGenresSelect.addEventListener('change', function() {
            if (this.value && userSelections.favoriteGenres.length < 5) {
                userSelections.favoriteGenres.push(this.value);
                updateSelectedItems('selectedFavoriteGenres', userSelections.favoriteGenres);
                console.log('Updated favorite genres:', userSelections.favoriteGenres);
            }
            this.value = '';
        });
    }

    // Disliked Genres
    const dislikedGenresSelect = document.getElementById('dislikedGenres');
    if (dislikedGenresSelect) {
        dislikedGenresSelect.addEventListener('change', function() {
            if (this.value && userSelections.dislikedGenres.length < 5) {
                userSelections.dislikedGenres.push(this.value);
                updateSelectedItems('selectedDislikedGenres', userSelections.dislikedGenres);
                console.log('Updated disliked genres:', userSelections.dislikedGenres);
            }
            this.value = '';
        });
    }

    // Characteristics
    document.querySelectorAll('input[name="characteristics"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                userSelections.characteristics.push(this.value);
            } else {
                userSelections.characteristics = userSelections.characteristics.filter(c => c !== this.value);
            }
            console.log('Updated characteristics:', userSelections.characteristics);
        });
    });

    // Turn-offs
    document.querySelectorAll('input[name="turnoffs"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (userSelections.turnoffs.length >= 3 && this.checked) {
                this.checked = false;
                return;
            }
            if (this.checked) {
                userSelections.turnoffs.push(this.value);
            } else {
                userSelections.turnoffs = userSelections.turnoffs.filter(t => t !== this.value);
            }
            console.log('Updated turnoffs:', userSelections.turnoffs);
        });
    });

    // Moods
    document.querySelectorAll('input[name="moods"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                userSelections.moods.push(this.value);
            } else {
                userSelections.moods = userSelections.moods.filter(m => m !== this.value);
            }
            console.log('Updated moods:', userSelections.moods);
        });
    });

    // Book Length
    document.querySelectorAll('input[name="bookLength"]').forEach(radio => {
        radio.addEventListener('change', function() {
            userSelections.bookLength = this.value;
            console.log('Updated book length:', userSelections.bookLength);
        });
    });

    // Minimum Rating
    document.querySelectorAll('input[name="minRating"]').forEach(radio => {
        radio.addEventListener('change', function() {
            userSelections.minRating = this.value;
            console.log('Updated minimum rating:', userSelections.minRating);
        });
    });

    // Search Input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            userSelections.searchQuery = this.value;
            console.log('Updated search query:', userSelections.searchQuery);
        });
    }
}

function updateSelectedItems(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    items.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'selected-item';
        itemElement.innerHTML = `
            ${item}
            <span class="remove-item" onclick="removeItem('${containerId}', '${item}')">×</span>
        `;
        container.appendChild(itemElement);
    });
}

function removeItem(containerId, item) {
    console.log(`Removing ${item} from ${containerId}`);
    if (containerId === 'selectedFavoriteGenres') {
        userSelections.favoriteGenres = userSelections.favoriteGenres.filter(g => g !== item);
        updateSelectedItems('selectedFavoriteGenres', userSelections.favoriteGenres);
    } else if (containerId === 'selectedDislikedGenres') {
        userSelections.dislikedGenres = userSelections.dislikedGenres.filter(g => g !== item);
        updateSelectedItems('selectedDislikedGenres', userSelections.dislikedGenres);
    }
}

function submitPreferences() {
    console.log('Submitting preferences:', userSelections);
    
    fetch('/api/recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userSelections)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Received recommendations:', data);
        if (data.success) {
            // Use session storage or another method to pass the recommendations
            sessionStorage.setItem('recommendations', JSON.stringify(data.recommendations));
            window.location.href = '/api/results';
        } else {
            console.error('Error:', data.error);
        }
    })
    .catch(error => {
        console.error('Error submitting preferences:', error);
    });
}

// On the results page, ensure the DOM is loaded before displaying recommendations
document.addEventListener('DOMContentLoaded', function() {
    const recommendations = JSON.parse(sessionStorage.getItem('recommendations'));
    if (recommendations) {
        displayRecommendations(recommendations);
    }
});

/*
function displayRecommendations(recommendations) {
    console.log('Displaying multi-genre recommendations');
    
    // Display survey-based recommendations
    const surveyContainer = document.querySelector('#surveyBasedCarousel .carousel-inner');
    if (surveyContainer) {
        if (recommendations.survey_based && recommendations.survey_based.length > 0) {
            displayBookGroup(recommendations.survey_based, surveyContainer);
        } else {
            surveyContainer.innerHTML = '<div class="empty-message">No survey-based recommendations found</div>';
        }
    }

    // Display genre-based recommendations
    const genreSectionsContainer = document.getElementById('genreBasedSections');
    if (genreSectionsContainer) {
        genreSectionsContainer.innerHTML = ''; // Clear existing sections
        
        if (!recommendations.genre_based || Object.keys(recommendations.genre_based).length === 0) {
            genreSectionsContainer.innerHTML = '<div class="empty-message">No genre-based recommendations found</div>';
            return;
        }

        // Create a carousel for each genre
        Object.entries(recommendations.genre_based).forEach(([genre, books]) => {
            const genreSection = document.createElement('div');
            genreSection.className = 'recommendation-section';
            genreSection.innerHTML = `
                <h3>Based on Your Interest in ${genre}</h3>
                <div id="${genre}Carousel" class="carousel slide" data-ride="carousel" data-bs-ride="false">
                    <div class="carousel-inner"></div>
                    <a class="carousel-control-prev" href="#${genre}Carousel" role="button" data-slide="prev">
                        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                        <span class="sr-only">Previous</span>
                    </a>
                    <a class="carousel-control-next" href="#${genre}Carousel" role="button" data-slide="next">
                        <span class="carousel-control-next-icon" aria-hidden="true"></span>
                        <span class="sr-only">Next</span>
                    </a>
                </div>
            `;
            
            const gridContainer = genreSection.querySelector('.carousel-inner');
            displayBookGroup(books, gridContainer);
            genreSectionsContainer.appendChild(genreSection);
        });
    }
}

function displayBookGroup(books, container) {
    if (!container) return;

    container.innerHTML = '';
    for (let i = 0; i < books.length; i += 4) {
        const slideBooks = books.slice(i, i + 4);
        const slide = document.createElement('div');
        slide.className = `carousel-item ${i === 0 ? 'active' : ''}`;

        const row = document.createElement('div');
        row.className = 'row book-row';

        slideBooks.forEach(book => {
            const bookHTML = `
                <div class="col-md-3">
                    <div class="book-card">
                        <img src="${book.coverImage || '/static/placeholder.jpg'}" 
                            alt="${book.title}" 
                            data-toggle="modal"                                               
                            data-target="#bookModal"
                            data-book-title="{{ book.title }}"
                            data-book-author="{{ book.author }}"
                            data-book-pages="{{ book.pages }}"
                            data-book-rating="{{ book.rating }}"
                            data-book-awards="{{ book.awards|default(0) }}"
                            data-book-cover="{{ book.coverImage }}"
                            data-book-description="{{book.description}}"
                            style="cursor: pointer;"
                            class="book-cover">
                        <div class="book-details">
                            <h6 class="book-title">${book.title}</h6>
                           
                        </div>
                    </div>
                </div>
            `;
            row.insertAdjacentHTML('beforeend', bookHTML);
        });

        slide.appendChild(row);
        container.appendChild(slide);
    }
}*/

function displayBookGroup(books, container) {
    if (!container) return;

    container.innerHTML = '';
    for (let i = 0; i < books.length; i += 4) {
        const slideBooks = books.slice(i, i + 4);
        const slide = document.createElement('div');
        slide.className = `carousel-item ${i === 0 ? 'active' : ''}`;

        const row = document.createElement('div');
        row.className = 'row book-row';

        slideBooks.forEach(book => {
            const bookHTML = `
                <div class="col-md-3">
                    <div class="book-card">
                        <img src="${book.coverImage || '/static/placeholder.jpg'}" 
                            alt="${book.title}" 
                            data-toggle="modal"                                               
                            data-target="#bookModal"
                            data-book-title="${book.title}"
                            data-book-author="${book.author}"
                            data-book-pages="${book.pages}"
                            data-book-rating="${book.rating}"
                            data-book-awards="${book.awards || 0}"
                            data-book-cover="${book.coverImage}"
                            data-book-description="${book.description}"
                            style="cursor: pointer;"
                            class="book-cover">
                        <div class="book-details">
                            <h6 class="book-title">${book.title}</h6>
                        </div>
                    </div>
                </div>
            `;
            row.insertAdjacentHTML('beforeend', bookHTML);
        });

        slide.appendChild(row);
        container.appendChild(slide);
    }
}

function displayRecommendations(recommendations) {
    console.log('Displaying multi-genre recommendations');
    
    // Display survey-based recommendations
    const surveyContainer = document.querySelector('#surveyBasedCarousel .carousel-inner');
    if (surveyContainer) {
        if (recommendations.survey_based && recommendations.survey_based.length > 0) {
            displayBookGroup(recommendations.survey_based, surveyContainer);
        } else {
            surveyContainer.innerHTML = '<div class="empty-message">No survey-based recommendations found</div>';
        }
    }

    // Display genre-based recommendations
    const genreSectionsContainer = document.getElementById('genreBasedSections');
    if (genreSectionsContainer) {
        genreSectionsContainer.innerHTML = ''; // Clear existing sections
        
        if (!recommendations.genre_based || Object.keys(recommendations.genre_based).length === 0) {
            genreSectionsContainer.innerHTML = '<div class="empty-message">No genre-based recommendations found</div>';
            return;
        }

        // Create a carousel for each genre
        Object.entries(recommendations.genre_based).forEach(([genre, books]) => {
            const genreSection = document.createElement('div');
            genreSection.className = 'recommendation-section';
            genreSection.innerHTML = `
                <h2>Based on Your Interest in ${genre}</h2>
                <div id="${genre}Carousel" class="carousel slide" data-ride="carousel" data-interval="false">
                    <div class="carousel-inner"></div>
                    <a class="carousel-control-prev" href="#${genre}Carousel" role="button" data-slide="prev">
                        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                        <span class="sr-only">Previous</span>
                    </a>
                    <a class="carousel-control-next" href="#${genre}Carousel" role="button" data-slide="next">
                        <span class="carousel-control-next-icon" aria-hidden="true"></span>
                        <span class="sr-only">Next</span>
                    </a>
                </div>
            `;
            
            const gridContainer = genreSection.querySelector('.carousel-inner');
            displayBookGroup(books, gridContainer);
            genreSectionsContainer.appendChild(genreSection);
        });
    }

    // Initialize all carousels with no auto-sliding
    $('.carousel').carousel({
        interval: false
    });
}



function formatRating(rating) {
    if (!rating) return 'No rating';
    const ratingNum = parseFloat(rating);
    const fullStars = Math.floor(ratingNum);
    const halfStar = ratingNum % 1 >= 0.5;
    const stars = '★'.repeat(fullStars) + (halfStar ? '½' : '') + '☆'.repeat(5 - Math.ceil(ratingNum));
    return `${stars} (${ratingNum.toFixed(1)})`;
}

function formatGenres(genres) {
    if (!genres) return '';
    if (Array.isArray(genres)) {
        return genres.slice(0, 3).join(', ') + (genres.length > 3 ? '...' : '');
    }
    return genres;
}

function formatAwards(awards) {
    if (!awards || awards.length === 0) return '';
    if (Array.isArray(awards)) {
        return awards.slice(0, 2).join(', ') + (awards.length > 2 ? '...' : '');
    }
    return awards;
}

$('#bookModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var modal = $(this);

    var title = button.data('book-title');
    var author = button.data('book-author');
    var pages = button.data('book-pages');
    var rating = button.data('book-rating');
    var awards = button.data('book-awards');
    var cover = button.data('book-cover');
    var description = button.data('book-description');

    modal.find('#modalBookTitle').text(title);
    modal.find('#modalBookAuthor').text(author);
    modal.find('#modalBookPages').text(pages);
    modal.find('#modalBookRating').text(rating);
    modal.find('#modalBookReviews').text(awards);
    modal.find('#modalBookDescription').text(description);
    modal.find('#modalBookCover').attr('src', cover);
});

// Initialize recommendations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const recommendations = JSON.parse(sessionStorage.getItem('recommendations'));
    if (recommendations) {
        displayRecommendations(recommendations);
    }
});
/* 
function displayRecommendations(recommendations) {
    console.log('Displaying recommendations');
    const container = document.getElementById('recommendationsList');
    if (!container) return;

    container.innerHTML = '';
    recommendations.forEach(book => {
        const bookCard = document.createElement('div');
        bookCard.className = 'book-card';
        bookCard.innerHTML = `
            <img src="${book.coverImage || '/static/placeholder-book.jpg'}" alt="${book.title}">
            <h3>${book.title}</h3>
            <div class="book-info">
                <p>Author: ${book.author}</p>
                <p>Rating: ${'★'.repeat(Math.round(book.rating))}</p>
                ${book.genres ? `<p>Genres: ${Array.isArray(book.genres) ? book.genres.join(', ') : book.genres}</p>` : ''}
            </div>
        `;
        container.appendChild(bookCard);
    });
} */