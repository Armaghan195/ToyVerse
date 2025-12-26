import '../css/variables.css';
import '../css/style.css';
import '../css/search.css';
import api from './api.js';
import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';

renderNavbar('#catalog-navbar', 'catalog');
initChatbot();

// State
let allProducts = [];
let wishlistProductIds = new Set(); // Track wishlisted product IDs
let filters = {
  category: [],
  priceMax: 500,
  rating: 0,
  inStock: false,
  search: ''
};

// DOM Elements
const grid = document.querySelector('.shop-grid');
const priceRange = document.querySelector('.price-range');
const searchInput = document.getElementById('search-input');
const priceValDisplay = document.getElementById('price-val');

// --- RENDER ---
function render(products) {
  if (!products || products.length === 0) {
    grid.innerHTML = '<div class="no-results">No products found matching your criteria.</div>';
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

    // Check if product is in wishlist
    const isWishlisted = wishlistProductIds.has(item.id);
    const heartClass = isWishlisted ? 'heart-btn wishlisted' : 'heart-btn';

    return `
        <div class="shop-card" data-id="${item.id}">
            <button class="${heartClass}" data-product-id="${item.id}" onclick="event.stopPropagation(); toggleWishlist(${item.id})">❤</button>
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

      // Track product view for recommendations
      const viewHistory = JSON.parse(localStorage.getItem('product_view_history') || '[]');
      const product = allProducts.find(p => String(p.id) === String(id));

      if (product) {
        viewHistory.unshift({
          product_id: id,
          category: product.category,
          timestamp: new Date().toISOString(),
          type: 'view'
        });

        // Keep only last 50 interactions
        localStorage.setItem('product_view_history', JSON.stringify(viewHistory.slice(0, 50)));
      }

      window.location.href = `/pages/product-details.html?id=${id}`;
    });
  });

  // Attach Event Listeners to Buttons
  document.querySelectorAll('.add-cart-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = e.target.dataset.id;
      addToCart(id);
    });
  });

  document.querySelectorAll('.buy-now-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = e.target.dataset.id;
      addToCart(id, true);
    });
  });
}

// --- FILTERING ---
function applyFilters() {
  let result = [...allProducts];

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
    const val = e.target.value; // Use value attribute directly
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

    // Update Label
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

// --- DATA LOADING & ACTIONS ---
async function loadWishlistState() {
  try {
    const token = localStorage.getItem('access_token');
    if (token) {
      const data = await api.getWishlistProductIds();
      wishlistProductIds = new Set(data.product_ids || []);
    }
  } catch (err) {
    console.error('Failed to load wishlist state', err);
    // Not logged in or error - continue without wishlist
    wishlistProductIds = new Set();
  }
}

async function loadProducts() {
  grid.innerHTML = '<div class="no-results">Loading products...</div>';
  try {
    // Load wishlist state first
    await loadWishlistState();

    const products = await api.getProducts();
    // Normalize fields
    allProducts = products.map(p => ({
      ...p,
      rating: p.rating || 0,
      reviews: p.reviews || 0,
      price: parseFloat(p.price)
    }));

    // Check URL Search
    const params = new URLSearchParams(window.location.search);
    const searchParam = params.get('search');
    if (searchParam) {
      filters.search = decodeURIComponent(searchParam);
      if (searchInput) searchInput.value = filters.search;
      applyFilters();
    } else {
      render(allProducts);
    }
  } catch (err) {
    console.error('Failed to load products', err);
    grid.innerHTML = `<div class="no-results" style="color:red;">Unable to load products. ${err.message}</div>`;
  }
}

async function addToCart(id, goToCart = false) {
  const product = allProducts.find(p => String(p.id) === String(id));
  if (!product) {
    alert('Product not found.');
    return;
  }

  try {
    await api.addToCart(product.id, 1);
    alert(`${product.title} added to cart!`);
    window.dispatchEvent(new Event('cart-updated'));
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

// Toggle wishlist (global function for onclick)
window.toggleWishlist = async function(productId) {
  const product = allProducts.find(p => p.id === productId);
  if (!product) {
    alert('Product not found.');
    return;
  }

  const isCurrentlyWishlisted = wishlistProductIds.has(productId);

  try {
    if (isCurrentlyWishlisted) {
      // Remove from wishlist
      await api.removeFromWishlist(productId);
      wishlistProductIds.delete(productId);

      // Update button immediately
      const heartBtn = document.querySelector(`.heart-btn[data-product-id="${productId}"]`);
      if (heartBtn) {
        heartBtn.classList.remove('wishlisted');
      }

      // Show notification
      showNotification(`💔 Removed from wishlist`, 'info');
    } else {
      // Add to wishlist
      await api.addToWishlist(productId);
      wishlistProductIds.add(productId);

      // Update button immediately
      const heartBtn = document.querySelector(`.heart-btn[data-product-id="${productId}"]`);
      if (heartBtn) {
        heartBtn.classList.add('wishlisted');
      }

      // Show notification
      showNotification(`❤️ Added to wishlist!`, 'success');
    }
  } catch (err) {
    console.error('Wishlist toggle failed', err);
    if (err.message && err.message.toLowerCase().includes('unauthorized')) {
      alert('Please log in to manage your wishlist.');
      window.location.href = '/pages/auth.html';
    } else {
      alert(`Could not update wishlist: ${err.message}`);
    }
  }
}

// Helper function to show notifications
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `wishlist-notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 100px;
    right: 20px;
    background: ${type === 'success' ? 'linear-gradient(135deg, #4caf50, #66bb6a)' : 'linear-gradient(135deg, #2196f3, #42a5f5)'};
    color: white;
    padding: 15px 25px;
    border-radius: 50px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    z-index: 10000;
    font-weight: 600;
    font-size: 1rem;
    animation: slideIn 0.3s ease;
  `;

  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(400px);
        opacity: 0;
      }
    }
  `;
  if (!document.querySelector('#wishlist-notification-styles')) {
    style.id = 'wishlist-notification-styles';
    document.head.appendChild(style);
  }

  document.body.appendChild(notification);

  // Auto remove after 3 seconds
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Initial Render
document.addEventListener('DOMContentLoaded', () => {
  // Inject extra styles for "Buy Now" button and wishlist heart if not in CSS
  const style = document.createElement('style');
  style.innerHTML = `
        .card-actions { display: flex; gap: 0.5rem; margin-top: 1rem; }
        .buy-now-btn { flex: 1; background: var(--accent-orange); color: white; border: none; padding: 0.5rem; border-radius: 8px; cursor: pointer; font-weight: bold;}
        .add-cart-btn { flex: 1; }
        .shop-card { cursor: pointer; transition: transform 0.2s; }
        .shop-card:hover { transform: translateY(-5px); }

        /* Wishlist heart button styles */
        .heart-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10;
            filter: grayscale(1);
        }

        .heart-btn:hover {
            transform: scale(1.15);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        }

        .heart-btn.wishlisted {
            filter: grayscale(0);
            background: rgba(255, 255, 255, 1);
            animation: heartBeat 0.3s ease;
        }

        @keyframes heartBeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
    `;
  document.head.appendChild(style);

  loadProducts();
});
