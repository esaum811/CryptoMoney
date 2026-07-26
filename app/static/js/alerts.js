function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('liveToast');
    if (!toastEl) return;
    const toastBody = document.getElementById('toastBody');
    const toastTitle = document.getElementById('toastTitle');
    const toastIcon = document.getElementById('toastIcon');
    
    toastTitle.innerText = title;
    toastBody.innerText = message;
    
    toastIcon.className = 'bi me-2';
    if (type === 'success') {
        toastIcon.classList.add('bi-check-circle-fill', 'text-success');
    } else if (type === 'danger') {
        toastIcon.classList.add('bi-exclamation-triangle-fill', 'text-danger');
    } else if (type === 'warning') {
        toastIcon.classList.add('bi-exclamation-circle-fill', 'text-warning');
    } else {
        toastIcon.classList.add('bi-info-circle-fill', 'text-info');
    }

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

function openAlertModal(cryptoName) {
    document.getElementById('alertSymbol').value = cryptoName;
    document.getElementById('alertSymbolDisplay').innerText = cryptoName;
    
    fetch(`/symbol_info?symbol=${cryptoName}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('alertCurrentPrice').innerText = `$${parseFloat(data.current_price).toFixed(2)}`;
            const modal = new bootstrap.Modal(document.getElementById('alertModal'));
            modal.show();
        })
        .catch(err => {
            console.error(err);
            showToast('Error', 'Failed to fetch current price', 'danger');
        });
}

function submitAlert() {
    const symbol = document.getElementById('alertSymbol').value;
    const alertType = document.getElementById('alertType').value;
    const targetPrice = parseFloat(document.getElementById('alertPrice').value);

    if (!targetPrice || targetPrice <= 0) {
        showToast('Error', 'Please enter a valid price', 'danger');
        return;
    }

    // Map the modal's single-price design to the backend's lower/upper limit model
    let lower = 0;
    let upper = 999999999;
    if (alertType === 'UPPER') {
        upper = targetPrice;
    } else {
        lower = targetPrice;
    }

    fetch('/add_price_alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            crypto_name: symbol,
            lower_limit: lower,
            upper_limit: upper
        })
    })
    .then(res => res.json())
    .then(data => {
        showToast('Success', data.message || 'Alert created', 'success');
        const modalEl = document.getElementById('alertModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        // Clear the input
        document.getElementById('alertPrice').value = '';
    })
    .catch(err => {
        console.error(err);
        showToast('Error', 'Server error', 'danger');
    });
}

async function checkForAlerts() {
    try {
        const response = await fetch('/check_alerts');
        if (response.ok) {
            const data = await response.json();
            if (data.triggered_alerts && data.triggered_alerts.length > 0) {
                data.triggered_alerts.forEach(symbol => {
                    showToast('Alert Triggered!', `${symbol} crossed a price limit!`, 'warning');
                });
            }
        }
    } catch (e) {
        console.error('Error checking alerts:', e);
    }
}

function removeFromWatchlist(cryptoName) {
    if (confirm(`Remove ${cryptoName} from watchlist?`)) {
        fetch(`/remove_from_watchlist/${cryptoName}`, {
            method: 'POST'
        })
        .then(res => res.json())
        .then(data => {
            const item = document.getElementById(`watchlist-item-${cryptoName}`);
            if (item) item.remove();
            showToast('Removed', data.message || `${cryptoName} removed`, 'success');
        })
        .catch(err => console.error(err));
    }
}

function addToWatchlist() {
    const select = document.getElementById('crypto-select');
    const searchInput = document.getElementById('crypto-search');
    let symbol = select ? select.value : '';

    if (!symbol && select && select.options.length > 1) {
        for (let i = 0; i < select.options.length; i++) {
            if (!select.options[i].disabled && select.options[i].value) {
                symbol = select.options[i].value;
                select.selectedIndex = i;
                break;
            }
        }
    }

    if (!symbol) {
        showToast('Info', 'Please select a cryptocurrency', 'warning');
        return;
    }

    
    const formData = new FormData();
    formData.append('crypto', symbol);
    
    fetch('/add_to_watchlist', {
        method: 'POST',
        body: formData
    })
    .then(res => {
        if (res.redirected) {
            window.location.reload();
            return;
        }
        return res.text();
    })
    .then(() => {
        window.location.reload();
    })
    .catch(err => console.error(err));
}

function togglePortfolioEmail() {
    const isChecked = document.getElementById('portfolioEmailToggle').checked;
    fetch('/sign_up_for_portfolio_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sign_up: isChecked })
    })
    .then(res => res.json())
    .then(data => {
        showToast('Preferences', data.message || 'Updated', 'success');
    })
    .catch(err => console.error(err));
}

function getUserEmailPreference() {
    fetch('/check_portfolio_email')
    .then(res => {
        if (!res.ok) return;
        return res.json();
    })
    .then(data => {
        if (data && data.value !== undefined) {
            const toggle = document.getElementById('portfolioEmailToggle');
            if (toggle) toggle.checked = data.value;
        }
    })
    .catch(err => console.error(err));
}
