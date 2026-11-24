/**
 * Ascent - Professional Trading Journal & Playbook
 * Core Client-side Application Logic (INR & Multi-Market Categorization)
 */

// Global Application State
let state = {
    trades: [],
    rules: [],
    checklist: [],
    journal: [],
    prep: {
        bias: "",
        levels: "",
        events: "",
        executionPlan: ""
    }
};

// Global Category Filter State
let activeMarketFilter = "ALL";

// Default Checklist and Rules for first-time setup
const DEFAULT_CHECKLIST = [
    "Higher timeframe trend alignment verified",
    "Support and resistance levels identified on chart",
    "Risk-to-Reward ratio is at least 1:2",
    "No major high-impact economic news in the next 30 minutes",
    "Stop Loss price calculated and order details pre-filled"
];

const DEFAULT_RULES = [
    "Never risk more than 1% of the account on any single trade.",
    "Always place a hard Stop Loss immediately upon execution.",
    "Do not add to a losing position.",
    "Maximum of 3 trades per day. If hit, shut down trading terminal.",
    "Do not trade when feeling angry, impatient, or after a large win/loss (tilted)."
];

// Seed trades containing realistic INR amounts and different markets
const DEFAULT_MOCK_TRADES = [
    {
        date: "2026-05-25T09:30",
        symbol: "RELIANCE",
        market: "Indian Market",
        action: "LONG",
        qty: 50,
        entry: 2450.00,
        exit: 2510.00,
        sl: 2420.00,
        tp: 2550.00,
        fees: 40.00,
        setup: "Pullback",
        emotion: "Disciplined",
        notes: "Entered Reliance on daily breakout retest. Rebounded cleanly off key support zone. Scalped exit near local resistance.",
        pnl: 2960.00, // Gross: (2510 - 2450)*50 = 3000. Fees: 40. Net: 2960
        rMultiple: 2.0, // Risk = (2450 - 2420)*50 = 1500. Gross: 3000 / 1500 = 2.0R
        outcome: "WIN"
    },
    {
        date: "2026-05-26T14:15",
        symbol: "BTC",
        market: "Crypto",
        action: "SHORT",
        qty: 0.1,
        entry: 5800000.00, // INR value of BTC
        exit: 5850000.00,
        sl: 5760000.00,
        tp: 5600000.00,
        fees: 1500.00,
        setup: "Breakout",
        emotion: "Greedy",
        notes: "Chased short breakdown in Bitcoin, but price reversed and stopped out.",
        pnl: -6500.00, // Short: entry - exit = (5800k - 5850k)*0.1 = -5000. Fees: 1500. Net: -6500
        rMultiple: -1.25, // Risk = (5760k - 5800k)*0.1 = 4000. Gross: -5000 / 4000 = -1.25R
        outcome: "LOSS"
    },
    {
        date: "2026-05-28T10:05",
        symbol: "EURUSD",
        market: "Forex",
        action: "LONG",
        qty: 10000,
        entry: 90.20, // USD INR conversion rate
        exit: 91.10,
        sl: 89.80,
        tp: 91.50,
        fees: 100.00,
        setup: "Range Trade",
        emotion: "Disciplined",
        notes: "Perfect range rebound execution. Risk managed tightly. Exited near daily highs.",
        pnl: 8900.00, // Gross: (91.10 - 90.20)*10000 = 9000. Net: 8900
        rMultiple: 2.25, // Risk = (90.20 - 89.80)*10000 = 4000. Gross: 9000 / 4000 = 2.25R
        outcome: "WIN"
    },
    {
        date: "2026-05-30T11:45",
        symbol: "TATASTEEL",
        market: "Indian Market",
        action: "LONG",
        qty: 800,
        entry: 160.00,
        exit: 155.00,
        sl: 156.50,
        tp: 170.00,
        fees: 80.00,
        setup: "Pullback",
        emotion: "Anxious",
        notes: "Exited early before Stop Loss hit. Standard market noise scared me. Emotion override.",
        pnl: -4080.00, // Gross: (155 - 160)*800 = -4000. Net: -4080
        rMultiple: -1.43, // Risk = (160 - 156.5)*800 = 2800. Gross: -4000 / 2800 = -1.43R
        outcome: "LOSS"
    },
    {
        date: "2026-06-02T15:20",
        symbol: "ETH",
        market: "Crypto",
        action: "LONG",
        qty: 1.5,
        entry: 290000.00,
        exit: 290000.00,
        sl: 280000.00,
        tp: 310000.00,
        fees: 250.00,
        setup: "VWAP Rebound",
        emotion: "Calm",
        notes: "Moved stop to breakeven after clean bounce. Taken out at cost. Risk free.",
        pnl: -250.00, // Net: -250
        rMultiple: 0.0,
        outcome: "BREAKEVEN"
    },
    {
        date: "2026-06-04T09:45",
        symbol: "NIFTY-OPT",
        market: "Indian Market",
        action: "LONG",
        qty: 250, // 5 lots
        entry: 120.00,
        exit: 172.00,
        sl: 95.00,
        tp: 180.00,
        fees: 120.00,
        setup: "Support/Resistance Rebound",
        emotion: "Disciplined",
        notes: "Perfect option scalp. Rebound off weekly pivot point. Clean trend execution.",
        pnl: 12880.00, // Gross: (172 - 120)*250 = 13000. Net: 12880
        rMultiple: 2.08, // Risk = (120 - 95)*250 = 6250. Gross: 13000 / 6250 = 2.08R
        outcome: "WIN"
    }
];

const DEFAULT_MOCK_JOURNAL = [
    {
        date: "2026-06-04",
        title: "Very patient execution today",
        grade: "A",
        emotion: "Calm & Balanced",
        marketMood: "Trending Cleanly",
        content: "Wait time was long but paid off handsomely. Stuck to my key setups on Nifty Options. Closed ETH trade at breakeven without remorse. A-grade discipline. Keep it up."
    },
    {
        date: "2026-05-30",
        title: "Felt anxious and exit micro-managed",
        grade: "C",
        emotion: "Anxious & Hesitant",
        marketMood: "Choppy / Rangebound",
        content: "Managed TATASTEEL trade terribly today. Panic-sold when the stock pulled back a little. I need to walk away once my brackets are placed. Trading is mental."
    }
];

// Global Chart References
let equityChartInstance = null;
let outcomeChartInstance = null;

// DOM Elements
const viewDashboard = document.getElementById("view-dashboard");
const viewTradeLog = document.getElementById("view-tradelog");
const viewPlanner = document.getElementById("view-planner");
const viewCalculators = document.getElementById("view-calculators");
const viewJournal = document.getElementById("view-journal");
const viewSettings = document.getElementById("view-settings");

const views = {
    dashboard: viewDashboard,
    tradelog: viewTradeLog,
    planner: viewPlanner,
    calculators: viewCalculators,
    journal: viewJournal,
    settings: viewSettings
};

const pageTitle = document.getElementById("page-title");
const pageSubtitle = document.getElementById("page-subtitle");
const navItems = document.querySelectorAll(".nav-item");

/* ==========================================================================
   INITIALIZATION & DATA LOADING
   ========================================================================== */
document.addEventListener("DOMContentLoaded", () => {
    loadStateFromStorage();
    initAppRouting();
    initMarketFilter();
    initCalculators();
    initModals();
    initFilters();
    initPlannerView();
    initJournalView();
    initSettingsView();
    
    // Initial UI render & dashboard charts
    updateUI();
});

function loadStateFromStorage() {
    try {
        const storedTrades = localStorage.getItem("ascent_trades");
        const storedRules = localStorage.getItem("ascent_rules");
        const storedChecklist = localStorage.getItem("ascent_checklist");
        const storedJournal = localStorage.getItem("ascent_journal");
        const storedPrep = localStorage.getItem("ascent_market_prep");

        if (storedTrades === null) {
            // First run: Seed with mock data
            state.trades = [...DEFAULT_MOCK_TRADES];
            state.rules = [...DEFAULT_RULES];
            state.checklist = [...DEFAULT_CHECKLIST];
            state.journal = [...DEFAULT_MOCK_JOURNAL];
            state.prep = {
                bias: "NIFTY 50 holds above 22,800. Daily chart shows continuation. Reliance consolidates near key support of ₹2,450. Crypto showing sideways range structure with support at $67,000.",
                levels: "NIFTY: Support 22800, 22650 | Resistance 23100\nReliance: Support 2450, 2400 | Resistance 2530\nBTC: Support 67000, 65500 | Resistance 69000",
                events: "RBI Interest Rate Decision next Friday. US CPI data next Wednesday.",
                executionPlan: "NIFTY: Look for pullback bounces near 22,800 with tight options risk. Reliance: Take long pullbacks at ₹2,450. Crypto: HODL positions, no leverage entries today."
            };
            saveAllToStorage();
            showToast("Welcome to Ascent! Loaded demo portfolio in Indian Rupees (₹).", "success");
        } else {
            state.trades = JSON.parse(storedTrades) || [];
            state.rules = JSON.parse(storedRules) || [];
            state.checklist = JSON.parse(storedChecklist) || [];
            state.journal = JSON.parse(storedJournal) || [];
            state.prep = JSON.parse(storedPrep) || { bias: "", levels: "", events: "", executionPlan: "" };
        }
    } catch (e) {
        console.error("Failed to load local storage state:", e);
        showToast("Error loading saved data. Resetting in memory.", "error");
    }
}

function saveAllToStorage() {
    localStorage.setItem("ascent_trades", JSON.stringify(state.trades));
    localStorage.setItem("ascent_rules", JSON.stringify(state.rules));
    localStorage.setItem("ascent_checklist", JSON.stringify(state.checklist));
    localStorage.setItem("ascent_journal", JSON.stringify(state.journal));
    localStorage.setItem("ascent_market_prep", JSON.stringify(state.prep));
}

/* ==========================================================================
   ROUTING & VIEW NAVIGATION
   ========================================================================== */
function initAppRouting() {
    // Nav bar clicks
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const tabName = item.getAttribute("data-tab");
            switchTab(tabName);
        });
    });

    // Quick links
    document.getElementById("view-all-trades-btn").addEventListener("click", () => switchTab("tradelog"));
    document.getElementById("go-to-playbook-btn").addEventListener("click", () => switchTab("planner"));

    // Hash check on load
    const hash = window.location.hash.replace("#", "");
    if (hash && views[hash]) {
        switchTab(hash);
    }
}

function switchTab(tabName) {
    if (!views[tabName]) return;

    // Toggle nav active classes
    navItems.forEach(item => {
        if (item.getAttribute("data-tab") === tabName) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });

    // Toggle view panels
    Object.keys(views).forEach(key => {
        if (key === tabName) {
            views[key].classList.add("active-view");
        } else {
            views[key].classList.remove("active-view");
        }
    });

    // Show/Hide Global Market Segment Bar based on tab
    const filterBar = document.getElementById("global-market-filter");
    if (filterBar) {
        if (tabName === "dashboard" || tabName === "tradelog") {
            filterBar.style.display = "flex";
        } else {
            filterBar.style.display = "none";
        }
    }

    // Update Titles
    const titleConfig = {
        dashboard: { title: "Performance Dashboard", subtitle: "Real-time statistics & visual analytics of your trading performance." },
        tradelog: { title: "Trade Journal", subtitle: "Record executions, write review notes, and monitor performance outcomes." },
        planner: { title: "Playbook & Planner", subtitle: "Define your market bias, check checklists, and manage your strict rules." },
        calculators: { title: "Trader Tools", subtitle: "Compute accurate mathematical position sizes and verify risk/reward boundaries." },
        journal: { title: "Daily Reflections", subtitle: "Reflect on psychology, list lessons, and log session diaries." },
        settings: { title: "Settings & Backup", subtitle: "Configure rules, export data backups, or factory reset application database." }
    };

    if (titleConfig[tabName]) {
        pageTitle.textContent = titleConfig[tabName].title;
        pageSubtitle.textContent = titleConfig[tabName].subtitle;
    }

    // Set Window Hash
    window.location.hash = tabName;

    // Special renders/refresh on tab load
    if (tabName === "dashboard") {
        updateUI(); // Redraws charts cleanly
    } else if (tabName === "tradelog") {
        renderTradeLogTable();
    } else if (tabName === "planner") {
        renderPlannerRules();
    } else if (tabName === "journal") {
        renderJournalLogs();
    }
}

/* ==========================================================================
   MARKET SEGMENT FILTER EVENTS
   ========================================================================== */
function initMarketFilter() {
    const filterBar = document.getElementById("global-market-filter");
    if (!filterBar) return;

    const buttons = filterBar.querySelectorAll(".segment-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeMarketFilter = btn.getAttribute("data-market");
            
            // Refresh whichever page is currently open
            const activeTab = document.querySelector(".nav-item.active").getAttribute("data-tab");
            if (activeTab === "dashboard") {
                updateUI();
            } else if (activeTab === "tradelog") {
                renderTradeLogTable();
            }
        });
    });
}

/* ==========================================================================
   ANALYTICS & METRICS CALCULATIONS
   ========================================================================== */
function calculateMetrics() {
    // Filter trades based on market category
    const trades = state.trades.filter(t => {
        if (activeMarketFilter === "ALL") return true;
        return t.market === activeMarketFilter;
    });

    const totalTrades = trades.length;
    
    if (totalTrades === 0) {
        return {
            netPnL: 0,
            winRate: 0,
            winsCount: 0,
            lossesCount: 0,
            profitFactor: 0,
            avgTradePnL: 0,
            grossProfit: 0,
            grossLoss: 0
        };
    }

    let netPnL = 0;
    let winsCount = 0;
    let lossesCount = 0;
    let breakevenCount = 0;
    let grossProfit = 0;
    let grossLoss = 0;

    trades.forEach(t => {
        netPnL += t.pnl;
        if (t.pnl > 0.01) {
            winsCount++;
            grossProfit += t.pnl;
        } else if (t.pnl < -0.01) {
            lossesCount++;
            grossLoss += Math.abs(t.pnl);
        } else {
            breakevenCount++;
        }
    });

    const winRate = totalTrades > 0 ? (winsCount / totalTrades) * 100 : 0;
    const profitFactor = grossLoss > 0 ? (grossProfit / grossLoss) : grossProfit > 0 ? 99.9 : 0;
    const avgTradePnL = netPnL / totalTrades;

    return {
        netPnL,
        winRate,
        winsCount,
        lossesCount,
        profitFactor,
        avgTradePnL,
        grossProfit,
        grossLoss
    };
}

/* ==========================================================================
   DASHBOARD UI UPDATING & CHARTS
   ========================================================================== */
function updateUI() {
    const metrics = calculateMetrics();

    // 1. Update metric values
    const netPnlEl = document.getElementById("stat-net-pnl");
    netPnlEl.textContent = formatCurrency(metrics.netPnL);
    netPnlEl.className = "stat-value " + (metrics.netPnL >= 0 ? "text-success" : "text-danger");

    const growthPctEl = document.getElementById("stat-net-pnl-pct");
    const accountInitialSize = 100000; // Benchmark account ₹1,00,000
    const growthPct = (metrics.netPnL / accountInitialSize) * 100;
    growthPctEl.textContent = `${growthPct >= 0 ? '+' : ''}${growthPct.toFixed(2)}% net account delta`;
    growthPctEl.className = `stat-trend ${growthPct >= 0 ? 'trend-up' : 'trend-down'}`;

    document.getElementById("stat-win-rate").textContent = `${metrics.winRate.toFixed(1)}%`;
    document.getElementById("stat-win-loss-ratio").textContent = `${metrics.winsCount} Wins / ${metrics.lossesCount} Losses`;

    document.getElementById("stat-profit-factor").textContent = metrics.profitFactor.toFixed(2);
    document.getElementById("stat-gross-pnl").textContent = `Gross Profit: ${formatCurrency(metrics.grossProfit)} | Loss: ${formatCurrency(metrics.grossLoss)}`;

    // Display correct count of filtered trades
    const filteredTradesCount = state.trades.filter(t => activeMarketFilter === "ALL" || t.market === activeMarketFilter).length;
    document.getElementById("stat-total-trades").textContent = filteredTradesCount;
    document.getElementById("stat-avg-pnl").textContent = `Avg. Trade P&L: ${formatCurrency(metrics.avgTradePnL)}`;

    // 2. Render Charts
    renderEquityCurveChart();
    renderOutcomeDoughnutChart();

    // 3. Render dashboard widgets
    renderDashboardRecentTrades();
    renderDashboardQuickChecklist();
}

function formatCurrency(amount) {
    const formatter = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return formatter.format(amount);
}

function renderEquityCurveChart() {
    const ctx = document.getElementById('equityChart').getContext('2d');
    
    // Destroy previous instance
    if (equityChartInstance) {
        equityChartInstance.destroy();
    }

    // Filter trades based on market category
    const filteredTrades = state.trades.filter(t => {
        if (activeMarketFilter === "ALL") return true;
        return t.market === activeMarketFilter;
    });

    // Sort trades chronologically
    const sortedTrades = [...filteredTrades].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    const startingBalance = 100000; // ₹1,00,000 base
    let runningBalance = startingBalance;
    const balanceData = [startingBalance];
    const labels = ["Start"];

    sortedTrades.forEach((trade, index) => {
        runningBalance += trade.pnl;
        balanceData.push(runningBalance);
        labels.push(`Trade #${index + 1} (${trade.symbol})`);
    });

    const isProfitable = runningBalance >= startingBalance;

    equityChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Account Equity (₹)',
                data: balanceData,
                borderColor: isProfitable ? '#10b981' : '#ef4444',
                backgroundColor: isProfitable ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)',
                borderWidth: 2.5,
                pointBackgroundColor: isProfitable ? '#10b981' : '#ef4444',
                pointHoverRadius: 6,
                fill: true,
                tension: 0.15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(18, 24, 38, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#f8fafc',
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Equity: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.02)' },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.02)' },
                    ticks: {
                        color: '#64748b',
                        font: { family: 'Outfit', size: 11 },
                        callback: function(value) {
                            return '₹' + value.toLocaleString('en-IN');
                        }
                    }
                }
            }
        }
    });
}

function renderOutcomeDoughnutChart() {
    const ctx = document.getElementById('outcomeChart').getContext('2d');

    if (outcomeChartInstance) {
        outcomeChartInstance.destroy();
    }

    // Filter trades based on market category
    const filteredTrades = state.trades.filter(t => {
        if (activeMarketFilter === "ALL") return true;
        return t.market === activeMarketFilter;
    });

    const wins = filteredTrades.filter(t => t.pnl > 0.01).length;
    const losses = filteredTrades.filter(t => t.pnl < -0.01).length;
    const breakeven = filteredTrades.filter(t => Math.abs(t.pnl) <= 0.01).length;

    if (filteredTrades.length === 0) {
        // Render an empty state chart structure
        outcomeChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['No Data'],
                datasets: [{
                    data: [100],
                    backgroundColor: ['rgba(255,255,255,0.05)'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
        return;
    }

    outcomeChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Wins', 'Losses', 'Breakeven'],
            datasets: [{
                data: [wins, losses, breakeven],
                backgroundColor: [
                    '#10b981', // green
                    '#ef4444', // red
                    '#64748b'  // gray
                ],
                borderColor: '#121826',
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 12 },
                        boxWidth: 12,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(18, 24, 38, 0.95)',
                    titleColor: '#f8fafc',
                    bodyColor: '#f8fafc',
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

function renderDashboardRecentTrades() {
    const tbody = document.getElementById("recent-trades-tbody");
    tbody.innerHTML = "";

    // Filter trades based on market category
    const filteredTrades = state.trades.filter(t => {
        if (activeMarketFilter === "ALL") return true;
        return t.market === activeMarketFilter;
    });

    // Show recent 5 trades
    const sortedTrades = [...filteredTrades].sort((a, b) => new Date(b.date) - new Date(a.date));
    const recent = sortedTrades.slice(0, 5);

    if (recent.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 24px;">No trades recorded in this segment. Click 'Add Trade' to start.</td></tr>`;
        return;
    }

    recent.forEach(t => {
        const row = document.createElement("tr");
        const formattedDate = new Date(t.date).toLocaleDateString('en-IN', {month: 'short', day: 'numeric'});
        
        let badgeClass = t.action === "LONG" ? "badge-success" : "badge-danger";
        let outcomeBadge = "badge-neutral";
        if (t.outcome === "WIN") outcomeBadge = "badge-success";
        if (t.outcome === "LOSS") outcomeBadge = "badge-danger";

        row.innerHTML = `
            <td>${formattedDate}</td>
            <td><strong>${t.symbol}</strong><br><span class="badge badge-neutral" style="font-size: 8px; padding: 1px 3px; text-transform: uppercase;">${t.market || 'Indian Market'}</span></td>
            <td><span class="badge ${badgeClass}">${t.action}</span></td>
            <td>${t.setup || 'N/A'}</td>
            <td><span class="badge ${outcomeBadge}">${t.outcome}</span></td>
            <td class="${t.pnl >= 0 ? 'text-success' : 'text-danger'}">${t.pnl >= 0 ? '+' : ''}${formatCurrency(t.pnl)}</td>
        `;
        tbody.appendChild(row);
    });
}

function renderDashboardQuickChecklist() {
    const container = document.getElementById("quick-rules-container");
    container.innerHTML = "";

    if (state.rules.length === 0) {
        container.innerHTML = `<p class="text-muted" style="text-align: center; padding: 16px 0;">No discipline rules set up yet.</p>`;
        return;
    }

    // Display first 4 rules
    const firstRules = state.rules.slice(0, 4);
    firstRules.forEach((rule, index) => {
        const div = document.createElement("div");
        div.className = "quick-rule-item";
        div.innerHTML = `
            <input type="checkbox" class="quick-rule-check" id="q-rule-${index}">
            <label for="q-rule-${index}" class="quick-rule-text">${rule}</label>
        `;
        container.appendChild(div);

        // Interactive strikeout logic
        const checkbox = div.querySelector(".quick-rule-check");
        const label = div.querySelector(".quick-rule-text");
        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                label.classList.add("checked");
            } else {
                label.classList.remove("checked");
            }
        });
    });
}

/* ==========================================================================
   VIEW 2: JOURNAL & TRADE LOG IMPLEMENTATION
   ========================================================================== */
let tradeFilters = {
    search: "",
    action: "all",
    setup: "all",
    outcome: "all"
};

function initFilters() {
    document.getElementById("filter-search").addEventListener("input", (e) => {
        tradeFilters.search = e.target.value.trim().toUpperCase();
        renderTradeLogTable();
    });

    document.getElementById("filter-action").addEventListener("change", (e) => {
        tradeFilters.action = e.target.value;
        renderTradeLogTable();
    });

    document.getElementById("filter-setup").addEventListener("change", (e) => {
        tradeFilters.setup = e.target.value;
        renderTradeLogTable();
    });

    document.getElementById("filter-outcome").addEventListener("change", (e) => {
        tradeFilters.outcome = e.target.value;
        renderTradeLogTable();
    });

    document.getElementById("reset-filters-btn").addEventListener("click", () => {
        document.getElementById("filter-search").value = "";
        document.getElementById("filter-action").value = "all";
        document.getElementById("filter-setup").value = "all";
        document.getElementById("filter-outcome").value = "all";
        
        tradeFilters = { search: "", action: "all", setup: "all", outcome: "all" };
        renderTradeLogTable();
    });
}

function updateSetupDatalists() {
    const selectFilter = document.getElementById("filter-setup");
    
    // Fetch unique setups
    const setups = new Set();
    state.trades.forEach(t => { if (t.setup) setups.add(t.setup); });

    // Rebuild select options
    selectFilter.innerHTML = '<option value="all">All Setups</option>';
    setups.forEach(setup => {
        const option = document.createElement("option");
        option.value = setup;
        option.textContent = setup;
        selectFilter.appendChild(option);
    });

    // Rebuild datalist in modal
    const datalist = document.getElementById("setup-datalist");
    datalist.innerHTML = "";
    const commonSetups = ["Breakout", "Pullback", "Mean Reversion", "VWAP Rebound", "Support/Resistance Rebound"];
    const merged = Array.from(new Set([...commonSetups, ...setups]));
    merged.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s;
        datalist.appendChild(opt);
    });
}

function renderTradeLogTable() {
    const tbody = document.getElementById("trade-log-tbody");
    tbody.innerHTML = "";

    // Dynamically filter trades (including Active Market Filter)
    let filteredTrades = state.trades.filter(t => {
        const matchesMarket = activeMarketFilter === "ALL" || t.market === activeMarketFilter;
        const matchesSearch = t.symbol.toUpperCase().includes(tradeFilters.search);
        const matchesAction = tradeFilters.action === "all" || t.action === tradeFilters.action;
        const matchesSetup = tradeFilters.setup === "all" || t.setup === tradeFilters.setup;
        const matchesOutcome = tradeFilters.outcome === "all" || t.outcome === tradeFilters.outcome;
        return matchesMarket && matchesSearch && matchesAction && matchesSetup && matchesOutcome;
    });

    // Sort chronologically descending (newest first)
    filteredTrades.sort((a, b) => new Date(b.date) - new Date(a.date));

    // Update entry title counters
    document.getElementById("trade-log-counter").textContent = `Journal Entries (${filteredTrades.length})`;

    if (filteredTrades.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--text-muted); padding: 32px;">No matching trade journal records found.</td></tr>`;
        return;
    }

    filteredTrades.forEach((t) => {
        // Find index in main state array to match edits/deletes
        const mainIndex = state.trades.findIndex(origin => origin.date === t.date && origin.symbol === t.symbol && origin.entry === t.entry);

        const row = document.createElement("tr");
        const formattedDate = new Date(t.date).toLocaleString('en-IN', {month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'});
        
        let actionBadge = t.action === "LONG" ? "badge-success" : "badge-danger";
        let outcomeBadge = "badge-neutral";
        if (t.outcome === "WIN") outcomeBadge = "badge-success";
        if (t.outcome === "LOSS") outcomeBadge = "badge-danger";

        const pnlFormatted = `${t.pnl >= 0 ? '+' : ''}${formatCurrency(t.pnl)}`;
        const rMultipleFormatted = t.rMultiple !== undefined && !isNaN(t.rMultiple) ? `${t.rMultiple >= 0 ? '+' : ''}${t.rMultiple.toFixed(2)}R` : 'N/A';

        row.innerHTML = `
            <td>${formattedDate}</td>
            <td>
                <strong>${t.symbol}</strong><br>
                <span class="badge badge-neutral" style="font-size: 8px; padding: 2px 4px; margin-top: 4px; letter-spacing: 0.5px;">${t.market || 'Indian Market'}</span>
            </td>
            <td><span class="badge ${actionBadge}">${t.action}</span></td>
            <td>${formatCurrency(t.entry)} / ${formatCurrency(t.exit)}</td>
            <td>${t.qty}</td>
            <td>SL: ${t.sl ? formatCurrency(t.sl) : 'N/A'} <br> TP: ${t.tp ? formatCurrency(t.tp) : 'N/A'}</td>
            <td>${formatCurrency(t.fees)}</td>
            <td>${t.setup || '<span class="text-muted">-</span>'}</td>
            <td><span class="text-muted" style="font-size: 12px;">${t.emotion || 'Calm'}</span></td>
            <td class="${t.pnl >= 0 ? 'text-success' : 'text-danger'}">
                <strong>${pnlFormatted}</strong> <br>
                <span style="font-size: 11px; opacity: 0.8;">${rMultipleFormatted}</span>
            </td>
            <td>
                <div class="actions-cell">
                    <button class="btn btn-secondary btn-icon-only edit-trade-btn" data-index="${mainIndex}" title="Edit Journal Entry">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button class="btn btn-danger btn-icon-only delete-trade-btn" data-index="${mainIndex}" title="Delete Record">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });

    // Re-bind listeners for newly generated buttons
    document.querySelectorAll(".edit-trade-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const index = e.currentTarget.getAttribute("data-index");
            openTradeModal(parseInt(index));
        });
    });

    document.querySelectorAll(".delete-trade-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const index = e.currentTarget.getAttribute("data-index");
            if (confirm("Are you sure you want to delete this trade record permanently?")) {
                state.trades.splice(parseInt(index), 1);
                saveAllToStorage();
                renderTradeLogTable();
                updateSetupDatalists();
                showToast("Trade record deleted successfully.", "error");
            }
        });
    });

    updateSetupDatalists();
}

/* ==========================================================================
   MODAL DIALOG IMPLEMENTATION
   ========================================================================== */
const tradeModal = document.getElementById("trade-modal");
const tradeForm = document.getElementById("trade-form");
const modalTitle = document.getElementById("modal-title");
const tradeIndexInput = document.getElementById("trade-index");

function initModals() {
    document.getElementById("quick-add-btn").addEventListener("click", () => openTradeModal());
    document.getElementById("add-trade-btn").addEventListener("click", () => openTradeModal());
    document.getElementById("close-modal-btn").addEventListener("click", closeTradeModal);
    document.getElementById("cancel-modal-btn").addEventListener("click", closeTradeModal);

    // Modal backdrop click closes modal
    tradeModal.addEventListener("click", (e) => {
        if (e.target === tradeModal) closeTradeModal();
    });

    // Form submit listener
    tradeForm.addEventListener("submit", handleTradeFormSubmit);
}

function openTradeModal(editIndex = null) {
    tradeForm.reset();
    
    // Autofill with local time for convenience
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById("trade-datetime").value = now.toISOString().slice(0, 16);

    if (editIndex !== null) {
        // Mode: EDIT
        modalTitle.textContent = "Edit Journal Entry";
        tradeIndexInput.value = editIndex;

        const t = state.trades[editIndex];
        document.getElementById("trade-datetime").value = t.date;
        document.getElementById("trade-symbol").value = t.symbol;
        document.getElementById("trade-market").value = t.market || "Indian Market";
        document.getElementById("trade-action").value = t.action;
        document.getElementById("trade-qty").value = t.qty;
        document.getElementById("trade-entry").value = t.entry;
        document.getElementById("trade-exit").value = t.exit;
        document.getElementById("trade-sl").value = t.sl || "";
        document.getElementById("trade-tp").value = t.tp || "";
        document.getElementById("trade-fees").value = t.fees || "0.00";
        document.getElementById("trade-setup").value = t.setup || "";
        document.getElementById("trade-emotion").value = t.emotion || "Disciplined";
        document.getElementById("trade-notes").value = t.notes || "";
    } else {
        // Mode: CREATE
        modalTitle.textContent = "Record New Execution";
        tradeIndexInput.value = "";
    }

    tradeModal.classList.add("show");
}

function closeTradeModal() {
    tradeModal.classList.remove("show");
}

function handleTradeFormSubmit(e) {
    e.preventDefault();

    const editIndex = tradeIndexInput.value;
    const datetime = document.getElementById("trade-datetime").value;
    const symbol = document.getElementById("trade-symbol").value.trim().toUpperCase();
    const market = document.getElementById("trade-market").value;
    const action = document.getElementById("trade-action").value;
    const qty = parseFloat(document.getElementById("trade-qty").value);
    const entry = parseFloat(document.getElementById("trade-entry").value);
    const exit = parseFloat(document.getElementById("trade-exit").value);
    const sl = parseFloat(document.getElementById("trade-sl").value) || null;
    const tp = parseFloat(document.getElementById("trade-tp").value) || null;
    const fees = parseFloat(document.getElementById("trade-fees").value) || 0;
    const setup = document.getElementById("trade-setup").value.trim();
    const emotion = document.getElementById("trade-emotion").value;
    const notes = document.getElementById("trade-notes").value.trim();

    // 1. Math Validations
    if (qty <= 0 || entry <= 0 || exit <= 0 || fees < 0) {
        showToast("Numeric quantities, entries, and exits must be greater than zero.", "error");
        return;
    }

    // 2. Calculations
    let pnl = 0;
    if (action === "LONG") {
        pnl = (exit - entry) * qty - fees;
    } else {
        pnl = (entry - exit) * qty - fees;
    }

    // Determine Outcome Label
    let outcome = "BREAKEVEN";
    if (pnl > 0.01) outcome = "WIN";
    else if (pnl < -0.01) outcome = "LOSS";

    // Risk Multiple logic
    let rMultiple = 0;
    if (sl) {
        let riskPerShare = 0;
        if (action === "LONG") {
            riskPerShare = entry - sl;
        } else {
            riskPerShare = sl - entry;
        }
        
        const totalRisk = riskPerShare * qty;
        if (totalRisk > 0) {
            // Gross profit divided by total cash risk
            const grossProfit = action === "LONG" ? (exit - entry) * qty : (entry - exit) * qty;
            rMultiple = grossProfit / totalRisk;
        }
    }

    const tradeObject = {
        date: datetime,
        symbol,
        market,
        action,
        qty,
        entry,
        exit,
        sl,
        tp,
        fees,
        setup,
        emotion,
        notes,
        pnl,
        rMultiple,
        outcome
    };

    if (editIndex !== "") {
        // Update
        state.trades[parseInt(editIndex)] = tradeObject;
        showToast(`Updated entry for ${symbol}.`, "success");
    } else {
        // Insert
        state.trades.push(tradeObject);
        showToast(`Recorded trade for ${symbol} (${outcome}).`, "success");
    }

    saveAllToStorage();
    closeTradeModal();
    
    // Refresh views
    if (window.location.hash === "#tradelog") {
        renderTradeLogTable();
    } else {
        switchTab("tradelog");
    }
}

/* ==========================================================================
   VIEW 3: PLANNER & PLAYBOOK IMPLEMENTATION
   ========================================================================== */
function initPlannerView() {
    // 1. Setup daily market prep fields bindings
    const biasArea = document.getElementById("prep-bias");
    const levelsArea = document.getElementById("prep-levels");
    const eventsInput = document.getElementById("prep-events");
    const planArea = document.getElementById("prep-execution-plan");

    // Load initial prep data
    biasArea.value = state.prep.bias || "";
    levelsArea.value = state.prep.levels || "";
    eventsInput.value = state.prep.events || "";
    planArea.value = state.prep.executionPlan || "";

    // Save button event listener
    document.getElementById("save-prep-btn").addEventListener("click", () => {
        state.prep = {
            bias: biasArea.value,
            levels: levelsArea.value,
            events: eventsInput.value,
            executionPlan: planArea.value
        };
        saveAllToStorage();
        
        // Show saved animation
        const indicator = document.getElementById("prep-saved-indicator");
        indicator.classList.add("show");
        setTimeout(() => {
            indicator.classList.remove("show");
        }, 2000);

        showToast("Market prep plan saved successfully.", "success");
    });

    // 2. Pre-trade Checklist handlers
    document.getElementById("add-checklist-btn").addEventListener("click", () => {
        const input = document.getElementById("new-checklist-input");
        const val = input.value.trim();
        if (val) {
            state.checklist.push(val);
            saveAllToStorage();
            renderPlannerRules();
            input.value = "";
            showToast("Added checklist item.", "success");
        }
    });

    // 3. Discipline rules handlers
    document.getElementById("add-rule-btn").addEventListener("click", () => {
        const input = document.getElementById("new-rule-input");
        const val = input.value.trim();
        if (val) {
            state.rules.push(val);
            saveAllToStorage();
            renderPlannerRules();
            input.value = "";
            showToast("Added discipline rule.", "success");
        }
    });
}

function renderPlannerRules() {
    // Render Checklist
    const checklistList = document.getElementById("checklist-items-list");
    checklistList.innerHTML = "";
    
    if (state.checklist.length === 0) {
        checklistList.innerHTML = `<p class="text-muted" style="padding: 12px; font-size:13px;">No checklist items. Create criteria below.</p>`;
    } else {
        state.checklist.forEach((item, index) => {
            const div = document.createElement("div");
            div.className = "interactive-rule-item";
            div.innerHTML = `
                <div class="rule-left">
                    <span class="badge badge-primary" style="margin-right:8px;">#${index+1}</span>
                    <span>${item}</span>
                </div>
                <button class="rule-delete-btn" data-type="checklist" data-index="${index}">
                    <svg class="rule-delete-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            `;
            checklistList.appendChild(div);
        });
    }

    // Render Rules
    const rulesList = document.getElementById("rules-items-list");
    rulesList.innerHTML = "";
    
    if (state.rules.length === 0) {
        rulesList.innerHTML = `<p class="text-muted" style="padding: 12px; font-size:13px;">No rules defined yet. Define rules to keep you safe.</p>`;
    } else {
        state.rules.forEach((rule, index) => {
            const div = document.createElement("div");
            div.className = "interactive-rule-item";
            div.innerHTML = `
                <div class="rule-left">
                    <span class="badge badge-danger" style="margin-right:8px;">Rule</span>
                    <span>${rule}</span>
                </div>
                <button class="rule-delete-btn" data-type="rule" data-index="${index}">
                    <svg class="rule-delete-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            `;
            rulesList.appendChild(div);
        });
    }

    // Bind deletes
    document.querySelectorAll(".rule-delete-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const type = e.currentTarget.getAttribute("data-type");
            const index = parseInt(e.currentTarget.getAttribute("data-index"));
            
            if (type === "checklist") {
                state.checklist.splice(index, 1);
                showToast("Removed checklist item.", "error");
            } else {
                state.rules.splice(index, 1);
                showToast("Removed discipline rule.", "error");
            }
            saveAllToStorage();
            renderPlannerRules();
        });
    });
}

/* ==========================================================================
   VIEW 4: REAL-TIME POSITION & RISK CALCULATORS
   ========================================================================== */
function initCalculators() {
    // 1. Position Size Calculator bindings
    const calcAccSize = document.getElementById("calc-acc-size");
    const calcRiskPct = document.getElementById("calc-risk-pct");
    const calcEntry = document.getElementById("calc-entry");
    const calcStop = document.getElementById("calc-stop");

    const updatePositionSize = () => {
        const accSize = parseFloat(calcAccSize.value) || 0;
        const riskPct = parseFloat(calcRiskPct.value) || 0;
        const entry = parseFloat(calcEntry.value) || 0;
        const stop = parseFloat(calcStop.value) || 0;

        const cashRisk = accSize * (riskPct / 100);
        const stopDistance = Math.abs(entry - stop);
        const stopDistancePct = entry > 0 ? (stopDistance / entry) * 100 : 0;

        let quantity = 0;
        let totalNotional = 0;

        if (stopDistance > 0 && entry > 0) {
            quantity = cashRisk / stopDistance;
            totalNotional = quantity * entry;
        }

        document.getElementById("result-cash-risk").textContent = formatCurrency(cashRisk);
        document.getElementById("result-shares").textContent = isNaN(quantity) || quantity === Infinity ? "0 units" : `${quantity.toLocaleString(undefined, {maximumFractionDigits: 4})} units`;
        document.getElementById("result-notional-value").textContent = isNaN(totalNotional) || totalNotional === Infinity ? "₹0.00" : formatCurrency(totalNotional);
        document.getElementById("result-stop-dist").textContent = `${formatCurrency(stopDistance)} (${stopDistancePct.toFixed(2)}%)`;
    };

    [calcAccSize, calcRiskPct, calcEntry, calcStop].forEach(input => {
        input.addEventListener("input", updatePositionSize);
    });

    // Initial calc load
    updatePositionSize();

    // 2. Risk/Reward Calculator bindings
    const rrEntry = document.getElementById("rr-entry");
    const rrStop = document.getElementById("rr-stop");
    const rrTarget = document.getElementById("rr-target");

    const updateRiskReward = () => {
        const entry = parseFloat(rrEntry.value) || 0;
        const stop = parseFloat(rrStop.value) || 0;
        const target = parseFloat(rrTarget.value) || 0;

        const risk = Math.abs(entry - stop);
        const reward = Math.abs(target - entry);
        const ratio = risk > 0 ? (reward / risk) : 0;

        document.getElementById("rr-result-risk").textContent = formatCurrency(risk);
        document.getElementById("rr-result-reward").textContent = formatCurrency(reward);
        document.getElementById("rr-result-ratio").textContent = `1 : ${ratio.toFixed(2)}`;
        
        const badge = document.getElementById("rr-result-multiple");
        badge.textContent = `${ratio.toFixed(1)}R`;
        if (ratio >= 2) {
            badge.className = "badge badge-success";
        } else if (ratio >= 1) {
            badge.className = "badge badge-primary";
        } else {
            badge.className = "badge badge-danger";
        }
    };

    [rrEntry, rrStop, rrTarget].forEach(input => {
        input.addEventListener("input", updateRiskReward);
    });

    updateRiskReward();
}

/* ==========================================================================
   VIEW 5: DAILY JOURNAL REFLECTIONS
   ========================================================================== */
function initJournalView() {
    // Set default date picker to today
    const journalDateInput = document.getElementById("journal-date");
    const today = new Date().toISOString().split("T")[0];
    journalDateInput.value = today;

    // Save reflection
    document.getElementById("save-journal-btn").addEventListener("click", () => {
        const date = journalDateInput.value;
        const grade = document.getElementById("journal-grade").value;
        const title = document.getElementById("journal-title").value.trim();
        const emotion = document.getElementById("journal-emotion").value;
        const marketMood = document.getElementById("journal-market-mood").value;
        const content = document.getElementById("journal-content").value.trim();

        if (!title || !content) {
            showToast("Please write both a title and reflection body content.", "error");
            return;
        }

        const journalEntry = {
            date,
            grade,
            title,
            emotion,
            marketMood,
            content
        };

        // Check if entry for date already exists (to update instead of duplicate)
        const existingIndex = state.journal.findIndex(j => j.date === date);
        if (existingIndex > -1) {
            state.journal[existingIndex] = journalEntry;
            showToast(`Updated daily reflection for ${date}.`, "success");
        } else {
            state.journal.push(journalEntry);
            showToast(`Added daily reflection for ${date}.`, "success");
        }

        saveAllToStorage();
        renderJournalLogs();

        // Clear inputs (except date)
        document.getElementById("journal-title").value = "";
        document.getElementById("journal-content").value = "";
    });

    document.getElementById("clear-journal-btn").addEventListener("click", () => {
        document.getElementById("journal-title").value = "";
        document.getElementById("journal-content").value = "";
    });
}

function renderJournalLogs() {
    const list = document.getElementById("journal-logs-list");
    list.innerHTML = "";

    // Sort logs descending (newest date first)
    const sortedLogs = [...state.journal].sort((a, b) => new Date(b.date) - new Date(a.date));

    if (sortedLogs.length === 0) {
        list.innerHTML = `<p class="text-muted" style="text-align: center; padding: 32px;">No reflection logs recorded yet. Write your first reflection on the left.</p>`;
        return;
    }

    sortedLogs.forEach((j, index) => {
        // Match actual index in state array for deletion
        const originIndex = state.journal.findIndex(origin => origin.date === j.date);

        const div = document.createElement("div");
        div.className = `journal-log-entry grade-${j.grade}`;
        
        const formattedDate = new Date(j.date + "T00:00").toLocaleDateString('en-IN', {
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        });

        div.innerHTML = `
            <div class="log-entry-header">
                <div class="log-entry-meta">
                    <span class="log-entry-date">${formattedDate}</span>
                    <h4 class="log-entry-title">${j.title}</h4>
                    <div class="log-entry-tags">
                        <span class="badge badge-primary">${j.emotion}</span>
                        <span class="badge badge-neutral">${j.marketMood}</span>
                    </div>
                </div>
                <span class="badge ${j.grade === 'A' || j.grade === 'B' ? 'badge-success' : j.grade === 'C' ? 'badge-primary' : 'badge-danger'}" style="font-size:14px; font-weight:700;">Grade: ${j.grade}</span>
            </div>
            <p class="log-entry-body">${j.content}</p>
            <div class="log-entry-footer">
                <button class="btn btn-danger btn-small delete-journal-btn" data-index="${originIndex}">Delete</button>
            </div>
        `;
        list.appendChild(div);
    });

    // Bind delete buttons
    document.querySelectorAll(".delete-journal-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const index = parseInt(e.currentTarget.getAttribute("data-index"));
            if (confirm("Are you sure you want to delete this reflection log permanently?")) {
                state.journal.splice(index, 1);
                saveAllToStorage();
                renderJournalLogs();
                showToast("Reflection log deleted.", "error");
            }
        });
    });
}

/* ==========================================================================
   VIEW 6: SETTINGS, BACKUP, RESTORE & DANGER ZONE
   ========================================================================== */
function initSettingsView() {
    // File selector update name
    const fileInput = document.getElementById("import-file-input");
    const fileName = document.getElementById("import-file-name");
    const importBtn = document.getElementById("btn-import-data");

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            fileName.textContent = e.target.files[0].name;
            importBtn.disabled = false;
        } else {
            fileName.textContent = "No file chosen";
            importBtn.disabled = true;
        }
    });

    // Export Action
    document.getElementById("btn-export-data").addEventListener("click", () => {
        const backupData = {
            trades: state.trades,
            rules: state.rules,
            checklist: state.checklist,
            journal: state.journal,
            prep: state.prep,
            version: "1.0",
            exportedAt: new Date().toISOString()
        };

        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(backupData, null, 2));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        
        const timestamp = new Date().toISOString().slice(0, 10);
        downloadAnchor.setAttribute("download", `ascent_trading_backup_${timestamp}.json`);
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();

        showToast("Backup JSON file exported successfully.", "success");
    });

    // Import Action
    importBtn.addEventListener("click", () => {
        const file = fileInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const parsed = JSON.parse(e.target.result);
                
                // Validate required keys to ensure it's a valid backup file
                if (!parsed.trades || !parsed.rules || !parsed.checklist || !parsed.journal) {
                    throw new Error("Missing critical keys (trades, rules, checklist, journal).");
                }

                state.trades = parsed.trades;
                state.rules = parsed.rules;
                state.checklist = parsed.checklist;
                state.journal = parsed.journal;
                state.prep = parsed.prep || { bias: "", levels: "", events: "", executionPlan: "" };

                saveAllToStorage();
                showToast("Backup imported successfully! Reloading views...", "success");
                
                // Reset file fields
                fileInput.value = "";
                fileName.textContent = "No file chosen";
                importBtn.disabled = true;

                // Re-route to dashboard
                setTimeout(() => {
                    switchTab("dashboard");
                }, 1000);

            } catch (err) {
                console.error(err);
                showToast("Failed to parse file. Make sure it's a valid Ascent JSON backup.", "error");
            }
        };
        reader.readAsText(file);
    });

    // Factory Reset Action
    document.getElementById("btn-reset-db").addEventListener("click", () => {
        if (confirm("WARNING: This will delete ALL trades, playbooks, rules, and journal logs. This action cannot be undone. Are you absolutely sure?")) {
            localStorage.clear();
            state.trades = [];
            state.rules = [];
            state.checklist = [];
            state.journal = [];
            state.prep = { bias: "", levels: "", events: "", executionPlan: "" };
            
            showToast("Database wiped. Loading defaults...", "error");

            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    });
}

/* ==========================================================================
   TOAST NOTIFICATION ENGINE
   ========================================================================== */
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="toast-close">&times;</button>
    `;
    
    container.appendChild(toast);

    // Auto-remove after 4 seconds
    const autoRemoveTimer = setTimeout(() => {
        removeToast(toast);
    }, 4000);

    // Close button listener
    toast.querySelector(".toast-close").addEventListener("click", () => {
        clearTimeout(autoRemoveTimer);
        removeToast(toast);
    });
}

function removeToast(toast) {
    toast.style.animation = "none";
    toast.offsetHeight; // Trigger reflow
    toast.style.transition = "all 0.3s ease";
    toast.style.transform = "translateX(120%)";
    toast.style.opacity = "0";

    setTimeout(() => {
        toast.remove();
    }, 300);
}
