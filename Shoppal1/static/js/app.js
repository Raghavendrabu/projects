// Shoppal India - Core Frontend Logic
let appState = {
    currentCategory: 'All',
    searchQuery: '',
    user: null,
    favorites: [],
    activeProduct: null,
    chartInstance: null,
    cachedProducts: [],
    filters: {
        brands: [],
        priceRange: null,
        rating: 0,
        discount: 0,
        inStock: false,
        freeDelivery: false
    }
};

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    checkSystemStatus();
    checkAuthStatus();
    loadCatalog();
});

// 1. Fetch System & Database Health
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/system-status');
        const data = await response.json();
        const dbDisplay = document.getElementById('db-type-display');
        
        if (data.mongodb_connected) {
            dbDisplay.innerHTML = `<span class="text-emerald-400 font-extrabold"><i class="fa-solid fa-leaf"></i> MongoDB (Active Production)</span>`;
        } else {
            dbDisplay.innerHTML = `<span class="text-amber-400 font-extrabold"><i class="fa-solid fa-file-code"></i> JSON Fallback (Bulletproof Failover)</span>`;
        }
    } catch (e) {
        console.error("System status check failed: ", e);
    }
}

// 2. Session Authentication Checker
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        
        const authButtons = document.getElementById('auth-buttons');
        const userProfile = document.getElementById('user-profile');
        const usernameDisplay = document.getElementById('username-display');
        
        if (data.logged_in) {
            appState.user = data.user;
            authButtons.classList.add('hidden');
            userProfile.classList.remove('hidden');
            userProfile.classList.add('flex');
            usernameDisplay.innerText = data.user.name;
            // Fetch favorited list in background
            loadFavorites();
        } else {
            appState.user = null;
            authButtons.classList.remove('hidden');
            userProfile.classList.add('hidden');
            userProfile.classList.remove('flex');
        }
    } catch (e) {
        console.error("Auth status verification failed:", e);
    }
}

// 3. Load Main Catalog
async function loadCatalog(keepFilters = false) {
    const grid = document.getElementById('products-grid');
    const resultsCount = document.getElementById('results-count');
    
    // Set loader spinner
    grid.innerHTML = `
        <div class="col-span-full py-24 flex flex-col items-center justify-center text-white space-y-4 animate__animated animate__fadeIn">
            <div class="loader"></div>
            <p class="font-semibold text-lg text-indigo-100">Curating verified comparison deals...</p>
        </div>
    `;
    
    if (!keepFilters) {
        appState.filters = {
            brands: [],
            priceRange: null,
            rating: 0,
            discount: 0,
            inStock: false,
            freeDelivery: false
        };
        resetFilterDOM();
    }
    
    try {
        let url = `/api/products?category=${encodeURIComponent(appState.currentCategory)}`;
        if (appState.searchQuery) {
            url += `&q=${encodeURIComponent(appState.searchQuery)}`;
        }
        
        const response = await fetch(url);
        const products = await response.json();
        
        appState.cachedProducts = products;
        
        // Populate the dynamic filters panel based on these fetched products
        renderDynamicFilterOptions();
        
        // Update the dynamic matching count
        updateFiltersCount();
        
        if (keepFilters) {
            // Apply current filters to local cache and display
            applyAdvancedFilters();
        } else {
            resultsCount.innerText = `${products.length} product(s) found`;
            
            if (products.length === 0) {
                grid.innerHTML = `
                    <div class="col-span-full py-16 text-center text-white space-y-4">
                        <div class="text-5xl"><i class="fa-solid fa-magnifying-glass"></i></div>
                        <h3 class="font-display font-bold text-xl">No matching deals found</h3>
                        <p class="text-indigo-200 text-sm max-w-md mx-auto">Try typing another product name or brand (e.g. sunscreen, jeans, Milton, Prestige, boAt).</p>
                        <button onclick="resetFilters()" class="bg-white text-brand-600 font-bold px-6 py-2.5 rounded-xl shadow-md">Clear Search Filters</button>
                    </div>
                `;
                return;
            }
            
            renderProductGrid(products, 'products-grid');
        }
    } catch (e) {
        console.error("Error loading products:", e);
        grid.innerHTML = `
            <div class="col-span-full py-12 text-center text-white space-y-4 bg-white/10 rounded-2xl p-6 border border-white/10">
                <i class="fa-solid fa-triangle-exclamation text-amber-300 text-3xl"></i>
                <h3 class="font-bold">Failed to load product catalog</h3>
                <p class="text-sm">Verify that your flask server backend is running on python app.py.</p>
            </div>
        `;
    }
}

// 4. Load User's Watchlist
async function loadFavorites() {
    if (!appState.user) return;
    
    const grid = document.getElementById('favorites-grid');
    const emptyState = document.getElementById('favs-empty-state');
    
    try {
        const response = await fetch('/api/favorites');
        if (response.status === 401) return; // not logged in
        
        const products = await response.json();
        appState.favorites = products.map(p => p._id);
        
        if (products.length === 0) {
            grid.innerHTML = '';
            emptyState.classList.remove('hidden');
        } else {
            emptyState.classList.add('hidden');
            renderProductGrid(products, 'favorites-grid');
        }
    } catch (e) {
        console.error("Error loading favorites:", e);
    }
}

// 5. Render E-Commerce Grid Cards
function renderProductGrid(products, gridId) {
    const grid = document.getElementById(gridId);
    grid.innerHTML = '';
    
    products.forEach(p => {
        const isFav = appState.favorites.includes(p._id) || p.is_favorited;
        const favIconClass = isFav ? 'fa-solid fa-heart text-rose-500' : 'fa-regular fa-heart text-gray-400 hover:text-rose-500';
        
        // Dynamically assign category emoji representation
        let catIcon = "🧴";
        if (p.category === "Clothing") catIcon = "👗";
        else if (p.category === "Kitchen") catIcon = "🍳";
        else if (p.category === "Stationery") catIcon = "📚";
        else if (p.category === "Electronics") catIcon = "💻";
        else if (p.category === "Grocery") catIcon = "🛒";
        
        // Render rating stars HTML
        let starsHTML = '';
        const fullStars = Math.floor(p.rating);
        for(let i=0; i<5; i++) {
            if(i < fullStars) {
                starsHTML += `<i class="fa-solid fa-star text-amber-400"></i>`;
            } else if (i === fullStars && p.rating % 1 !== 0) {
                starsHTML += `<i class="fa-solid fa-star-half-stroke text-amber-400"></i>`;
            } else {
                starsHTML += `<i class="fa-regular fa-star text-gray-300"></i>`;
            }
        }
        
        // Competitors prices HTML as direct search-result links
        let competitorsHTML = '';
        p.vendors.forEach(v => {
            competitorsHTML += `
                <a href="${v.link}" target="_blank" onclick="event.stopPropagation();" class="flex items-center justify-between text-xs border-b border-gray-50 pb-1.5 pt-0.5 hover:text-brand-600 transition-colors block">
                    <span class="text-gray-500 font-semibold uppercase tracking-wider">${v.name}:</span>
                    <span class="font-bold text-gray-900 flex items-center gap-1">₹${v.price} <i class="fa-solid fa-arrow-up-right-from-square text-[8px] text-gray-400"></i></span>
                </a>
            `;
        });

        // AI prediction badge color styling
        let predictionClass = "bg-indigo-50 border-indigo-200 text-brand-700";
        if (p.ai_insight && p.ai_insight.includes("Best")) {
            predictionClass = "bg-emerald-50 border-emerald-200 text-emerald-700 font-bold";
        }
        
        // Find cheapest vendor for split action redirects
        const cheapestVendor = p.vendors.reduce((prev, current) => (prev.price < current.price) ? prev : current);
        
        const card = document.createElement('div');
        card.className = `glass-card rounded-3xl shadow-lg p-5 border border-gray-150 flex flex-col justify-between hover:shadow-2xl transition-all duration-300 group hover:-translate-y-1 animate__animated animate__fadeInUp cursor-pointer`;
        card.onclick = () => viewProductDetail(p._id);
        
        card.innerHTML = `
            <div class="relative space-y-4">
                <!-- Card Header Image Area -->
                <div class="relative bg-gray-50 rounded-2xl h-44 flex items-center justify-center overflow-hidden border border-gray-100/50">
                    ${p.image ? `
                        <img src="${p.image}" alt="${p.title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                    ` : `
                        <div class="text-5xl filter drop-shadow-md group-hover:scale-110 transition-transform duration-300">${catIcon}</div>
                    `}
                    
                    <!-- Category Badge -->
                    <span class="absolute top-3 left-3 bg-white/90 backdrop-blur-sm border border-gray-250/30 text-gray-700 px-2.5 py-1 rounded-lg text-[10px] font-extrabold uppercase tracking-wider shadow-sm">
                        ${p.category}
                    </span>
                    
                    <!-- Favorite Toggle Button -->
                    <button onclick="handleFavoriteToggle(event, '${p._id}')" class="absolute top-3 right-3 bg-white hover:bg-rose-50 p-2.5 rounded-full shadow-md flex items-center justify-center transition-all scale-95 hover:scale-105 active:scale-95 border border-gray-100">
                        <i class="${favIconClass} text-sm"></i>
                    </button>
                </div>
                
                <!-- Title & Brand -->
                <div class="space-y-1">
                    <span class="text-[10px] font-bold text-brand-500 uppercase tracking-widest">${p.brand}</span>
                    <h3 class="font-display font-extrabold text-lg text-gray-900 leading-tight group-hover:text-brand-600 transition-colors line-clamp-1 cursor-pointer">
                        ${p.title}
                    </h3>
                </div>

                <!-- Stars Ratings -->
                <div class="flex items-center gap-1.5 text-xs">
                    <div class="flex">${starsHTML}</div>
                    <span class="text-gray-500 font-semibold">${p.rating}/5</span>
                    <span class="text-gray-400">(${p.num_reviews.toLocaleString()} reviews)</span>
                </div>

                <!-- Price Area -->
                <div class="flex items-baseline gap-2 pt-1">
                    <span class="font-display font-extrabold text-2xl text-brand-600">₹${p.current_price}</span>
                    <span class="text-sm text-gray-400 line-through">₹${p.original_price}</span>
                    <span class="bg-rose-100 border border-rose-200 text-rose-700 text-xs font-black px-2 py-0.5 rounded-lg ml-auto animate-pulse">
                        ${p.discount_pct}% OFF
                    </span>
                </div>

                <!-- Live Market Pricing List -->
                <div class="bg-gray-50 rounded-xl p-3 border border-gray-100 space-y-1.5">
                    ${competitorsHTML}
                </div>

                <!-- AI Insights Panel -->
                <div class="space-y-2 border-t border-gray-100 pt-3">
                    <div class="flex items-center gap-1.5 text-xs ${predictionClass} px-2.5 py-1.5 rounded-lg border">
                        <i class="fa-solid fa-robot"></i>
                        <span>AI Insight: <span class="font-bold">${p.ai_insight}</span></span>
                    </div>
                    <div class="flex items-center gap-1.5 text-xs bg-sky-50 border-sky-100 text-sky-700 px-2.5 py-1.5 rounded-lg border">
                        <i class="fa-solid fa-shield-halved"></i>
                        <span>Discount Check: <span class="font-semibold">${p.discount_check}</span></span>
                    </div>
                    <div class="flex items-center gap-1.5 text-xs bg-amber-50 border-amber-100 text-amber-700 px-2.5 py-1.5 rounded-lg border">
                        <i class="fa-solid fa-magnifying-glass-chart"></i>
                        <span>Review Analysis: <span class="font-semibold">${p.review_sentiment}</span></span>
                    </div>
                </div>
            </div>
            
            <!-- Actions Buy Now / Compare Split -->
            <div class="pt-4 flex gap-2">
                <a href="${cheapestVendor.link}" target="_blank" onclick="event.stopPropagation();" class="flex-[2] bg-brand-600 hover:bg-brand-700 text-white font-bold py-2.5 px-3 rounded-xl text-xs transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-1 text-center">
                    <i class="fa-solid fa-cart-shopping"></i> Buy on ${cheapestVendor.name.toUpperCase()}
                </a>
                <button class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-2.5 px-3 rounded-xl text-xs transition-all flex items-center justify-center gap-1 border border-gray-200">
                    <i class="fa-solid fa-chart-line"></i> Compare
                </button>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// 6. View Product Details Modal (Fetch Dynamic Data)
async function viewProductDetail(productId) {
    try {
        const response = await fetch(`/api/products/${productId}`);
        const product = await response.json();
        
        if (response.status !== 200) {
            alert(product.error || "Failed to load product details.");
            return;
        }
        
        appState.activeProduct = product;
        
        // Show the audit button since we have an active product
        const auditBtn = document.getElementById('quick-prompt-audit');
        if (auditBtn) {
            auditBtn.classList.remove('hidden');
        }
        
        // Populate static content
        document.getElementById('modal-product-title').innerText = product.title;
        document.getElementById('modal-product-brand').innerText = product.brand;
        
        // Render Stock and Delivery Badges in modal
        const badgesContainer = document.getElementById('modal-badges-container');
        if (badgesContainer) {
            badgesContainer.innerHTML = '';
            if (product.in_stock) {
                badgesContainer.innerHTML += `
                    <span class="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded shadow-[0_0_8px_rgba(16,185,129,0.2)] flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> In Stock
                    </span>
                `;
            } else {
                badgesContainer.innerHTML += `
                    <span class="bg-red-500/20 text-red-300 border border-red-500/30 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span> Out of Stock
                    </span>
                `;
            }
            if (product.free_delivery) {
                badgesContainer.innerHTML += `
                    <span class="bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded shadow-[0_0_8px_rgba(168,85,247,0.2)] flex items-center gap-1">
                        <i class="fa-solid fa-truck text-[9px]"></i> Free Delivery
                    </span>
                `;
            }
        }
        
        const modalImg = document.getElementById('modal-product-image');
        if (modalImg) {
            if (product.image) {
                modalImg.src = product.image;
                modalImg.classList.remove('hidden');
            } else {
                modalImg.classList.add('hidden');
            }
        }
        
        // TAB 1: Real-Time Comparison Lists
        const vendorsList = document.getElementById('modal-vendors-list');
        vendorsList.innerHTML = '';
        product.vendors.forEach(v => {
            vendorsList.innerHTML += `
                <div class="bg-gray-50 p-4 rounded-2xl border border-gray-150 flex flex-col justify-between hover:bg-brand-50 hover:border-brand-300 transition-colors">
                    <div>
                        <span class="text-xs font-bold text-gray-500 uppercase tracking-widest">${v.name}</span>
                        <h5 class="font-display font-extrabold text-2xl text-gray-900 mt-1">₹${v.price}</h5>
                    </div>
                    <a href="${v.link}" target="_blank" class="mt-3 bg-white border border-gray-200 text-brand-600 hover:bg-brand-600 hover:text-white font-bold py-1.5 rounded-lg text-xs text-center transition-all shadow-sm">
                        Go to Store <i class="fa-solid fa-arrow-up-right-from-square ml-1 text-[10px]"></i>
                    </a>
                </div>
            `;
        });
        
        // Prediction Title & Details
        document.getElementById('modal-prediction-title').innerText = product.ai_price_prediction.recommendation;
        document.getElementById('modal-prediction-title').className = `font-extrabold ${product.ai_price_prediction.recommendation.includes('Buy') ? 'text-rose-600' : 'text-emerald-600'}`;
        document.getElementById('modal-prediction-detail').innerText = product.ai_price_prediction.recommendation_detail;
        
        // Buy Button
        const cheapestVendor = product.vendors.reduce((prev, current) => (prev.price < current.price) ? prev : current);
        const buyBtn = document.getElementById('modal-buy-button');
        buyBtn.href = cheapestVendor.link;
        buyBtn.innerHTML = `<i class="fa-solid fa-arrow-up-right-from-square"></i> Buy on ${cheapestVendor.name.toUpperCase()} at ₹${cheapestVendor.price}`;
        
        // TAB 2: AI Audit Reviews
        // Fake discount scores
        const fScore = product.ai_fake_discount.score;
        document.getElementById('modal-fake-discount-rating').innerText = product.ai_fake_discount.rating;
        document.getElementById('modal-fake-discount-rating').className = product.ai_fake_discount.class;
        document.getElementById('modal-fake-discount-score').innerText = `${fScore} / 100`;
        const fBar = document.getElementById('modal-fake-discount-bar');
        fBar.style.width = `${fScore}%`;
        // color grading
        if(fScore > 70) fBar.className = "bg-rose-500 h-2.5 transition-all";
        else if(fScore > 35) fBar.className = "bg-amber-500 h-2.5 transition-all";
        else fBar.className = "bg-emerald-500 h-2.5 transition-all";
        document.getElementById('modal-fake-discount-detail').innerText = product.ai_fake_discount.detail;
        
        // Sentiment breakdowns
        const sent = product.ai_sentiment;
        document.getElementById('sentiment-pos-pct').innerText = `${sent.positive_percentage}%`;
        document.getElementById('sentiment-pos-bar').style.width = `${sent.positive_percentage}%`;
        document.getElementById('sentiment-neu-pct').innerText = `${sent.neutral_percentage}%`;
        document.getElementById('sentiment-neu-bar').style.width = `${sent.neutral_percentage}%`;
        document.getElementById('sentiment-neg-pct').innerText = `${sent.negative_percentage}%`;
        document.getElementById('sentiment-neg-bar').style.width = `${sent.negative_percentage}%`;
        document.getElementById('modal-sentiment-summary').innerHTML = `<i class="fa-solid fa-brain mr-1.5 text-brand-600"></i> <strong class="text-brand-900">${sent.overall_sentiment}:</strong> ${sent.summary}`;
        
        // Customer reviews lists
        const reviewsList = document.getElementById('modal-reviews-list');
        reviewsList.innerHTML = '';
        product.reviews.forEach(r => {
            let revStars = '';
            for(let i=0; i<5; i++) {
                revStars += i < r.rating ? `<i class="fa-solid fa-star text-amber-400"></i>` : `<i class="fa-regular fa-star text-gray-300"></i>`;
            }
            
            reviewsList.innerHTML += `
                <div class="bg-gray-50 p-3.5 rounded-2xl border border-gray-100 text-xs space-y-2">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="font-bold text-gray-800">${r.user}</span>
                            <div class="flex gap-0.5">${revStars}</div>
                        </div>
                        <span class="text-gray-400 text-[10px]">${r.date}</span>
                    </div>
                    <p class="text-gray-600 leading-relaxed">${r.text}</p>
                </div>
            `;
        });
        
        // TAB 3: Similar Products Grid
        const simGrid = document.getElementById('modal-similar-grid');
        simGrid.innerHTML = '';
        if(product.similar_products.length === 0) {
            simGrid.innerHTML = `<div class="col-span-full text-center text-gray-400 text-xs py-6">No matching alternative products found.</div>`;
        } else {
            product.similar_products.forEach(s => {
                simGrid.innerHTML += `
                    <div class="bg-white p-4 border border-gray-150 rounded-2xl shadow-sm hover:border-brand-500 hover:shadow-md transition-all flex flex-col justify-between cursor-pointer" onclick="viewProductDetail('${s._id}')">
                        <div class="space-y-3">
                            <!-- Crop-cropped thumbnail visual -->
                            ${s.image ? `
                                <div class="w-full h-28 rounded-xl overflow-hidden bg-gray-50 border border-gray-100 shadow-sm">
                                    <img src="${s.image}" alt="${s.title}" class="w-full h-full object-cover">
                                </div>
                            ` : ''}
                            <div>
                                <span class="text-[9px] font-bold text-brand-500 uppercase tracking-widest">${s.brand}</span>
                                <h5 class="font-bold text-gray-900 text-sm line-clamp-1">${s.title}</h5>
                                <div class="flex items-baseline gap-1.5 pt-2">
                                    <span class="font-display font-extrabold text-base text-brand-600">₹${s.current_price}</span>
                                    <span class="text-xs text-gray-400 line-through">₹${s.original_price}</span>
                                </div>
                            </div>
                        </div>
                        <button class="w-full bg-brand-50 text-brand-700 hover:bg-brand-600 hover:text-white font-bold py-1.5 rounded-lg text-[10px] text-center mt-3 transition-colors">
                            Compare Deal <i class="fa-solid fa-chevron-right ml-0.5"></i>
                        </button>
                    </div>
                `;
            });
        }

        // Open Modal and render dynamic Chart
        openModal('product-detail-modal');
        switchTab('tab-comparison');
        setTimeout(() => renderPriceChart(product), 250);
        
    } catch(e) {
        console.error("Failed to render modal data: ", e);
        alert("Unexpected error parsing detailed product catalog.");
    }
}

// 7. Render Chart.js Multi-Line Graph
function renderPriceChart(product) {
    const ctx = document.getElementById('priceHistoryChart').getContext('2d');
    
    // Clear previous instance
    if (appState.chartInstance) {
        appState.chartInstance.destroy();
    }
    
    const history = product.price_history;
    const labels = history.map(h => h.date);
    
    // Vendor datasets
    const vendorNames = product.vendors.map(v => v.name);
    
    // Build datasets for each vendor
    const datasets = [];
    
    const colors = {
        'amazon': { border: '#38bdf8', bg: 'rgba(56, 189, 248, 0.1)' },
        'flipkart': { border: '#f97316', bg: 'rgba(249, 115, 22, 0.1)' },
        'nykaa': { border: '#ec4899', bg: 'rgba(236, 72, 153, 0.1)' },
        'myntra': { border: '#a855f7', bg: 'rgba(168, 85, 247, 0.1)' },
        'reliance': { border: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' },
        'tatacliq': { border: '#06b6d4', bg: 'rgba(6, 182, 212, 0.1)' },
        'dmart': { border: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' }
    };
    
    vendorNames.forEach(vendor => {
        const prices = history.map(h => h[vendor] || h.amazon || h.flipkart);
        const col = colors[vendor] || { border: '#6366f1', bg: 'rgba(99, 102, 241, 0.1)' };
        
        datasets.push({
            label: vendor.toUpperCase(),
            data: prices,
            borderColor: col.border,
            backgroundColor: col.bg,
            borderWidth: 2,
            tension: 0.3,
            fill: false,
            pointRadius: 1,
            pointHoverRadius: 4
        });
    });
    
    // AI Predictions datasets (append at the end of the history)
    const predictions = product.ai_price_prediction.predictions_7_days;
    if (predictions && predictions.length > 0) {
        // Expand labels for predictions
        const allLabels = [...labels, ...predictions.map(p => p.date)];
        
        // Dotted forecasting line starting from last historical point
        const forecastPrices = Array(labels.length - 1).fill(null);
        
        // Add the very last historical point to connect the line cleanly
        const cheapestVendor = minVendorName(product.vendors);
        forecastPrices.push(history[history.length - 1][cheapestVendor]);
        
        // Add prediction prices
        predictions.forEach(p => forecastPrices.push(p.price));
        
        datasets.push({
            label: 'AI 7-DAY FORECAST',
            data: forecastPrices,
            borderColor: '#7c3aed',
            borderWidth: 2,
            borderDash: [5, 5],
            pointBackgroundColor: '#7c3aed',
            pointRadius: 3,
            fill: false
        });
        
        appState.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allLabels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: { family: 'Outfit', size: 10, weight: 'bold' },
                            color: '#374151'
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: { family: 'Inter', size: 9 },
                            maxRotation: 45,
                            autoSkip: true,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        grid: { color: '#f3f4f6' },
                        ticks: {
                            font: { family: 'Inter', size: 9 },
                            callback: function(value) { return '₹' + value; }
                        }
                    }
                }
            }
        });
    }
}

function minVendorName(vendors) {
    return vendors.reduce((prev, current) => (prev.price < current.price) ? prev : current).name;
}

// 8. Add / Remove Favorites (Secure Authentication Check)
async function handleFavoriteToggle(event, productId) {
    event.stopPropagation(); // prevent card opening click
    
    if (!appState.user) {
        openModal('login-modal');
        document.getElementById('login-error').innerText = "Please log in to add items to your personal watchlist.";
        document.getElementById('login-error').classList.remove('hidden');
        return;
    }
    
    try {
        const response = await fetch('/api/favorites/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });
        
        const data = await response.json();
        
        if (response.status === 200) {
            // Re-sync favorites
            loadFavorites();
            loadCatalog(true);
        } else {
            alert(data.error || "Failed to edit favorites.");
        }
    } catch(e) {
        console.error("Favorite toggler error:", e);
    }
}

// 9. UI Action Forms Handler
function filterCategory(categoryName) {
    appState.currentCategory = categoryName;
    
    // Switch active buttons
    document.querySelectorAll('.category-pill').forEach(btn => {
        btn.className = "category-pill bg-white text-gray-600 border border-gray-200 hover:border-brand-500 hover:text-brand-600 font-semibold px-4 py-2 rounded-xl text-sm transition-all hover:scale-105 flex items-center gap-1.5";
    });
    
    event.target.className = "category-pill active bg-brand-600 text-white font-semibold px-5 py-2 rounded-xl text-sm shadow-md transition-all hover:scale-105";
    
    document.getElementById('catalog-title').innerText = categoryName === 'All' ? 'Recommended AI-Powered Deals' : `Best Deals in ${categoryName}`;
    
    loadCatalog();
}

function handleSearch(event) {
    event.preventDefault();
    appState.searchQuery = document.getElementById('search-input').value.trim();
    loadCatalog();
}

function resetFilters() {
    appState.currentCategory = 'All';
    appState.searchQuery = '';
    document.getElementById('search-input').value = '';
    
    // reset pills
    document.querySelectorAll('.category-pill').forEach((btn, idx) => {
        if(idx === 0) {
            btn.className = "category-pill active bg-brand-600 text-white font-semibold px-5 py-2 rounded-xl text-sm shadow-md transition-all hover:scale-105";
        } else {
            btn.className = "category-pill bg-white text-gray-600 border border-gray-200 hover:border-brand-500 hover:text-brand-600 font-semibold px-4 py-2 rounded-xl text-sm transition-all hover:scale-105 flex items-center gap-1.5";
        }
    });
    
    document.getElementById('catalog-title').innerText = 'Recommended AI-Powered Deals';
    loadCatalog();
}

// Section routing navigation
function showSection(sectionId) {
    const home = document.getElementById('home-section');
    const favs = document.getElementById('favorites-section');
    
    const navHome = document.getElementById('nav-home');
    const navFavs = document.getElementById('nav-favs');
    
    if (sectionId === 'home') {
        home.classList.remove('hidden');
        favs.classList.add('hidden');
        
        navHome.className = "text-brand-600 bg-brand-50 font-bold py-1 px-3 rounded-lg";
        navFavs.className = "text-gray-600 hover:text-brand-600 font-semibold py-1 px-3 rounded-lg hover:bg-brand-50 flex items-center gap-1.5";
    } else {
        home.classList.add('hidden');
        favs.classList.remove('hidden');
        
        navHome.className = "text-gray-600 hover:text-brand-600 font-semibold py-1 px-3 rounded-lg hover:bg-brand-50";
        navFavs.className = "text-brand-600 bg-brand-50 font-bold py-1 px-3 rounded-lg flex items-center gap-1.5";
        
        loadFavorites();
    }
}

// Modal open/close controls
function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
    document.getElementById(modalId).classList.add('flex');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
    document.getElementById(modalId).classList.remove('flex');
    
    // Clear auth errors on close
    document.getElementById('login-error').classList.add('hidden');
    document.getElementById('signup-error').classList.add('hidden');
}

// Tab navigation within details modal
function switchTab(tabId) {
    // Hide all contents
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(tabId).classList.remove('hidden');
    
    // Deactivate all buttons
    document.querySelectorAll('.tab-btn').forEach(b => {
        b.className = "tab-btn border-b-2 border-transparent text-gray-500 font-bold text-sm px-4 py-3 hover:text-brand-600 transition-colors whitespace-nowrap";
    });
    
    // Activate clicked button
    document.getElementById(`${tabId}-btn`).className = "tab-btn active border-b-2 border-brand-600 text-brand-600 font-bold text-sm px-4 py-3 hover:text-brand-600 transition-colors whitespace-nowrap";
}

// 10. AJAX Authentication Submission
async function handleLoginSubmit(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.status === 200) {
            closeModal('login-modal');
            checkAuthStatus();
            loadCatalog();
        } else {
            errorDiv.innerText = data.error || "Authentication failed.";
            errorDiv.classList.remove('hidden');
        }
    } catch(e) {
        errorDiv.innerText = "Network connection failed. Backend offline.";
        errorDiv.classList.remove('hidden');
    }
}

async function handleSignupSubmit(event) {
    event.preventDefault();
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const errorDiv = document.getElementById('signup-error');
    
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.status === 200) {
            closeModal('signup-modal');
            checkAuthStatus();
            loadCatalog();
        } else {
            errorDiv.innerText = data.error || "Failed to create account.";
            errorDiv.classList.remove('hidden');
        }
    } catch(e) {
        errorDiv.innerText = "Network connection failed. Backend offline.";
        errorDiv.classList.remove('hidden');
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        appState.user = null;
        appState.favorites = [];
        checkAuthStatus();
        showSection('home');
        loadCatalog();
    } catch (e) {
        console.error("Failed to logout:", e);
    }
}

// 11. AI Shopping Agent Chatbot Logic
function toggleAIChat() {
    const chatWindow = document.getElementById('ai-chat-window');
    if (!chatWindow) return;
    
    if (chatWindow.classList.contains('hidden')) {
        chatWindow.classList.remove('hidden');
        chatWindow.classList.add('flex');
        // Scroll to bottom on open
        const messagesContainer = document.getElementById('ai-chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        // Focus the input field
        const chatInput = document.getElementById('ai-chat-input');
        if (chatInput) chatInput.focus();
    } else {
        chatWindow.classList.add('hidden');
        chatWindow.classList.remove('flex');
    }
}

function sendQuickPrompt(promptText) {
    const chatInput = document.getElementById('ai-chat-input');
    if (!chatInput) return;
    
    chatInput.value = promptText;
    
    // Auto-submit
    const event = { preventDefault: () => {} };
    handleAIChatSubmit(event);
}

// Simple client-side Markdown to HTML parser
function parseMarkdown(text) {
    if (!text) return '';
    let html = text;
    
    // Parse bold text (**text**)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Parse italic text (*text*)
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Parse unordered lists (- item)
    html = html.split('\n').map(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            return `<li class="ml-4 list-disc">${trimmed.substring(2)}</li>`;
        }
        return line;
    }).join('\n');
    
    // Parse bullet items or numbers starting lines
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

async function handleAIChatSubmit(event) {
    if (event && event.preventDefault) {
        event.preventDefault();
    }
    
    const chatInput = document.getElementById('ai-chat-input');
    const messagesContainer = document.getElementById('ai-chat-messages');
    const typingIndicator = document.getElementById('ai-chat-typing');
    
    if (!chatInput || !messagesContainer || !typingIndicator) return;
    
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;
    
    // 1. Clear input
    chatInput.value = '';
    
    // 2. Append User Bubble to Container
    const userBubble = document.createElement('div');
    userBubble.className = "flex items-start gap-2.5 max-w-[85%] self-end ml-auto animate__animated animate__fadeInUp";
    userBubble.innerHTML = `
        <div class="bg-brand-600 text-white p-3 rounded-2xl rounded-tr-none shadow-sm text-xs leading-relaxed">
            ${userMessage}
        </div>
        <div class="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-100 text-brand-600 flex items-center justify-center flex-shrink-0 text-xs font-bold flex items-center justify-center font-display">
            U
        </div>
    `;
    messagesContainer.appendChild(userBubble);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // 3. Show Typing Indicator
    typingIndicator.classList.remove('hidden');
    
    try {
        // 4. Fetch Response from Flask API
        const payload = {
            message: userMessage,
            product_id: appState.activeProduct ? appState.activeProduct._id : null
        };
        
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.classList.add('hidden');
        
        if (response.status === 200) {
            // 5. Append AI Bubble to Container
            const aiBubble = document.createElement('div');
            aiBubble.className = "flex items-start gap-2.5 max-w-[85%] animate__animated animate__fadeInUp";
            
            let bubbleHTML = `
                <div class="w-8 h-8 rounded-full bg-brand-100 border border-brand-200 text-brand-600 flex items-center justify-center flex-shrink-0 text-xs">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="bg-white border border-gray-150 p-3 rounded-2xl rounded-tl-none shadow-sm text-xs text-gray-800 leading-relaxed space-y-3">
                    <div>${parseMarkdown(data.response)}</div>
            `;
            
            // Render suggested products as micro cards
            if (data.suggested_products && data.suggested_products.length > 0) {
                let cardsHTML = `<div class="mt-3 pt-3 border-t border-gray-100 space-y-2">
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Recommended Products:</p>`;
                
                data.suggested_products.forEach(p => {
                    let catIcon = "🧴";
                    if (p.category === "Clothing") catIcon = "👗";
                    else if (p.category === "Kitchen") catIcon = "🍳";
                    else if (p.category === "Stationery") catIcon = "📚";
                    else if (p.category === "Electronics") catIcon = "💻";
                    else if (p.category === "Grocery") catIcon = "🛒";
                    
                    cardsHTML += `
                        <div onclick="viewProductDetail('${p._id}')" class="flex items-center gap-2.5 bg-gray-50 border border-gray-150 rounded-xl p-2 hover:bg-brand-50 hover:border-brand-300 transition-all cursor-pointer group">
                            <div class="w-10 h-10 rounded-lg overflow-hidden bg-white border border-gray-100 flex items-center justify-center flex-shrink-0 text-lg shadow-sm">
                                ${p.image ? `<img src="${p.image}" alt="${p.title}" class="w-full h-full object-cover">` : catIcon}
                            </div>
                            <div class="flex-1 min-w-0 text-left">
                                <h5 class="font-bold text-gray-900 text-[11px] line-clamp-1 group-hover:text-brand-600 transition-colors">${p.title}</h5>
                                <div class="flex items-center gap-1.5 mt-0.5">
                                    <span class="text-brand-600 font-extrabold text-[11px]">₹${p.current_price}</span>
                                    <span class="text-gray-400 line-through text-[10px]">₹${p.original_price}</span>
                                    <span class="text-rose-600 text-[9px] font-black">${p.discount_pct}% OFF</span>
                                </div>
                            </div>
                            <div class="text-gray-400 group-hover:text-brand-600 transition-colors">
                                <i class="fa-solid fa-chevron-right text-[10px]"></i>
                            </div>
                        </div>
                    `;
                });
                
                cardsHTML += `</div>`;
                bubbleHTML += cardsHTML;
            }
            
            bubbleHTML += `</div>`;
            aiBubble.innerHTML = bubbleHTML;
            messagesContainer.appendChild(aiBubble);
            
        } else {
            // Error bubble
            const errorBubble = document.createElement('div');
            errorBubble.className = "flex items-start gap-2.5 max-w-[85%] animate__animated animate__fadeInUp";
            errorBubble.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-rose-100 border border-rose-200 text-rose-600 flex items-center justify-center flex-shrink-0 text-xs">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                </div>
                <div class="bg-rose-50 border border-rose-100 text-rose-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-xs leading-relaxed">
                    Sorry, the AI Shopping Agent seems to be experiencing difficulties. Please try again.
                </div>
            `;
            messagesContainer.appendChild(errorBubble);
        }
        
    } catch(e) {
        console.error("AI chat communication failure:", e);
        typingIndicator.classList.add('hidden');
        
        const offlineBubble = document.createElement('div');
        offlineBubble.className = "flex items-start gap-2.5 max-w-[85%] animate__animated animate__fadeInUp";
        offlineBubble.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-rose-100 border border-rose-200 text-rose-600 flex items-center justify-center flex-shrink-0 text-xs">
                <i class="fa-solid fa-wifi"></i>
            </div>
            <div class="bg-rose-50 border border-rose-100 text-rose-700 p-3 rounded-2xl rounded-tl-none shadow-sm text-xs leading-relaxed">
                Network connection to AI engine failed. Please check if python app.py is running.
            </div>
        `;
        messagesContainer.appendChild(offlineBubble);
    }
    
    // Always scroll to bottom after appending message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ==========================================
// Phase 2: Dynamic Advanced Filter Utilities
// ==========================================

// Helper to reset static filter options in DOM
function resetFilterDOM() {
    // Uncheck all brands
    document.querySelectorAll('input[name="filter-brand"]').forEach(cb => {
        cb.checked = false;
    });
    
    // Reset price radio to all
    const priceAllRadio = document.querySelector('input[name="filter-price"][value="all"]');
    if (priceAllRadio) priceAllRadio.checked = true;
    
    // Reset rating radio to 0 (All Ratings)
    const ratingAllRadio = document.querySelector('input[name="filter-rating"][value="0"]');
    if (ratingAllRadio) ratingAllRadio.checked = true;
    
    // Reset discount radio to 0 (Any Discount)
    const discountAllRadio = document.querySelector('input[name="filter-discount"][value="0"]');
    if (discountAllRadio) discountAllRadio.checked = true;
    
    // Reset checkboxes
    const stockCheckbox = document.getElementById('filter-stock');
    if (stockCheckbox) stockCheckbox.checked = false;
    
    const deliveryCheckbox = document.getElementById('filter-delivery');
    if (deliveryCheckbox) deliveryCheckbox.checked = false;
}

// Generate category-specific brands and price ranges dynamically
function renderDynamicFilterOptions() {
    const brandsListContainer = document.getElementById('filter-brands-list');
    const pricesListContainer = document.getElementById('filter-prices-list');
    
    if (!brandsListContainer || !pricesListContainer) return;
    
    // 1. Dynamic Brands (extract unique from loaded category catalog)
    const brands = [...new Set(appState.cachedProducts.map(p => p.brand))].filter(Boolean).sort();
    
    brandsListContainer.innerHTML = '';
    if (brands.length === 0) {
        brandsListContainer.innerHTML = `<span class="text-xs text-gray-400">No brands found</span>`;
    } else {
        brands.forEach(brand => {
            const isChecked = appState.filters.brands.includes(brand);
            brandsListContainer.innerHTML += `
                <label class="flex items-center gap-2 text-sm text-gray-600 hover:text-brand-600 cursor-pointer font-medium">
                    <input type="checkbox" name="filter-brand" value="${brand}" ${isChecked ? 'checked' : ''} onchange="updateFiltersCount()" class="rounded text-brand-600 focus:ring-brand-500 border-gray-300">
                    <span>${brand}</span>
                </label>
            `;
        });
    }
    
    // 2. Dynamic Price Ranges matching the flowchart specs
    const cat = appState.currentCategory;
    let priceRanges = [];
    
    if (cat === 'Skincare') {
        priceRanges = [
            { label: '₹0 - ₹500', value: '0-500' },
            { label: '₹500 - ₹1000', value: '500-1000' }
        ];
    } else if (cat === 'Clothing') {
        priceRanges = [
            { label: '₹0 - ₹1000', value: '0-1000' },
            { label: '₹1000 - ₹2000', value: '1000-2000' }
        ];
    } else if (cat === 'Kitchen') {
        priceRanges = [
            { label: '₹0 - ₹500', value: '0-500' },
            { label: '₹500 - ₹1500', value: '500-1500' }
        ];
    } else if (cat === 'Stationery') {
        priceRanges = [
            { label: '₹0 - ₹100', value: '0-100' },
            { label: '₹100 - ₹500', value: '100-500' }
        ];
    } else if (cat === 'Electronics') {
        priceRanges = [
            { label: '₹0 - ₹1500', value: '0-1500' },
            { label: '₹1500 - ₹5000', value: '1500-5000' }
        ];
    } else {
        // Default range
        priceRanges = [
            { label: '₹0 - ₹500', value: '0-500' },
            { label: '₹500 - ₹1500', value: '500-1500' },
            { label: '₹1500 - ₹5000', value: '1500-5000' }
        ];
    }
    
    pricesListContainer.innerHTML = `
        <label class="flex items-center gap-2 text-sm text-gray-600 hover:text-brand-600 cursor-pointer font-medium">
            <input type="radio" name="filter-price" value="all" ${appState.filters.priceRange === null ? 'checked' : ''} onchange="updateFiltersCount()" class="rounded text-brand-600 focus:ring-brand-500 border-gray-300">
            <span>All Prices</span>
        </label>
    `;
    
    priceRanges.forEach(range => {
        const isChecked = appState.filters.priceRange === range.value;
        pricesListContainer.innerHTML += `
            <label class="flex items-center gap-2 text-sm text-gray-600 hover:text-brand-600 cursor-pointer font-medium">
                <input type="radio" name="filter-price" value="${range.value}" ${isChecked ? 'checked' : ''} onchange="updateFiltersCount()" class="rounded text-brand-600 focus:ring-brand-500 border-gray-300">
                <span>${range.label}</span>
            </label>
        `;
    });
}

// Compute client-side matching products based on active UI checkboxes/radios
function getFilteredProducts() {
    // Brand Checklist
    const brandCheckboxes = document.querySelectorAll('input[name="filter-brand"]:checked');
    const selectedBrands = Array.from(brandCheckboxes).map(cb => cb.value);
    
    // Price Range Radio
    const priceRadio = document.querySelector('input[name="filter-price"]:checked');
    const selectedPriceRange = priceRadio ? priceRadio.value : 'all';
    
    // Rating Radio
    const ratingRadio = document.querySelector('input[name="filter-rating"]:checked');
    const selectedRating = ratingRadio ? parseFloat(ratingRadio.value) : 0;
    
    // Discount Radio
    const discountRadio = document.querySelector('input[name="filter-discount"]:checked');
    const selectedDiscount = discountRadio ? parseInt(discountRadio.value) : 0;
    
    // Availability Stock Checkbox
    const stockCheckbox = document.getElementById('filter-stock');
    const inStockOnly = stockCheckbox ? stockCheckbox.checked : false;
    
    // Availability Delivery Checkbox
    const deliveryCheckbox = document.getElementById('filter-delivery');
    const freeDeliveryOnly = deliveryCheckbox ? deliveryCheckbox.checked : false;
    
    return appState.cachedProducts.filter(p => {
        // 1. Brand filter
        if (selectedBrands.length > 0 && !selectedBrands.includes(p.brand)) {
            return false;
        }
        
        // 2. Price range filter
        if (selectedPriceRange !== 'all') {
            const parts = selectedPriceRange.split('-');
            const minPrice = parseFloat(parts[0]);
            const maxPrice = parseFloat(parts[1]);
            if (p.current_price < minPrice || p.current_price > maxPrice) {
                return false;
            }
        }
        
        // 3. Rating filter
        if (p.rating < selectedRating) {
            return false;
        }
        
        // 4. Discount filter
        if (p.discount_pct < selectedDiscount) {
            return false;
        }
        
        // 5. Stock availability filter
        if (inStockOnly && !p.in_stock) {
            return false;
        }
        
        // 6. Free delivery filter
        if (freeDeliveryOnly && !p.free_delivery) {
            return false;
        }
        
        return true;
    });
}

// Instantly updates the "X products matching" indicator badge
function updateFiltersCount() {
    const filtered = getFilteredProducts();
    const badge = document.getElementById('matching-products-count');
    if (badge) {
        badge.innerText = `${filtered.length} product(s) matching`;
    }
}

// Apply selected filters, persistence in state, and render results grid
function applyAdvancedFilters() {
    const filtered = getFilteredProducts();
    const grid = document.getElementById('products-grid');
    const resultsCount = document.getElementById('results-count');
    
    // Sync filters selections into state
    const brandCheckboxes = document.querySelectorAll('input[name="filter-brand"]:checked');
    appState.filters.brands = Array.from(brandCheckboxes).map(cb => cb.value);
    
    const priceRadio = document.querySelector('input[name="filter-price"]:checked');
    appState.filters.priceRange = priceRadio && priceRadio.value !== 'all' ? priceRadio.value : null;
    
    const ratingRadio = document.querySelector('input[name="filter-rating"]:checked');
    appState.filters.rating = ratingRadio ? parseFloat(ratingRadio.value) : 0;
    
    const discountRadio = document.querySelector('input[name="filter-discount"]:checked');
    appState.filters.discount = discountRadio ? parseInt(discountRadio.value) : 0;
    
    const stockCheckbox = document.getElementById('filter-stock');
    appState.filters.inStock = stockCheckbox ? stockCheckbox.checked : false;
    
    const deliveryCheckbox = document.getElementById('filter-delivery');
    appState.filters.freeDelivery = deliveryCheckbox ? deliveryCheckbox.checked : false;
    
    resultsCount.innerText = `${filtered.length} product(s) found`;
    
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center text-white space-y-4">
                <div class="text-5xl"><i class="fa-solid fa-magnifying-glass"></i></div>
                <h3 class="font-display font-bold text-xl">No matching deals found</h3>
                <p class="text-indigo-200 text-sm max-w-md mx-auto">Try relaxing your advanced filter settings to see more products.</p>
                <button onclick="clearAdvancedFilters()" class="bg-white text-brand-600 font-bold px-6 py-2.5 rounded-xl shadow-md">Reset Advanced Filters</button>
            </div>
        `;
        return;
    }
    
    renderProductGrid(filtered, 'products-grid');
}

// Reset all selection inputs back to unfiltered defaults
function clearAdvancedFilters() {
    // 1. Reset state object
    appState.filters = {
        brands: [],
        priceRange: null,
        rating: 0,
        discount: 0,
        inStock: false,
        freeDelivery: false
    };
    
    // 2. Clear inputs in DOM
    resetFilterDOM();
    
    // 3. Update matching count label
    updateFiltersCount();
    
    // 4. Render entire catalog back to grid
    const resultsCount = document.getElementById('results-count');
    resultsCount.innerText = `${appState.cachedProducts.length} product(s) found`;
    renderProductGrid(appState.cachedProducts, 'products-grid');
}

// Collapses / Expands the Smart Filter Panel with subtle chevron rotation
function toggleFiltersPanel() {
    const content = document.getElementById('filters-content');
    const chevron = document.getElementById('filters-chevron');
    const btnText = document.getElementById('toggle-filters-text');
    
    if (!content || !chevron || !btnText) return;
    
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        chevron.classList.add('rotate-180');
        btnText.innerText = 'Collapse Filters';
    } else {
        content.classList.add('hidden');
        chevron.classList.remove('rotate-180');
        btnText.innerText = 'Expand Filters';
    }
}
