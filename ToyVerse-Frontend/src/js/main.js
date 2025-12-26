import '../css/variables.css';
import '../css/style.css';
import '../css/search.css';
// import heroBg from '../assets/hero-bg.png'; // Removed image import

import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';

initChatbot();
document.querySelector('#app').innerHTML = `
  <header class="navbar-container" id="main-navbar"></header>
  
  <main>
    <section class="hero">
      <div class="hero-bg-container">
        <!-- Video Background -->
        <video class="hero-bg-video" muted playsinline autoplay>
            <source src="/assets/Video Project.mp4" type="video/mp4">
        </video>
      </div>
      <div class="video-overlay"></div>
      <div class="hero-text-container">
        <!-- The big text "TOY TOWN" is layered over the image in the design -->
        <h1 class="hero-title">TOY TOWN</h1>
      </div>

      <!-- Scroll Indicator -->
      <div class="scroll-indicator">
        <div class="mouse">
          <div class="wheel"></div>
        </div>
        <div class="arrow-scroll"></div>
      </div>
      
      <!-- Floating Feature Cards -->
      <div class="feature-cards">
        <div class="feature-card glass">
          <h3>Naturalness</h3>
          <p>Toys are made of natural wood, which does not cause allergies and is safe for the child's health.</p>
        </div>
        <div class="feature-card glass">
          <h3>Eco-friendly</h3>
          <p>The toys are made of eco-friendly materials that are not harmful to the environment.</p>
        </div>
      </div>
    </section>

    <section class="catalog container">
      <h2 class="section-title">CATALOG</h2>
      <div class="catalog-grid">
        <div class="cat-item large blue">
          <h3>SETS</h3>
          <p>Build iconic towers, castles, and more.</p>
          <div class="cat-img-placeholder">🏰</div>
        </div>
        <div class="cat-item square yellow">
          <h3>PLUSHIES</h3>
          <p>Soft, cuddly friends for everyone.</p>
          <div class="cat-img-placeholder">🧸</div>
        </div>
        <div class="cat-item small gray">
          <h3>BLOCKS</h3>
          <p>Build, create, and explore.</p>
          <div class="cat-img-placeholder">🧱</div>
        </div>
        <div class="cat-item tall teal">
          <h3>TECH</h3>
          <p>Interactive toys for modern play.</p>
          <div class="cat-img-placeholder">🤖</div>
        </div>
        <div class="cat-item wide pink">
          <h3>ALL TOYS</h3>
          <p>Explore our complete collection.</p>
          <div class="cat-img-placeholder">🎁</div>
        </div>
      </div>
      <div class="center-btn">
        <button class="pill-btn primary" onclick="window.location.href='/pages/catalog.html'">All products</button>
      </div>
    </section>

    <section class="special-offer container">
      <h2 class="section-title">SPECIAL OFFER</h2>
      <div class="offer-grid">
        <div class="offer-card gray-bg">
          <div class="offer-tag">-25%</div>
          <h3>FAVORITE TOYS<br>FOR ALL TASTES</h3>
          <div class="offer-img-placeholder">🎨</div>
        </div>
        <div class="offer-card gray-bg">
          <div class="offer-tag warning">-10%</div>
          <h3>BEST PRICES ON ALL MUSICAL<br>INSTRUMENTS</h3>
          <div class="offer-img-placeholder">🎹</div>
          <div class="offer-overlay">
            <p>We present a wide range of quality and safe products for children at favorable prices.</p>
            <button class="arrow-btn">→</button>
          </div>
        </div>
         <div class="offer-card gray-bg">
          <div class="offer-tag">-20%</div>
          <h3>DISCOUNTS ON TOYS<br>FOR TODDLERS</h3>
          <div class="offer-img-placeholder">🧩</div>
        </div>
        <div class="offer-card gray-bg">
          <div class="offer-tag warning">-50%</div>
          <h3>BOARD GAMES<br>AND EDUCATIONAL TOYS</h3>
          <div class="offer-img-placeholder">🎲</div>
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
          <a href="#">Brand suggestions</a>
          <a href="support.html">Support</a>
          <a href="#">About</a>
        </div>
        <div class="site-links">
           <a href="catalog.html">Catalog</a>
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
  
  <!-- Custom Cursor Element -->
  <div id="custom-cursor">
    <div class="cursor-ring"></div>
    <div class="cursor-ball">🏈</div>
  </div>
`;

renderNavbar('#main-navbar', 'home');

// Custom Cursor Logic
const cursor = document.querySelector('#custom-cursor');
if (cursor) {
  document.body.classList.add('use-custom-cursor');
  document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
  });
}

// Scroll Parallax Effect
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  const viewportHeight = window.innerHeight;

  // 1. Hero Parallax
  const heroBg = document.querySelector('.hero-bg-video');
  const heroTitle = document.querySelector('.hero-title');
  const featureCards = document.querySelector('.feature-cards');

  if (scrollY < viewportHeight * 1.5) {
    if (heroBg) heroBg.style.transform = `translateY(${scrollY * 0.5}px)`;
    if (heroTitle) heroTitle.style.transform = `translateY(${scrollY * 0.3}px)`;
    if (featureCards) featureCards.style.transform = `translateY(-${scrollY * 0.1}px)`;
  }

  // 2. Catalog Section Parallax (Staggered Grid)
  const catItems = document.querySelectorAll('.cat-item');
  if (catItems.length) {
    catItems.forEach((item, index) => {
      const rect = item.getBoundingClientRect();
      const isVisible = rect.top < viewportHeight && rect.bottom > 0;

      if (isVisible) {
        // Even items move slower, odd items move faster
        const speed = (index % 2 === 0) ? 0.05 : 0.12;
        const offset = (rect.top - viewportHeight * 0.5) * speed;
        item.style.transform = `translateY(${offset}px)`;
      } else {
        item.style.transform = 'translateY(0)';
      }
    });
  }

  // 3. Special Offers Parallax (Floating Cards)
  const offerCards = document.querySelectorAll('.offer-card');
  if (offerCards.length) {
    offerCards.forEach((card, index) => {
      const rect = card.getBoundingClientRect();
      const isVisible = rect.top < viewportHeight && rect.bottom > 0;

      if (isVisible) {
        // Different speeds for left vs right columns
        const speed = (index % 2 === 0) ? -0.05 : 0.05;
        const offset = (rect.top - viewportHeight * 0.5) * speed;
        card.style.transform = `translateY(${offset}px)`;
      }
    });
  }
});

// Video Hero Logic
const heroVideo = document.querySelector('.hero-bg-video');
const heroTitleText = document.querySelector('.hero-title');
const featureCardsContainer = document.querySelector('.feature-cards');
const scrollIndicator = document.querySelector('.scroll-indicator');

// 1. Lock scroll initially
document.body.classList.add('no-scroll');

if (heroVideo) {
  // Speed up video
  heroVideo.playbackRate = 1.5;

  // 2. Monitor time for text animation
  heroVideo.addEventListener('timeupdate', () => {
    // Text appears at 12s
    if (heroVideo.currentTime >= 12 && !heroTitleText.classList.contains('visible')) {
      heroTitleText.classList.add('visible');
    }
  });

  // 3. Unlock on end and LOOP last 1 second
  heroVideo.addEventListener('ended', () => {
    // Unlock interface (first time)
    document.body.classList.remove('no-scroll');
    if (featureCardsContainer) featureCardsContainer.classList.add('visible');

    // Reveal Scroll Indicator
    if (scrollIndicator) scrollIndicator.classList.add('visible');

    // Loop Logic: Seek back to 13.1s (0.13.10) and play
    if (heroVideo.duration > 13.1) {
      heroVideo.currentTime = 13.1;
      heroVideo.playbackRate = 1.0; // Normal speed for loop
      heroVideo.play();
    }
  });
}
