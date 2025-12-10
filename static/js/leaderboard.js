const rows = document.querySelectorAll('.leaderboard-row');

// Animate rows on load
rows.forEach((row, index) => {
    setTimeout(() => {
        row.classList.add('slide-in');
    }, index * 80);
});

// Sorting
const sortSelect = document.getElementById('sortLeaderboard');

if (sortSelect) {
    sortSelect.addEventListener('change', () => {
        const option = sortSelect.value;
        const table = document.getElementById('leaderboardTable');
        const rowsArray = Array.from(rows);

        rowsArray.sort((a, b) => {
            let aVal = Number(a.getAttribute(`data-${option}`));
            let bVal = Number(b.getAttribute(`data-${option}`));
            return bVal - aVal;
        });

        rowsArray.forEach(row => table.appendChild(row));
    });
}
