# 🏰 ToyVerse

> **Where Imagination Comes to Life.**

ToyVerse is a modern, immersive e-commerce web application designed to provide a magical shopping experience for kids and parents alike. Built with a focus on visual storytelling and interactive design, it features a dynamic user interface, real-time product filtering, and a seamless checkout process.



## ✨ Key Features

### 🎨 Immersive User Interface
- **Parallax Scroll Effects**: A dynamic landing page that responds to user scrolling, creating a depth-filled visual experience.
- **Custom Cursor**: A playful, animated cursor that adds a touch of whimsy to the navigation.
- **Glassmorphism Design**: Modern, semi-transparent UI elements that provide a sleek, premium feel.

### 🛍️ Smart Catalog & Shopping
- **Interactive Product Grid**: Browse a wide range of toys with smooth hover effects.
- **Advanced Filtering**: Filter products by category (Sets, Plushies, Tech, etc.), price range, rating, and availability.
- **Instant Search**: Real-time search functionality available globally and within the catalog.
- **Product Details**: Detailed views with image galleries, reviews, and related product suggestions.

### 🛒 Seamless Checkout
- **Persistent Cart**: Shopping cart data is saved locally, so you never lose your selected items.
- **Flexible Payment Options**: Choose between **Cash on Delivery** or a secure **Online Payment** simulation.
- **Mock Billing Portal**: A realistic billing modal for processing credit card payments (simulation only).

### 👥 User Features
- **User Accounts**: Sign up and log in functionality (simulated with LocalStorage).
- **Order History**: Track past orders and view order status.
- **Review System**: Registered users can leave ratings and reviews for products.

### 🤖 Customer Support
- **AI Chatbot**: A friendly automated assistant to help with common queries.
- **interactive FAQ**: Accordion-style frequently asked questions.
- **Direct Support**: Contact form for personalized assistance.

## 🛠️ Technology Stack

- **Core**: HTML5, CSS3 (Custom Properties & Variables), JavaScript (ES6+ Modules)
- **Build Tool**: [Vite](https://vitejs.dev/) - For lightning-fast development and optimized builds.
- **Storage**: Browser LocalStorage (No external database required for demo).
- **Styling**: Vanilla CSS with comprehensive variable systems for theming and responsiveness.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- Node.js (v14 or higher)
- npm (Node Package Manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Armaghan195/ToyVerse.git
   cd ToyVerse
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to the local URL provided in the terminal (usually `http://localhost:5173`).

## 📂 Project Structure

```
ToyVerse/
├── public/              # Static assets (images, videos)
├── pages/               # HTML pages (Catalog, Cart, Auth, etc.)
├── src/
│   ├── css/             # Stylesheets (Variables, Components)
│   ├── js/              # JavaScript Logic
│   │   ├── dataManager.js  # LocalStorage Data Handling
│   │   ├── main.js         # Landing Page Logic
│   │   ├── catalog.js      # Catalog & Filtering Logic
│   │   ├── cart.js         # Cart & Checkout Logic
│   │   └── ...
│   └── assets/          # Source assets
├── index.html           # Main Landing Page
├── package.json         # Project Dependencies
└── vite.config.js       # Vite Configuration
```

## 🔐 Mock Data & Persistence

This project uses a `DataManager` class to simulate a backend. All data (products, users, orders) is initialized and stored in your browser's **LocalStorage**. 
- **Admin Access**: A default admin user is created on first load (`username: admin`, `password: password`).
- **Resetting Data**: To reset the application state, simply clear your browser's LocalStorage for the site.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by the ToyVerse Team.
