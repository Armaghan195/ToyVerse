import '../css/variables.css';
import '../css/style.css';
import '../css/search.css';
import api from './api.js';
import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';

renderNavbar('#suggestions-navbar', 'brand-suggestions');
initChatbot();

// State
let allRecommendations = [];
let filters = {
  category: [],
  priceMax: 200,
  rating: 0,
  inStock: false,
  search: '',
  recType: 'all'
};

// DOM Elements
const grid = document.querySelector('.shop-grid');
const priceRange = document.querySelector('.price-range');
const searchInput = document.getElementById('search-input');
const priceValDisplay = document.getElementById('price-val');
const statusMessage = document.getElementById('status-message');
const clearHistoryBtn = document.getElementById('clear-history-btn');

// --- RENDER ---
function render(products) {
  if (!products || products.length === 0) {
    grid.innerHTML = `
      <div class="no-results" style="text-align: center; padding: 3rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🎁</div>
        <h3>No recommendations yet!</h3>
        <p style="color: #777; margin: 1rem 0;">Browse products in the catalog to get personalized recommendations.</p>
        <a href="/pages/catalog.html" style="display: inline-block; padding: 1rem 2rem; background: var(--accent-blue); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 1rem;">
          Browse Catalog
        </a>
      </div>
    `;
    return;
  }

  grid.innerHTML = products.map(item => {
    // Image Logic
    let imageHtml = `<div class="shop-icon">${item.icon || '🧸'}</div>`;
    if (item.images && item.images.length > 0) {
      imageHtml = `<img src="${item.images[0]}" alt="${item.title}" style="width:100%; height:100%; object-fit:contain; border-radius:10px;">`;
    }

    const ratingVal = item.rating ?? 0;
    const reviewsVal = item.reviews ?? 0;
    const reason = item.reason || 'Recommended for you';

    return `
        <div class="shop-card" data-id="${item.id}">
            <div class="rec-badge" style="position: absolute; top: 10px; left: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; z-index: 10;">
              ✨ ${reason}
            </div>
            <button class="heart-btn" onclick="event.stopPropagation(); alert('Added to Wishlist!')">❤</button>
            <div class="shop-icon-container">
               ${imageHtml}
            </div>
            <div class="shop-details">
                <h3>${item.title}</h3>
                <div class="rating-container">
                  <span class="stars">${'★'.repeat(ratingVal)}${'☆'.repeat(5 - ratingVal)}</span>
                  <span class="reviews">(${reviewsVal})</span>
                </div>
                <div class="price">$${Number(item.price).toFixed(2)}</div>

                <div class="card-actions" onclick="event.stopPropagation()">
                    <button class="add-cart-btn" data-id="${item.id}">Add to Cart</button>
                    <button class="buy-now-btn" data-id="${item.id}">Buy Now</button>
                </div>
            </div>
        </div>
    `;
  }).join('');

  // Attach Card Click Listeners for Detail View
  document.querySelectorAll('.shop-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      // Product view will be tracked on product-details page
      window.location.href = `/pages/product-details.html?id=${id}`;
    });
  });

  // Attach Event Listeners to Buttons
  document.querySelectorAll('.add-cart-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.target.dataset.id;
      await addToCart(id);
    });
  });

  document.querySelectorAll('.buy-now-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.target.dataset.id;
      await addToCart(id, true);
    });
  });
}

// --- FILTERING ---
function applyFilters() {
  let result = [...allRecommendations];

  // Category
  if (filters.category.length > 0) {
    result = result.filter(p => filters.category.includes(p.category));
  }

  // Price
  result = result.filter(p => Number(p.price) <= filters.priceMax);

  // Search
  if (filters.search) {
    const term = filters.search.toLowerCase();
    result = result.filter(p =>
      p.title.toLowerCase().includes(term) ||
      (p.description && p.description.toLowerCase().includes(term))
    );
  }

  // Rating
  if (filters.rating > 0) {
    result = result.filter(p => (p.rating ?? 0) >= filters.rating);
  }

  // Stock
  if (filters.inStock) {
    result = result.filter(p => (p.stock ?? 0) > 0);
  }

  render(result);
}

// Sidebar Listeners
if (searchInput) {
  searchInput.addEventListener('input', (e) => {
    filters.search = e.target.value.trim();
    applyFilters();
  });
}

document.querySelectorAll('.filter-group input[type="checkbox"]').forEach(box => {
  // Skip if it's the stock checker
  if (box.id === 'stock-check') return;

  box.addEventListener('change', (e) => {
    const val = e.target.value;
    if (e.target.checked) {
      filters.category.push(val);
    } else {
      filters.category = filters.category.filter(c => c !== val);
    }
    applyFilters();
  });
});

if (priceRange) {
  priceRange.addEventListener('input', (e) => {
    const val = Number(e.target.value);
    filters.priceMax = val;

    if (priceValDisplay) {
      priceValDisplay.innerText = `$${val}`;
    }

    applyFilters();
  });
}

document.querySelectorAll('input[name="rating"]').forEach(radio => {
  radio.addEventListener('change', (e) => {
    filters.rating = parseInt(e.target.value, 10);
    applyFilters();
  });
});

const stockCheck = document.getElementById('stock-check');
if (stockCheck) {
  stockCheck.addEventListener('change', (e) => {
    filters.inStock = e.target.checked;
    applyFilters();
  });
}

// Recommendation Type Filter
document.querySelectorAll('input[name="rec-type"]').forEach(radio => {
  radio.addEventListener('change', (e) => {
    filters.recType = e.target.value;
    loadRecommendations();
  });
});

// Clear History Button
if (clearHistoryBtn) {
  clearHistoryBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear your browsing history? This will reset your recommendations.')) {
      localStorage.removeItem('product_view_history');
      localStorage.removeItem('product_categories_viewed');
      alert('Browsing history cleared!');
      loadRecommendations();
    }
  });
}

// --- GENERATE RECOMMENDATIONS ---
async function generateRecommendations() {
  try {
    const viewHistory = JSON.parse(localStorage.getItem('product_view_history') || '[]');
    const allProducts = await api.getProducts();

    if (viewHistory.length === 0) {
      // No history - return popular products
      return allProducts
        .sort((a, b) => (b.rating * (b.reviews || 1)) - (a.rating * (a.reviews || 1)))
        .slice(0, 12)
        .map(p => ({ ...p, reason: 'Popular' }));
    }

    // Get viewed product IDs
    const viewedIds = viewHistory.map(v => v.product_id);
    const viewedProducts = allProducts.filter(p => viewedIds.includes(String(p.id)));

    // Count category frequencies to find user's preferred categories
    const categoryCount = {};
    viewedProducts.forEach(p => {
      categoryCount[p.category] = (categoryCount[p.category] || 0) + 1;
    });

    // Sort categories by frequency (most viewed first)
    const sortedCategories = Object.entries(categoryCount)
      .sort((a, b) => b[1] - a[1])
      .map(entry => entry[0]);

    // Store categories for future use
    localStorage.setItem('product_categories_viewed', JSON.stringify(sortedCategories));

    let recommendations = [];

    // PRIORITY 1: Category-based recommendations (user's interest)
    if (filters.recType === 'all' || filters.recType === 'category') {
      // For each preferred category, get products sorted by rating
      sortedCategories.forEach(category => {
        const categoryProducts = allProducts
          .filter(p => p.category === category && !viewedIds.includes(String(p.id)))
          .sort((a, b) => (b.rating * (b.reviews || 1)) - (a.rating * (a.reviews || 1)))
          .slice(0, 8) // Get top 8 from each category
          .map(p => ({
            ...p,
            reason: `You like ${category}`,
            categoryScore: categoryCount[category] // Track how much user likes this category
          }));

        recommendations.push(...categoryProducts);
      });
    }

    // PRIORITY 2: Similar price range (if user has consistent budget)
    if (filters.recType === 'all' || filters.recType === 'viewed') {
      const avgPrice = viewedProducts.reduce((sum, p) => sum + Number(p.price), 0) / viewedProducts.length;
      const priceRange = allProducts
        .filter(p => {
          const price = Number(p.price);
          return !viewedIds.includes(String(p.id)) &&
                 price >= avgPrice * 0.7 &&
                 price <= avgPrice * 1.3 &&
                 sortedCategories.includes(p.category); // Prefer same categories
        })
        .sort((a, b) => (b.rating * (b.reviews || 1)) - (a.rating * (a.reviews || 1)))
        .slice(0, 5)
        .map(p => ({ ...p, reason: 'Matches your budget' }));

      recommendations.push(...priceRange);
    }

    // PRIORITY 3: Popular products from preferred categories
    if (filters.recType === 'all' || filters.recType === 'popular') {
      const popularInCategories = allProducts
        .filter(p => sortedCategories.includes(p.category) && !viewedIds.includes(String(p.id)))
        .sort((a, b) => (b.rating * (b.reviews || 1)) - (a.rating * (a.reviews || 1)))
        .slice(0, 8)
        .map(p => ({ ...p, reason: 'Trending in your interests' }));

      recommendations.push(...popularInCategories);
    }

    // Remove duplicates, prioritize by category score
    const uniqueRecs = [];
    const seenIds = new Set();

    // Sort by category score first (categories user viewed most)
    recommendations.sort((a, b) => (b.categoryScore || 0) - (a.categoryScore || 0));

    for (const rec of recommendations) {
      if (!seenIds.has(rec.id)) {
        seenIds.add(rec.id);
        uniqueRecs.push(rec);
      }
    }

    return uniqueRecs.slice(0, 20);
  } catch (error) {
    console.error('Error generating recommendations:', error);
    return [];
  }
}

// --- DATA LOADING & ACTIONS ---
async function loadRecommendations() {
  grid.innerHTML = '<div class="loading-state">Loading your personalized recommendations... ✨</div>';

  try {
    const user = JSON.parse(localStorage.getItem('current_user') || 'null');
    const viewHistory = JSON.parse(localStorage.getItem('product_view_history') || '[]');

    // Count category preferences
    const categoryCount = {};
    viewHistory.forEach(item => {
      if (item.category) {
        categoryCount[item.category] = (categoryCount[item.category] || 0) + 1;
      }
    });

    const topCategories = Object.entries(categoryCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(entry => entry[0]);

    // Update status message
    if (statusMessage) {
      if (viewHistory.length === 0) {
        statusMessage.innerHTML = `🎯 Browse products in the catalog to get personalized recommendations based on your interests!`;
      } else if (topCategories.length > 0) {
        const categoriesText = topCategories.join(', ');
        const userName = user ? `<strong>${user.full_name || user.username}</strong>` : 'there';
        statusMessage.innerHTML = `👋 Hey ${userName}! We noticed you like <strong>${categoriesText}</strong> products. Here are recommendations based on your interests (${viewHistory.length} products viewed).`;
      } else if (user) {
        statusMessage.innerHTML = `👋 Welcome back, <strong>${user.full_name || user.username}</strong>! Here are your personalized recommendations based on ${viewHistory.length} product views.`;
      } else {
        statusMessage.innerHTML = `🎯 Showing recommendations based on your browsing activity (${viewHistory.length} products viewed).`;
      }
    }

    // Try to get recommendations from backend first
    let recommendations = [];
    try {
      if (user) {
        // If logged in, try to get from backend
        recommendations = await api.getRecommendations(filters.recType);
      }
    } catch (err) {
      console.log('Backend recommendations not available, using local algorithm:', err.message);
    }

    // If backend fails or no user, use local algorithm
    if (!recommendations || recommendations.length === 0) {
      recommendations = await generateRecommendations();
    }

    allRecommendations = recommendations.map(p => ({
      ...p,
      rating: p.rating || 0,
      reviews: p.reviews || 0,
      price: parseFloat(p.price)
    }));

    render(allRecommendations);
  } catch (err) {
    console.error('Failed to load recommendations', err);
    grid.innerHTML = `<div class="no-results" style="color:red;">Unable to load recommendations. ${err.message}</div>`;
  }
}

async function addToCart(id, goToCart = false) {
  const product = allRecommendations.find(p => String(p.id) === String(id));
  if (!product) {
    alert('Product not found.');
    return;
  }

  try {
    await api.addToCart(product.id, 1);

    // Track interaction
    const viewHistory = JSON.parse(localStorage.getItem('product_view_history') || '[]');
    viewHistory.unshift({
      product_id: product.id,
      timestamp: new Date().toISOString(),
      type: 'add_to_cart'
    });
    localStorage.setItem('product_view_history', JSON.stringify(viewHistory.slice(0, 50)));

    alert(`${product.title} added to cart!`);
    if (goToCart) window.location.href = '/pages/cart.html';
  } catch (err) {
    console.error('Add to cart failed', err);
    if (err.message && err.message.toLowerCase().includes('unauthorized')) {
      alert('Please log in to add items to your cart.');
      window.location.href = '/pages/auth.html';
    } else {
      alert(`Could not add to cart: ${err.message}`);
    }
  }
}

// Initial Render
document.addEventListener('DOMContentLoaded', () => {
  // Inject extra styles
  const style = document.createElement('style');
  style.innerHTML = `
        .card-actions { display: flex; gap: 0.5rem; margin-top: 1rem; }
        .buy-now-btn { flex: 1; background: var(--accent-orange); color: white; border: none; padding: 0.5rem; border-radius: 8px; cursor: pointer; font-weight: bold;}
        .add-cart-btn { flex: 1; }
        .shop-card { cursor: pointer; transition: transform 0.2s; position: relative; }
        .shop-card:hover { transform: translateY(-5px); }
        .loading-state { text-align: center; padding: 3rem; font-size: 1.2rem; color: #666; }
        .no-results { text-align: center; padding: 3rem; font-size: 1.1rem; color: #666; }
    `;
  document.head.appendChild(style);

  loadRecommendations();
});
