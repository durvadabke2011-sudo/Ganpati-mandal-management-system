/**
 * Sahakar Mandal - Configuration
 * Global configuration and API endpoints
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000';
const API_TIMEOUT = 30000; // 30 seconds

// Firebase Configuration
const FIREBASE_CONFIG = {
    apiKey: "AIzaSyDk....", // Replace with your Firebase API key
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "...",
    appId: "1:....:web:...",
    measurementId: "G-..."
};

// Razorpay Configuration
const RAZORPAY_KEY = "rzp_test_..."; // Replace with your Razorpay key

// Application Constants
const APP_NAME = 'Sahakar Mandal';
const APP_VERSION = '1.0.0';

// Roles
const ROLES = {
    ADMIN: 'admin',
    FINANCE: 'finance',
    COLLECTION: 'collection',
    EVENT: 'event',
    VOLUNTEER: 'volunteer'
};

// Token Storage Keys
const TOKEN_KEY = 'sahakar_token';
const USER_KEY = 'sahakar_user';
const ROLE_KEY = 'sahakar_role';

// API Endpoints
const API_ENDPOINTS = {
    // Authentication
    AUTH: {
        SIGNUP: '/api/auth/signup',
        LOGIN: '/api/auth/login',
        LOGOUT: '/api/auth/logout',
        ME: '/api/auth/me'
    },
    
    // Donations
    DONATIONS: {
        LIST: '/api/donations',
        CREATE: '/api/donations',
        GET: (id) => `/api/donations/${id}`,
        UPDATE: (id) => `/api/donations/${id}`,
        DELETE: (id) => `/api/donations/${id}`
    },
    
    // Receipts
    RECEIPTS: {
        LIST: '/api/receipts',
        GET: (id) => `/api/receipts/${id}`,
        GENERATE: (id) => `/api/receipts/${id}/generate`,
        QR: (id) => `/api/receipts/${id}/qrcode`,
        PDF: (id) => `/api/receipts/${id}/pdf`
    },
    
    // Payments
    PAYMENTS: {
        CREATE_ORDER: '/api/payments/razorpay/order',
        VERIFY: '/api/payments/razorpay/verify',
        UPI_QR: '/api/payments/upi/qrcode'
    },
    
    // Expenses
    EXPENSES: {
        LIST: '/api/expenses',
        CREATE: '/api/expenses',
        GET: (id) => `/api/expenses/${id}`,
        UPDATE: (id) => `/api/expenses/${id}`,
        DELETE: (id) => `/api/expenses/${id}`
    },
    
    // Dashboard
    DASHBOARD: {
        SUMMARY: '/api/dashboard/summary',
        YEARLY: '/api/dashboard/donations-yearly',
        TOP_DONORS: '/api/dashboard/top-donors'
    },
    
    // Events
    EVENTS: {
        LIST: '/api/events',
        CREATE: '/api/events',
        GET: (id) => `/api/events/${id}`,
        UPDATE: (id) => `/api/events/${id}`,
        DELETE: (id) => `/api/events/${id}`
    },
    
    // Gallery
    GALLERY: {
        LIST: '/api/gallery',
        UPLOAD: '/api/gallery'
    },
    
    // Users
    USERS: {
        LIST: '/api/users',
        UPDATE_ROLE: (id) => `/api/users/${id}/role`
    },
    
    // Inventory
    INVENTORY: {
        LIST: '/api/inventory',
        CREATE: '/api/inventory',
        GET: (id) => `/api/inventory/${id}`,
        UPDATE: (id) => `/api/inventory/${id}`,
        DELETE: (id) => `/api/inventory/${id}`
    },
    
    // Health
    HEALTH: '/api/health'
};

// Utility Functions
class StorageManager {
    static setToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    }

    static getToken() {
        return localStorage.getItem(TOKEN_KEY);
    }

    static setUser(user) {
        localStorage.setItem(USER_KEY, JSON.stringify(user));
    }

    static getUser() {
        const user = localStorage.getItem(USER_KEY);
        return user ? JSON.parse(user) : null;
    }

    static setRole(role) {
        localStorage.setItem(ROLE_KEY, role);
    }

    static getRole() {
        return localStorage.getItem(ROLE_KEY);
    }

    static clear() {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem(ROLE_KEY);
    }
}

// API Request Helper
class APIClient {
    static async request(method, endpoint, data = null) {
        const token = StorageManager.getToken();
        const headers = {
            'Content-Type': 'application/json',
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const options = {
            method,
            headers,
            timeout: API_TIMEOUT
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            const result = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: result.message || 'An error occurred',
                    data: result
                };
            }

            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    static get(endpoint) {
        return this.request('GET', endpoint);
    }

    static post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }

    static put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }

    static delete(endpoint) {
        return this.request('DELETE', endpoint);
    }

    static async upload(endpoint, formData) {
        const token = StorageManager.getToken();
        const headers = {};

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers,
                body: formData,
                timeout: API_TIMEOUT
            });

            const result = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: result.message || 'Upload failed',
                    data: result
                };
            }

            return result;
        } catch (error) {
            console.error('Upload Error:', error);
            throw error;
        }
    }
}

// UI Utilities
class UIUtils {
    static showLoading(elementId = 'loading-spinner') {
        const element = document.getElementById(elementId);
        if (element) element.style.display = 'flex';
    }

    static hideLoading(elementId = 'loading-spinner') {
        const element = document.getElementById(elementId);
        if (element) element.style.display = 'none';
    }

    static showToast(message, type = 'info', duration = 3000) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show`;
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to body
        document.body.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.remove();
        }, duration);
    }

    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    static formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Validation Utilities
class Validator {
    static isEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    static isPhoneNumber(phone) {
        return /^[0-9]{10}$/.test(phone.replace(/\D/g, ''));
    }

    static isStrongPassword(password) {
        return password.length >= 8 && 
               /[A-Z]/.test(password) && 
               /[0-9]/.test(password);
    }

    static validateForm(formData) {
        const errors = [];

        if (formData.email && !this.isEmail(formData.email)) {
            errors.push('Invalid email address');
        }

        if (formData.phone && !this.isPhoneNumber(formData.phone)) {
            errors.push('Phone number must be 10 digits');
        }

        if (formData.password && !this.isStrongPassword(formData.password)) {
            errors.push('Password must be at least 8 characters with uppercase and numbers');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

// Initialize app
console.log(`${APP_NAME} v${APP_VERSION} - Frontend Initialized`);
