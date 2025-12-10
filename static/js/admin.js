// Buttons: approve or reject uploads
const actionButtons = document.querySelectorAll('.verify-btn');

actionButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const photoId = btn.getAttribute('data-id');
        const action = btn.getAttribute('data-action');

        // Confirm action
        if (!confirm(`Are you sure you want to ${action} this photo?`)) return;

        // Send action to backend
        fetch(`/verify_photo/${photoId}/${action}`, {
            method: 'POST'
        })
        .then(res => {
            if (res.ok) {
                // Remove card from page
                document.getElementById(`photo-${photoId}`).remove();
            }
        })
        .catch(err => {
            console.error("Error:", err);
            alert("Something went wrong.");
        });
    });
});
