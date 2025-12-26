from typing import Optional, List, Dict, Any
import logging
import os
from groq import Groq

from app.services.base_service import BaseService
from app.repositories.chat_repository import ChatRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)

class ChatbotService(BaseService[ChatMessage]):
    def __init__(
        self,
        repository: ChatRepository,
        product_repository: ProductRepository,
        order_repository: OrderRepository
    ):
        super().__init__(repository)
        self._product_repository = product_repository
        self._order_repository = order_repository

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set. Chatbot will use fallback responses.")
            self._groq_client = None
        else:
            self._groq_client = Groq(api_key=api_key)

    def get_by_id(self, id: int) -> Optional[ChatMessage]:
        try:
            return self._repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Error getting chat message: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        try:
            return self._repository.get_all(skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting all chat messages: {e}")
            return []

    def create(self, data: dict) -> Optional[ChatMessage]:
        try:
            if not self._validate(data):
                return None

            message = ChatMessage(
                user_id=data.get('user_id'),
                session_id=data.get('session_id'),
                message=data.get('message'),
                response=data.get('response'),
                context_used=data.get('context_used')
            )

            return self._repository.create(message)
        except Exception as e:
            self._logger.error(f"Error creating chat message: {e}")
            return None

    def update(self, id: int, data: dict) -> Optional[ChatMessage]:
        try:
            return self._repository.update(id, data)
        except Exception as e:
            self._logger.error(f"Error updating chat message: {e}")
            return None

    def delete(self, id: int) -> bool:
        try:
            return self._repository.delete(id)
        except Exception as e:
            self._logger.error(f"Error deleting chat message: {e}")
            return False

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        try:
            return self._repository.get_by_session(session_id, skip=0, limit=limit)
        except Exception as e:
            self._logger.error(f"Error getting conversation history: {e}")
            return []

    def process_message(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            conversation_history = self.get_conversation_history(session_id, limit=5)

            context = self._build_context(message, user_id)

            response = self._generate_response(message, conversation_history, context)

            chat_message = self.create({
                'user_id': user_id,
                'session_id': session_id,
                'message': message,
                'response': response,
                'context_used': context.get('summary', '')
            })

            return {
                'message': message,
                'response': response,
                'session_id': session_id,
                'chat_id': chat_message.id if chat_message else None
            }

        except Exception as e:
            self._logger.error(f"Error processing message: {e}")
            return {
                'message': message,
                'response': "I'm sorry, I encountered an error. Please try again.",
                'session_id': session_id,
                'error': str(e)
            }

    def _build_context(self, message: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        context = {
            'products': [],
            'orders': [],
            'summary': ''
        }

        message_lower = message.lower()

        if any(word in message_lower for word in ['product', 'toy', 'price', 'stock', 'available', 'buy', 'add', 'cart', 'purchase']):
            products = self._product_repository.get_all(skip=0, limit=20)
            context['products'] = [
                {
                    'id': p.id,
                    'title': p.title,
                    'price': float(p.price),
                    'category': p.category,
                    'stock': p.stock,
                    'rating': p.rating,
                    'in_stock': p.is_in_stock
                }
                for p in products
            ]
            context['summary'] += f"Available products: {len(products)}. "
            context['user_logged_in'] = user_id is not None

        if user_id and any(word in message_lower for word in ['order', 'purchase', 'bought', 'track']):
            orders = self._order_repository.get_by_user_id(user_id, skip=0, limit=5)
            context['orders'] = [
                {
                    'order_number': o.order_number,
                    'status': o.status,
                    'total': float(o.total),
                    'items_count': len(o.items)
                }
                for o in orders
            ]
            context['summary'] += f"User orders: {len(orders)}. "

        return context

    def _generate_response(
        self,
        message: str,
        history: List[ChatMessage],
        context: Dict[str, Any]
    ) -> str:
        if not self._groq_client:
            return self._fallback_response(message, context)

        try:
            system_prompt = self._build_system_prompt(context)

            messages = [{"role": "system", "content": system_prompt}]

            for msg in history[-5:]:
                messages.append({"role": "user", "content": msg.message})
                messages.append({"role": "assistant", "content": msg.response})

            messages.append({"role": "user", "content": message})

            completion = self._groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                stream=False
            )

            return completion.choices[0].message.content

        except Exception as e:
            self._logger.error(f"Error calling Groq API: {e}")
            return self._fallback_response(message, context)

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        user_logged_in = context.get('user_logged_in', False)

        prompt = """You are ToyVerse Assistant 🧸, a helpful and friendly AI chatbot for ToyVerse - an online toy store specializing in quality toys for kids.

Your responsibilities:
1. 🔍 Help customers discover and find the perfect toys
2. 💰 Answer questions about products, prices, stock availability, and categories
3. 🛒 Help users add items to their cart (only if they're logged in)
4. 📦 Track orders and provide order status updates
5. ℹ️ Answer FAQs about shipping, returns, payment methods, and store policies
6. 🎁 Suggest products based on age, interests, or categories (Sets, Plushies, Blocks, Tech)
7. 🛍️ Guide users through the shopping process (browsing, cart, checkout)

Product Categories Available:
- 🏰 Sets: Building sets, playsets, themed collections
- 🧸 Plushies: Soft toys, stuffed animals, character plushies
- 🧱 Blocks: Building blocks, construction toys
- 🤖 Tech: Electronic toys, interactive gadgets

Adding to Cart:
- When a user wants to add a product to cart, respond with: "ADD_TO_CART:PRODUCT_ID"
- Example: If they want "Hogwarts Castle" (ID: 8), respond: "ADD_TO_CART:8"
- ONLY use this format if the user is logged in and explicitly wants to add to cart
- If user is NOT logged in, tell them: "Please log in to add items to your cart! 🔐"
- The format is: ADD_TO_CART:PRODUCT_ID (nothing else on that line)

"""

        if user_logged_in:
            prompt += "\n✅ USER IS LOGGED IN - You can help them add items to cart!\n"
        else:
            prompt += "\n⚠️ USER IS NOT LOGGED IN - Ask them to log in before adding to cart.\n"

        prompt += """
Guidelines:
- Keep responses concise (2-4 sentences) but informative
- Use emojis to make conversations engaging and fun
- If asking about a specific product, reference its ID, name, price, and availability
- For product recommendations, suggest 2-3 relevant items with prices
- If you don't have information, politely admit it and suggest browsing the catalog
- Never make up prices, stock levels, or product details
- Be warm, helpful, and child-friendly in tone
- For orders, always mention order number and status clearly

Payment & Shipping Info:
- Payment: Cash on Delivery (COD) available
- Shipping: Delivered to your doorstep in Islamabad, Pakistan
- Returns: 7-day return policy for unopened items
- Support: Email at kidstoys@gmail.com

"""

        if context['products']:
            prompt += f"\n\nAvailable Products ({len(context['products'])}):\n"
            for p in context['products'][:10]:
                stock_status = "In Stock" if p['in_stock'] else "Out of Stock"
                prompt += f"- {p['title']}: ${p['price']} ({p['category']}) - {stock_status} - Rating: {p['rating']}/5\n"

        if context['orders']:
            prompt += f"\n\nCustomer's Recent Orders ({len(context['orders'])}):\n"
            for o in context['orders']:
                prompt += f"- Order #{o['order_number']}: Status: {o['status']}, Total: ${o['total']}\n"

        prompt += "\n\nFAQs:\n"
        prompt += "- Shipping: Free shipping on orders over $50\n"
        prompt += "- Returns: 30-day return policy\n"
        prompt += "- Payment: We accept COD and online payment\n"
        prompt += "- Delivery: 3-5 business days\n"

        return prompt

    def _fallback_response(self, message: str, context: Dict[str, Any]) -> str:
        message_lower = message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! 👋 Welcome to ToyVerse! I'm your friendly toy shopping assistant. How can I help you find the perfect toy today? 🧸"

        if any(word in message_lower for word in ['product', 'toy', 'available', 'show', 'list']):
            if context['products']:
                products_list = "\n".join([f"• {p['title']} - ${p['price']} ({p['stock']} in stock)" for p in context['products'][:5]])
                return f"🎁 Here are some awesome toys we have:\n{products_list}\n\nWant to know more about any of these?"
            return "🏪 We have a wide selection of toys! Browse by category:\n🏰 Sets | 🧸 Plushies | 🧱 Blocks | 🤖 Tech\n\nWhich category interests you?"

        if any(word in message_lower for word in ['recommend', 'suggest', 'best', 'popular']):
            if context['products']:
                top_products = sorted(context['products'], key=lambda x: x.get('rating', 0) * x.get('reviews', 1), reverse=True)[:3]
                products_list = "\n".join([f"⭐ {p['title']} (ID: {p['id']}) - ${p['price']} ({p['rating']}★)" for p in top_products])
                return f"🎯 Here are our most popular toys:\n{products_list}\n\nAll are highly rated! Want to add any to your cart?"
            return "✨ Our customers love our building sets and plushies! Check out the catalog for top-rated items."

        if any(word in message_lower for word in ['add to cart', 'add cart', 'buy this', 'purchase this', 'i want this', 'get this']):
            user_logged_in = context.get('user_logged_in', False)
            if not user_logged_in:
                return "🔐 Please log in to add items to your cart! You can log in from the top-right corner of the page."

            if context['products']:
                return f"📝 Please tell me the product ID or name you want to add. For example:\n• 'Add ID 8 to cart' for Hogwarts Castle\n• 'I want The Child'\n\nWhich product would you like?"
            return "🛒 I can help you add items to cart! First, tell me which product you're interested in."

        if 'sets' in message_lower or 'building' in message_lower:
            return "🏰 Our Sets category includes building sets, playsets, and themed collections like Avengers Tower, Hogwarts Castle, and more! Prices range from $29.99 to $120.99."

        if 'plush' in message_lower or 'soft' in message_lower or 'stuffed' in message_lower:
            return "🧸 We have adorable plushies including Venomized Groot, The Child (Baby Yoda), and Dobby! Perfect for cuddling and collecting. Prices start at $19.99."

        if 'blocks' in message_lower or 'brick' in message_lower:
            return "🧱 Check out our Blocks category! We have Monkey King, Mighty Bowser, and other creative building toys for imaginative play."

        if 'price' in message_lower or 'cost' in message_lower or 'how much' in message_lower:
            if context['products']:
                return f"💰 Our toys range from ${min(p['price'] for p in context['products']):.2f} to ${max(p['price'] for p in context['products']):.2f}. Which product are you interested in?"
            return "💰 Our toys range from $19.99 to $120.99. Tell me what type of toy you're looking for and I'll show you options!"

        if any(word in message_lower for word in ['order', 'track', 'purchase']):
            if context['orders']:
                latest_order = context['orders'][0]
                return f"📦 Your latest order #{latest_order['order_number']} is currently {latest_order['status']}. Total: ${latest_order['total']:.2f}"
            return "📦 I can help you track your orders! Please log in to view your order history and status."

        if 'ship' in message_lower or 'deliver' in message_lower:
            return "📦 Shipping Info:\n• We deliver to Islamabad, Pakistan\n• Delivery takes 3-5 business days\n• Cash on Delivery (COD) available\n• Track your order anytime!"

        if 'return' in message_lower or 'refund' in message_lower:
            return "↩️ Returns Policy:\n• 7-day return for unopened items\n• Items must be in original condition\n• Contact kidstoys@gmail.com for return requests"

        if 'payment' in message_lower or 'pay' in message_lower or 'cod' in message_lower:
            return "💳 Payment Options:\n• Cash on Delivery (COD) - Pay when you receive\n• Safe and convenient\n• No prepayment required!"

        if 'stock' in message_lower or 'in stock' in message_lower:
            if context['products']:
                in_stock = [p for p in context['products'] if p['stock'] > 0]
                return f"✅ We currently have {len(in_stock)} products in stock! Which category are you interested in?"
            return "📊 Check our catalog for real-time stock availability. All products show current stock levels!"

        if any(word in message_lower for word in ['help', 'support', 'assist']):
            return "🤝 I'm here to help! I can assist with:\n🔍 Finding products & recommendations\n💰 Checking prices & availability\n📦 Tracking orders\n🚚 Shipping & delivery info\n↩️ Returns policy\n💳 Payment methods\n\nWhat would you like to know?"

        return "🧸 I'm ToyVerse Assistant! Ask me about:\n• Product recommendations\n• Prices & stock\n• Orders & tracking\n• Shipping & returns\n• Payment methods\n\nHow can I help you today? 😊"

    def clear_conversation(self, session_id: str) -> bool:
        try:
            return self._repository.clear_session(session_id)
        except Exception as e:
            self._logger.error(f"Error clearing conversation: {e}")
            return False

    def _validate(self, data: dict) -> bool:
        required_fields = ['session_id', 'message', 'response']
        for field in required_fields:
            if field not in data or not data[field]:
                self._logger.warning(f"Missing required field: {field}")
                return False
        return True
