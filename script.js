// Initialize Telegram Mini App
if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    window.Telegram.WebApp.setHeaderColor('#000000');
    window.Telegram.WebApp.setBackgroundColor('#000000');
}

let tradeDirection = 'long';

// Navigation Functions
function showFibCalculator() {
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('fib-screen').style.display = 'block';
}

function showJournal() {
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('journal-screen').style.display = 'block';
}

function showAsianTracker() {
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('asian-screen').style.display = 'block';
}

function goBack() {
    document.querySelectorAll('.tool-screen').forEach(screen => screen.style.display = 'none');
    document.getElementById('main-app').style.display = 'block';
}

function setDirection(dir) {
    tradeDirection = dir;
    document.getElementById('btn-long').className = dir === 'long' ? 'toggle-btn active' : 'toggle-btn';
    document.getElementById('btn-short').className = dir === 'short' ? 'toggle-btn active short-active' : 'toggle-btn';
}

// Fibonacci Calculation Logic
function calculateFib() {
    const high = parseFloat(document.getElementById('fib-high').value);
    const low = parseFloat(document.getElementById('fib-low').value);
    
    if (isNaN(high) || isNaN(low) || high <= low) {
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.showAlert("⚠️ Please enter valid High and Low prices. High must be greater than Low.");
        } else {
            alert("⚠️ Please enter valid High and Low prices. High must be greater than Low.");
        }
        return;
    }

    const range = high - low;
    let lvl0, lvl50, lvl618, lvl718, lvl100;

    if (tradeDirection === 'long') {
        // Retracement from High to Low
        lvl0 = high;
        lvl50 = high - (range * 0.5);
        lvl618 = high - (range * 0.618);
        lvl718 = high - (range * 0.718);
        lvl100 = low;
    } else {
        // Retracement from Low to High
        lvl0 = low;
        lvl50 = low + (range * 0.5);
        lvl618 = low + (range * 0.618);
        lvl718 = low + (range * 0.718);
        lvl100 = high;
    }

    // Display results
    document.getElementById('lvl-0').textContent = `$${lvl0.toFixed(2)}`;
    document.getElementById('lvl-50').textContent = `$${lvl50.toFixed(2)}`;
    document.getElementById('lvl-618').textContent = `$${lvl618.toFixed(2)}`;
    document.getElementById('lvl-718').textContent = `$${lvl718.toFixed(2)}`;
    document.getElementById('lvl-100').textContent = `$${lvl100.toFixed(2)}`;

    document.getElementById('fib-results').style.display = 'block';
}

// Fetch Daily Briefing Data
async function loadDailyBriefing() {
    const briefingContainer = document.getElementById('briefing-content');
    try {
        const response = await fetch('https://raw.githubusercontent.com/Jeromany/limitless-club-app/main/briefing.json');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        briefingContainer.innerHTML = `
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
        briefingContainer.innerHTML = `<p class="briefing-text" style="color: #FF3D00;">⚠️ Live data is being generated. Check back after the 8:00 AM EST automation runs!</p>`;
    }
}

// Load data on startup
document.addEventListener('DOMContentLoaded', loadDailyBriefing);
