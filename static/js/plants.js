const searchInput = document.getElementById('plantSearch');
const difficultyFilter = document.getElementById('difficultyFilter');
const plantCardsList = document.querySelectorAll('.plant-info-card');

// Search + filter function
function updatePlantList() {
    const query = searchInput.value.toLowerCase();
    const difficulty = difficultyFilter.value;

    plantCardsList.forEach(card => {
        const name = card.getAttribute('data-name').toLowerCase();
        const diff = card.getAttribute('data-difficulty');

        const matchesSearch = name.includes(query);
        const matchesDifficulty = difficulty === "all" || difficulty === diff;

        if (matchesSearch && matchesDifficulty) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// Event listeners
if (searchInput) {
    searchInput.addEventListener('input', updatePlantList);
}

if (difficultyFilter) {
    difficultyFilter.addEventListener('change', updatePlantList);
}
