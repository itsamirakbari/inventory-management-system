document.addEventListener("DOMContentLoaded", function () {
        const searchInput = document.getElementById("categories-search");
        const searchEmpty = document.getElementById("categories-search-empty");
        const countElement = document.querySelector(".categories-count");

        if (!searchInput || !countElement) {
            return;
        }

        const rows = Array.from(document.querySelectorAll("tr[data-category-search]"));
        const totalCount = rows.length;

        const updateCountLabel = function (visibleCount) {
            countElement.textContent = `${visibleCount} ${visibleCount === 1 ? "Category" : "Categories"}`;
        };

        updateCountLabel(totalCount);

        searchInput.addEventListener("input", function () {
            const query = searchInput.value.trim().toLowerCase();
            let visibleCount = 0;

            rows.forEach(function (row) {
                const haystack = row.dataset.categorySearch || "";
                const matches = haystack.includes(query);
                row.style.display = matches ? "" : "none";

                if (matches) {
                    visibleCount += 1;
                }
            });

            updateCountLabel(visibleCount);

            if (searchEmpty) {
                searchEmpty.hidden = visibleCount !== 0;
            }
        });
    });
