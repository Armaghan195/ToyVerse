import '../css/style.css';
import '../css/variables.css';
import api from './api.js';
import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';

renderNavbar('#c-navbar');
initChatbot();

// DOM
const list = document.getElementById('cart-list');
const subtotalEl = document.getElementById('subtotal');
const totalEl = document.getElementById('total');
const form = document.getElementById('order-form');

// State
let cart = [];

async function loadCart() {
    list.innerHTML = '<div class="empty-msg">Loading cart...</div>';
    try {
        const response = await api.getCart();
        cart = response.items || [];
        render();
    } catch (err) {
        console.error('Load cart failed', err);
        if (err.message && err.message.toLowerCase().includes('unauthorized')) {
            alert('Please log in to view your cart.');
            window.location.href = '/pages/auth.html';
        } else {
            list.innerHTML = `<div class="empty-msg" style="color:red;">Unable to load cart. ${err.message}</div>`;
        }
    }
}

function render() {
    if (!cart || cart.length === 0) {
        list.innerHTML = '<div class="empty-msg">Your cart is empty. <a href="catalog.html">Go shopping!</a></div>';
        subtotalEl.innerText = '$0.00';
        totalEl.innerText = '$0.00';
        return;
    }

    list.innerHTML = cart.map(item => {
        const product = item.product || {};
        const img = product.images && product.images.length ? product.images[0] : null;
        const iconHtml = img
            ? `<img src="${img}" alt="${product.title || 'Product'}" style="width:48px;height:48px;object-fit:cover;border-radius:8px;">`
            : (product.icon || '🧸');
        return `
        <div class="cart-item">
            <div class="item-info">
                <div class="item-icon">${iconHtml}</div>
                <div>
                    <h4>${product.title || 'Product'}</h4>
                    <div style="color: var(--color-teal); font-weight: 600;">$${Number(product.price || 0).toFixed(2)}</div>
                </div>
            </div>
            <div class="quantity-controls">
                <div class="quantity-wrapper">
                    <button class="qty-btn" onclick="decreaseQ(${item.id}, ${item.quantity})">−</button>
                    <div class="qty-display">${item.quantity}</div>
                    <button class="qty-btn" onclick="increaseQ(${item.id}, ${item.quantity}, ${product.stock || 99})">+</button>
                </div>
                <button class="remove-btn" onclick="removeItem(${item.id})">
                    <span>🗑️</span>
                    <span>Remove</span>
                </button>
            </div>
        </div>
    `;
    }).join('');

    const total = cart.reduce((sum, item) => sum + Number(item.subtotal || 0), 0);
    subtotalEl.innerText = `$${total.toFixed(2)}`;
    totalEl.innerText = `$${total.toFixed(2)}`;
}

// Global actions for HTML event attributes
window.updateQ = async (id, newQ) => {
    try {
        await api.updateCartItem(id, parseInt(newQ, 10));
        await loadCart();
        window.dispatchEvent(new Event('cart-updated'));
    } catch (err) {
        console.error('Update cart failed', err);
        alert(err.message || 'Could not update quantity.');
    }
};

// Increase quantity with cute + button
window.increaseQ = async (id, currentQty, maxStock) => {
    if (currentQty >= maxStock) {
        alert(`Maximum stock available is ${maxStock}`);
        return;
    }
    await window.updateQ(id, currentQty + 1);
};

// Decrease quantity with cute - button
window.decreaseQ = async (id, currentQty) => {
    if (currentQty <= 1) {
        alert('Quantity cannot be less than 1. Use Remove button to delete item.');
        return;
    }
    await window.updateQ(id, currentQty - 1);
};

window.removeItem = async (id) => {
    try {
        await api.removeFromCart(id);
        await loadCart();
        window.dispatchEvent(new Event('cart-updated'));
    } catch (err) {
        console.error('Remove cart item failed', err);
        alert(err.message || 'Could not remove item.');
    }
};

// Checkout
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!cart || cart.length === 0) {
        alert("Cart is empty!");
        return;
    }

    const paymentMethod = document.querySelector('input[name="payment-method"]:checked').value;

    const customer = {
        name: document.getElementById('cust-name').value,
        email: document.getElementById('cust-email').value,
        address: document.getElementById('cust-address').value,
        // Backend requires these fields; use simple fallbacks if not collected in UI
        phone: document.getElementById('cust-phone') ? document.getElementById('cust-phone').value : 'N/A',
        city: document.getElementById('cust-city') ? document.getElementById('cust-city').value : 'Unknown',
        postal_code: document.getElementById('cust-postal') ? document.getElementById('cust-postal').value : '00000'
    };

    if (paymentMethod === 'online') {
        document.getElementById('billing-modal').classList.remove('hidden');
        window.currentCustomer = { ...customer, paymentMethod };
    } else {
        placeOrder(customer, paymentMethod);
    }
});

// Modal Logic
const modal = document.getElementById('billing-modal');
const closeModal = document.getElementById('close-modal');
const billingForm = document.getElementById('billing-form');

if (closeModal) {
    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });
}

if (billingForm) {
    billingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = billingForm.querySelector('button');
        const originalText = btn.innerText;
        btn.innerText = "Processing...";
        btn.disabled = true;

        try {
            await placeOrder(window.currentCustomer, 'online');
            modal.classList.add('hidden');
        } finally {
            btn.innerText = originalText;
            btn.disabled = false;
        }
    });
}

async function placeOrder(customer, paymentMethod) {
    try {
        const result = await api.createOrder(customer, paymentMethod === 'online' ? 'ONLINE' : 'COD');
        window.dispatchEvent(new Event('cart-updated'));
        window.location.href = 'order-confirmation.html?orderId=' + (result.id || result.order_number || '');
    } catch (err) {
        console.error('Order failed', err);
        if (err.message && err.message.toLowerCase().includes('unauthorized')) {
            alert('Please log in to place an order.');
            window.location.href = '/pages/auth.html';
        } else {
            const detail = err.detail || err.message || err;
            alert('Error placing order: ' + detail);
        }
    }
}

// Init
document.addEventListener('DOMContentLoaded', loadCart);
