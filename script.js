// Initialize Telegram Mini App
if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    window.Telegram.WebApp.setHeaderColor('#000000');
    window.Telegram.WebApp.setBackgroundColor('#000000');
}

let tradeDirection = 'long';

// ==================== NAVIGATION ====================
function showFibCalculator() {
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('fib-screen').style.display = 'block';
}

function showAsianTracker() {
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('asian-screen').style.display = 'block';
    startCountdown();
    loadSavedAsianRange();
}

function showJournal() {
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('journal-screen').style.display = 'block';
}

function goBack() {
    document.querySelectorAll('.tool-screen').forEach(s => s.style.display = 'none');
    document.getElementById('main-app').style.display = 'block';
}

// ==================== FIB CALCULATOR ====================
function setDirection(dir) {
    tradeDirection = dir;
    document.getElementById('btn-long').className = dir === 'long' ? 'toggle-btn active' : 'toggle-btn';
    document.getElementById('btn-short').className = dir === 'short' ? 'toggle-btn active short-active' : 'toggle-btn';
}

function calculateFib() {
    const high = parseFloat(document.getElementById('fib-high').value);
    const low = parseFloat(document.getElementById('fib-low').value);
    if (isNaN(high) || isNaN(low) || high <= low) {
        const msg = "⚠️ High must be greater than Low.";
        window.Telegram?.WebApp?.showAlert(msg) || alert(msg);
        return;
    }
    const range = high - low;
    let lvl0, lvl50, lvl618, lvl718, lvl100;
    if (tradeDirection === 'long') {
        lvl0 = high; lvl50 = high - (range * 0.5); lvl618 = high - (range * 0.618);
        lvl718 = high - (range * 0.718); lvl100 = low;
    } else {
        lvl0 = low; lvl50 = low + (range * 0.5); lvl618 = low + (range * 0.618);
        lvl718 = low + (range * 0.718); lvl100 = high;
    }
    document.getElementById('lvl-0').textContent = `$${lvl0.toFixed(2)}`;
    document.getElementById('lvl-50').textContent = `$${lvl50.toFixed(2)}`;
    document.getElementById('lvl-618').textContent = `$${lvl618.toFixed(2)}`;
    document.getElementById('lvl-718').textContent = `$${lvl718.toFixed(2)}`;
    document.getElementById('lvl-100').textContent = `$${lvl100.toFixed(2)}`;
    document.getElementById('fib-results').style.display = 'block';
}

// ==================== ASIAN SESSION TRACKER ====================
// Asian Session: 8:00 PM EST to 3:00 AM EST = 01:00 UTC to 08:00 UTC
const ASIAN_OPEN_UTC = 1;  // 1:00 AM UTC (8 PM EST)
const ASIAN_CLOSE_UTC = 8; // 8:00 AM UTC (3 AM EST)

function startCountdown() {
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

function updateCountdown() {
    const now = new Date();
    const utcHour = now.getUTCHours();
    const utcMin = now.getUTCMinutes();
    const utcSec = now.getUTCSeconds();
    const currentUTC = utcHour + utcMin / 60 + utcSec / 3600;

    const statusEl = document.getElementById('session-status');
    const timerEl = document.getElementById('countdown-timer');

    if (currentUTC >= ASIAN_OPEN_UTC && currentUTC < ASIAN_CLOSE_UTC) {
        // Asian Session is ACTIVE
        statusEl.textContent = "🟢 ASIAN SESSION IS LIVE";
        statusEl.className = "session-status active";

        // Countdown to close
        const closeTime = new Date(now);
        closeTime.setUTCHours(ASIAN_CLOSE_UTC, 0, 0, 0);
        const diff = closeTime - now;
        timerEl.textContent = formatTime(diff);
    } else {
        // Asian Session is CLOSED
        statusEl.textContent = "🔴 ASIAN SESSION IS CLOSED";
        statusEl.className = "session-status";

        // Countdown to next open
        const openTime = new Date(now);
        if (currentUTC >= ASIAN_CLOSE_UTC) {
            openTime.setUTCDate(openTime.getUTCDate() + 1);
        }
        openTime.setUTCHours(ASIAN_OPEN_UTC, 0, 0, 0);
        const diff = openTime - now;
        timerEl.textContent = formatTime(diff);
    }
}

function formatTime(ms) {
    const totalSec = Math.floor(ms / 1000);
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function saveAsianRange() {
    const high = document.getElementById('asian-high').value;
    const low = document.getElementById('asian-low').value;
    if (!high || !low || parseFloat(high) <= parseFloat(low)) {
        const msg = "⚠️ Please enter valid High and Low prices.";
        window.Telegram?.WebApp?.showAlert(msg) || alert(msg);
        return;
    }
    const rangeData = { high, low, date: new Date().toLocaleDateString() };
    localStorage.setItem('asianRange', JSON.stringify(rangeData));
    displaySavedRange(rangeData);
    const msg = "✅ Asian Range saved!";
    window.Telegram?.WebApp?.showAlert(msg) || alert(msg);
}

function loadSavedAsianRange() {
    const saved = localStorage.getItem('asianRange');
    if (saved) {
        const data = JSON.parse(saved);
        const today = new Date().toLocaleDateString();
        if (data.date === today) {
            displaySavedRange(data);
        } else {
            localStorage.removeItem('asianRange');
            document.getElementById('asian-saved').style.display = 'none';
        }
    }
}

function displaySavedRange(data) {
    const rangeSize = (parseFloat(data.high) - parseFloat(data.low)).toFixed(2);
    document.getElementById('saved-high').textContent = `$${parseFloat(data.high).toFixed(2)}`;
    document.getElementById('saved-low').textContent = `$${parseFloat(data.low).toFixed(2)}`;
    document.getElementById('saved-range').textContent = `$${rangeSize}`;
    document.getElementById('asian-saved').style.display = 'block';
}

function clearAsianRange() {
    localStorage.removeItem('asianRange');
    document.getElementById('asian-saved').style.display = 'none';
    document.getElementById('asian-high').value = '';
    document.getElementById('asian-low').value = '';
}

// ==================== DAILY BRIEFING ====================
async function loadDailyBriefing() {
    const container = document.getElementById('briefing-content');
    try {
        const response = await fetch('https://raw.githubusercontent.com/Jeromany/limitless-club-app/main/briefing.json');
        if (!response.ok) throw new Error('Network error');
        const data = await response.json();
        container.innerHTML = `
            <p class="briefing-text"><strong>Date:</strong> ${data.date}</p>
            <p class="briefing-text"><strong>Current Price:</strong> <span style="color: #FFD700;">$${data.price} (${data.change})</span></p>
            <br>
            <p class="briefing-text"><strong>Market Analysis:</strong><br>${data.analysis}</p>
            <br>
            <p class="briefing-text"><strong>Action Plan:</strong><br><span style="color: #00BFFF;">${data.action}</span></p>
            <br>
            <img src="${data.chartUrl}" alt="Daily Gold Chart" style="width: 100%; border-radius: 8px; border: 1px solid #333; margin-top: 10px;" onerror="this.style.display='none'">
        `;
    } catch (error) {
        container.innerHTML = `<p class="briefing-text" style="color: #FF3D00;">⚠️ Live data is being generated. Check back after 8:00 AM EST!</p>`;
    }
}

document.addEventListener('DOMContentLoaded', loadDailyBriefing);
