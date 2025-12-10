// Show preview of uploaded image before submitting
const fileInputs = document.querySelectorAll('.upload-input');

fileInputs.forEach(input => {
    input.addEventListener('change', function () {
        const previewId = this.getAttribute('data-preview');
        const previewImage = document.getElementById(previewId);

        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
            };
            reader.readAsDataURL(this.files[0]);
        }
    });
});
