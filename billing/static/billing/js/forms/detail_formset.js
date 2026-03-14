document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-item-formset]').forEach(function (formsetSection) {
        initializeDetailFormset(formsetSection);
    });
});

function initializeDetailFormset(formsetSection) {
    const cards = Array.from(formsetSection.querySelectorAll('[data-item-form-card]'));
    const addButton = formsetSection.querySelector('[data-formset-add]');
    const countLabel = formsetSection.querySelector('[data-formset-count]');
    const subtotalLabel = formsetSection.querySelector('[data-formset-subtotal]');
    const taxRateLabel = formsetSection.querySelector('[data-formset-tax-rate]');
    const taxAmountLabel = formsetSection.querySelector('[data-formset-tax-amount]');
    const totalAmountLabel = formsetSection.querySelector('[data-formset-total-amount]');
    const taxRateInput = document.getElementById('id_tax_rate');
    const currencyInput = document.getElementById('id_currency');
    const maxItems = Number(formsetSection.dataset.maxItems || cards.length || 0);

    const isVisible = (card) => !card.classList.contains('hidden');
    const visibleCards = () => cards.filter(isVisible);

    const getDeleteInput = (card) => card.querySelector('input[name$="-DELETE"]');
    const getVisibilityInput = (card) => card.querySelector('[data-form-visibility]');
    const getDisplayOrderInput = (card) => card.querySelector('input[name$="-display_order"]');
    const getQuantityInput = (card) => card.querySelector('input[name$="-quantity"]');
    const getUnitPriceInput = (card) => card.querySelector('input[name$="-unit_price"]');
    const getLineTotalLabel = (card) => card.querySelector('[data-line-total]');
    const getRemoveButton = (card) => card.querySelector('[data-formset-remove]');
    const getEditableFields = (card) => Array.from(card.querySelectorAll('input, textarea, select')).filter((element) => {
        const name = element.name || '';
        const type = (element.type || '').toLowerCase();
        return name && !name.endsWith('-id') && !name.endsWith('-DELETE') && type !== 'hidden';
    });

    const getCurrencyCode = () => String(currencyInput?.value || 'JPY').toUpperCase();

    const parseAmount = (value) => {
        const normalized = String(value || '').replace(/,/g, '');
        const parsed = Number(normalized);
        return Number.isFinite(parsed) ? parsed : 0;
    };

    const roundAmount = (value) => {
        if (getCurrencyCode() === 'JPY') {
            return Math.round(value);
        }
        return Math.round(value * 100) / 100;
    };

    const formatAmount = (value) => {
        const currency = getCurrencyCode();
        const rounded = roundAmount(value);
        const digits = currency === 'JPY' ? 0 : 2;
        const suffix = currency === 'JPY' ? ' 円' : ' ' + currency;
        return rounded.toLocaleString('ja-JP', {
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        }) + suffix;
    };

    const clearCard = (card) => {
        getEditableFields(card).forEach((element) => {
            const tagName = element.tagName.toLowerCase();
            const type = (element.type || '').toLowerCase();

            if (tagName === 'select') {
                Array.from(element.options).forEach((option) => {
                    option.selected = option.defaultSelected;
                });
                if (element.selectedIndex < 0 && element.options.length > 0) {
                    element.selectedIndex = 0;
                }
                return;
            }

            if (type === 'checkbox' || type === 'radio') {
                element.checked = element.defaultChecked;
                return;
            }

            element.value = element.defaultValue;
        });

        const deleteInput = getDeleteInput(card);
        if (deleteInput) {
            deleteInput.checked = false;
        }
    };

    const calculateLineTotal = (card) => {
        if (!isVisible(card)) {
            return 0;
        }
        const deleteInput = getDeleteInput(card);
        if (deleteInput && deleteInput.checked) {
            return 0;
        }
        const quantity = parseAmount(getQuantityInput(card)?.value);
        const unitPrice = parseAmount(getUnitPriceInput(card)?.value);
        return roundAmount(quantity * unitPrice);
    };

    const updateAmounts = () => {
        cards.forEach((card) => {
            const lineTotalLabel = getLineTotalLabel(card);
            if (lineTotalLabel) {
                lineTotalLabel.textContent = formatAmount(calculateLineTotal(card));
            }
        });

        const subtotal = visibleCards().reduce((sum, card) => sum + calculateLineTotal(card), 0);
        const taxRate = parseAmount(taxRateInput?.value);
        const taxAmount = roundAmount(subtotal * (taxRate / 100));
        const totalAmount = roundAmount(subtotal + taxAmount);

        if (subtotalLabel) {
            subtotalLabel.textContent = formatAmount(subtotal);
        }
        if (taxRateLabel) {
            taxRateLabel.textContent = taxRate.toLocaleString('ja-JP', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            });
        }
        if (taxAmountLabel) {
            taxAmountLabel.textContent = formatAmount(taxAmount);
        }
        if (totalAmountLabel) {
            totalAmountLabel.textContent = formatAmount(totalAmount);
        }
    };

    const updateFormsetState = () => {
        const activeCards = visibleCards();

        activeCards.forEach((card, index) => {
            const number = index + 1;
            const title = card.querySelector('[data-form-row-title]');
            const displayOrderInput = getDisplayOrderInput(card);
            const visibilityInput = getVisibilityInput(card);

            if (title) {
                title.textContent = '明細 ' + number;
            }
            if (displayOrderInput) {
                displayOrderInput.value = String(number);
            }
            if (visibilityInput) {
                visibilityInput.value = '1';
            }
        });

        cards.filter((card) => !isVisible(card)).forEach((card) => {
            const visibilityInput = getVisibilityInput(card);
            if (visibilityInput) {
                visibilityInput.value = '0';
            }
        });

        if (countLabel) {
            countLabel.textContent = activeCards.length + ' / ' + maxItems + ' 件を表示中';
        }

        if (addButton) {
            const reachedLimit = activeCards.length >= maxItems;
            addButton.disabled = reachedLimit;
            addButton.classList.toggle('opacity-40', reachedLimit);
            addButton.classList.toggle('pointer-events-none', reachedLimit);
        }

        cards.forEach((card) => {
            const removeButton = getRemoveButton(card);
            if (!removeButton) {
                return;
            }
            const preventHide = activeCards.length <= 1 && isVisible(card);
            removeButton.disabled = preventHide;
            removeButton.classList.toggle('opacity-40', preventHide);
            removeButton.classList.toggle('pointer-events-none', preventHide);
        });

        updateAmounts();
    };

    const showCard = (card) => {
        const deleteInput = getDeleteInput(card);
        const visibilityInput = getVisibilityInput(card);
        if (deleteInput) {
            deleteInput.checked = false;
        }
        if (visibilityInput) {
            visibilityInput.value = '1';
        }
        card.classList.remove('hidden');
        updateFormsetState();
    };

    const hideCard = (card) => {
        if (visibleCards().length <= 1 && isVisible(card)) {
            return;
        }

        const visibilityInput = getVisibilityInput(card);
        if (visibilityInput) {
            visibilityInput.value = '0';
        }

        if (card.dataset.existing === 'true') {
            const deleteInput = getDeleteInput(card);
            if (deleteInput) {
                deleteInput.checked = true;
            }
        } else {
            clearCard(card);
        }

        card.classList.add('hidden');
        updateFormsetState();
    };

    cards.forEach((card) => {
        const removeButton = getRemoveButton(card);
        if (removeButton) {
            removeButton.addEventListener('click', function () {
                hideCard(card);
            });
        }

        [getQuantityInput(card), getUnitPriceInput(card)].forEach((input) => {
            if (input) {
                input.addEventListener('input', updateAmounts);
            }
        });
    });

    if (taxRateInput) {
        taxRateInput.addEventListener('input', updateAmounts);
    }
    if (currencyInput) {
        currencyInput.addEventListener('input', updateAmounts);
        currencyInput.addEventListener('change', updateAmounts);
    }

    if (addButton) {
        addButton.addEventListener('click', function () {
            const nextHiddenCard = cards.find((card) => !isVisible(card));
            if (nextHiddenCard) {
                showCard(nextHiddenCard);
            }
        });
    }

    updateFormsetState();
}

