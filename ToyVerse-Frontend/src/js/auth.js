import '../css/variables.css';
import '../css/style.css';
import api from './api.js';

document.querySelector('#auth-app').innerHTML = `
  <div class="auth-page">
    <!-- Navbar -->
    <header class="auth-navbar">
      <a href="/index.html" class="logo">🏰 KID TOYS</a>
    </header>

    <main class="auth-container">
      <!-- Login Form -->
      <div id="login-card" class="auth-card">
        <h2>Welcome Back! 👋</h2>
        <p class="auth-subtitle">Log in to continue shopping</p>
        <p class="error-msg" id="login-error"></p>

        <form id="login-form" class="auth-form">
          <div class="form-group">
            <label>Username or Email</label>
            <input type="text" id="login-username" placeholder="Enter your username or email" required autocomplete="username">
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" id="login-password" placeholder="Enter your password" required autocomplete="current-password">
          </div>
          <button type="submit" class="auth-btn" id="login-btn">
            <span class="btn-text">Log In</span>
            <span class="btn-loader hidden">Logging in...</span>
          </button>
        </form>

        <div class="toggle-text">
          New here? <span class="toggle-link" id="show-register">Create Account</span>
        </div>
      </div>

      <!-- Register Form -->
      <div id="register-card" class="auth-card hidden">
        <h2>Join ToyVerse! 🎁</h2>
        <p class="auth-subtitle">Create an account to start shopping</p>
        <p class="error-msg" id="register-error"></p>

        <form id="register-form" class="auth-form">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" id="reg-name" placeholder="Enter your full name" required autocomplete="name">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" id="reg-email" placeholder="Enter your email" required autocomplete="email">
          </div>
          <div class="form-group">
            <label>Username</label>
            <input type="text" id="reg-username" placeholder="Choose a username" required autocomplete="username">
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" id="reg-password" placeholder="Create a password (min 6 characters)" required autocomplete="new-password" minlength="6">
          </div>
          <button type="submit" class="auth-btn" id="register-btn">
            <span class="btn-text">Create Account</span>
            <span class="btn-loader hidden">Creating account...</span>
          </button>
        </form>

        <div class="toggle-text">
          Already have an account? <span class="toggle-link" id="show-login">Log In</span>
        </div>
      </div>
    </main>

    <div class="auth-footer">
      <p>© 2024 ToyVerse - Quality Toys for Happy Kids 🧸</p>
    </div>
  </div>

  <style>
    .auth-page {
      min-height: 100vh;
      background: linear-gradient(135deg, #12c2e9 0%, #c471ed 50%, #f64f59 100%);
      display: flex;
      flex-direction: column;
    }

    .auth-navbar {
      padding: 20px 40px;
    }

    .auth-navbar .logo {
      font-family: 'Fredoka One', cursive;
      font-size: 1.8rem;
      color: white;
      text-decoration: none;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    .auth-container {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
    }

    .auth-card {
      background: white;
      padding: 50px 40px;
      border-radius: 30px;
      width: 100%;
      max-width: 450px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
      animation: slideUp 0.4s ease-out;
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .auth-card h2 {
      font-family: 'Fredoka One', cursive;
      font-size: 2rem;
      color: var(--text-dark);
      margin: 0 0 10px 0;
      text-align: center;
    }

    .auth-subtitle {
      text-align: center;
      color: #666;
      margin: 0 0 30px 0;
      font-size: 0.95rem;
    }

    .auth-form {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .form-group {
      text-align: left;
    }

    .form-group label {
      display: block;
      margin-bottom: 8px;
      font-weight: 600;
      color: var(--text-dark);
      font-size: 0.95rem;
    }

    .form-group input {
      width: 100%;
      padding: 14px 18px;
      border-radius: 12px;
      border: 2px solid #e0e0e0;
      background: #f9f9f9;
      font-size: 1rem;
      outline: none;
      transition: all 0.3s;
      font-family: 'Nunito', sans-serif;
    }

    .form-group input:focus {
      border-color: #12c2e9;
      background: white;
      box-shadow: 0 0 0 3px rgba(18, 194, 233, 0.1);
    }

    .error-msg {
      color: #e74c3c;
      font-size: 0.9rem;
      text-align: center;
      min-height: 20px;
      margin: -10px 0 10px 0;
      font-weight: 600;
    }

    .auth-btn {
      background: var(--gradient-primary);
      color: white;
      border: none;
      padding: 16px;
      border-radius: 12px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      margin-top: 10px;
      position: relative;
    }

    .auth-btn:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(18, 194, 233, 0.4);
    }

    .auth-btn:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }

    .btn-loader {
      display: none;
    }

    .btn-loader.hidden {
      display: none;
    }

    .toggle-text {
      text-align: center;
      margin-top: 25px;
      font-size: 0.95rem;
      color: #666;
    }

    .toggle-link {
      color: #12c2e9;
      cursor: pointer;
      font-weight: 700;
      text-decoration: none;
      transition: color 0.2s;
    }

    .toggle-link:hover {
      color: #c471ed;
      text-decoration: underline;
    }

    .hidden {
      display: none !important;
    }

    .auth-footer {
      padding: 20px;
      text-align: center;
      color: white;
      font-size: 0.9rem;
      opacity: 0.9;
    }

    @media (max-width: 768px) {
      .auth-card {
        padding: 40px 30px;
      }

      .auth-card h2 {
        font-size: 1.6rem;
      }
    }
  </style>
`;

// DOM Elements
const loginCard = document.getElementById('login-card');
const registerCard = document.getElementById('register-card');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginError = document.getElementById('login-error');
const registerError = document.getElementById('register-error');
const showRegisterLink = document.getElementById('show-register');
const showLoginLink = document.getElementById('show-login');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');

// Toggle between login and register
showRegisterLink.addEventListener('click', () => {
  loginCard.classList.add('hidden');
  registerCard.classList.remove('hidden');
  loginError.textContent = '';
  loginForm.reset();
});

showLoginLink.addEventListener('click', () => {
  registerCard.classList.add('hidden');
  loginCard.classList.remove('hidden');
  registerError.textContent = '';
  registerForm.reset();
});

// Handle Login
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.textContent = '';

  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;

  if (!username || !password) {
    loginError.textContent = 'Please fill in all fields';
    return;
  }

  // Show loading state
  loginBtn.disabled = true;
  loginBtn.querySelector('.btn-text').classList.add('hidden');
  loginBtn.querySelector('.btn-loader').classList.remove('hidden');

  try {
    const result = await api.login(username, password);

    // Block admins from using customer portal
    if (result.user && result.user.role === 'admin') {
      loginError.textContent = 'Admin accounts cannot access the customer portal';
      api.logout();
      loginBtn.disabled = false;
      loginBtn.querySelector('.btn-text').classList.remove('hidden');
      loginBtn.querySelector('.btn-loader').classList.add('hidden');
      return;
    }

    // Success - redirect to catalog
    window.location.href = '/pages/catalog.html';
  } catch (err) {
    console.error('Login failed:', err);
    loginError.textContent = err.message || 'Invalid username or password';

    // Reset button
    loginBtn.disabled = false;
    loginBtn.querySelector('.btn-text').classList.remove('hidden');
    loginBtn.querySelector('.btn-loader').classList.add('hidden');
  }
});

// Handle Register
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  registerError.textContent = '';

  const name = document.getElementById('reg-name').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;

  // Validation
  if (!name || !email || !username || !password) {
    registerError.textContent = 'Please fill in all fields';
    return;
  }

  if (password.length < 6) {
    registerError.textContent = 'Password must be at least 6 characters';
    return;
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    registerError.textContent = 'Please enter a valid email address';
    return;
  }

  // Show loading state
  registerBtn.disabled = true;
  registerBtn.querySelector('.btn-text').classList.add('hidden');
  registerBtn.querySelector('.btn-loader').classList.remove('hidden');

  try {
    await api.register({
      name,
      username,
      password,
      email,
      role: 'customer'
    });

    // Success - show message and switch to login
    alert('🎉 Account created successfully! Please log in to continue.');

    // Switch to login form
    registerCard.classList.add('hidden');
    loginCard.classList.remove('hidden');
    registerForm.reset();

    // Pre-fill username
    document.getElementById('login-username').value = username;
    document.getElementById('login-password').focus();

  } catch (err) {
    console.error('Registration failed:', err);
    registerError.textContent = err.message || 'Registration failed. Username or email may already exist.';
  } finally {
    // Reset button
    registerBtn.disabled = false;
    registerBtn.querySelector('.btn-text').classList.remove('hidden');
    registerBtn.querySelector('.btn-loader').classList.add('hidden');
  }
});

// Check if user is already logged in
const currentUser = localStorage.getItem('current_user');
if (currentUser) {
  // Already logged in, redirect to catalog
  window.location.href = '/pages/catalog.html';
}
