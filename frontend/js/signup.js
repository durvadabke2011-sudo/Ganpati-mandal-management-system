/**
 * Sahakar Mandal - Signup Page
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (AuthManager.isAuthenticated()) {
        window.location.href = 'dashboard.html';
        return;
    }

    const signupForm = document.getElementById('signup-form');

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            try {
                UIUtils.showLoading();

                const name = document.getElementById('name').value.trim();
                const email = document.getElementById('email').value.trim();
                const phone = document.getElementById('phone').value.trim();
                const area = document.getElementById('area').value.trim();
                const role = document.getElementById('role').value;
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirm-password').value;
                const terms = document.getElementById('terms').checked;

                // Validation
                if (!name || !email || !phone || !password || !confirmPassword) {
                    UIUtils.showToast('Please fill in all required fields', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                if (!Validator.isEmail(email)) {
                    UIUtils.showToast('Please enter a valid email', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                if (!Validator.isPhoneNumber(phone)) {
                    UIUtils.showToast('Phone number must be 10 digits', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                if (!Validator.isStrongPassword(password)) {
                    UIUtils.showToast('Password must be at least 8 characters with uppercase letter and number', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                if (password !== confirmPassword) {
                    UIUtils.showToast('Passwords do not match', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                if (!terms) {
                    UIUtils.showToast('Please accept terms and conditions', 'warning');
                    UIUtils.hideLoading();
                    return;
                }

                // Attempt signup
                const response = await AuthManager.signup({
                    name,
                    email,
                    phone,
                    area,
                    role: role || ROLES.VOLUNTEER,
                    password
                });

                UIUtils.hideLoading();
                UIUtils.showToast('Account created successfully!', 'success');

                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);

            } catch (error) {
                UIUtils.hideLoading();
                console.error('Signup error:', error);
                
                let errorMessage = 'Signup failed. Please try again.';
                if (error.message) {
                    errorMessage = error.message;
                } else if (error.status === 400) {
                    errorMessage = error.data?.message || 'Invalid input. Please check your details.';
                }
                
                UIUtils.showToast(errorMessage, 'danger');
            }
        });
    }

    // Real-time password validation
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', (e) => {
            const password = e.target.value;
            let feedback = [];

            if (password.length < 8) {
                feedback.push('At least 8 characters');
            }
            if (!/[A-Z]/.test(password)) {
                feedback.push('One uppercase letter');
            }
            if (!/[0-9]/.test(password)) {
                feedback.push('One number');
            }

            // Show feedback if password is not valid
            if (feedback.length > 0) {
                console.log('Password requirements:', feedback);
            }
        });
    }
});
