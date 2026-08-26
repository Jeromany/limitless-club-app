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
// Fetches live registry from GitHub. Codes are hashed for security.
async function hashString(str) {
    const buffer = new TextEncoder().encode(str);
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

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
    document.getElementById('passcode-error').textContent = 'Invalid passcode.';
}

async function verifyPasscode() {
    const input = document.getElementById('passcode-input').value.trim();
    const errorMsg = document.getElementById('passcode-error');
    errorMsg.style.display = 'none';

    try {
        const response = await fetch('https://raw.githubusercontent.com/Jeromany/limitless-club-app/main/app_registry.json');
        const registry = await response.json();
        const inputHash = await hashString(input);
        const user = registry.users.find(u => u.codeHash === inputHash);
        
        if (user && user.status === 'active') {
            localStorage.setItem('limitless_premium', 'true');
            localStorage.setItem('limitless_member', user.name);
            closePremiumModal();
            alert(`Welcome, ${user.name}!`);
        } else if (user && user.status !== 'active') {
            errorMsg.textContent = 'Access paused. Message Jeremy to reactivate.';
            errorMsg.style.display = 'block';
        } else {
            errorMsg.textContent = 'Invalid code. Check your DMs or message Jeremy.';
            errorMsg.style.display = 'block';
        }
    } catch (err) {
        errorMsg.textContent = 'Network error. Please try again.';
        errorMsg.style.display = 'block';
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
    
    // Standard TradingView Logic
    if (currentDirection === 'long') {
        document.getElementById('lvl-0').innerText = high.toFixed(2);
        document.getElementById('lvl-50').innerText = (high - diff * 0.5).toFixed(2);
        document.getElementById('lvl-618').innerText = (high - diff * 0.618).toFixed(2);
        document.getElementById('lvl-718').innerText = (high - diff * 0.718).toFixed(2);
        document.getElementById('lvl-100').innerText = low.toFixed(2);
    } else {
        document.getElementById('lvl-0').innerText = low.toFixed(2);
        document.getElementById('lvl-50').innerText = (low + diff * 0.5).toFixed(2);
        document.getElementById('lvl-618').innerText = (low + diff * 0.618).toFixed(2);
        document.getElementById('lvl-718').innerText = (low + diff * 0.718).toFixed(2);
        document.getElementById('lvl-100').innerText = high.toFixed(2);
    }

    document.getElementById('fib-results').style.display = 'block';
}

// --- ASIAN SESSION TRACKER (FIXED TIMEZONE LOGIC) ---
function updateAsianSessionCountdown() {
    const now = new Date();
    
    const astFormatter = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Port_of_Spain',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
        hour12: false
    });
    
    const astTimeParts = astFormatter.formatToParts(now);
    const astHours = parseInt(astTimeParts.find(p => p.type === 'hour').value, 10);
    const astMinutes = parseInt(astTimeParts.find(p => p.type === 'minute').value, 10);
    const astSeconds = parseInt(astTimeParts.find(p => p.type === 'second').value, 10);

    const statusEl = document.getElementById('session-status');
    const timerEl = document.getElementById('countdown-timer');
    
    const isSessionOpen = astHours >= 19 && astHours < 24;

    if (isSessionOpen) {
        statusEl.innerText = " ASIAN SESSION IS OPEN";
        statusEl.style.color = "#00FF00";
        
        let diffHours = 23 - astHours;
        let diffMinutes = 59 - astMinutes;
        let diffSeconds = 59 - astSeconds;
        
        timerEl.innerText = `${String(diffHours).padStart(2, '0')}:${String(diffMinutes).padStart(2, '0')}:${String(diffSeconds).padStart(2, '0')}`;
    } else {
        statusEl.innerText = "🔴 ASIAN SESSION IS CLOSED";
        statusEl.style.color = "#FF3D00";
        
        let diffHours = 18 - astHours;
        let diffMinutes = 59 - astMinutes;
        let diffSeconds = 59 - astSeconds;
        
        if (diffHours < 0) diffHours += 24; 
        
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

// --- DAILY BRIEFING (Automated from GitHub JSON) ---
async function loadDailyBriefing() {
    try {
        const response = await fetch('briefing.json');
        const data = await response.json();

        document.getElementById('briefing-content').innerHTML = `
            <p style="color: #FFD700; font-weight: bold; font-size: 1.1rem;">
                Gold Update: $${data.price} (${data.change})
            </p>
            <p style="margin: 10px 0;">${data.analysis}</p>
            <p style="margin: 10px 0; font-style: italic; color: #fff;">
                <strong>Action:</strong> ${data.action}
            </p>
            <p style="font-size: 0.8rem; color: #888; margin-top: 15px; border-top: 1px solid #333; padding-top: 10px;">
                Last updated: ${data.date}
            </p>
        `;
    } catch (error) {
        console.error('Error loading briefing:', error);
        document.getElementById('briefing-content').innerHTML = `
            <p class="loading">Loading today's analysis...</p>
        `;
    }
}

// --- WEEKLY CONTENT (Roadmap + War Room from JSON) ---
async function loadWeeklyContent() {
    try {
        const response = await fetch('weekly-content.json');
        const data = await response.json();
        const r = data.roadmap;
        const w = data.warRoom;
        
        // --- ROADMAP ---
        const roadmapVideoCard = document.getElementById('roadmap-video-card');
        if (roadmapVideoCard) {
            roadmapVideoCard.innerHTML = `
                <h3>🎥 This Week's Analysis</h3>
                <p style="text-align: center; margin-bottom: 20px;">Watch this week's Gold Roadmap breakdown on YouTube</p>
                <a href="${r.videoUrl}" target="_blank" class="payhip-btn" style="background-color: #FF0000; color: white; border: none; text-align: center; display: block; text-decoration: none; padding: 15px;">
                    ▶️ Watch ${r.title}
                </a>
                <p style="text-align: center; font-size: 0.8rem; color: #888; margin-top: 10px;">(Opens in YouTube app)</p>
            `;
        }
        
        const levelsCard = document.getElementById('levels-card');
        if (levelsCard) {
            levelsCard.innerHTML = `
                <h3>📌 Key Levels This Week</h3>
                <div class="fib-level"><span>Resistance</span> <span class="price">${r.resistance}</span></div>
                <div class="fib-level"><span>Support</span> <span class="price">${r.support}</span></div>
                <div class="fib-level golden-zone"><span>Bias</span> <span class="price">${r.bias}</span></div>
            `;
        }
        
        // --- WAR ROOM ---
        const warroomVideoCard = document.getElementById('warroom-video-card');
        if (warroomVideoCard) {
            warroomVideoCard.innerHTML = `
                <h3>🎬 Latest Episode</h3>
                <p style="text-align: center; margin-bottom: 20px;">Weekly Gold market breakdown with institutional analysis</p>
                <a href="${w.videoUrl}" target="_blank" class="payhip-btn" style="background-color: #FF0000; color: white; border: none; text-align: center; display: block; text-decoration: none; padding: 15px;">
                    ▶️ Watch Gold War Room ${w.episode}
                </a>
                <p style="text-align: center; font-size: 0.8rem; color: #888; margin-top: 10px;">(Opens in YouTube app)</p>
            `;
        }
        
        const battleCard = document.getElementById('warroom-battle-card');
        if (battleCard) {
            battleCard.innerHTML = `
                <h3>📊 This Week's Battle</h3>
                <div class="fib-level"><span>Theme</span> <span class="price">${w.theme}</span></div>
                <div class="fib-level"><span>Bias</span> <span class="price">${w.bias}</span></div>
                <div class="fib-level golden-zone"><span>Liquidity Zone</span> <span class="price">${w.liquidityZone}</span></div>
                <div class="fib-level"><span>Macro Target</span> <span class="price">${w.macroTarget}</span></div>
            `;
        }
    } catch (error) {
        console.error('Error loading weekly content:', error);
    }
}

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.tool-screen').forEach(screen => screen.style.display = 'none');
    document.getElementById('premium-modal').style.display = 'none';
    
    loadDailyBriefing();
    loadWeeklyContent();  // Loads BOTH Roadmap and War Room from JSON
    
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('trade-date').value = today;
});
