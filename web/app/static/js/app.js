document.addEventListener("DOMContentLoaded", function () {

    // ===== INGREDIENT CHIPS =====
    function createChip(text, parent) {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = text + " ��";
        chip.onclick = () => chip.remove();
        parent.appendChild(chip);
    }

    const includeInput = document.getElementById("include-input");
    const includeList = document.getElementById("include-list");
    const excludeInput = document.getElementById("exclude-input");
    const excludeList = document.getElementById("exclude-list");

    if (includeInput) {
        includeInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && includeInput.value.trim()) {
                createChip(includeInput.value.trim(), includeList);
                includeInput.value = "";
            }
        });
    }

    if (excludeInput) {
        excludeInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && excludeInput.value.trim()) {
                createChip(excludeInput.value.trim(), excludeList);
                excludeInput.value = "";
            }
        });
    }

    // ===== SUBMIT TO BACKEND =====
    const submitBtn = document.getElementById("submit-btn");
    if (submitBtn) {
        submitBtn.onclick = async () => {
            const include = Array.from(includeList.children).map(c => c.textContent.replace(" ��", ""));
            const exclude = Array.from(excludeList.children).map(c => c.textContent.replace(" ��", ""));

            const payload = {
                include,
                exclude,
                dont_have,
                tools_have,
                cuisine: document.getElementById("cuisine").value,
                taste: document.getElementById("taste").value,
                diet: document.getElementById("diet").value
            };

            const res = await axios.post("/api/recommend", payload);
            const data = res.data;

            const results = document.getElementById("results");
            results.innerHTML = "";

            data.best_recipes.forEach(r => {
                const div = document.createElement("div");
                div.innerHTML = `
                    <h4>${r.name}</h4>
                    <button class="btn" onclick="window.location='/result?recipe_id=${r._id}'">Open</button>
                `;
                results.appendChild(div);
            });
        };
    }

    // ===== INGREDIENT REPLACEMENT =====
    const ingredientButtons = document.querySelectorAll(".replace-btn");
    ingredientButtons.forEach(btn => {
        btn.onclick = async () => {
            const currentIngredient = btn.dataset.from;
            const recipeId = btn.dataset.recipe;

            const newIng = prompt(`Replace "${currentIngredient}" with:`);
            if (!newIng) return;

            const res = await axios.post("/api/replace", {
                recipe_id: recipeId,
                from: currentIngredient,
                to: newIng
            });

            alert("Ingredient replaced!");
            location.reload();
        };
    });

});
