
/**
 * DataManager - Simulates a backend using localStorage.
 * Handles Products, Users, Cart, and Orders.
 */

const PRODUCTS_KEY = 'toys_products';
const LOGS_KEY = 'toys_logs';
const CART_KEY = 'toys_cart';
const USERS_KEY = 'toys_users';
const ORDERS_KEY = 'toys_orders';

// Initial Seed Data (from original catalog.js)
const INITIAL_PRODUCTS = [
    { id: '1', title: "Avengers Tower", price: 40.99, icon: "🏢", rating: 5, reviews: 30, category: "Sets", stock: 10, description: "Build the iconic Avengers Tower!" },
    { id: '2', title: "Venomized Groot", price: 35.99, icon: "🪴", rating: 4, reviews: 12, category: "Plushies", stock: 5, description: "A spooky twist on everyone's favorite tree." },
    { id: '3', title: "Expecto Patronum", price: 69.99, icon: "🦌", rating: 5, reviews: 45, category: "Sets", stock: 8, description: "Cast the spell and protect Hogwarts." },
    { id: '4', title: "The Child", price: 40.99, icon: "🐸", rating: 5, reviews: 88, category: "Plushies", stock: 20, description: "This is the way." },
    { id: '5', title: "Alpine Lodge", price: 80.99, icon: "🏠", rating: 5, reviews: 15, category: "Sets", stock: 3, description: "Cozy winter getaway." },
    { id: '6', title: "Monkey King", price: 45.59, icon: "🐵", rating: 4, reviews: 21, category: "Blocks", stock: 12, description: "Legendary warrior in block form." },
    { id: '7', title: "Tusken Raider", price: 19.99, icon: "👺", rating: 3, reviews: 6, category: "Sets", stock: 15, description: "Desert dweller from Tatooine." },
    { id: '8', title: "Hogwarts Castle", price: 120.99, icon: "🏰", rating: 5, reviews: 102, category: "Sets", stock: 2, description: "The magical school of witchcraft and wizardry." },
    { id: '9', title: "Mighty Bowser", price: 59.99, icon: "🐢", rating: 5, reviews: 34, category: "Blocks", stock: 7, description: "The King of Koopas." },
    { id: '10', title: "Dobby Experience", price: 29.99, icon: "🧦", rating: 4, reviews: 9, category: "Plushies", stock: 25, description: "Master has given Dobby a sock!" },
    { id: '11', title: "Orchid Plant", price: 49.99, icon: "🌺", rating: 5, reviews: 55, category: "Sets", stock: 18, description: "Beautiful botanical collection." },
    { id: '12', title: "London Skyline", price: 39.99, icon: "🎡", rating: 5, reviews: 23, category: "Sets", stock: 10, description: "Build the city of London." },
];

class DataManager {
    static init() {
        if (!localStorage.getItem(PRODUCTS_KEY)) {
            localStorage.setItem(PRODUCTS_KEY, JSON.stringify(INITIAL_PRODUCTS));
            this.log('System', 'Initialized default products.');
        }
        if (!localStorage.getItem(CART_KEY)) {
            localStorage.setItem(CART_KEY, JSON.stringify([]));
        }
        // Create Default Admin if not exists
        const users = this.getUsers();
        if (!users.find(u => u.username === 'admin')) {
            this.register({ name: 'Admin User', username: 'admin', password: 'password', role: 'admin' });
        }
    }

    // --- PRODUCTS ---
    static getProducts() {
        return JSON.parse(localStorage.getItem(PRODUCTS_KEY) || '[]');
    }

    static getProductById(id) {
        const products = this.getProducts();
        return products.find(p => p.id === id);
    }

    static saveProduct(product) {
        const products = this.getProducts();
        if (product.id) {
            // Edit
            const index = products.findIndex(p => p.id === product.id);
            if (index !== -1) {
                products[index] = { ...products[index], ...product };
                this.log('Admin', `Updated product: ${product.title}`);
            }
        } else {
            // Add
            product.id = Date.now().toString();
            // Defaults
            if (!product.rating) product.rating = 0;
            if (!product.reviews) product.reviews = 0;
            products.push(product);
            this.log('Admin', `Added new product: ${product.title}`);
        }
        localStorage.setItem(PRODUCTS_KEY, JSON.stringify(products));
    }

    static deleteProduct(id) {
        let products = this.getProducts();
        const product = products.find(p => p.id === id);
        if (product) {
            products = products.filter(p => p.id !== id);
            localStorage.setItem(PRODUCTS_KEY, JSON.stringify(products));
            this.log('Admin', `Deleted product: ${product.title}`);
        }
    }

    // --- CART ---
    static getCart() {
        return JSON.parse(localStorage.getItem(CART_KEY) || '[]');
    }

    static addToCart(product, quantity = 1) {
        let cart = this.getCart();
        const existing = cart.find(item => item.id === product.id);
        if (existing) {
            existing.quantity += quantity;
        } else {
            cart.push({ ...product, quantity });
        }
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        // Dispatch event for UI updates
        window.dispatchEvent(new Event('cart-updated'));
    }

    static removeFromCart(id) {
        let cart = this.getCart();
        cart = cart.filter(item => item.id !== id);
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
        window.dispatchEvent(new Event('cart-updated'));
    }

    static updateCartQuantity(id, quantity) {
        let cart = this.getCart();
        const item = cart.find(i => i.id === id);
        if (item) {
            item.quantity = quantity;
            if (item.quantity <= 0) {
                this.removeFromCart(id);
                return;
            }
            localStorage.setItem(CART_KEY, JSON.stringify(cart));
            window.dispatchEvent(new Event('cart-updated'));
        }
    }

    static clearCart() {
        localStorage.setItem(CART_KEY, JSON.stringify([]));
        window.dispatchEvent(new Event('cart-updated'));
    }

    // --- AUTH ---
    static getUsers() {
        return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    }

    static register(user) {
        const users = this.getUsers();
        if (users.find(u => u.username === user.username)) {
            return { success: false, message: "Username already exists" };
        }
        // Default role if not specified
        if (!user.role) user.role = 'customer';

        users.push(user);
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
        return { success: true };
    }

    static login(username, password) {
        const users = this.getUsers();
        const user = users.find(u => u.username === username && u.password === password);
        if (user) {
            localStorage.setItem('current_user', JSON.stringify(user));
            return { success: true, user };
        }
        return { success: false, message: "Invalid credentials" };
    }

    static logout() {
        console.warn("DataManager: Logout called. Clearing current_user.");
        localStorage.removeItem('current_user');
        window.location.href = '/index.html';
    }

    static getCurrentUser() {
        return JSON.parse(localStorage.getItem('current_user'));
    }

    // --- ORDERS ---
    static createOrder(customerDetails) {
        const cart = this.getCart();
        if (cart.length === 0) return { success: false, message: "Cart is empty" };

        const order = {
            id: 'ORD-' + Date.now(),
            date: new Date().toISOString(),
            customer: customerDetails, // { name, email, box }
            items: cart,
            total: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0),
            status: 'Pending'
        };

        const orders = JSON.parse(localStorage.getItem(ORDERS_KEY) || '[]');
        orders.push(order);
        localStorage.setItem(ORDERS_KEY, JSON.stringify(orders));

        this.clearCart();
        this.log('Order', `New Order ${order.id} placed by ${customerDetails.name}`);
        return { success: true, orderId: order.id };
    }

    static getOrders() {
        return JSON.parse(localStorage.getItem(ORDERS_KEY) || '[]');
    }

    // --- LOGS ---
    static log(actor, action) {
        const logs = JSON.parse(localStorage.getItem(LOGS_KEY) || '[]');
        logs.unshift({ timestamp: new Date().toLocaleString(), actor, action });
        if (logs.length > 50) logs.pop(); // Keep last 50
        localStorage.setItem(LOGS_KEY, JSON.stringify(logs));
    }

    static getLogs() {
        return JSON.parse(localStorage.getItem(LOGS_KEY) || '[]');
    }

    // --- REVIEWS ---
    static getReviews(productId) {
        const reviews = JSON.parse(localStorage.getItem('toys_reviews') || '[]');
        return reviews.filter(r => r.productId === productId);
    }

    static addReview(review) {
        const reviews = JSON.parse(localStorage.getItem('toys_reviews') || '[]');
        review.id = 'REV-' + Date.now();
        review.date = new Date().toLocaleDateString();
        reviews.push(review);
        localStorage.setItem('toys_reviews', JSON.stringify(reviews));

        // Update product average rating
        const productReviews = reviews.filter(r => r.productId === review.productId);
        const avg = productReviews.reduce((sum, r) => sum + r.rating, 0) / productReviews.length;

        const products = this.getProducts();
        const pIndex = products.findIndex(p => p.id === review.productId);
        if (pIndex !== -1) {
            products[pIndex].rating = Math.round(avg); // Simple integer stars for now
            products[pIndex].reviews = productReviews.length;
            localStorage.setItem(PRODUCTS_KEY, JSON.stringify(products));
        }

        return { success: true };
    }
}

export default DataManager;
