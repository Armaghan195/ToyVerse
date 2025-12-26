
import '../css/style.css';
import '../css/admin.css';
import api from './api.js';

// Verify Admin Access
const token = localStorage.getItem('access_token');
const user = JSON.parse(localStorage.getItem('current_user') || 'null');

if (!token || !user || user.role !== 'admin') {
    alert("Access Denied. Admins only.");
    window.location.href = 'auth.html';
}

// DOM Elements
const productsTableBody = document.querySelector('#products-table tbody');
const ordersTableBody = document.querySelector('#orders-table tbody');
const logsList = document.querySelector('#logs-list');
const modal = document.querySelector('#product-modal');
const productForm = document.querySelector('#product-form');
const logoutBtn = document.querySelector('#logout-btn');

// Tabs Logic
const tabs = document.querySelectorAll('.sidebar-menu li');
const sections = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class
        tabs.forEach(t => t.classList.remove('active'));
        sections.forEach(s => s.classList.remove('active'));

        // Add active
        tab.classList.add('active');
        const target = tab.getAttribute('data-tab');
        document.getElementById(`${target}-section`).classList.add('active');
    });
});

// --- RENDER FUNCTIONS ---

async function renderProducts() {
    try {
        productsTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center">Loading products...</td></tr>';

        const products = await api.getProducts();

        if (!products || products.length === 0) {
            productsTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center">No products found.</td></tr>';
            return;
        }

        productsTableBody.innerHTML = products.map(p => `
            <tr>
                <td style="font-size: 1.5rem;">
                    ${p.images && p.images.length
                        ? `<img src="${p.images[0]}" alt="${p.title}" style="width:40px;height:40px;object-fit:cover;border-radius:6px;">`
                        : (p.icon || '??')
                    }
                </td>
                <td>${p.id}</td>
                <td><strong>${p.title}</strong></td>
                <td><span class="badge">${p.category}</span></td>
                <td>$${parseFloat(p.price).toFixed(2)}</td>
                <td>${p.stock}</td>
                <td>
                    <button class="btn-sm edit-btn" data-id="${p.id}">Edit</button>
                    <button class="btn-sm delete-btn" data-id="${p.id}">Delete</button>
                </td>
            </tr>
        `).join('');

        // Re-attach listeners
        document.querySelectorAll('.edit-btn').forEach(btn =>
            btn.addEventListener('click', () => openModal(btn.dataset.id))
        );
        document.querySelectorAll('.delete-btn').forEach(btn =>
            btn.addEventListener('click', () => confirmDelete(btn.dataset.id))
        );
    } catch (error) {
        console.error('Error loading products:', error);
        productsTableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:red;">Error loading products: ${error.message}</td></tr>`;
    }
}

async function renderOrders() {
    try {
        ordersTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center">Loading orders...</td></tr>';

        const orders = await api.getAllOrders();

        if (!orders || orders.length === 0) {
            ordersTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center">No orders yet.</td></tr>';
            return;
        }

        ordersTableBody.innerHTML = orders.map(o => {
            const customerName = o.customer_details?.name || 'Unknown';
            const itemCount = o.items?.length || 0;
            const orderDate = new Date(o.created_at).toLocaleDateString();

            return `
                <tr>
                    <td>${o.order_number || o.id}</td>
                    <td>${orderDate}</td>
                    <td>${customerName}</td>
                    <td>${itemCount} items</td>
                    <td>$${parseFloat(o.total).toFixed(2)}</td>
                    <td>
                        <select class="status-select" data-order-id="${o.id}" style="padding:5px; border-radius:4px;">
                            <option value="pending" ${o.status === 'pending' ? 'selected' : ''}>Pending</option>
                            <option value="processing" ${o.status === 'processing' ? 'selected' : ''}>Processing</option>
                            <option value="shipped" ${o.status === 'shipped' ? 'selected' : ''}>Shipped</option>
                            <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
                            <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select>
                    </td>
                </tr>
            `;
        }).join('');

        // Attach status change listeners
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', async (e) => {
                const orderId = e.target.dataset.orderId;
                const newStatus = e.target.value;
                await updateOrderStatus(orderId, newStatus);
            });
        });
    } catch (error) {
        console.error('Error loading orders:', error);
        ordersTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:red;">Error loading orders: ${error.message}</td></tr>`;
    }
}

async function renderLogs() {
    try {
        logsList.innerHTML = '<div style="text-align:center">Loading logs...</div>';

        const logs = await api.getActivityLogs();

        if (!logs || logs.length === 0) {
            logsList.innerHTML = '<div style="text-align:center">No activity logs yet.</div>';
            return;
        }

        logsList.innerHTML = logs.map(l => {
            const timestamp = new Date(l.timestamp).toLocaleString();
            return `
                <div class="log-item">
                    <span style="color:#aaa; margin-right:10px;">[${timestamp}]</span>
                    <strong>${l.actor}</strong>: ${l.action}
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading logs:', error);
        logsList.innerHTML = `<div style="text-align:center; color:red;">Error loading logs: ${error.message}</div>`;
    }
}

// --- ORDER STATUS UPDATE ---

async function updateOrderStatus(orderId, status) {
    try {
        await api.updateOrderStatus(orderId, status);

        // Log the action
        await api.createActivityLog(user.username, `Updated order #${orderId} status to ${status}`);

        // Refresh logs
        await renderLogs();

        alert(`Order status updated to ${status}`);
    } catch (error) {
        console.error('Error updating order status:', error);
        alert(`Failed to update order status: ${error.message}`);
        await renderOrders(); // Refresh to reset select
    }
}

// --- MODAL LOGIC ---

// Image State
let currentImages = [];
let currentImageFiles = [];

function renderImagePreviews() {
    const container = document.getElementById('image-preview');
    container.innerHTML = currentImages.map((img, index) => `
        <div style="position:relative; width:50px; height:50px;">
            <img src="${img}" style="width:100%; height:100%; object-fit:cover; border-radius:4px;">
            <button type="button" onclick="window.removeImage(${index})" style="position:absolute; top:-5px; right:-5px; background:red; color:white; border:none; border-radius:50%; width:15px; height:15px; font-size:10px; cursor:pointer;">×</button>
        </div>
    `).join('');
}

window.removeImage = (index) => {
    currentImages.splice(index, 1);
    currentImageFiles.splice(index, 1);
    renderImagePreviews();
};

window.openModal = async (id = null) => {
    modal.classList.remove('hidden');
    const preview = document.getElementById('image-preview');
    preview.innerHTML = '';
    currentImages = [];
    currentImageFiles = [];

    if (id) {
        try {
            // Edit Mode - Fetch product from backend
            const product = await api.getProductById(id);

            document.getElementById('modal-title').innerText = 'Edit Product';
            document.getElementById('prod-id').value = product.id;
            document.getElementById('prod-title').value = product.title;
            document.getElementById('prod-category').value = product.category;
            document.getElementById('prod-price').value = product.price;
            document.getElementById('prod-stock').value = product.stock;
            document.getElementById('prod-desc').value = product.description || '';
            document.getElementById('prod-detailed-desc').value = product.detailed_description || '';
            document.getElementById('prod-rating').value = product.rating;

            // Load existing images
            if (product.images && product.images.length > 0) {
                currentImages = [...product.images];
                renderImagePreviews();
            }
        } catch (error) {
            console.error('Error loading product:', error);
            alert(`Failed to load product: ${error.message}`);
            closeModal();
        }
    } else {
        // Add Mode
        document.getElementById('modal-title').innerText = 'Add New Product';
        productForm.reset();
        document.getElementById('prod-id').value = '';
    }
};

window.closeModal = () => {
    modal.classList.add('hidden');
};

// Image Inputs
document.getElementById('prod-images-file').addEventListener('change', (e) => {
    Array.from(e.target.files).forEach(file => {
        currentImageFiles.push(file);

        const reader = new FileReader();
        reader.onload = (ev) => {
            currentImages.push(ev.target.result);
            renderImagePreviews();
        };
        reader.readAsDataURL(file);
    });
});

document.getElementById('prod-image-url').addEventListener('change', (e) => {
    if (e.target.value) {
        currentImages.push(e.target.value);
        e.target.value = '';
        renderImagePreviews();
    }
});

productForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const productId = document.getElementById('prod-id').value || null;
    const submitBtn = productForm.querySelector('.save-btn');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';

    try {
        // Upload new image files if any
        let uploadedImageUrls = [];
        if (currentImageFiles.length > 0) {
            const uploadResult = await api.uploadProductImages(currentImageFiles);
            uploadedImageUrls = uploadResult.uploaded.map(img => `http://localhost:8000${img.url}`);
        }

        // Combine uploaded URLs with existing URLs
        const allImageUrls = [...uploadedImageUrls];
        currentImages.forEach(img => {
            // If it's a URL (not a data URL), add it
            if (img.startsWith('http') && !uploadedImageUrls.includes(img)) {
                allImageUrls.push(img);
            }
        });

        const productData = {
            title: document.getElementById('prod-title').value,
            category: document.getElementById('prod-category').value,
            price: parseFloat(document.getElementById('prod-price').value),
            stock: parseInt(document.getElementById('prod-stock').value),
            rating: parseInt(document.getElementById('prod-rating').value),
            icon: allImageUrls.length > 0 ? '🧸' : '📦',
            description: document.getElementById('prod-desc').value,
            detailed_description: document.getElementById('prod-detailed-desc').value,
            images: allImageUrls
        };

        if (productId) {
            // Update existing product
            await api.updateProduct(productId, productData);
            await api.createActivityLog(user.username, `Updated product: ${productData.title}`);
        } else {
            // Create new product
            await api.createProduct(productData);
            await api.createActivityLog(user.username, `Added new product: ${productData.title}`);
        }

        closeModal();
        await renderProducts();
        await renderLogs();

        alert(productId ? 'Product updated successfully!' : 'Product created successfully!');
    } catch (error) {
        console.error('Error saving product:', error);
        alert(`Failed to save product: ${error.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save';
    }
});

// --- ACTIONS ---

async function confirmDelete(id) {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }

    try {
        const product = await api.getProductById(id);
        await api.deleteProduct(id);
        await api.createActivityLog(user.username, `Deleted product: ${product.title}`);

        await renderProducts();
        await renderLogs();

        alert('Product deleted successfully!');
    } catch (error) {
        console.error('Error deleting product:', error);
        alert(`Failed to delete product: ${error.message}`);
    }
}

// Add Product Button
document.getElementById('add-product-btn').addEventListener('click', () => openModal());

// Logout
logoutBtn.addEventListener('click', () => {
    api.logout();
});

// Initial Render
(async function init() {
    await renderProducts();
    await renderOrders();
    await renderLogs();
})();
