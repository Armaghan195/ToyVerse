import '../css/variables.css';
import '../css/style.css';
import '../css/search.css';
import '../css/support.css';

import { renderNavbar } from './navbar.js';
import { initChatbot } from './chatbot.js';
import api from './api.js';

document.querySelector('#support-app').innerHTML = `
  <!-- Navbar -->
  <header class="navbar-container" id="support-navbar"></header>


  <main class="container support-page">

    <!-- Support Banner -->
    <section class="support-banner">
      <div class="support-content">
        <h1>How can we help?</h1>
        <p>Find answers to common questions or get in touch with our friendly team.</p>
        <div class="search-bar">
            <input type="text" id="help-search-input" placeholder="Search for help..." autocomplete="off">
            <button id="help-search-btn">🔍</button>
        </div>
        <div id="help-search-result" class="help-search-result hidden"></div>
      </div>
      <div class="support-img">
        🤖
      </div>
    </section>

    <div class="support-layout">
      <!-- FAQ Section -->
      <section class="faq-section">
        <h2>Frequently Asked Questions</h2>

        <div class="faq-accordion">
            <div class="faq-item">
                <button class="faq-question">What is your return policy? <span class="arrow">▼</span></button>
                <div class="faq-answer">
                    <p>We offer a 30-day return policy for all unused items in their original packaging. Simply contact us to start a return.</p>
                </div>
            </div>

            <div class="faq-item">
                <button class="faq-question">How long does shipping take? <span class="arrow">▼</span></button>
                <div class="faq-answer">
                    <p>Standard shipping takes 3-5 business days. Express shipping options are available at checkout.</p>
                </div>
            </div>

            <div class="faq-item">
                <button class="faq-question">Do you ship internationally? <span class="arrow">▼</span></button>
                <div class="faq-answer">
                    <p>Yes! We ship to over 50 countries worldwide. Shipping rates vary by location.</p>
                </div>
            </div>

            <div class="faq-item">
                <button class="faq-question">How can I track my order? <span class="arrow">▼</span></button>
                <div class="faq-answer">
                    <p>Once shipped, you'll receive an email with a tracking number to view real-time updates.</p>
                </div>
            </div>
        </div>
      </section>

      <!-- Contact Form -->
      <section class="contact-section">
        <div class="contact-card">
            <h2>Contact Us</h2>
            <form class="contact-form" id="contact-form">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" id="contact-name" placeholder="Your name" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="contact-email" placeholder="Your email" required>
                </div>
                <div class="form-group">
                    <label>Message</label>
                    <textarea id="contact-message" rows="4" placeholder="How can we help you?" required></textarea>
                </div>
                <button type="submit" class="pill-btn primary" id="contact-submit-btn">Send Message</button>
                <div id="contact-form-status" class="form-status hidden"></div>
            </form>
        </div>
      </section>
    </div>

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
          <a href="#">Brand suggestions</a>
          <a href="support.html">Support</a>
          <a href="#">About</a>
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

renderNavbar('#support-navbar', 'support');
initChatbot();

// FAQ Logic
const questions = document.querySelectorAll('.faq-question');
questions.forEach(q => {
  q.addEventListener('click', () => {
    const item = q.parentElement;
    item.classList.toggle('active');
  });
});

// ==================== HELP SEARCH ====================
const helpSearchInput = document.getElementById('help-search-input');
const helpSearchBtn = document.getElementById('help-search-btn');
const helpSearchResult = document.getElementById('help-search-result');

// Search on button click
helpSearchBtn.addEventListener('click', async () => {
  const query = helpSearchInput.value.trim();
  if (!query) return;

  await performHelpSearch(query);
});

// Search on Enter key
helpSearchInput.addEventListener('keydown', async (e) => {
  if (e.key === 'Enter') {
    const query = helpSearchInput.value.trim();
    if (!query) return;

    await performHelpSearch(query);
  }
});

async function performHelpSearch(query) {
  try {
    // Show loading state
    helpSearchResult.classList.remove('hidden');
    helpSearchResult.innerHTML = `
      <div class="search-loading">
        <div class="typing-indicator">
          <span>●</span><span>●</span><span>●</span>
        </div>
        <p>Searching for help...</p>
      </div>
    `;

    // Call API
    const response = await api.searchHelp(query);

    // Show result
    helpSearchResult.innerHTML = `
      <div class="search-result-header">
        <strong>🔍 Search Result</strong>
        <button class="close-result-btn" onclick="document.getElementById('help-search-result').classList.add('hidden')">×</button>
      </div>
      <div class="search-result-content">
        ${response.response.replace(/\n/g, '<br>')}
      </div>
      <div class="search-result-footer">
        <small>Powered by ${response.source === 'groq' ? 'AI Assistant' : 'ToyVerse Support'}</small>
      </div>
    `;
  } catch (error) {
    console.error('Help search error:', error);
    helpSearchResult.innerHTML = `
      <div class="search-result-header">
        <strong>❌ Error</strong>
        <button class="close-result-btn" onclick="document.getElementById('help-search-result').classList.add('hidden')">×</button>
      </div>
      <div class="search-result-content">
        Sorry, we couldn't process your search at the moment. Please try again or contact support directly.
      </div>
    `;
  }
}

// ==================== CONTACT FORM ====================
const contactForm = document.getElementById('contact-form');
const contactName = document.getElementById('contact-name');
const contactEmail = document.getElementById('contact-email');
const contactMessage = document.getElementById('contact-message');
const contactSubmitBtn = document.getElementById('contact-submit-btn');
const contactFormStatus = document.getElementById('contact-form-status');

contactForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const name = contactName.value.trim();
  const email = contactEmail.value.trim();
  const message = contactMessage.value.trim();

  // Basic validation
  if (!name || !email || !message) {
    showFormStatus('error', 'Please fill in all fields.');
    return;
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showFormStatus('error', 'Please enter a valid email address.');
    return;
  }

  try {
    // Disable submit button
    contactSubmitBtn.disabled = true;
    contactSubmitBtn.textContent = 'Sending...';

    // Call API
    const response = await api.submitContactForm(name, email, message);

    if (response.success) {
      showFormStatus('success', response.message);

      // Clear form
      contactForm.reset();

      // Re-enable button after delay
      setTimeout(() => {
        contactSubmitBtn.disabled = false;
        contactSubmitBtn.textContent = 'Send Message';
      }, 3000);
    } else {
      throw new Error('Failed to send message');
    }
  } catch (error) {
    console.error('Contact form error:', error);
    showFormStatus('error', 'Failed to send message. Please try again or email us directly at zuhad.clasher@gmail.com');

    // Re-enable button
    contactSubmitBtn.disabled = false;
    contactSubmitBtn.textContent = 'Send Message';
  }
});

function showFormStatus(type, message) {
  contactFormStatus.className = `form-status ${type}`;
  contactFormStatus.textContent = message;
  contactFormStatus.classList.remove('hidden');

  // Auto-hide after 5 seconds
  setTimeout(() => {
    contactFormStatus.classList.add('hidden');
  }, 5000);
}
