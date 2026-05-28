// LoanWallet — main.js

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-8px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(function () { alert.remove(); }, 300);
        }, 5000);
    });
});

// Toggle sidebar for mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar) sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('open');
}

// Number formatting helper
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Animate count-up for stat values
function animateCountUp(element, endValue, duration) {
    const start = 0;
    const startTime = performance.now();
    const isDecimal = endValue.toString().includes('.');
    const numericEnd = parseFloat(endValue.replace(/[^0-9.]/g, '')) || 0;
    const prefix = endValue.startsWith('$') ? '$' : '';

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = numericEnd * eased;
        element.textContent = prefix + current.toLocaleString('en-US', {
            minimumFractionDigits: isDecimal ? 2 : 0,
            maximumFractionDigits: isDecimal ? 2 : 0
        });
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

document.addEventListener('DOMContentLoaded', function () {
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(function (el) {
        const text = el.textContent.trim();
        if (text.startsWith('$') && !isNaN(parseFloat(text.replace(/[$,]/g, '')))) {
            animateCountUp(el, text, 800);
        }
    });
});

// Close modals on Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(function (m) {
            m.classList.remove('active');
        });
    }
});
