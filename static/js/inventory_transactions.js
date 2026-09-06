document.addEventListener("DOMContentLoaded", function () {
    const transactionType = document.getElementById("transaction_type");
    const reason = document.getElementById("reason");

    if (transactionType && reason) {
        const reasonOptions = Array.from(reason.querySelectorAll("option[data-types]"));

        const updateReasonOptions = function () {
            const selectedType = transactionType.value;

            reason.value = "";
            reason.disabled = !selectedType;

            reasonOptions.forEach(function (option) {
                const allowedTypes = option.dataset.types.split(" ");
                const isAllowed = allowedTypes.includes(selectedType);

                option.hidden = !isAllowed;
                option.disabled = !isAllowed;
            });
        };

        transactionType.addEventListener("change", updateReasonOptions);
        updateReasonOptions();
    }

    const searchInput = document.getElementById("inventory-transactions-search");
    const searchEmpty = document.getElementById("inventory-transactions-search-empty");
    const countElement = document.querySelector(".inventory-transactions-count");

    if (!searchInput || !countElement) {
        return;
    }

    const rows = Array.from(document.querySelectorAll("tr[data-transaction-search]"));
    const totalCount = rows.length;

    const updateCountLabel = function (visibleCount) {
        countElement.textContent = `${visibleCount} ${visibleCount === 1 ? "Transaction" : "Transactions"}`;
    };

    updateCountLabel(totalCount);

    searchInput.addEventListener("input", function () {
        const query = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        rows.forEach(function (row) {
            const haystack = row.dataset.transactionSearch || "";
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
