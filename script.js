// Initialize Telegram Mini App (if opened inside Telegram)
if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand(); // Makes the app full screen
    
    // Set header color to match our black theme
    window.Telegram.WebApp.setHeaderColor('#000000');
    window.Telegram.WebApp.setBackgroundColor('#000000');
}

// Mock Daily Briefing Data (We will connect this to your GitHub automation later)
const mockBriefing = {
    date: new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
    price: "4012.70",
    change: "+0.68%",
    analysis: "Gold is currently respecting the $3962.50 support and $4091.20 resistance levels. Watch for a reaction at the 61.8% Fib level ($4045.00) during the NY session. Bias remains neutral until a clean break of the Asian Session range.",
    action: "Wait for liquidity sweep of Asia high before seeking short entries at key supply."
};

// Render the briefing to the screen
document.addEventListener('DOMContentLoaded', () => {
    const briefingContainer = document.getElementById('briefing-content');
    
    briefingContainer.innerHTML = `
        <p class="briefing-text"><strong>Date:</strong> ${mockBriefing.date}</p>
        <p class="briefing-text"><strong>Current Price:</strong> <span style="color: #FFD700;">$${mockBriefing.price} (${mockBriefing.change})</span></p>
        <br>
        <p class="briefing-text"><strong>Market Analysis:</strong><br>${mockBriefing.analysis}</p>
        <br>
        <p class="briefing-text"><strong>Action Plan:</strong><br><span style="color: #00BFFF;">${mockBriefing.action}</span></p>
    `;
});
