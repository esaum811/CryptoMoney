function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('liveToast');
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
    
    // Fetch current price
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
    const targetPrice = document.getElementById('alertPrice').value;

    const formData = new FormData();
    formData.append('symbol', symbol);
    formData.append('alert_type', alertType);
    formData.append('target_price', targetPrice);

    fetch('/add_price_alert', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast('Success', 'Alert created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('alertModal')).hide();
        } else {
            showToast('Error', data.message || 'Failed to create alert', 'danger');
        }
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
            if (data.triggered && data.triggered.length > 0) {
                data.triggered.forEach(alert => {
                    showToast('Alert Triggered!', `${alert.symbol} crossed ${alert.alert_type} limit of $${alert.limit_value}`, 'warning');
                });
            }
        }
    } catch (e) {
        console.error('Error checking alerts:', e);
    }
}

function removeFromWatchlist(symbol) {
    if (confirm(`Remove ${symbol} from watchlist?`)) {
        fetch(`/remove_from_watchlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `crypto_name=${symbol}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`watchlist-item-${symbol}`).remove();
                showToast('Removed', `${symbol} removed from watchlist`, 'success');
            }
        });
    }
}

function addToWatchlist() {
    const symbol = document.getElementById('crypto-select').value;
    if (!symbol) return;
    
    // Fallback logic assuming standard form submission or fetch if endpoint provided
    showToast('Info', 'Add to watchlist functionality requires endpoint setup', 'info');
}

function togglePortfolioEmail() {
    const isChecked = document.getElementById('portfolioEmailToggle').checked;
    fetch('/toggle_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `enabled=${isChecked}`
    })
    .then(res => res.json())
    .then(data => {
        showToast('Preferences Updated', data.message || `Email alerts ${isChecked ? 'enabled' : 'disabled'}`, 'success');
    });
}

function getUserEmailPreference() {
    fetch('/check_email_pref')
    .then(res => res.json())
    .then(data => {
        if (data.enabled !== undefined) {
            document.getElementById('portfolioEmailToggle').checked = data.enabled;
        }
    });
}
