// Initialize Telegram Mini App
if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
    window.Telegram.WebApp.setHeaderColor('#000000');
    window.Telegram.WebApp.setBackgroundColor('#000000');
}

// Function to fetch real data from GitHub
async function loadDailyBriefing() {
    const briefingContainer = document.getElementById('briefing-content');
    
    try {
        // FETCHING FROM YOUR EXACT GITHUB USERNAME: Jeromany
        const response = await fetch('https://raw.githubusercontent.com/Jeromany/limitless-club-app/main/briefing.json');
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
                
        const data = await response.json();
        
        // Render the REAL data to the screen
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
        console.error("Failed to load briefing:", error);
        // Fallback message if fetch fails
        briefingContainer.innerHTML = `
            <p class="briefing-text" style="color: #FF3D00;">⚠️ Live data is being generated. Check back after the 8:00 AM EST automation runs!</p>
        `;
    }
}

// Load the data when the page opens
document.addEventListener('DOMContentLoaded', loadDailyBriefing);

// Placeholder functions for the tools (We will build these in Phase 3!)
function openJournal() {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.showAlert("🚧 Trading Journal is coming in the next update!");
    } else {
        alert("🚧 Trading Journal is coming in the next update!");
    }
}

function openFib() {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.showAlert("🚧 Fib Calculator is coming in the next update!");
    } else {
        alert("🚧 Fib Calculator is coming in the next update!");
    }
}

function openAsian() {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.showAlert("🚧 Asian Session Tracker is coming in the next update!");
    } else {
        alert("🚧 Asian Session Tracker is coming in the next update!");
    }
}
