/**
 * Profile Page Script
 * Handles user profile management, updates, and profile picture uploads
 */

import api from './api.js';

// DOM Elements
const profilePictureEl = document.getElementById('profile-picture');
const profilePictureInput = document.getElementById('profile-picture-input');
const deletePictureBtn = document.getElementById('delete-picture-btn');
const profileForm = document.getElementById('profile-form');
const changePasswordToggle = document.getElementById('change-password-toggle');
const passwordFields = document.getElementById('password-fields');
const saveBtn = document.getElementById('save-btn');
const successMessage = document.getElementById('success-message');
const errorMessage = document.getElementById('error-message');

// Form inputs
const usernameInput = document.getElementById('username');
const roleInput = document.getElementById('role');
const fullNameInput = document.getElementById('full-name');
const emailInput = document.getElementById('email');
const currentPasswordInput = document.getElementById('current-password');
const newPasswordInput = document.getElementById('new-password');
const confirmPasswordInput = document.getElementById('confirm-password');
const accountInfo = document.getElementById('account-info');

// Current user data
let currentUser = null;

/**
 * Initialize profile page
 */
async function init() {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/pages/auth.html';
        return;
    }

    // Load user profile
    await loadProfile();

    // Attach event listeners
    attachEventListeners();
}

/**
 * Load user profile data
 */
async function loadProfile() {
    try {
        showLoading();

        // Get profile from API
        const profile = await api.getProfile();
        currentUser = profile;

        // Update UI with profile data
        displayProfile(profile);

    } catch (error) {
        console.error('Failed to load profile:', error);
        showError('Failed to load profile. Please refresh the page.');
    }
}

/**
 * Display profile data in the form
 */
function displayProfile(profile) {
    // Basic information
    usernameInput.value = profile.username || '';
    roleInput.value = profile.role === 'admin' ? '👑 Admin' : '👤 Customer';
    fullNameInput.value = profile.full_name || '';
    emailInput.value = profile.email || '';

    // Profile picture
    if (profile.profile_picture) {
        profilePictureEl.style.backgroundImage = `url('http://localhost:8000${profile.profile_picture}')`;
        profilePictureEl.textContent = '';
        deletePictureBtn.style.display = 'inline-block';
    } else {
        // Show initial letter
        const initial = profile.full_name
            ? profile.full_name.charAt(0).toUpperCase()
            : profile.username.charAt(0).toUpperCase();
        profilePictureEl.textContent = initial;
        profilePictureEl.style.backgroundImage = 'none';
        deletePictureBtn.style.display = 'none';
    }

    // Account info
    const memberSince = new Date(profile.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    accountInfo.textContent = `Member since: ${memberSince}`;

    hideLoading();
}

/**
 * Attach event listeners
 */
function attachEventListeners() {
    // Profile picture upload
    profilePictureInput.addEventListener('change', handleProfilePictureUpload);

    // Delete profile picture
    deletePictureBtn.addEventListener('click', handleDeleteProfilePicture);

    // Toggle password fields
    changePasswordToggle.addEventListener('click', () => {
        passwordFields.classList.toggle('active');

        // Clear password fields when toggling off
        if (!passwordFields.classList.contains('active')) {
            currentPasswordInput.value = '';
            newPasswordInput.value = '';
            confirmPasswordInput.value = '';
        }
    });

    // Form submission
    profileForm.addEventListener('submit', handleFormSubmit);
}

/**
 * Handle profile picture upload
 */
async function handleProfilePictureUpload(event) {
    const file = event.target.files[0];

    if (!file) {
        return;
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showError('Invalid file type. Please upload an image (JPG, PNG, GIF, or WebP).');
        profilePictureInput.value = '';
        return;
    }

    // Validate file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
        showError('File size must be less than 5MB.');
        profilePictureInput.value = '';
        return;
    }

    try {
        showLoading();

        // Upload to backend
        const result = await api.uploadProfilePicture(file);

        // Update UI immediately
        profilePictureEl.style.backgroundImage = `url('http://localhost:8000${result.profile_picture}')`;
        profilePictureEl.textContent = '';
        deletePictureBtn.style.display = 'inline-block';

        // Update current user
        currentUser.profile_picture = result.profile_picture;

        // Reload navbar to update avatar
        window.location.reload();

        showSuccess('Profile picture updated successfully!');

    } catch (error) {
        console.error('Failed to upload profile picture:', error);
        showError(error.message || 'Failed to upload profile picture.');
    } finally {
        hideLoading();
        profilePictureInput.value = '';
    }
}

/**
 * Handle delete profile picture
 */
async function handleDeleteProfilePicture() {
    if (!confirm('Are you sure you want to delete your profile picture?')) {
        return;
    }

    try {
        showLoading();

        await api.deleteProfilePicture();

        // Update UI
        const initial = currentUser.full_name
            ? currentUser.full_name.charAt(0).toUpperCase()
            : currentUser.username.charAt(0).toUpperCase();
        profilePictureEl.style.backgroundImage = 'none';
        profilePictureEl.textContent = initial;
        deletePictureBtn.style.display = 'none';

        // Update current user
        currentUser.profile_picture = null;

        // Reload navbar to update avatar
        window.location.reload();

        showSuccess('Profile picture deleted successfully!');

    } catch (error) {
        console.error('Failed to delete profile picture:', error);
        showError(error.message || 'Failed to delete profile picture.');
    } finally {
        hideLoading();
    }
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();

    // Clear previous messages
    hideSuccess();
    hideError();

    // Validate form
    const validation = validateForm();
    if (!validation.valid) {
        showError(validation.message);
        return;
    }

    // Prepare update data
    const updateData = {
        full_name: fullNameInput.value.trim(),
        email: emailInput.value.trim()
    };

    // Add password if changing
    if (passwordFields.classList.contains('active')) {
        const currentPassword = currentPasswordInput.value;
        const newPassword = newPasswordInput.value;

        if (newPassword) {
            updateData.current_password = currentPassword;
            updateData.new_password = newPassword;
        }
    }

    try {
        showLoading();

        // Update profile
        const updatedProfile = await api.updateProfile(updateData);

        // Update UI
        displayProfile(updatedProfile);

        // Reset password fields
        passwordFields.classList.remove('active');
        currentPasswordInput.value = '';
        newPasswordInput.value = '';
        confirmPasswordInput.value = '';

        showSuccess('Profile updated successfully!');

        // Reload page after 1 second to update navbar
        setTimeout(() => {
            window.location.reload();
        }, 1000);

    } catch (error) {
        console.error('Failed to update profile:', error);
        showError(error.message || 'Failed to update profile.');
    } finally {
        hideLoading();
    }
}

/**
 * Validate form data
 */
function validateForm() {
    // Validate full name
    const fullName = fullNameInput.value.trim();
    if (!fullName) {
        return { valid: false, message: 'Full name is required.' };
    }

    // Validate email
    const email = emailInput.value.trim();
    if (!email) {
        return { valid: false, message: 'Email is required.' };
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return { valid: false, message: 'Please enter a valid email address.' };
    }

    // Validate password if changing
    if (passwordFields.classList.contains('active')) {
        const currentPassword = currentPasswordInput.value;
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (newPassword) {
            // Current password required
            if (!currentPassword) {
                return { valid: false, message: 'Current password is required to change password.' };
            }

            // Minimum length
            if (newPassword.length < 6) {
                return { valid: false, message: 'New password must be at least 6 characters long.' };
            }

            // Passwords match
            if (newPassword !== confirmPassword) {
                return { valid: false, message: 'New passwords do not match.' };
            }
        }
    }

    return { valid: true };
}

/**
 * Show success message
 */
function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.classList.add('show');

    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideSuccess();
    }, 5000);
}

/**
 * Hide success message
 */
function hideSuccess() {
    successMessage.classList.remove('show');
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');

    // Auto-hide after 7 seconds
    setTimeout(() => {
        hideError();
    }, 7000);
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.classList.remove('show');
}

/**
 * Show loading state
 */
function showLoading() {
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
}

/**
 * Hide loading state
 */
function hideLoading() {
    saveBtn.disabled = false;
    saveBtn.textContent = 'Save Changes';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
