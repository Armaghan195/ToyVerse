import '../css/variables.css';
import '../css/style.css';
import '../css/about.css';

import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';

document.querySelector('#about-app').innerHTML = `
  <!-- Navbar -->
  <header class="navbar-container" id="about-navbar"></header>

  <main class="about-page">

    <!-- Hero Section -->
    <section class="about-hero">
      <div class="hero-content">
        <div class="hero-badge">🎁 Welcome to ToyVerse</div>
        <h1 class="hero-title">Bringing Joy to Kids<br/>One Toy at a Time</h1>
        <p class="hero-description">
          Your trusted online destination for quality toys that inspire creativity,
          learning, and endless fun for children of all ages.
        </p>
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">500+</div>
            <div class="stat-label">Happy Customers</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">1000+</div>
            <div class="stat-label">Toys Delivered</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">4.8★</div>
            <div class="stat-label">Average Rating</div>
          </div>
        </div>
      </div>
      <div class="hero-emoji">🧸</div>
    </section>

    <!-- Our Story Section -->
    <section class="story-section container">
      <div class="section-header">
        <h2>Our Story</h2>
        <div class="section-underline"></div>
      </div>

      <div class="story-content">
        <div class="story-text">
          <p class="story-intro">
            ToyVerse began with a simple mission: to make quality toys accessible to every child in Pakistan.
            We believe that play is essential for childhood development, and every child deserves toys that
            inspire imagination and creativity.
          </p>

          <p>
            Based in <strong>Islamabad, Pakistan</strong>, we've built a carefully curated collection of toys
            that combines quality, safety, and fun. From educational building sets to cuddly plushies,
            each product in our store is selected with care.
          </p>

          <p>
            What started as a small venture has grown into a trusted name among parents who want the best
            for their children. We're proud to serve families across Islamabad and beyond, delivering
            smiles one package at a time.
          </p>
        </div>

        <div class="story-image">
          <div class="image-placeholder">
            <div class="emoji-grid">
              <span>🏰</span>
              <span>🧸</span>
              <span>🚂</span>
              <span>🎨</span>
              <span>🦒</span>
              <span>🎁</span>
              <span>🧩</span>
              <span>🤖</span>
              <span>⭐</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Our Values Section -->
    <section class="values-section">
      <div class="container">
        <div class="section-header">
          <h2>What We Stand For</h2>
          <div class="section-underline"></div>
        </div>

        <div class="values-grid">
          <div class="value-card">
            <div class="value-icon">✨</div>
            <h3>Quality First</h3>
            <p>Every toy is carefully selected to meet high safety and quality standards. We only offer products we'd give to our own children.</p>
          </div>

          <div class="value-card">
            <div class="value-icon">💝</div>
            <h3>Customer Happiness</h3>
            <p>Your satisfaction is our priority. From browsing to delivery, we ensure a smooth and delightful shopping experience.</p>
          </div>

          <div class="value-card">
            <div class="value-icon">🌟</div>
            <h3>Affordable Prices</h3>
            <p>Quality toys shouldn't break the bank. We offer competitive prices and great value for every rupee spent.</p>
          </div>

          <div class="value-card">
            <div class="value-icon">🚀</div>
            <h3>Fast Delivery</h3>
            <p>We know kids can't wait! That's why we offer quick delivery (3-5 days) with Cash on Delivery option.</p>
          </div>

          <div class="value-card">
            <div class="value-icon">🛡️</div>
            <h3>Safe & Secure</h3>
            <p>All our toys meet international safety standards. Your child's safety is our top concern.</p>
          </div>

          <div class="value-card">
            <div class="value-icon">💬</div>
            <h3>Always Here</h3>
            <p>Got questions? Our friendly support team is ready to help. Reach us anytime at kidstoys@gmail.com</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Categories Section -->
    <section class="categories-section container">
      <div class="section-header">
        <h2>What We Offer</h2>
        <div class="section-underline"></div>
      </div>

      <div class="categories-grid">
        <div class="category-card" onclick="window.location.href='/pages/catalog.html?category=Sets'">
          <div class="category-emoji">🏰</div>
          <h3>Building Sets</h3>
          <p>Complex sets that challenge creativity and problem-solving skills.</p>
          <button class="category-btn">Explore Sets</button>
        </div>

        <div class="category-card" onclick="window.location.href='/pages/catalog.html?category=Plushies'">
          <div class="category-emoji">🧸</div>
          <h3>Plushies</h3>
          <p>Soft, cuddly friends that provide comfort and companionship.</p>
          <button class="category-btn">Explore Plushies</button>
        </div>

        <div class="category-card" onclick="window.location.href='/pages/catalog.html?category=Blocks'">
          <div class="category-emoji">🧱</div>
          <h3>Building Blocks</h3>
          <p>Classic blocks that inspire endless creative possibilities.</p>
          <button class="category-btn">Explore Blocks</button>
        </div>

        <div class="category-card" onclick="window.location.href='/pages/catalog.html?category=Tech'">
          <div class="category-emoji">🤖</div>
          <h3>Tech Toys</h3>
          <p>Interactive gadgets that blend fun with learning.</p>
          <button class="category-btn">Explore Tech</button>
        </div>
      </div>
    </section>

    <!-- Why Choose Us Section -->
    <section class="why-us-section">
      <div class="container">
        <div class="section-header">
          <h2>Why Parents Trust ToyVerse</h2>
          <div class="section-underline"></div>
        </div>

        <div class="features-list">
          <div class="feature-item">
            <div class="feature-icon">📦</div>
            <div class="feature-content">
              <h4>Cash on Delivery</h4>
              <p>Pay only when you receive your order. No prepayment required!</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">🔄</div>
            <div class="feature-content">
              <h4>7-Day Returns</h4>
              <p>Not satisfied? Return unopened items within 7 days for a full refund.</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div class="feature-content">
              <h4>Quality Guaranteed</h4>
              <p>Every product is inspected to ensure it meets our high standards.</p>
            </div>
          </div>

          <div class="feature-item">
            <div class="feature-icon">💬</div>
            <div class="feature-content">
              <h4>24/7 Support</h4>
              <p>Our AI chatbot and support team are always ready to help you.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact CTA Section -->
    <section class="cta-section">
      <div class="cta-content">
        <h2>Have Questions?</h2>
        <p>We'd love to hear from you! Get in touch with our friendly team.</p>
        <div class="cta-buttons">
          <button class="pill-btn primary" onclick="window.location.href='/pages/support.html'">Contact Support</button>
          <button class="pill-btn secondary" onclick="window.location.href='/pages/catalog.html'">Browse Catalog</button>
        </div>
      </div>
    </section>

  </main>

  <footer class="footer container">
    <div class="footer-card">
      <div class="footer-links">
        <div class="contact-info">
          <p>E-mail:<br><strong>kidstoys@gmail.com</strong></p>
          <p>Address:<br><strong>Islamabad, Pakistan, (44150)</strong></p>
        </div>
        <div class="site-links">
          <a href="catalog.html">Catalog</a>
          <a href="brand-suggestions.html">Brand suggestions</a>
          <a href="support.html">Support</a>
          <a href="about.html">About</a>
        </div>
        <div class="site-links">
           <a href="#">Contact</a>
           <a href="#">FAQ</a>
        </div>
      </div>
      <div class="footer-illustration">
         🦒🧸🚂
      </div>
    </div>
    <div class="copyright">
      © 2024 All rights reserved
    </div>
  </footer>
`;

renderNavbar('#about-navbar', 'about');
initChatbot();
