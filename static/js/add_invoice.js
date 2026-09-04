document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("add-invoice-form");

    if (!form) {
        return;
    }

    const customerSelect = document.getElementById("customer_id");
    const invoiceDateInput = document.getElementById("invoice_date");
    const itemsBody = document.getElementById("invoice-items-body");
    const itemTemplate = document.getElementById("invoice-item-template");
    const addItemButton = document.getElementById("invoice-add-item");
    const itemsCount = document.getElementById("invoice-items-count");
    const grandTotal = document.getElementById("invoice-grand-total");

    const customerName = document.getElementById("invoice-customer-name");
    const customerContact = document.getElementById("invoice-customer-contact");
    const customerAddress = document.getElementById("invoice-customer-address");
    const customerLocation = document.getElementById("invoice-customer-location");
    const customerCommunication = document.getElementById("invoice-customer-communication");

    const formatCurrency = function (amount) {
        return new Intl.NumberFormat("de-DE", {
            style: "currency",
            currency: "EUR"
        }).format(amount);
    };

    const joinAvailableValues = function (values, separator) {
        const availableValues = values.filter(function (value) {
            return value && value.trim();
        });

        return availableValues.length ? availableValues.join(separator) : "—";
    };

    const updateCustomerPreview = function () {
        const selectedOption = customerSelect.options[customerSelect.selectedIndex];

        if (!selectedOption || !selectedOption.value) {
            customerName.textContent = "No customer selected";
            customerContact.textContent = "—";
            customerAddress.textContent = "—";
            customerLocation.textContent = "—";
            customerCommunication.textContent = "—";
            return;
        }

        customerName.textContent = selectedOption.dataset.name || selectedOption.textContent.trim();
        customerContact.textContent = selectedOption.dataset.contact || "—";
        customerAddress.textContent = joinAvailableValues([
            selectedOption.dataset.street,
            selectedOption.dataset.houseNumber
        ], " ");
        customerLocation.textContent = joinAvailableValues([
            selectedOption.dataset.postalCode,
            selectedOption.dataset.city,
            selectedOption.dataset.country
        ], " · ");
        customerCommunication.textContent = joinAvailableValues([
            selectedOption.dataset.email,
            selectedOption.dataset.phone
        ], " · ");
    };

    const updateGrandTotal = function () {
        if (!itemsBody) {
            return;
        }

        let totalQuantity = 0;
        let totalAmount = 0;

        itemsBody.querySelectorAll("[data-invoice-item-row]").forEach(function (row) {
            const productSelect = row.querySelector(".invoice-product-select");
            const quantityInput = row.querySelector(".invoice-item-quantity");
            const selectedOption = productSelect.options[productSelect.selectedIndex];

            if (!selectedOption || !selectedOption.value) {
                return;
            }

            const quantity = Number.parseInt(quantityInput.value, 10) || 0;
            const price = Number.parseFloat(selectedOption.dataset.price) || 0;

            totalQuantity += quantity;
            totalAmount += price * quantity;
        });

        itemsCount.textContent = totalQuantity;
        grandTotal.textContent = formatCurrency(totalAmount);
    };

    const updateRemoveButtons = function () {
        if (!itemsBody) {
            return;
        }

        itemsBody.querySelectorAll("[data-invoice-item-row]").forEach(function (row) {
            const removeButton = row.querySelector(".invoice-remove-item-btn");
            removeButton.disabled = false;
        });
    };

    const validateProductSelections = function () {
        if (!itemsBody) {
            return;
        }

        const selectedProductIds = new Set();

        itemsBody.querySelectorAll(".invoice-product-select").forEach(function (productSelect) {
            productSelect.setCustomValidity("");

            if (!productSelect.value) {
                return;
            }

            if (selectedProductIds.has(productSelect.value)) {
                productSelect.setCustomValidity("Please select each product only once.");
            } else {
                selectedProductIds.add(productSelect.value);
            }
        });
    };

    const updateItemRow = function (row) {
        const productSelect = row.querySelector(".invoice-product-select");
        const quantityInput = row.querySelector(".invoice-item-quantity");
        const sku = row.querySelector(".invoice-item-sku");
        const stock = row.querySelector(".invoice-item-stock");
        const price = row.querySelector(".invoice-item-price");
        const lineTotal = row.querySelector(".invoice-item-total");
        const selectedOption = productSelect.options[productSelect.selectedIndex];

        quantityInput.setCustomValidity("");

        if (!selectedOption || !selectedOption.value) {
            sku.textContent = "—";
            stock.textContent = "—";
            price.textContent = formatCurrency(0);
            lineTotal.textContent = formatCurrency(0);
            quantityInput.removeAttribute("max");
            validateProductSelections();
            updateGrandTotal();
            return;
        }

        const availableStock = Number.parseInt(selectedOption.dataset.stock, 10) || 0;
        const unitPrice = Number.parseFloat(selectedOption.dataset.price) || 0;
        const quantity = Number.parseInt(quantityInput.value, 10) || 0;

        sku.textContent = selectedOption.dataset.sku || "—";
        stock.textContent = availableStock;
        price.textContent = formatCurrency(unitPrice);
        lineTotal.textContent = formatCurrency(unitPrice * quantity);
        quantityInput.max = availableStock;

        if (quantity > availableStock) {
            quantityInput.setCustomValidity(`Only ${availableStock} item(s) are available.`);
        }

        validateProductSelections();
        updateGrandTotal();
    };

    const connectItemRow = function (row) {
        const productSelect = row.querySelector(".invoice-product-select");
        const quantityInput = row.querySelector(".invoice-item-quantity");
        const removeButton = row.querySelector(".invoice-remove-item-btn");

        productSelect.addEventListener("change", function () {
            updateItemRow(row);
        });

        quantityInput.addEventListener("input", function () {
            updateItemRow(row);
        });

        removeButton.addEventListener("click", function () {
            const rows = itemsBody.querySelectorAll("[data-invoice-item-row]");

            if (rows.length === 1) {
                productSelect.value = "";
                quantityInput.value = "1";
                updateItemRow(row);
            } else {
                row.remove();
            }

            validateProductSelections();
            updateRemoveButtons();
            updateGrandTotal();
        });

        updateItemRow(row);
    };

    if (invoiceDateInput && !invoiceDateInput.value) {
        const today = new Date();
        const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000);
        invoiceDateInput.value = localDate.toISOString().slice(0, 10);
    }

    if (customerSelect) {
        customerSelect.addEventListener("change", updateCustomerPreview);
        updateCustomerPreview();
    }

    if (itemsBody) {
        itemsBody.querySelectorAll("[data-invoice-item-row]").forEach(connectItemRow);
        updateRemoveButtons();
    }

    if (addItemButton && itemsBody && itemTemplate) {
        addItemButton.addEventListener("click", function () {
            const newRow = itemTemplate.content.firstElementChild.cloneNode(true);
            itemsBody.appendChild(newRow);
            connectItemRow(newRow);
            updateRemoveButtons();
        });
    }

    form.addEventListener("submit", function (event) {
        validateProductSelections();

        if (!form.checkValidity()) {
            event.preventDefault();
            form.reportValidity();
        }
    });
});
