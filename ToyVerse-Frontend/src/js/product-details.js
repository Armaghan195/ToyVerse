import '../css/style.css';
import '../css/variables.css';
import '../css/search.css';
import api from './api.js';
import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';

renderNavbar('#p-navbar');
initChatbot();

// Get ID from URL
const params = new URLSearchParams(window.location.search);
const id = params.get('id');

// Elements
const els = {
    title: document.getElementById('p-title'),
    price: document.getElementById('p-price'),
    icon: document.getElementById('p-icon'),
    desc: document.getElementById('p-desc'),
    category: document.getElementById('p-category'),
    stock: document.getElementById('p-stock'),
    rating: document.getElementById('p-rating'),
    id: document.getElementById('p-id'),
    qty: document.getElementById('qty-input'),
    addBtn: document.getElementById('add-to-cart-btn'),
    wishlistBtn: document.getElementById('wishlist-btn'),
    detailed: document.getElementById('p-detailed-desc'),
    detailsSection: document.getElementById('more-details-section'),
    reviewsList: document.getElementById('reviews-list'),
    reviewForm: document.getElementById('add-review-form'),
    loginMsg: document.getElementById('login-to-review')
};

let currentProduct = null;
let similarProducts = [];
let isWishlisted = false;

async function loadProduct() {
    try {
        currentProduct = await api.getProductById(id);

        // Check if product is in wishlist
        await checkWishlistStatus();

        // Track product view for recommendations
        const viewHistory = JSON.parse(localStorage.getItem('product_view_history') || '[]');

        viewHistory.unshift({
            product_id: currentProduct.id,
            category: currentProduct.category,
            timestamp: new Date().toISOString(),
            type: 'view_details'
        });

        // Keep only last 50 interactions
        localStorage.setItem('product_view_history', JSON.stringify(viewHistory.slice(0, 50)));

        renderProduct(currentProduct);
        await renderSimilarItems(currentProduct);
        await renderReviews();
    } catch (err) {
        console.error('Product load failed', err);
        document.body.innerHTML = `<h1>Product not found.</h1><a href='/pages/catalog.html'>Go Back</a>`;
    }
}

async function checkWishlistStatus() {
    try {
        const token = localStorage.getItem('access_token');
        if (token && currentProduct) {
            const result = await api.checkInWishlist(currentProduct.id);
            isWishlisted = result.is_wishlisted;
            updateWishlistButton();
        }
    } catch (err) {
        console.error('Failed to check wishlist status', err);
        isWishlisted = false;
    }
}

function updateWishlistButton() {
    if (els.wishlistBtn) {
        if (isWishlisted) {
            els.wishlistBtn.classList.add('wishlisted');
            els.wishlistBtn.title = 'Remove from Wishlist';
        } else {
            els.wishlistBtn.classList.remove('wishlisted');
            els.wishlistBtn.title = 'Add to Wishlist';
        }
    }
}

function renderProduct(product) {
    els.title.innerText = product.title;
    els.price.innerText = `$${Number(product.price).toFixed(2)}`;
    els.desc.innerText = product.description || 'No description available.';
    els.category.innerText = product.category;
    els.id.innerText = product.id;

    // Images
    els.icon.innerHTML = '';
    if (product.images && product.images.length > 0) {
        const mainImg = product.images[0];
        els.icon.innerHTML = `<img src="${mainImg}" style="width:100%; height:100%; object-fit:contain; border-radius:20px;">`;
    } else {
        els.icon.innerText = product.icon || '🧸';
        els.icon.style.fontSize = '10rem';
    }
    els.icon.style.display = 'flex';
    els.icon.style.justifyContent = 'center';
    els.icon.style.alignItems = 'center';
    els.icon.style.overflow = 'hidden';

    // Stock
    if ((product.stock ?? 0) > 0) {
        els.stock.innerText = 'In Stock';
        els.stock.style.color = 'green';
    } else {
        els.stock.innerText = 'Out of Stock';
        els.stock.style.color = 'red';
        els.addBtn.disabled = true;
        els.addBtn.innerText = 'Sold Out';
        els.addBtn.style.background = '#ccc';
    }

    // Rating
    const ratingVal = product.rating || 0;
    els.rating.innerText = '★'.repeat(ratingVal) + '☆'.repeat(5 - ratingVal);

    // Detailed overview
    if (product.detailed_description) {
        els.detailed.innerHTML = product.detailed_description;
        if (els.detailsSection) els.detailsSection.style.display = 'block';
    } else if (els.detailsSection) {
        els.detailsSection.style.display = 'none';
    }
}

async function renderSimilarItems(product) {
    try {
        const all = await api.getProducts({ category: product.category });
        similarProducts = all.filter(p => p.id !== product.id).slice(0, 8);
    } catch (err) {
        console.error('Similar products failed', err);
        similarProducts = [];
    }

    const container = document.getElementById('similar-list');
    if (!container) return;

    if (similarProducts.length === 0) {
        container.innerHTML = '<p>No similar items found.</p>';
        return;
    }

    container.innerHTML = similarProducts.map(item => {
        let imageHtml = `<div class="shop-icon">${item.icon || '🧸'}</div>`;
        if (item.images && item.images.length > 0) {
            imageHtml = `<img src="${item.images[0]}" style="width:100%; height:100%; object-fit:contain; border-radius:10px;">`;
        }

        const rating = '★'.repeat(item.rating || 0) + '☆'.repeat(5 - (item.rating || 0));
        const desc = item.description ? (item.description.substring(0, 60) + '...') : 'Great toy for kids!';

        return `
        <div class="shop-card" onclick="window.location.href='product-details.html?id=${item.id}'" style="cursor:pointer; text-align:left; min-height: 380px;">
            <div class="shop-icon-container" style="height:150px; margin-bottom:10px;">
               ${imageHtml}
            </div>
            <div class="shop-details" style="display:flex; flex-direction:column; gap:5px;">
                <h3 style="font-size:1rem; margin:0;">${item.title}</h3>
                <div style="color:gold; font-size:1rem;">${rating}</div>
                <div class="price" style="font-size:1.1rem; color:var(--accent-blue); font-weight:bold;">$${Number(item.price).toFixed(2)}</div>
                <p style="font-size:0.85rem; color:#666; margin-bottom:10px;">${desc}</p>
                <button class="add-cart-btn" onclick="event.stopPropagation(); buySimilar(${item.id})">Add to Cart</button>
            </div>
        </div>
        `;
    }).join('');
}

async function renderReviews() {
    if (!els.reviewsList) return;
    try {
        const reviews = await api.getProductReviews(id);
        if (!reviews || reviews.length === 0) {
            els.reviewsList.innerHTML = '<p style="color:#666; font-style:italic;">No reviews yet. Be the first to review!</p>';
        } else {
            els.reviewsList.innerHTML = reviews.map(r => `
                <div class="review-item" style="background:white; padding:20px; border-radius:10px; border:1px solid #eee;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <strong>${r.user_id || 'User'}</strong>
                        <span style="color:#888; font-size:0.9rem;">${new Date(r.created_at).toLocaleDateString()}</span>
                    </div>
                    <div style="color:gold; margin-bottom:10px;">${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}</div>
                    <p style="color:#555; line-height:1.5;">${r.text || ''}</p>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error('Reviews load failed', err);
        els.reviewsList.innerHTML = '<p style="color:red;">Unable to load reviews.</p>';
    }

    // Show/Hide add review form based on auth token
    const hasToken = !!localStorage.getItem('access_token');
    if (els.reviewForm && els.loginMsg) {
        if (hasToken) {
            els.reviewForm.style.display = 'block';
            els.loginMsg.style.display = 'none';
            els.reviewForm.onsubmit = submitReview;
        } else {
            els.reviewForm.style.display = 'none';
            els.loginMsg.style.display = 'block';
        }
    }
}

async function submitReview(e) {
    e.preventDefault();
    const rating = parseInt(document.getElementById('review-rating').value, 10);
    const text = document.getElementById('review-text').value;
    try {
        await api.createReview(Number(id), rating, text);
        document.getElementById('review-text').value = '';
        await renderReviews();
        alert('Review submitted! Thank you.');
    } catch (err) {
        console.error('Review submit failed', err);
        if (err.message && err.message.toLowerCase().includes('unauthorized')) {
            alert('Please log in to submit a review.');
            window.location.href = '/pages/auth.html';
        } else {
            alert(`Could not submit review: ${err.message}`);
        }
    }
}

// Similar items add-to-cart
window.buySimilar = async (productId) => {
    await addToCart(productId);
};

// Quantity change
window.changeQty = (delta) => {
    let val = parseInt(els.qty.value, 10);
    val += delta;
    if (val < 1) val = 1;
    if (currentProduct && val > (currentProduct.stock ?? val)) val = currentProduct.stock;
    els.qty.value = val;
};

els.addBtn.addEventListener('click', () => {
    if (!currentProduct) return;
    const qty = parseInt(els.qty.value, 10) || 1;
    addToCart(currentProduct.id, qty);
});

async function addToCart(productId, quantity = 1) {
    try {
        await api.addToCart(productId, quantity);
        alert('Added to cart!');
        window.dispatchEvent(new Event('cart-updated'));
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

async function toggleWishlist() {
    if (!currentProduct) return;

    try {
        if (isWishlisted) {
            await api.removeFromWishlist(currentProduct.id);
            isWishlisted = false;
            showWishlistNotification('💔 Removed from wishlist', 'info');
        } else {
            await api.addToWishlist(currentProduct.id);
            isWishlisted = true;
            showWishlistNotification('❤️ Added to wishlist!', 'success');
        }
        updateWishlistButton();
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

function showWishlistNotification(message, type = 'info') {
    const notification = document.createElement('div');
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
        animation: slideInRight 0.3s ease;
    `;

    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    if (!document.querySelector('#wishlist-notif-style')) {
        style.id = 'wishlist-notif-style';
        document.head.appendChild(style);
    }

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Start
document.addEventListener('DOMContentLoaded', () => {
    loadProduct();

    // Attach wishlist button handler
    if (els.wishlistBtn) {
        els.wishlistBtn.addEventListener('click', toggleWishlist);
    }
});
