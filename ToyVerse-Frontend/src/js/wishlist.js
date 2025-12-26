import '../css/style.css';
import '../css/variables.css';
import api from './api.js';
import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';

renderNavbar('#w-navbar', 'wishlist');
initChatbot();

// DOM Elements
const container = document.getElementById('wishlist-container');
const clearAllBtn = document.getElementById('clear-all-btn');

// State
let wishlist = [];

// Load wishlist
async function loadWishlist() {
    container.innerHTML = '<div class="loading-msg">Loading your wishlist...</div>';

    try {
        const data = await api.getWishlist();
        wishlist = data || [];
        renderWishlist();
    } catch (err) {
        console.error('Failed to load wishlist:', err);
        if (err.message && err.message.toLowerCase().includes('unauthorized')) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🔒</div>
                    <h2>Please Log In</h2>
                    <p>You need to be logged in to view your wishlist.</p>
                    <a href="/pages/auth.html" class="browse-btn">Log In</a>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <h2>Error Loading Wishlist</h2>
                    <p>${err.message || 'Unable to load wishlist. Please try again later.'}</p>
                </div>
            `;
        }
    }
}

// Render wishlist
function renderWishlist() {
    if (!wishlist || wishlist.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">💔</div>
                <h2>Your Wishlist is Empty</h2>
                <p>Start adding products you love to your wishlist!</p>
                <a href="/pages/catalog.html" class="browse-btn">Browse Products</a>
            </div>
        `;
        clearAllBtn.style.display = 'none';
        return;
    }

    clearAllBtn.style.display = 'block';

    container.innerHTML = `
        <div class="wishlist-grid">
            ${wishlist.map(item => renderWishlistCard(item)).join('')}
        </div>
    `;

    // Add event listeners
    attachEventListeners();
}

// Render individual wishlist card
function renderWishlistCard(item) {
    const product = item.product || {};
    const img = product.images && product.images.length ? product.images[0] : null;

    const iconHtml = img
        ? `<img src="${img}" alt="${product.title || 'Product'}">`
        : (product.icon || '🧸');

    const stockClass = product.stock > 10 ? 'in-stock' : product.stock > 0 ? 'low-stock' : 'out-stock';
    const stockText = product.stock > 10 ? 'In Stock' : product.stock > 0 ? `Only ${product.stock} left` : 'Out of Stock';

    const stars = '⭐'.repeat(product.rating || 0);

    return `
        <div class="wishlist-card" data-product-id="${product.id}">
            <div class="product-icon-large">${iconHtml}</div>
            <h3 class="product-title">${product.title || 'Product'}</h3>
            <div class="product-price">$${Number(product.price || 0).toFixed(2)}</div>

            <div class="product-meta">
                <div class="product-rating" title="Rating: ${product.rating || 0}/5">
                    ${stars || '⭐⭐⭐⭐⭐'}
                </div>
                <span class="stock-badge ${stockClass}">${stockText}</span>
            </div>

            <div class="card-actions">
                <button class="add-to-cart-btn"
                    data-product-id="${product.id}"
                    ${product.stock <= 0 ? 'disabled' : ''}>
                    ${product.stock > 0 ? '🛒 Add to Cart' : 'Out of Stock'}
                </button>
                <button class="remove-wishlist-btn" data-product-id="${product.id}" title="Remove from wishlist">
                    💔
                </button>
            </div>
        </div>
    `;
}

// Attach event listeners
function attachEventListeners() {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', handleAddToCart);
    });

    // Remove from wishlist buttons
    document.querySelectorAll('.remove-wishlist-btn').forEach(btn => {
        btn.addEventListener('click', handleRemoveFromWishlist);
    });
}

// Handle add to cart
async function handleAddToCart(e) {
    const productId = parseInt(e.currentTarget.dataset.productId);
    const btn = e.currentTarget;
    const originalText = btn.innerHTML;

    btn.innerHTML = '⏳ Adding...';
    btn.disabled = true;

    try {
        await api.addToCart(productId, 1);
        btn.innerHTML = '✓ Added!';

        // Dispatch event to update cart count in navbar
        window.dispatchEvent(new Event('cart-updated'));

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 1500);
    } catch (err) {
        console.error('Failed to add to cart:', err);
        alert(err.message || 'Failed to add to cart. Please try again.');
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Handle remove from wishlist
async function handleRemoveFromWishlist(e) {
    const productId = parseInt(e.currentTarget.dataset.productId);

    if (!confirm('Remove this product from your wishlist?')) {
        return;
    }

    try {
        await api.removeFromWishlist(productId);

        // Remove the card with animation
        const card = e.currentTarget.closest('.wishlist-card');
        card.style.opacity = '0';
        card.style.transform = 'scale(0.8)';

        setTimeout(async () => {
            await loadWishlist();
        }, 300);
    } catch (err) {
        console.error('Failed to remove from wishlist:', err);
        alert(err.message || 'Failed to remove from wishlist. Please try again.');
    }
}

// Clear all wishlist
clearAllBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to clear your entire wishlist?')) {
        return;
    }

    try {
        await api.clearWishlist();
        await loadWishlist();
    } catch (err) {
        console.error('Failed to clear wishlist:', err);
        alert(err.message || 'Failed to clear wishlist. Please try again.');
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', loadWishlist);
