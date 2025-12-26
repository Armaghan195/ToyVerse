import '../css/chatbot.css';
import api from './api.js';

export function initChatbot() {
    // Check if already exists
    if (document.getElementById('chatbot-root')) return;

    // Inject HTML
    const root = document.createElement('div');
    root.id = 'chatbot-root';
    root.innerHTML = `
        <button class="chatbot-btn" id="open-chat-btn">
            🧸
        </button>

        <div class="chat-window" id="chat-window">
            <div class="chat-header">
                <div class="chat-avatar">🧸</div>
                <div class="chat-info">
                    <h3>ToyVerse Assistant</h3>
                    <span>Your friendly toy shopping helper! 🎁</span>
                </div>
                <button class="close-chat" id="close-chat-btn">×</button>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <!-- Messages go here -->
            </div>

            <form class="chat-input-area" id="chat-form">
                <input type="text" id="chat-input" placeholder="Type a message..." autocomplete="off">
                <button type="submit" class="send-btn">➤</button>
            </form>
        </div>
    `;

    document.body.appendChild(root);

    // Logic
    const btn = document.getElementById('open-chat-btn');
    const windowEl = document.getElementById('chat-window');
    const closeBtn = document.getElementById('close-chat-btn');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');

    // Generate unique session ID
    let sessionId = localStorage.getItem('chatbot_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatbot_session_id', sessionId);
    }

    // Toggle
    btn.addEventListener('click', () => {
        windowEl.classList.toggle('open');
        if (windowEl.classList.contains('open') && messages.children.length === 0) {
            // First open greeting
            addMessage('bot', "Hi there! 👋 I'm ToyVerse Assistant. How can I help you find the perfect toy today? 🧸");
        }
        if (windowEl.classList.contains('open')) {
            input.focus();
        }
    });

    closeBtn.addEventListener('click', () => {
        windowEl.classList.remove('open');
    });

    // Send Message
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        // User Message
        addMessage('user', text);
        input.value = '';

        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing';
        typingDiv.innerHTML = '<span>●</span><span>●</span><span>●</span>';
        messages.appendChild(typingDiv);
        messages.scrollTop = messages.scrollHeight;

        try {
            // Send to backend API
            const response = await api.sendChatMessage(text, sessionId);

            // Remove typing indicator
            messages.removeChild(typingDiv);

            // Check if response contains ADD_TO_CART command
            const botResponse = response.response;

            if (botResponse.includes('ADD_TO_CART:')) {
                // Extract product ID
                const match = botResponse.match(/ADD_TO_CART:(\d+)/);
                if (match) {
                    const productId = parseInt(match[1]);

                    try {
                        // Add to cart
                        await api.addToCart(productId, 1);

                        // Get product info
                        const product = await api.getProductById(productId);

                        // Show success message
                        const successMsg = `✅ Added "${product.title}" to your cart! 🛒\n\nWould you like to:\n• Continue shopping\n• View your cart\n• Checkout`;
                        addMessage('bot', successMsg);
                    } catch (cartError) {
                        console.error('Error adding to cart:', cartError);
                        addMessage('bot', `Sorry, I couldn't add that item to your cart. ${cartError.message}`);
                    }
                } else {
                    // Show the bot response as-is
                    addMessage('bot', botResponse);
                }
            } else {
                // Normal response
                addMessage('bot', botResponse);
            }
        } catch (error) {
            console.error('Chat error:', error);

            // Remove typing indicator
            if (typingDiv.parentNode) {
                messages.removeChild(typingDiv);
            }

            // Fallback response
            const fallbackResponse = getFallbackResponse(text);
            addMessage('bot', fallbackResponse);
        }
    });

    function addMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;

        // Format text with line breaks
        const formattedText = text.replace(/\n/g, '<br>');
        div.innerHTML = formattedText;

        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    function getFallbackResponse(text) {
        const lower = text.toLowerCase();

        // Greetings
        if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
            return "Hello! 👋 Welcome to ToyVerse! How can I help you find the perfect toy today? 🧸";
        }

        // Products
        if (lower.includes('product') || lower.includes('toy') || lower.includes('show')) {
            return "🏪 We have a wide selection of toys! Browse by category:\n🏰 Sets | 🧸 Plushies | 🧱 Blocks | 🤖 Tech\n\nWhat type of toy are you looking for?";
        }

        // Recommendations
        if (lower.includes('recommend') || lower.includes('suggest') || lower.includes('best')) {
            return "🎯 Check out our popular items:\n• Hogwarts Castle - $120.99 ⭐⭐⭐⭐⭐\n• The Child (Baby Yoda) - $40.99 ⭐⭐⭐⭐⭐\n• Avengers Tower - $40.99 ⭐⭐⭐⭐⭐\n\nAll highly rated by customers!";
        }

        // Orders
        if (lower.includes('order') || lower.includes('track')) {
            return "📦 I can help you track your orders! Please log in to view your order history and status.";
        }

        // Shipping
        if (lower.includes('ship') || lower.includes('deliver')) {
            return "📦 Shipping Info:\n• Delivered to Islamabad, Pakistan\n• 3-5 business days delivery\n• Cash on Delivery available\n• Track your order anytime!";
        }

        // Returns
        if (lower.includes('return') || lower.includes('refund')) {
            return "↩️ Returns Policy:\n• 7-day return for unopened items\n• Items must be in original condition\n• Email: kidstoys@gmail.com";
        }

        // Price
        if (lower.includes('price') || lower.includes('cost')) {
            return "💰 Our toys range from $19.99 to $120.99. Tell me what you're looking for!";
        }

        // Payment
        if (lower.includes('payment') || lower.includes('pay') || lower.includes('cod')) {
            return "💳 Payment: Cash on Delivery (COD) available - Pay when you receive! Safe and convenient.";
        }

        // Help
        if (lower.includes('help') || lower.includes('support')) {
            return "🤝 I can help with:\n🔍 Finding products\n💰 Prices & stock\n📦 Order tracking\n🚚 Shipping info\n↩️ Returns\n\nWhat do you need?";
        }

        // Default
        return "🧸 I'm ToyVerse Assistant! I can help you with:\n• Product recommendations\n• Prices & availability\n• Orders & tracking\n• Shipping & returns\n\nWhat would you like to know?";
    }
}
