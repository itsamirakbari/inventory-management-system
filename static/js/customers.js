function confirmCustomerStatusChange(customerName, isCurrentlyActive) {
        const nextStatus = isCurrentlyActive ? "inactive" : "active";
        return confirm(`Are you sure you want to set customer "${customerName}" to ${nextStatus}?`);
    }

    document.addEventListener("DOMContentLoaded", function () {
        const searchInput = document.getElementById("customers-search");
        const searchEmpty = document.getElementById("customers-search-empty");
        const countElement = document.querySelector(".customers-count");

        if (!searchInput || !countElement) {
            return;
        }

        const rows = Array.from(document.querySelectorAll("tr[data-customer-search]"));
        const totalCount = rows.length;

        const updateCountLabel = function (visibleCount) {
            countElement.textContent = `${visibleCount} ${visibleCount === 1 ? "Customer" : "Customers"}`;
        };

        updateCountLabel(totalCount);

        searchInput.addEventListener("input", function () {
            const query = searchInput.value.trim().toLowerCase();
            let visibleCount = 0;

            rows.forEach(function (row) {
                const haystack = row.dataset.customerSearch || "";
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