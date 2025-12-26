
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
import os
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/support", tags=["support"])

class HelpSearchRequest(BaseModel):
    query: str

class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

def get_groq_client():

    api_key = settings.groq_api_key
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Error initializing Groq client: {e}")
        return None

@router.post("/search")
async def search_help(request: HelpSearchRequest):

    try:
        query = request.query.strip()

        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        groq_client = get_groq_client()
        if groq_client:
            response = await generate_help_response(query, groq_client)
        else:
            response = get_fallback_help_response(query)

        return {
            "query": query,
            "response": response,
            "source": "groq" if groq_client else "fallback"
        }

    except Exception as e:
        logger.error(f"Error searching help: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process help request: {str(e)}"
        )

@router.post("/contact")
async def submit_contact_form(request: ContactFormRequest):

    try:

        if not request.name or not request.email or not request.message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )

        success = await send_contact_email(
            name=request.name,
            email=request.email,
            message=request.message
        )

        if success:
            return {
                "success": True,
                "message": "Your message has been sent successfully! We'll get back to you soon."
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email. Please try again later."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting contact form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit contact form: {str(e)}"
        )

async def generate_help_response(query: str, groq_client) -> str:

    try:
        system_prompt = """You are ToyVerse Support Assistant, a helpful customer support AI for ToyVerse - an online toy store.

Your role:
- Answer customer questions about products, orders, shipping, returns, and policies
- Provide clear, concise, and friendly responses
- Guide customers to appropriate resources
- Be professional yet warm and approachable

Store Information:
- Product Categories: Sets, Plushies, Blocks, Tech
- Shipping: Delivered to Islamabad, Pakistan (3-5 business days)
- Payment: Cash on Delivery (COD) available
- Returns: 7-day return policy for unopened items in original condition
- Email: kidstoys@gmail.com
- Support Email: zuhad.clasher@gmail.com

Guidelines:
- Keep responses concise (3-5 sentences)
- If you don't know something specific, suggest contacting support
- Be helpful and solution-oriented
- Use a friendly, professional tone
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        completion = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            top_p=1,
            stream=False
        )

        return completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return get_fallback_help_response(query)

def get_fallback_help_response(query: str) -> str:

    query_lower = query.lower()

    if any(word in query_lower for word in ['ship', 'deliver', 'delivery', 'shipping']):
        return "📦 We deliver to Islamabad, Pakistan within 3-5 business days. Cash on Delivery (COD) is available. You'll receive a tracking number once your order ships. For specific shipping questions, contact kidstoys@gmail.com"

    if any(word in query_lower for word in ['return', 'refund', 'exchange']):
        return "↩️ We have a 7-day return policy for unopened items in their original condition. To start a return, email us at kidstoys@gmail.com with your order number and reason for return."

    if any(word in query_lower for word in ['payment', 'pay', 'cod', 'cash']):
        return "💳 We accept Cash on Delivery (COD) - pay when you receive your order! It's safe, convenient, and requires no prepayment. For other payment options, please contact us."

    if any(word in query_lower for word in ['order', 'track', 'status']):
        return "📦 You can track your order using the tracking number sent to your email after shipment. Log in to your account to view all your orders and their current status. Need help? Contact kidstoys@gmail.com"

    if any(word in query_lower for word in ['product', 'toy', 'catalog', 'available', 'stock']):
        return "🧸 Browse our catalog to see all available toys in categories: Sets, Plushies, Blocks, and Tech. All products show real-time stock availability. Looking for something specific? Our chatbot can help!"

    if any(word in query_lower for word in ['account', 'login', 'register', 'password']):
        return "👤 Create an account to track orders, save favorites, and get personalized recommendations. Click the user icon in the top-right corner to register or log in. For password issues, contact support."

    if any(word in query_lower for word in ['price', 'cost', 'expensive', 'cheap']):
        return "💰 Our toys range from $19.99 to $120.99. Browse by category to see pricing. We offer great value on quality toys for kids! Use filters in the catalog to find toys in your budget."

    if any(word in query_lower for word in ['contact', 'email', 'support', 'help']):
        return "📧 Contact us at kidstoys@gmail.com for general inquiries or zuhad.clasher@gmail.com for support. We typically respond within 24 hours. You can also use our chatbot for instant help!"

    return "👋 I'm here to help! For specific questions about orders, shipping, returns, or products, please contact our support team at zuhad.clasher@gmail.com or kidstoys@gmail.com. You can also try our AI chatbot for instant assistance!"

async def send_contact_email(name: str, email: str, message: str) -> bool:

    try:

        smtp_server = settings.smtp_server
        smtp_port = settings.smtp_port
        smtp_username = settings.smtp_username
        smtp_password = settings.smtp_password

        if not smtp_username or not smtp_password:
            logger.warning("SMTP credentials not configured. Email not sent.")
            logger.info(f"Contact form submission: {name} ({email}): {message}")

            return True

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"ToyVerse Contact Form - Message from {name}"
        msg['From'] = smtp_username
        msg['To'] = "zuhad.clasher@gmail.com"
        msg['Reply-To'] = email

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700&display=swap');

        body {{
            font-family: 'Nunito', sans-serif;
            line-height: 1.6;
            color: #2d3748;
            max-width: 650px;
            margin: 0 auto;
            padding: 0;
            background: #f7fafc;
        }}
        .email-container {{
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            margin: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #ff6b9d 0%, #c471ed 50%, #12c2e9 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.2) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
        }}
        .logo {{
            font-family: 'Fredoka One', cursive;
            font-size: 32px;
            margin: 0 0 10px 0;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        .header-subtitle {{
            font-size: 16px;
            margin: 0;
            opacity: 0.95;
            position: relative;
            z-index: 1;
            font-weight: 600;
        }}
        .badge {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(10px);
            padding: 8px 20px;
            border-radius: 20px;
            margin-top: 15px;
            font-size: 14px;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }}
        .content {{
            padding: 40px 30px;
            background: #ffffff;
        }}
        .greeting {{
            font-size: 18px;
            color: #2d3748;
            margin: 0 0 25px 0;
            font-weight: 600;
        }}
        .info-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #ff6b9d;
        }}
        .info-row {{
            margin: 12px 0;
            display: flex;
            align-items: center;
        }}
        .info-label {{
            font-weight: 700;
            color: #c471ed;
            min-width: 90px;
            display: inline-block;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .info-value {{
            color: #2d3748;
            font-weight: 600;
        }}
        .info-value a {{
            color: #12c2e9;
            text-decoration: none;
            font-weight: 700;
        }}
        .info-value a:hover {{
            text-decoration: underline;
        }}
        .message-box {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            border: 2px solid #e9ecef;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}
        .message-header {{
            font-family: 'Fredoka One', cursive;
            color: #ff6b9d;
            font-size: 20px;
            margin: 0 0 15px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .message-text {{
            color: #4a5568;
            white-space: pre-wrap;
            line-height: 1.8;
            font-size: 15px;
        }}
        .action-box {{
            background: linear-gradient(135deg, #fff5f7 0%, #f3e7ff 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 25px 0;
            border: 2px dashed #c471ed;
        }}
        .action-text {{
            margin: 0;
            color: #5a67d8;
            font-size: 14px;
            font-weight: 600;
        }}
        .reply-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #ff6b9d 0%, #c471ed 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 700;
            margin-top: 10px;
            box-shadow: 0 4px 15px rgba(255, 107, 157, 0.4);
            transition: transform 0.2s;
        }}
        .reply-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 107, 157, 0.5);
        }}
        .footer {{
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .footer-links {{
            margin: 15px 0;
        }}
        .footer-links a {{
            color: #ff6b9d;
            text-decoration: none;
            margin: 0 15px;
            font-weight: 600;
        }}
        .footer-links a:hover {{
            color: #c471ed;
        }}
        .footer-text {{
            font-size: 13px;
            opacity: 0.8;
            margin: 10px 0;
        }}
        .divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent 0%, #e9ecef 50%, transparent 100%);
            margin: 25px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">🏰 KID TOYS</div>
            <div class="header-subtitle">Your Favorite Online Toy Store</div>
            <div class="badge">📬 NEW CONTACT MESSAGE</div>
        </div>

        <!-- Content -->
        <div class="content">
            <div class="greeting">
                Hello ToyVerse Team! 👋
            </div>

            <p style="color: #4a5568; margin-bottom: 25px;">
                You've received a new message from a customer through the contact form. Here are the details:
            </p>

            <!-- Customer Info Card -->
            <div class="info-card">
                <div class="info-row">
                    <span class="info-label">👤 Name:</span>
                    <span class="info-value">{name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📧 Email:</span>
                    <span class="info-value"><a href="mailto:{email}">{email}</a></span>
                </div>
            </div>

            <!-- Message Box -->
            <div class="message-box">
                <div class="message-header">
                    💬 Customer Message
                </div>
                <div class="message-text">{message}</div>
            </div>

            <!-- Action Box -->
            <div class="action-box">
                <p class="action-text">
                    💡 Quick Tip: Simply hit reply to respond directly to {name} at {email}
                </p>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <div style="font-family: 'Fredoka One', cursive; font-size: 20px; margin-bottom: 15px;">
                🧸 ToyVerse
            </div>
            <div class="footer-links">
                <a href="mailto:kidstoys@gmail.com">kidstoys@gmail.com</a>
                <span style="opacity: 0.5;">|</span>
                <a href="mailto:zuhad.clasher@gmail.com">Support</a>
            </div>
            <div class="divider"></div>
            <div class="footer-text">
                📍 Islamabad, Pakistan (44150)<br>
                🎁 Quality Toys for Happy Kids
            </div>
            <div style="font-size: 11px; opacity: 0.6; margin-top: 15px;">
                This email was automatically generated from the ToyVerse contact form
            </div>
        </div>
    </div>
</body>
</html>
"""

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        logger.info(f"Contact email sent successfully from {name} ({email})")
        return True

    except Exception as e:
        logger.error(f"Error sending contact email: {e}")

        logger.info(f"Contact form submission (failed to email): {name} ({email}): {message}")

        return True
