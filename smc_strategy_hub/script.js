/* ==========================================================================
   SMC & VOLATILITY TRADING STRATEGY HUB - JAVASCRIPT ENGINE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTabNavigation();
    initPatternSearch();
    initModalViewer();
    initCalculator();
    initCanvasSimulator();
});

/* --------------------------------------------------------------------------
   1. TAB NAVIGATION SYSTEM
   -------------------------------------------------------------------------- */
function initTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const viewSections = document.querySelectorAll('.view-section');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetViewId = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            viewSections.forEach(v => v.classList.remove('active'));

            btn.classList.add('active');
            const targetSection = document.getElementById(targetViewId);
            if (targetSection) {
                targetSection.classList.add('active');
            }

            // Redraw canvas if switching to canvas tab
            if (targetViewId === 'canvas-simulator') {
                setTimeout(() => renderActiveCanvasPattern(), 50);
            }
        });
    });
}

/* --------------------------------------------------------------------------
   2. PATTERN SEARCH & FILTERING
   -------------------------------------------------------------------------- */
function initPatternSearch() {
    const searchInput = document.getElementById('pattern-search');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const patternCards = document.querySelectorAll('.pattern-card-item');

    let currentFilter = 'all';
    let searchQuery = '';

    function filterCards() {
        patternCards.forEach(card => {
            const title = card.getAttribute('data-title').toLowerCase();
            const category = card.getAttribute('data-category');

            const matchesSearch = title.includes(searchQuery);
            const matchesFilter = currentFilter === 'all' || category === currentFilter;

            if (matchesSearch && matchesFilter) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase().trim();
            filterCards();
        });
    }

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('btn-primary'));
            btn.classList.add('btn-primary');
            currentFilter = btn.getAttribute('data-filter');
            filterCards();
        });
    });
}

/* --------------------------------------------------------------------------
   3. MODAL LIGHTBOX VIEWER
   -------------------------------------------------------------------------- */
function initModalViewer() {
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img-element');
    const modalTitle = document.getElementById('modal-title');
    const modalDesc = document.getElementById('modal-desc');
    const closeBtn = document.querySelector('.modal-close');

    const cards = document.querySelectorAll('.pattern-card-item');

    cards.forEach(card => {
        card.addEventListener('click', () => {
            const imgSrc = card.getAttribute('data-img');
            const title = card.getAttribute('data-title');
            const desc = card.getAttribute('data-desc');

            if (modal && modalImg) {
                modalImg.src = imgSrc;
                if (modalTitle) modalTitle.innerText = title;
                if (modalDesc) modalDesc.innerText = desc;
                modal.classList.add('active');
            }
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }

    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('active');
        });
    }
}

/* --------------------------------------------------------------------------
   4. RISK & POSITION CALCULATOR
   -------------------------------------------------------------------------- */
function initCalculator() {
    const capitalInput = document.getElementById('calc-capital');
    const riskPctInput = document.getElementById('calc-risk-pct');
    const entryInput = document.getElementById('calc-entry');
    const slInput = document.getElementById('calc-sl');
    const tpInput = document.getElementById('calc-tp');
    const lotSizeInput = document.getElementById('calc-lot-size');

    const resRiskAmt = document.getElementById('res-risk-amt');
    const resQty = document.getElementById('res-qty');
    const resLots = document.getElementById('res-lots');
    const resCapitalUsed = document.getElementById('res-capital-used');
    const resProfit = document.getElementById('res-profit');
    const resRrr = document.getElementById('res-rrr');
    const resBadge = document.getElementById('res-badge');

    function calculate() {
        const capital = parseFloat(capitalInput.value) || 0;
        const riskPct = parseFloat(riskPctInput.value) || 0;
        const entry = parseFloat(entryInput.value) || 0;
        const sl = parseFloat(slInput.value) || 0;
        const tp = parseFloat(tpInput.value) || 0;
        const lotSize = parseFloat(lotSizeInput.value) || 1;

        if (entry <= 0 || sl <= 0 || entry === sl) return;

        const maxRiskAmount = capital * (riskPct / 100);
        const riskPerUnit = Math.abs(entry - sl);
        const rewardPerUnit = Math.abs(tp - entry);

        let totalQty = Math.floor(maxRiskAmount / riskPerUnit);
        let numLots = Math.floor(totalQty / lotSize);
        if (numLots < 1) numLots = 1;
        totalQty = numLots * lotSize;

        const totalUsedCapital = totalQty * entry;
        const actualRiskAmount = totalQty * riskPerUnit;
        const totalProfitAmount = totalQty * rewardPerUnit;
        const rrr = rewardPerUnit / riskPerUnit;

        if (resRiskAmt) resRiskAmt.innerText = `₹${actualRiskAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
        if (resQty) resQty.innerText = `${totalQty} units`;
        if (resLots) resLots.innerText = `${numLots} Lots (${numLots * lotSize} qty)`;
        if (resCapitalUsed) resCapitalUsed.innerText = `₹${totalUsedCapital.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
        if (resProfit) resProfit.innerText = `₹${totalProfitAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
        if (resRrr) resRrr.innerText = `1 : ${rrr.toFixed(2)}`;

        if (resBadge) {
            if (rrr >= 2.0) {
                resBadge.innerText = 'EXCELLENT SETUP (RRR ≥ 1:2)';
                resBadge.className = 'badge badge-bull';
            } else if (rrr >= 1.5) {
                resBadge.innerText = 'GOOD SETUP (RRR ≥ 1:1.5)';
                resBadge.className = 'badge badge-cyan';
            } else {
                resBadge.innerText = 'POOR RRR (< 1:1.5)';
                resBadge.className = 'badge badge-bear';
            }
        }
    }

    const inputs = [capitalInput, riskPctInput, entryInput, slInput, tpInput, lotSizeInput];
    inputs.forEach(inp => {
        if (inp) inp.addEventListener('input', calculate);
    });

    calculate();
}

/* --------------------------------------------------------------------------
   5. INTERACTIVE HTML5 CANDLESTICK CANVAS SIMULATOR
   -------------------------------------------------------------------------- */
let activeCanvasPattern = 'bb_kc_squeeze';

function initCanvasSimulator() {
    const btns = document.querySelectorAll('.canvas-pattern-btn');
    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            btns.forEach(b => b.classList.remove('btn-primary'));
            btn.classList.add('btn-primary');
            activeCanvasPattern = btn.getAttribute('data-canvas-type');
            renderActiveCanvasPattern();
        });
    });

    window.addEventListener('resize', renderActiveCanvasPattern);
    renderActiveCanvasPattern();
}

function renderActiveCanvasPattern() {
    const canvas = document.getElementById('pattern-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width - 32;
    canvas.height = 400;

    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, w, h);

    // Draw Grid Lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let y = 50; y < h; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
    }
    for (let x = 80; x < w; x += 80) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
    }

    if (activeCanvasPattern === 'bb_kc_squeeze') {
        drawBBKCSqueezeCanvas(ctx, w, h);
    } else if (activeCanvasPattern === 'order_block') {
        drawOrderBlockCanvas(ctx, w, h);
    } else if (activeCanvasPattern === 'fvg') {
        drawFVGCanvas(ctx, w, h);
    } else if (activeCanvasPattern === 'liquidity_sweep') {
        drawSweepCanvas(ctx, w, h);
    }
}

function drawCandle(ctx, x, openY, highY, lowY, closeY, width, isBull) {
    const color = isBull ? '#10b981' : '#ef4444';
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 2;

    // Wick
    ctx.beginPath();
    ctx.moveTo(x, highY);
    ctx.lineTo(x, lowY);
    ctx.stroke();

    // Body
    const topY = Math.min(openY, closeY);
    const bodyH = Math.max(Math.abs(closeY - openY), 3);
    ctx.fillRect(x - width / 2, topY, width, bodyH);
}

function drawBBKCSqueezeCanvas(ctx, w, h) {
    // Title
    ctx.fillStyle = '#f8fafc';
    ctx.font = '600 16px Outfit';
    ctx.fillText('BOLLINGER BANDS + KELTNER CHANNEL VOLATILITY SQUEEZE & BREAKOUT', 20, 30);

    const candles = [
        { open: 240, high: 220, low: 250, close: 235, bull: false },
        { open: 235, high: 225, low: 245, close: 240, bull: true },
        { open: 240, high: 230, low: 245, close: 232, bull: false },
        { open: 232, high: 228, low: 238, close: 236, bull: true },
        // Squeeze Zone
        { open: 236, high: 232, low: 240, close: 234, bull: false },
        { open: 234, high: 230, low: 238, close: 237, bull: true },
        { open: 237, high: 233, low: 240, close: 235, bull: false },
        // Breakout
        { open: 235, high: 140, low: 235, close: 150, bull: true },
        { open: 150, high: 110, low: 155, close: 120, bull: true },
        { open: 120, high: 80, low: 125, close: 90, bull: true }
    ];

    const startX = 60;
    const gap = (w - 120) / candles.length;

    // Draw Squeeze Box
    const sqStartX = startX + gap * 3.5;
    const sqEndX = startX + gap * 6.5;
    ctx.fillStyle = 'rgba(99, 102, 241, 0.12)';
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.4)';
    ctx.setLineDash([4, 4]);
    ctx.fillRect(sqStartX, 180, sqEndX - sqStartX, 80);
    ctx.strokeRect(sqStartX, 180, sqEndX - sqStartX, 80);
    ctx.setLineDash([]);

    ctx.fillStyle = '#a855f7';
    ctx.font = '500 12px JetBrains Mono';
    ctx.fillText('SQUEEZE ZONE (BB inside KC)', sqStartX + 10, 265);

    // Draw 20 SMA
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    candles.forEach((c, idx) => {
        const x = startX + idx * gap;
        const smaY = 240 - idx * 12;
        if (idx === 0) ctx.moveTo(x, smaY);
        else ctx.lineTo(x, smaY);
    });
    ctx.stroke();

    // Draw Candles
    candles.forEach((c, idx) => {
        const x = startX + idx * gap;
        drawCandle(ctx, x, c.open, c.high, c.low, c.close, 14, c.bull);
    });

    // Buy Signal Marker
    const buyX = startX + 7 * gap;
    ctx.fillStyle = '#10b981';
    ctx.beginPath();
    ctx.arc(buyX, 290, 18, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px Outfit';
    ctx.fillText('BUY', buyX - 11, 294);
}

function drawOrderBlockCanvas(ctx, w, h) {
    ctx.fillStyle = '#f8fafc';
    ctx.font = '600 16px Outfit';
    ctx.fillText('INSTITUTIONAL BULLISH ORDER BLOCK (OB) RETEST ENTRY', 20, 30);

    const candles = [
        { open: 150, high: 140, low: 220, close: 210, bull: false }, // OB Candle
        { open: 210, high: 130, low: 210, close: 140, bull: true },  // Displacement
        { open: 140, high: 100, low: 145, close: 110, bull: true },
        { open: 110, high: 105, low: 170, close: 165, bull: false },
        { open: 165, high: 160, low: 205, close: 200, bull: false }, // Retest into OB
        { open: 200, high: 90, low: 200, close: 95, bull: true }     // Expansion
    ];

    const startX = 100;
    const gap = (w - 200) / candles.length;

    // Highlight OB Zone
    ctx.fillStyle = 'rgba(16, 185, 129, 0.2)';
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 1;
    ctx.fillRect(startX - 20, 150, gap * 5, 65);
    ctx.strokeRect(startX - 20, 150, gap * 5, 65);

    ctx.fillStyle = '#10b981';
    ctx.font = '600 12px Outfit';
    ctx.fillText('BULLISH ORDER BLOCK (BUY ZONE)', startX + gap * 2, 142);

    candles.forEach((c, idx) => {
        const x = startX + idx * gap;
        drawCandle(ctx, x, c.open, c.high, c.low, c.close, 16, c.bull);
    });
}

function drawFVGCanvas(ctx, w, h) {
    ctx.fillStyle = '#f8fafc';
    ctx.font = '600 16px Outfit';
    ctx.fillText('FAIR VALUE GAP (FVG) 3-CANDLE IMBALANCE', 20, 30);

    const candles = [
        { open: 260, high: 240, low: 270, close: 245, bull: true }, // C1
        { open: 245, high: 110, low: 245, close: 120, bull: true }, // C2 (Big impulse)
        { open: 120, high: 90, low: 160, close: 100, bull: true },  // C3
        { open: 100, high: 95, low: 210, close: 200, bull: false }, // Retest into FVG
        { open: 200, high: 70, low: 200, close: 80, bull: true }
    ];

    const startX = 120;
    const gap = (w - 240) / candles.length;

    // FVG Cyan Highlight
    ctx.fillStyle = 'rgba(6, 182, 212, 0.25)';
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 1.5;
    ctx.fillRect(startX, 160, gap * 3.5, 80);
    ctx.strokeRect(startX, 160, gap * 3.5, 80);

    ctx.fillStyle = '#06b6d4';
    ctx.font = '600 12px JetBrains Mono';
    ctx.fillText('FAIR VALUE GAP (Imbalance between C1 High & C3 Low)', startX + 20, 205);

    candles.forEach((c, idx) => {
        const x = startX + idx * gap;
        drawCandle(ctx, x, c.open, c.high, c.low, c.close, 18, c.bull);
    });
}

function drawSweepCanvas(ctx, w, h) {
    ctx.fillStyle = '#f8fafc';
    ctx.font = '600 16px Outfit';
    ctx.fillText('LIQUIDITY SWEEP (STOP HUNT) ABOVE EQUAL HIGHS (EQH)', 20, 30);

    const candles = [
        { open: 190, high: 140, low: 200, close: 150, bull: true },
        { open: 150, high: 145, low: 180, close: 175, bull: false },
        { open: 175, high: 140, low: 185, close: 148, bull: true },
        { open: 148, high: 90, low: 160, close: 200, bull: false }, // SWEEP WICK
        { open: 200, high: 195, low: 280, close: 270, bull: false }  // DISPLACEMENT DOWN
    ];

    const startX = 120;
    const gap = (w - 240) / candles.length;

    // Equal Highs Dotted Line
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(startX - 30, 140);
    ctx.lineTo(w - 100, 140);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#ef4444';
    ctx.font = '600 12px JetBrains Mono';
    ctx.fillText('EQUAL HIGHS (BUY SIDE LIQUIDITY RAIDED)', startX + 10, 130);

    candles.forEach((c, idx) => {
        const x = startX + idx * gap;
        drawCandle(ctx, x, c.open, c.high, c.low, c.close, 18, c.bull);
    });
}
