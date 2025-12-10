// ----------------------------------------------------
// 🌱 DASHBOARD SEARCH BAR (below "Let's Start")
// ----------------------------------------------------
const searchForm = document.getElementById("plantSearchForm");
const plantInfoBox = document.getElementById("plant-info-output");
const uploadForm = document.getElementById("uploadCustomForm");

if (searchForm) {
    searchForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // prevent normal form submission

        const query = document.getElementById("plantNameInput").value.trim();
        if (!query) return;

        plantInfoBox.innerHTML = `<p class="text-gray-600">Searching...</p>`;

        try {
            const response = await fetch('/get_plant_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plant_name: query })
            });

            const data = await response.json();

            if (data.error) {
                plantInfoBox.innerHTML = `<p class="text-red-600">${data.error}</p>`;
                uploadForm.classList.add("hidden");
                return;
            }

            // DISPLAY PLANT INFO BELOW DASHBOARD SEARCH
            plantInfoBox.innerHTML = `
                <div class="bg-white rounded-xl p-5 shadow">
                    <h3 class="text-2xl font-semibold mb-2">${data.title}</h3>
                    <p class="text-gray-600 mb-3">${data.description}</p>
                    <h4 class="font-semibold text-green-700">Care Instructions:</h4>
                    <p>${data.care}</p>
                </div>
            `;

            // SHOW UPLOAD FORM
            uploadForm.classList.remove("hidden");
            document.getElementById("customPlantName").value = data.title;

            // Scroll to results
            plantInfoBox.scrollIntoView({ behavior: "smooth" });

        } catch (err) {
            plantInfoBox.innerHTML = `<p class="text-red-600">Something went wrong.</p>`;
            uploadForm.classList.add("hidden");
        }
    });
}

// ----------------------------------------------------
// 📸 PREVIEW UPLOADED IMAGE
// ----------------------------------------------------
const fileInput = document.getElementById("customPlantPhoto");
const previewImg = document.getElementById("previewImage");

if (fileInput) {
    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = () => {
            previewImg.src = reader.result;
            previewImg.classList.remove("hidden");
        };
        reader.readAsDataURL(file);
    });
}