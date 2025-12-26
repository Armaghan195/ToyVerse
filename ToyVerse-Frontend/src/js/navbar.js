import api from './api.js';

/**
 * Shared Navbar Component
 * Renders the navigation bar into a target element.
 */
export function renderNavbar(targetSelector, activePage = '') {
  const target = document.querySelector(targetSelector);
  if (!target) return;

  const user = JSON.parse(localStorage.getItem('current_user') || 'null');

  const userClass = user ? 'logged-in' : '';

  // Decide button action: if logged in, toggle menu; if not, go to auth
  // We use a common ID and handle logic in listener
  const userBtnAttr = 'id="user-menu-btn"';

  // Prepare profile picture URL
  const profilePictureUrl = user && user.profile_picture
    ? `http://localhost:8000${user.profile_picture}`
    : '';
  const avatarInitial = user && (user.full_name ? user.full_name.charAt(0).toUpperCase() : user.username.charAt(0).toUpperCase());

  const menuHtml = user ? `
    <div class="user-dropdown hidden" id="user-dropdown">
        <div class="dropdown-header">
            <div class="user-avatar" style="${profilePictureUrl ? `background-image: url('${profilePictureUrl}');` : ''}">${profilePictureUrl ? '' : avatarInitial}</div>
            <div class="user-info">
                <strong class="user-name">${user.full_name || user.username}</strong>
                <span class="user-email">${user.email || ''}</span>
                <span class="user-role">${user.role === 'admin' ? '👑 Admin' : '👤 Customer'}</span>
            </div>
        </div>
        <div class="dropdown-divider"></div>
        <ul class="dropdown-items">
            <li><a href="/pages/profile.html"><span class="menu-icon">👤</span> My Profile</a></li>
            <li><a href="#" onclick="alert('Orders page coming soon!')"><span class="menu-icon">📦</span> My Orders</a></li>
            <li><a href="/pages/wishlist.html"><span class="menu-icon">❤️</span> My Wishlist</a></li>
            <li><a href="/pages/cart.html"><span class="menu-icon">🛒</span> My Cart</a></li>
            <li><a href="/pages/support.html"><span class="menu-icon">💬</span> Support</a></li>
            <li class="dropdown-divider"></li>
            <li><button id="logout-btn" class="logout-btn"><span class="menu-icon">🚪</span> Logout</button></li>
        </ul>
    </div>
  ` : '';

  target.innerHTML = `
    <nav class="navbar">
      <a href="/index.html" class="logo" style="text-decoration: none;">🏰 KID TOYS</a>
      <ul class="nav-links">
        <li><a href="/pages/catalog.html" class="${activePage === 'catalog' ? 'active' : ''}">Catalog</a></li>
        <li><a href="/pages/wishlist.html" class="${activePage === 'wishlist' ? 'active' : ''}">Wishlist</a></li>
        <li><a href="/pages/brand-suggestions.html" class="${activePage === 'brand-suggestions' ? 'active' : ''}">Brand suggestions</a></li>
        <li><a href="/pages/support.html" class="${activePage === 'support' ? 'active' : ''}">Support</a></li>
        <li><a href="/pages/about.html" class="${activePage === 'about' ? 'active' : ''}">About</a></li>
      </ul>
      <div class="nav-icons" style="position:relative;">
        <button class="icon-btn">🔍</button>
        <button class="icon-btn cart-btn" id="cart-btn" onclick="window.location.href='/pages/cart.html'">
          🛒
          <span id="cart-count" class="cart-count hidden">0</span>
        </button>
        <div class="divider">|</div>
        <span class="lang">EN</span>
        <div class="divider">|</div>
        <button class="icon-btn ${userClass}" ${userBtnAttr}>👤</button>
        ${menuHtml}
      </div>
    </nav>
    `;

  // Inject Search Dropdown
  // We attach it to the target container so it moves with the navbar
  if (!target.querySelector('#nav-search-dropdown')) {
    const searchDropdown = document.createElement('div');
    searchDropdown.id = 'nav-search-dropdown';
    searchDropdown.className = 'search-dropdown hidden';
    searchDropdown.innerHTML = `
        <div class="search-input-wrapper">
            <span class="search-icon">🔍</span>
            <input type="text" id="global-search-input" placeholder="Search toys..." autocomplete="off">
            <button class="close-search-small">&times;</button>
        </div>
      `;
    target.querySelector('.navbar').appendChild(searchDropdown);

    // Search Logic
    const input = searchDropdown.querySelector('input');
    const close = searchDropdown.querySelector('.close-search-small');
    const dropdownEl = searchDropdown;

    close.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdownEl.classList.add('hidden');
      input.value = '';
    });

    // Submit on Enter
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && input.value.trim().length > 0) {
        const term = encodeURIComponent(input.value.trim());
        dropdownEl.classList.add('hidden');
        window.location.href = `/pages/catalog.html?search=${term}`;
      }
    });
  }

  // Attach Listeners
  const btn = target.querySelector('#user-menu-btn');
  const dropdown = target.querySelector('#user-dropdown');
  const logout = target.querySelector('#logout-btn');
  const searchBtn = target.querySelector('.icon-btn:first-child');
  const searchDropdown = target.querySelector('#nav-search-dropdown');

  // Inject cart badge styles once
  if (!document.getElementById('nav-cart-badge-style')) {
    const style = document.createElement('style');
    style.id = 'nav-cart-badge-style';
    style.innerHTML = `
      .cart-btn { position: relative; }
      .cart-count { position: absolute; top: -6px; right: -8px; background: #ff6b6b; color: white; border-radius: 999px; padding: 0 6px; font-size: 10px; line-height: 18px; min-width: 18px; text-align: center; }
      .cart-count.hidden { display: none; }
    `;
    document.head.appendChild(style);
  }

  // Toggle Search
  if (searchBtn && searchDropdown) {
    searchBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Close user menu if open
      if (dropdown) dropdown.classList.add('hidden');

      searchDropdown.classList.toggle('hidden');
      if (!searchDropdown.classList.contains('hidden')) {
        const input = searchDropdown.querySelector('input');
        setTimeout(() => input.focus(), 50);
      }
    });

    // Close search when clicking outside
    document.addEventListener('click', (e) => {
      if (!searchDropdown.classList.contains('hidden') &&
        !searchDropdown.contains(e.target) &&
        e.target !== searchBtn) {
        searchDropdown.classList.add('hidden');
      }
    });
  }

  if (btn) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (user) {
        // Toggle Menu
        if (dropdown) dropdown.classList.toggle('hidden');
      } else {
        // Redirect to Auth
        window.location.href = '/pages/auth.html';
      }
    });
  }

  // Dropdown Close Logic
  if (user && dropdown) {
    document.addEventListener('click', (e) => {
      if (!dropdown.contains(e.target) && e.target !== btn) {
        dropdown.classList.add('hidden');
      }
    });

    if (logout) {
      logout.addEventListener('click', () => {
        api.logout();
        window.location.reload(); // Wait for reload
      });
    }
  }

  // Cart count updater
  const updateCartCount = async () => {
    const badge = target.querySelector('#cart-count');
    if (!badge) return;
    if (!localStorage.getItem('access_token')) {
      badge.classList.add('hidden');
      badge.innerText = '0';
      return;
    }
    try {
      const cart = await api.getCart();
      const count = (cart.items || []).reduce((sum, item) => sum + (item.quantity || 0), 0);
      if (count > 0) {
        badge.innerText = count;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    } catch (err) {
      badge.classList.add('hidden');
    }
  };

  updateCartCount();
  window.addEventListener('cart-updated', updateCartCount);
}



