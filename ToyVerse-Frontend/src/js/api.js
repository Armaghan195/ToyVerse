/**
 * API Service Layer
 * Handles all HTTP requests to the ToyVerse FastAPI Backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

class APIService {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem('access_token');
    }

    /**
     * Get authorization headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Set authentication token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    /**
     * Clear authentication token
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('current_user');
    }

    /**
     * Generic request handler
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);

            // Handle non-JSON responses (like 204 No Content)
            if (response.status === 204) {
                return { success: true };
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // ==================== AUTH ====================

    /**
     * Register a new user
     */
    async register(userData) {
        return await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                username: userData.username,
                email: userData.email,
                password: userData.password,
                full_name: userData.name,
                role: userData.role || 'customer'
            })
        });
    }

    /**
     * Login user
     */
    async login(username, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.access_token) {
            this.setToken(response.access_token);
            localStorage.setItem('current_user', JSON.stringify(response.user));
        }

        return response;
    }

    /**
     * Logout user
     */
    logout() {
        this.clearToken();
        window.location.href = '/index.html';
    }

    /**
     * Get current user info
     */
    async getCurrentUser() {
        return await this.request('/auth/me');
    }

    // ==================== PRODUCTS ====================

    /**
     * Get all products
     */
    async getProducts(filters = {}) {
        const params = new URLSearchParams(filters);
        const query = params.toString() ? `?${params.toString()}` : '';
        return await this.request(`/products${query}`);
    }

    /**
     * Get product by ID
     */
    async getProductById(id) {
        return await this.request(`/products/${id}`);
    }

    /**
     * Create new product (Admin only)
     */
    async createProduct(productData) {
        return await this.request('/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        });
    }

    /**
     * Update product (Admin only)
     */
    async updateProduct(id, productData) {
        return await this.request(`/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        });
    }

    /**
     * Delete product (Admin only)
     */
    async deleteProduct(id) {
        return await this.request(`/products/${id}`, {
            method: 'DELETE'
        });
    }

    // ==================== CART ====================

    /**
     * Get cart
     */
    async getCart() {
        return await this.request('/cart');
    }

    /**
     * Add item to cart
     */
    async addToCart(productId, quantity = 1) {
        return await this.request('/cart/add', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity })
        });
    }

    /**
     * Update cart item quantity
     */
    async updateCartItem(itemId, quantity) {
        return await this.request(`/cart/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify({ quantity })
        });
    }

    /**
     * Remove item from cart
     */
    async removeFromCart(itemId) {
        return await this.request(`/cart/${itemId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Clear cart
     */
    async clearCart() {
        return await this.request('/cart/clear', {
            method: 'DELETE'
        });
    }

    // ==================== ORDERS ====================

    /**
     * Create order from cart
     */
    async createOrder(customerDetails, paymentMethod = 'COD') {
        return await this.request('/orders', {
            method: 'POST',
            body: JSON.stringify({
                customer_details: customerDetails,
                payment_method: paymentMethod
            })
        });
    }

    /**
     * Get user orders
     */
    async getUserOrders() {
        return await this.request('/orders');
    }

    /**
     * Get order by ID
     */
    async getOrderById(id) {
        return await this.request(`/orders/${id}`);
    }

    /**
     * Update order status (Admin only)
     */
    async updateOrderStatus(id, status) {
        return await this.request(`/orders/${id}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
    }

    // ==================== REVIEWS ====================

    /**
     * Get product reviews
     */
    async getProductReviews(productId) {
        return await this.request(`/reviews/${productId}`);
    }

    /**
     * Create review
     */
    async createReview(productId, rating, text) {
        return await this.request('/reviews', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, rating, text })
        });
    }

    /**
     * Update review
     */
    async updateReview(reviewId, rating, text) {
        return await this.request(`/reviews/${reviewId}`, {
            method: 'PUT',
            body: JSON.stringify({ rating, text })
        });
    }

    /**
     * Delete review
     */
    async deleteReview(reviewId) {
        return await this.request(`/reviews/${reviewId}`, {
            method: 'DELETE'
        });
    }

    // ==================== ADMIN ====================

    /**
     * Get all orders (Admin only)
     */
    async getAllOrders(filters = {}) {
        const params = new URLSearchParams(filters);
        const query = params.toString() ? `?${params.toString()}` : '';
        return await this.request(`/admin/orders${query}`);
    }

    /**
     * Get activity logs (Admin only)
     */
    async getActivityLogs(filters = {}) {
        const params = new URLSearchParams(filters);
        const query = params.toString() ? `?${params.toString()}` : '';
        return await this.request(`/admin/logs${query}`);
    }

    /**
     * Create activity log (Admin only)
     */
    async createActivityLog(actor, action) {
        return await this.request(`/admin/logs?actor=${encodeURIComponent(actor)}&action=${encodeURIComponent(action)}`, {
            method: 'POST'
        });
    }

    // ==================== UPLOADS ====================

    /**
     * Upload product image (Admin only)
     */
    async uploadProductImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        const url = `${this.baseURL}/uploads/product-image`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return await response.json();
    }

    /**
     * Upload multiple product images (Admin only)
     */
    async uploadProductImages(files) {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });

        const url = `${this.baseURL}/uploads/product-images`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return await response.json();
    }

    // ==================== RECOMMENDATIONS ====================

    /**
     * Get personalized product recommendations
     */
    async getRecommendations(type = 'all') {
        return await this.request(`/recommendations?type=${type}`);
    }

    /**
     * Track product interaction (view, click, purchase)
     */
    async trackInteraction(productId, interactionType = 'view') {
        return await this.request('/recommendations/track', {
            method: 'POST',
            body: JSON.stringify({
                product_id: productId,
                interaction_type: interactionType
            })
        });
    }

    // ==================== CHATBOT ====================

    /**
     * Send message to chatbot
     */
    async sendChatMessage(message, sessionId) {
        return await this.request('/chatbot/message', {
            method: 'POST',
            body: JSON.stringify({ message, session_id: sessionId })
        });
    }

    /**
     * Get chat history
     */
    async getChatHistory(sessionId, limit = 50) {
        return await this.request(`/chatbot/history/${sessionId}?limit=${limit}`);
    }

    /**
     * Clear chat history
     */
    async clearChatHistory(sessionId) {
        return await this.request(`/chatbot/history/${sessionId}`, {
            method: 'DELETE'
        });
    }

    // ==================== SUPPORT ====================

    /**
     * Search for help using AI
     */
    async searchHelp(query) {
        return await this.request('/support/search', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    }

    /**
     * Submit contact form
     */
    async submitContactForm(name, email, message) {
        return await this.request('/support/contact', {
            method: 'POST',
            body: JSON.stringify({ name, email, message })
        });
    }

    // ==================== PROFILE ====================

    /**
     * Get current user's profile
     */
    async getProfile() {
        return await this.request('/profile/me');
    }

    /**
     * Update user profile
     */
    async updateProfile(profileData) {
        const formData = new FormData();

        if (profileData.full_name !== undefined) {
            formData.append('full_name', profileData.full_name);
        }
        if (profileData.email !== undefined) {
            formData.append('email', profileData.email);
        }
        if (profileData.current_password) {
            formData.append('current_password', profileData.current_password);
        }
        if (profileData.new_password) {
            formData.append('new_password', profileData.new_password);
        }

        const url = `${this.baseURL}/profile/update`;
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Update failed');
        }

        const data = await response.json();

        // Update localStorage with new user data
        localStorage.setItem('current_user', JSON.stringify(data));

        return data;
    }

    /**
     * Upload profile picture
     */
    async uploadProfilePicture(file) {
        const formData = new FormData();
        formData.append('file', file);

        const url = `${this.baseURL}/profile/upload-picture`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();

        // Update current_user in localStorage with new profile picture
        const currentUser = JSON.parse(localStorage.getItem('current_user') || '{}');
        currentUser.profile_picture = data.profile_picture;
        localStorage.setItem('current_user', JSON.stringify(currentUser));

        return data;
    }

    /**
     * Delete profile picture
     */
    async deleteProfilePicture() {
        const data = await this.request('/profile/delete-picture', {
            method: 'DELETE'
        });

        // Update current_user in localStorage
        const currentUser = JSON.parse(localStorage.getItem('current_user') || '{}');
        currentUser.profile_picture = null;
        localStorage.setItem('current_user', JSON.stringify(currentUser));

        return data;
    }

    // ==================== WISHLIST ====================

    /**
     * Get user's wishlist
     */
    async getWishlist() {
        return await this.request('/wishlist');
    }

    /**
     * Get product IDs in wishlist
     */
    async getWishlistProductIds() {
        return await this.request('/wishlist/product-ids');
    }

    /**
     * Add product to wishlist
     */
    async addToWishlist(productId) {
        return await this.request('/wishlist/add', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId })
        });
    }

    /**
     * Remove product from wishlist
     */
    async removeFromWishlist(productId) {
        return await this.request(`/wishlist/remove/${productId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Check if product is in wishlist
     */
    async checkInWishlist(productId) {
        return await this.request(`/wishlist/check/${productId}`);
    }

    /**
     * Clear entire wishlist
     */
    async clearWishlist() {
        return await this.request('/wishlist/clear', {
            method: 'DELETE'
        });
    }
}

// Export singleton instance
const api = new APIService();
export default api;
