// --- NAVIGATION & SCREENS ---
function showScreen(screenId) {
    document.getElementById('main-app').style.display = 'none';
    document.querySelectorAll('.tool-screen').forEach(screen => {
        screen.style.display = 'none';
    });
    document.getElementById(screenId).style.display = 'block';
    
    if (screenId === 'asian-screen') {
        updateAsianSessionCountdown();
        loadSavedAsianRange();
    }
    if (screenId === 'journal-screen') {
        loadTrades();
    }
}

function goBack() {
    document.querySelectorAll('.tool-screen').forEach(screen => {
        screen.style.display = 'none';
    });
    document.getElementById('main-app').style.display = 'block';
}

// --- PREMIUM ACCESS ---
function checkPremiumAccess(tool) {
    const isPremium = localStorage.getItem('limitless_premium') === 'true';
    if (isPremium) {
        showScreen(tool + '-screen');
    } else {
        document.getElementById('premium-modal').style.display = 'flex';
    }
}

function closePremiumModal() {
    document.getElementById('premium-modal').style.display = 'none';
    document.getElementById('passcode-input').value = '';
    document.getElementById('passcode-error').style.display = 'none';
}

function verifyPasscode() {
    const input = document.getElementById('passcode-input').value;
    if (input === 'LIMITLESS2026') {
        localStorage.setItem('limitless_premium', 'true');
        closePremiumModal();
        alert('Welcome to the Limitless Journeys Club!');
    } else {
        document.getElementById('passcode-error').style.display = 'block';
    }
}

// --- FIBONACCI CALCULATOR ---
let currentDirection = 'long';

function setDirection(dir) {
    currentDirection = dir;
    document.getElementById('btn-long').classList.toggle('active', dir === 'long');
    document.getElementById('btn-short').classList.toggle('active', dir === 'short');
}

function calculateFib() {
    const high = parseFloat(document.getElementById('fib-high').value);
    const low = parseFloat(document.getElementById('fib-low').value);

    if (isNaN(high) || isNaN(low)) {
        alert('Please enter valid Swing High and Swing Low prices.');
        return;
    }

    const diff = high - low;
    const lvl0 = currentDirection === 'long' ? low : high;
    const lvl100 = currentDirection === 'long' ? high : low;

    document.getElementById('lvl-0').innerText = lvl0.toFixed(2);
    document.getElementById('lvl-50').innerText = (lvl0 + diff * 0.5).toFixed(2);
    document.getElementById('lvl-618').innerText = (lvl0 + diff * 0.618).toFixed(2);
    document.getElementById('lvl-718').innerText = (lvl0 + diff * 0.718).toFixed(2);
    document.getElementById('lvl-100').innerText = lvl100.toFixed(2);

    document.getElementById('fib-results').style.display = 'block';
}

// --- ASIAN SESSION TRACKER (FIXED FOR 7 PM - 12 AM AST) ---
function updateAsianSessionCountdown() {
    const now = new Date();
    const astOffset = -4;
    const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
    const astTime = new Date(utcTime + (3600000 * astOffset));
    
    const astHours = astTime.getUTCHours();
    const astMinutes = astTime.getUTCMinutes();
    const astSeconds = astTime.getUTCSeconds();

    const statusEl = document.getElementById('session-status');
    const timerEl = document.getElementById('countdown-timer');
    const isSessionOpen = astHours >= 19;

    if (isSessionOpen) {
        statusEl.innerText = "🟢 ASIAN SESSION IS OPEN";
        statusEl.style.color = "#00FF00";
        let targetHours = 24; 
        let diffHours = targetHours - astHours - 1;
        let diffMinutes = 59 - astMinutes;
        let diffSeconds = 59 - astSeconds;
        timerEl.innerText = `${String(diffHours).padStart(2, '0')}:${String(diffMinutes).padStart(2, '0')}:${String(diffSeconds).padStart(2, '0')}`;
    } else {
        statusEl.innerText = "🔴 ASIAN SESSION IS CLOSED";
        statusEl.style.color = "#FF3D00";
        let targetHours = 19;
        let diffHours = targetHours - astHours - 1;
        let diffMinutes = 59 - astMinutes;
        let diffSeconds = 59 - astSeconds;
        if (diffHours < 0) diffHours = 0;
        timerEl.innerText = `${String(diffHours).padStart(2, '0')}:${String(diffMinutes).padStart(2, '0')}:${String(diffSeconds).padStart(2, '0')}`;
    }
}

setInterval(updateAsianSessionCountdown, 1000);

function saveAsianRange() {
    const high = document.getElementById('asian-high').value;
    const low = document.getElementById('asian-low').value;
    if (!high || !low) { alert('Please enter both High and Low prices.'); return; }
    const range = (parseFloat(high) - parseFloat(low)).toFixed(2);
    localStorage.setItem('asian_high', high);
    localStorage.setItem('asian_low', low);
    localStorage.setItem('asian_range', range);
    loadSavedAsianRange();
}

function loadSavedAsianRange() {
    const high = localStorage.getItem('asian_high');
    const low = localStorage.getItem('asian_low');
    const range = localStorage.getItem('asian_range');
    if (high && low) {
        document.getElementById('saved-high').innerText = high;
        document.getElementById('saved-low').innerText = low;
        document.getElementById('saved-range').innerText = range;
        document.getElementById('asian-saved').style.display = 'block';
    } else {
        document.getElementById('asian-saved').style.display = 'none';
    }
}

function clearAsianRange() {
    localStorage.removeItem('asian_high');
    localStorage.removeItem('asian_low');
    localStorage.removeItem('asian_range');
    document.getElementById('asian-high').value = '';
    document.getElementById('asian-low').value = '';
    loadSavedAsianRange();
}

// --- TRADING JOURNAL ---
let currentTradeDir = 'long';

function setTradeDirection(dir) {
    currentTradeDir = dir;
    document.getElementById('dir-long').classList.toggle('active', dir === 'long');
    document.getElementById('dir-short').classList.toggle('active', dir === 'short');
}

function saveTrade() {
    const date = document.getElementById('trade-date').value;
    const pair = document.getElementById('trade-pair').value;
    const entry = document.getElementById('trade-entry').value;
    const sl = document.getElementById('trade-sl').value;
    const tp = document.getElementById('trade-tp').value;
    const outcome = document.getElementById('trade-outcome').value;
    const notes = document.getElementById('trade-notes').value;

    if (!date || !entry) { alert('Please enter at least a Date and Entry Price.'); return; }

    const trade = { id: Date.now(), date, pair, direction: currentTradeDir, entry, sl, tp, outcome, notes };
    let trades = JSON.parse(localStorage.getItem('limitless_trades') || '[]');
    trades.unshift(trade);
    localStorage.setItem('limitless_trades', JSON.stringify(trades));

    alert('Trade saved successfully!');
    loadTrades();
    document.getElementById('trade-entry').value = '';
    document.getElementById('trade-sl').value = '';
    document.getElementById('trade-tp').value = '';
    document.getElementById('trade-notes').value = '';
}

function loadTrades() {
    const trades = JSON.parse(localStorage.getItem('limitless_trades') || '[]');
    const list = document.getElementById('trades-list');
    if (trades.length === 0) {
        list.innerHTML = '<p style="color: #888; text-align: center;">No trades logged yet.</p>';
        return;
    }
    list.innerHTML = trades.map(t => `
        <div style="border-bottom: 1px solid #333; padding: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <strong>${t.date} - ${t.pair}</strong>
                <span style="color: ${t.outcome === 'win' ? '#00FF00' : t.outcome === 'loss' ? '#FF3D00' : '#FFD700'}">${t.outcome.toUpperCase()}</span>
            </div>
            <div style="font-size: 0.8rem; color: #aaa;">
                ${t.direction.toUpperCase()} @ ${t.entry} | SL: ${t.sl} | TP: ${t.tp}
            </div>
            ${t.notes ? `<div style="font-size: 0.8rem; color: #888; margin-top: 5px;">${t.notes}</div>` : ''}
        </div>
    `).join('');
}

function clearAllTrades() {
    if (confirm('Are you sure you want to delete all trade history?')) {
        localStorage.removeItem('limitless_trades');
        loadTrades();
    }
}

// --- DAILY BRIEFING ---
function loadDailyBriefing() {
    document.getElementById('briefing-content').innerHTML = `
        <p style="color: #FFD700; font-weight: bold;">Gold is consolidating near key resistance.</p>
        <p>Watch for the Asian Session sweep before looking for entries at the 61.8% Golden Zone.</p>
        <p style="margin-top: 10px; font-size: 0.8rem; color: #888;">Next update: 8:00 AM EST</p>
    `;
}

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    // Hide all tool screens and modal on load
    document.querySelectorAll('.tool-screen').forEach(screen => screen.style.display = 'none');
    document.getElementById('premium-modal').style.display = 'none';
    
    loadDailyBriefing();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('trade-date').value = today;
});
