/**
 * Sahakar Mandal - Authentication Module
 * Handles user authentication and authorization
 */

class AuthManager {
    /**
     * Check if user is authenticated
     */
    static isAuthenticated() {
        return !!StorageManager.getToken();
    }

    /**
     * Get current user
     */
    static getCurrentUser() {
        return StorageManager.getUser();
    }

    /**
     * Get current user role
     */
    static getUserRole() {
        return StorageManager.getRole();
    }

    /**
     * Check if user has specific role
     */
    static hasRole(role) {
        return StorageManager.getRole() === role;
    }

    /**
     * Check if user has any of the specified roles
     */
    static hasAnyRole(...roles) {
        const userRole = StorageManager.getRole();
        return roles.includes(userRole);
    }

    /**
     * Register new user
     */
    static async signup(userData) {
        try {
            UIUtils.showLoading();
            
            const response = await APIClient.post(API_ENDPOINTS.AUTH.SIGNUP, {
                name: userData.name,
                email: userData.email,
                password: userData.password,
                phone: userData.phone,
                area: userData.area,
                role: userData.role || ROLES.VOLUNTEER
            });

            // Store token and user data
            StorageManager.setToken(response.token);
            StorageManager.setRole(response.role);

            UIUtils.hideLoading();
            return response;
        } catch (error) {
            UIUtils.hideLoading();
            throw error;
        }
    }

    /**
     * Login user
     */
    static async login(email, password) {
        try {
            UIUtils.showLoading();
            
            const response = await APIClient.post(API_ENDPOINTS.AUTH.LOGIN, {
                email,
                password
            });

            // Store token and user data
            StorageManager.setToken(response.token);
            StorageManager.setUser({
                user_id: response.user_id,
                name: response.name,
                email: response.email
            });
            StorageManager.setRole(response.role);

            UIUtils.hideLoading();
            return response;
        } catch (error) {
            UIUtils.hideLoading();
            throw error;
        }
    }

    /**
     * Logout user
     */
    static async logout() {
        try {
            UIUtils.showLoading();
            
            // Call logout endpoint
            await APIClient.post(API_ENDPOINTS.AUTH.LOGOUT, {});

            // Clear local storage
            StorageManager.clear();

            UIUtils.hideLoading();
            
            // Redirect to login
            window.location.href = 'login.html';
            return true;
        } catch (error) {
            // Even if API call fails, clear local storage
            StorageManager.clear();
            UIUtils.hideLoading();
            window.location.href = 'login.html';
            return false;
        }
    }

    /**
     * Get current user details
     */
    static async getCurrentUserDetails() {
        try {
            if (!this.isAuthenticated()) {
                throw new Error('User not authenticated');
            }

            const response = await APIClient.get(API_ENDPOINTS.AUTH.ME);
            
            // Update stored user data
            StorageManager.setUser(response);
            StorageManager.setRole(response.role);

            return response;
        } catch (error) {
            console.error('Error fetching user details:', error);
            throw error;
        }
    }

    /**
     * Refresh user session
     */
    static async refreshSession() {
        try {
            return await this.getCurrentUserDetails();
        } catch (error) {
            // Session expired
            StorageManager.clear();
            window.location.href = 'login.html';
            return null;
        }
    }

    /**
     * Check authentication and redirect if needed
     */
    static checkAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    /**
     * Require specific role
     */
    static requireRole(...roles) {
        const userRole = this.getUserRole();
        if (!roles.includes(userRole)) {
            UIUtils.showToast('You do not have permission to access this page', 'danger');
            window.location.href = 'dashboard.html';
            return false;
        }
        return true;
    }
}

/**
 * Authentication event listeners
 */
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication on protected pages
    const protectedPages = ['dashboard.html'];
    const currentPage = window.location.pathname.split('/').pop();

    if (protectedPages.some(page => currentPage.includes(page))) {
        AuthManager.checkAuth();
    }
});

/**
 * Global logout handler
 */
function globalLogout() {
    AuthManager.logout();
}

// Listen for storage changes (logout in other tabs)
window.addEventListener('storage', (event) => {
    if (event.key === TOKEN_KEY && !event.newValue) {
        // Token was removed in another tab
        window.location.href = 'login.html';
    }
});
