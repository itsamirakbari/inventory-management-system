document.addEventListener("DOMContentLoaded", function () {
        const searchInput = document.getElementById("invoices-search");
        const searchEmpty = document.getElementById("invoices-search-empty");
        const countElement = document.querySelector(".invoices-count");

        if (!searchInput || !countElement) {
            return;
        }

        const rows = Array.from(document.querySelectorAll("tr[data-invoice-search]"));

        const updateCountLabel = function (visibleCount) {
            countElement.textContent = `${visibleCount} ${visibleCount === 1 ? "Invoice" : "Invoices"}`;
        };

        updateCountLabel(rows.length);

        searchInput.addEventListener("input", function () {
            const query = searchInput.value.trim().toLowerCase();
            let visibleCount = 0;

            rows.forEach(function (row) {
                const haystack = row.dataset.invoiceSearch || "";
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

    function confirmInvoiceStatusChange(invoiceNumber, currentStatus) {
        const action = currentStatus === "open" ? "mark as paid" : "reopen";

        return window.confirm(
            `Do you want to ${action} invoice "${invoiceNumber}"?`
        );
    }