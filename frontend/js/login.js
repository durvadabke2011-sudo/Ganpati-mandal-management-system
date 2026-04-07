/**
 * Sahakar Mandal - Login Page
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (AuthManager.isAuthenticated()) {
        window.location.href = 'dashboard.html';
        return;
    }

    const loginForm = document.getElementById('login-form');
    const togglePasswordBtn = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    const guestLoginBtn = document.getElementById('guest-login');

    // Password visibility toggle
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            togglePasswordBtn.innerHTML = type === 'password' 
                ? '<i class="fas fa-eye"></i>' 
                : '<i class="fas fa-eye-slash"></i>';
        });
    }

    // Login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            try {
                UIUtils.showLoading();

                const email = document.getElementById('email').value.trim();
                const password = document.getElementById('password').value;
                const remember = document.getElementById('remember').checked;

                // Validate inputs
                if (!email || !password) {
                    UIUtils.showToast('Please fill in all fields', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                if (!Validator.isEmail(email)) {
                    UIUtils.showToast('Please enter a valid email', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                // Attempt login
                const response = await AuthManager.login(email, password);

                UIUtils.hideLoading();
                UIUtils.showToast(`Welcome ${response.name}!`, 'success');

                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);

            } catch (error) {
                UIUtils.hideLoading();
                console.error('Login error:', error);
                
                let errorMessage = 'Login failed. Please try again.';
                if (error.message) {
                    errorMessage = error.message;
                } else if (error.status === 401) {
                    errorMessage = 'Invalid email or password';
                } else if (error.status === 429) {
                    errorMessage = 'Too many login attempts. Please try again later.';
                }
                
                UIUtils.showToast(errorMessage, 'danger');
            }
        });
    }

    // Guest login
    if (guestLoginBtn) {
        guestLoginBtn.addEventListener('click', async () => {
            try {
                // Demo login
                await AuthManager.login('volunteer@sahakar.com', 'password123');
                UIUtils.showToast('Logged in as Guest', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } catch (error) {
                UIUtils.showToast('Guest login failed', 'danger');
            }
        });
    }

    // Auto-fill demo credentials if development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Only in development
        // document.getElementById('email').value = 'admin@sahakar.com';
        // document.getElementById('password').value = 'password123';
    }
});
