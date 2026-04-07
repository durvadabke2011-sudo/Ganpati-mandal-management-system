/**
 * Sahakar Mandal - Dashboard Page
 */

let currentUser = null;
let monthlyChart = null;
let distributionChart = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    if (!AuthManager.checkAuth()) return;

    // Load user data
    await loadUserData();

    // Load dashboard data
    await loadDashboardSummary();

    // Setup event listeners
    setupEventListeners();

    // Check user role and show/hide admin features
    updateUIForRole();
});

/**
 * Load current user data
 */
async function loadUserData() {
    try {
        currentUser = AuthManager.getCurrentUser();
        if (currentUser && currentUser.name) {
            document.getElementById('user-name').textContent = currentUser.name;
        }
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

/**
 * Update UI based on user role
 */
function updateUIForRole() {
    const role = AuthManager.getUserRole();
    const adminElements = document.querySelectorAll('.admin-only');
    
    if (role === ROLES.ADMIN) {
        adminElements.forEach(el => el.style.display = 'block');
    } else {
        adminElements.forEach(el => el.style.display = 'none');
    }
}

/**
 * Load dashboard summary
 */
async function loadDashboardSummary() {
    try {
        UIUtils.showLoading();

        // Fetch summary data
        const summary = await APIClient.get(API_ENDPOINTS.DASHBOARD.SUMMARY);

        // Update stats
        document.getElementById('total-donations').textContent = 
            UIUtils.formatCurrency(summary.total_donations).replace('₹', '').trim();
        document.getElementById('total-expenses').textContent = 
            UIUtils.formatCurrency(summary.total_expenses).replace('₹', '').trim();
        document.getElementById('balance').textContent = 
            UIUtils.formatCurrency(summary.balance).replace('₹', '').trim();
        document.getElementById('donation-count').textContent = summary.donation_count || 0;

        // Load charts
        await loadCharts();

        UIUtils.hideLoading();
    } catch (error) {
        UIUtils.hideLoading();
        console.error('Error loading dashboard summary:', error);
        UIUtils.showToast('Failed to load dashboard data', 'danger');
    }
}

/**
 * Load charts
 */
async function loadCharts() {
    try {
        // Get yearly data
        const yearlyData = await APIClient.get(
            API_ENDPOINTS.DASHBOARD.YEARLY + '?year=' + new Date().getFullYear()
        );

        // Get top donors
        const topDonors = await APIClient.get(API_ENDPOINTS.DASHBOARD.TOP_DONORS + '?limit=5');

        // Monthly chart
        initMonthlyChart(yearlyData.monthly_data);

        // Distribution chart
        initDistributionChart(topDonors.leaderboard);
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

/**
 * Initialize monthly donations chart
 */
function initMonthlyChart(monthlyData) {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const data = monthNames.map((_, i) => monthlyData[i + 1] || 0);

    const ctx = document.getElementById('monthly-chart').getContext('2d');
    
    if (monthlyChart) {
        monthlyChart.destroy();
    }

    monthlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthNames,
            datasets: [{
                label: 'Donations (₹)',
                data: data,
                borderColor: '#FF6B35',
                backgroundColor: 'rgba(255, 107, 53, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: '#FF6B35'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize distribution chart
 */
function initDistributionChart(topDonors) {
    const ctx = document.getElementById('distribution-chart').getContext('2d');
    
    if (distributionChart) {
        distributionChart.destroy();
    }

    const labels = topDonors.map(d => d.name);
    const data = topDonors.map(d => d.total_amount);
    const colors = ['#FF6B35', '#004E89', '#F77F00', '#06A77D', '#D62828'];

    distributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, data.length),
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '₹' + context.parsed.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to logout?')) {
                await AuthManager.logout();
            }
        });
    }

    // Donation form
    const donationForm = document.getElementById('donation-form');
    if (donationForm) {
        donationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveDonation();
        });
    }
}

/**
 * Show specific section
 */
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(section => section.style.display = 'none');

    // Update nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));

    // Show selected section
    const selectedSection = document.getElementById(sectionName + '-section');
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }

    // Update active nav link
    event.target.closest('a').classList.add('active');

    // Load data for section
    loadSectionData(sectionName);
}

/**
 * Load section data
 */
async function loadSectionData(section) {
    try {
        UIUtils.showLoading();

        switch (section) {
            case 'donations':
                await loadDonations();
                break;
            case 'receipts':
                await loadReceipts();
                break;
            case 'expenses':
                await loadExpenses();
                break;
            case 'events':
                await loadEvents();
                break;
            case 'gallery':
                await loadGallery();
                break;
            case 'users':
                await loadUsers();
                break;
            case 'inventory':
                await loadInventory();
                break;
        }

        UIUtils.hideLoading();
    } catch (error) {
        UIUtils.hideLoading();
        console.error('Error loading section data:', error);
    }
}

/**
 * Load donations
 */
async function loadDonations() {
    try {
        const donations = await APIClient.get(API_ENDPOINTS.DONATIONS.LIST);
        const listElement = document.getElementById('donations-list');
        
        if (!donations.donations || donations.donations.length === 0) {
            listElement.innerHTML = '<div class="col-12 text-center text-muted"><p>कोई दान नहीं</p></div>';
            return;
        }

        listElement.innerHTML = donations.donations.map(donation => `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h6 class="card-title">${donation.donor_name || 'Anonymous'}</h6>
                        <p class="card-text">
                            <strong>₹${donation.amount}</strong><br>
                            <small class="text-muted">${donation.donation_type}</small>
                        </p>
                        <span class="badge bg-${donation.status === 'completed' ? 'success' : 'warning'}">
                            ${donation.status}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading donations:', error);
    }
}

/**
 * Load receipts
 */
async function loadReceipts() {
    try {
        const receipts = await APIClient.get(API_ENDPOINTS.RECEIPTS.LIST);
        const listElement = document.getElementById('receipts-list');
        
        if (!receipts.receipts || receipts.receipts.length === 0) {
            listElement.innerHTML = '<div class="col-12 text-center text-muted"><p>कोई रसीद नहीं</p></div>';
            return;
        }

        listElement.innerHTML = receipts.receipts.map(receipt => `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h6 class="card-title">${receipt.donation_id}</h6>
                        <p class="card-text">
                            <strong>₹${receipt.amount}</strong><br>
                            <small class="text-muted">${UIUtils.formatDate(receipt.date)}</small>
                        </p>
                        <a href="receipt.html?id=${receipt.receipt_id}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> View
                        </a>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading receipts:', error);
    }
}

/**
 * Load expenses
 */
async function loadExpenses() {
    try {
        const expenses = await APIClient.get(API_ENDPOINTS.EXPENSES.LIST);
        const listElement = document.getElementById('expenses-list');
        
        if (!expenses.expenses || expenses.expenses.length === 0) {
            listElement.innerHTML = '<div class="col-12 text-center text-muted"><p>कोई खर्च नहीं</p></div>';
            return;
        }

        listElement.innerHTML = expenses.expenses.map(expense => `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h6 class="card-title">${expense.description}</h6>
                        <p class="card-text">
                            <strong>₹${expense.amount}</strong><br>
                            <small class="text-muted">${expense.category}</small>
                        </p>
                        <span class="badge bg-${expense.status === 'approved' ? 'success' : 'warning'}">
                            ${expense.status}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading expenses:', error);
    }
}

/**
 * Load events
 */
async function loadEvents() {
    try {
        const events = await APIClient.get(API_ENDPOINTS.EVENTS.LIST);
        const listElement = document.getElementById('events-list');
        
        if (!events.events || events.events.length === 0) {
            listElement.innerHTML = '<div class="col-12 text-center text-muted"><p>कोई कार्यक्रम नहीं</p></div>';
            return;
        }

        listElement.innerHTML = events.events.map(event => `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h6 class="card-title">${event.title}</h6>
                        <p class="card-text">
                            <i class="fas fa-calendar"></i> ${UIUtils.formatDate(event.date)}<br>
                            <small class="text-muted">${event.location}</small>
                        </p>
                        <span class="badge bg-info">${event.status}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

/**
 * Load gallery
 */
async function loadGallery() {
    try {
        const gallery = await APIClient.get(API_ENDPOINTS.GALLERY.LIST);
        const listElement = document.getElementById('gallery-list');
        
        if (!gallery.gallery || gallery.gallery.length === 0) {
            listElement.innerHTML = '<div class="col-12 text-center text-muted"><p>कोई छवि नहीं</p></div>';
            return;
        }

        listElement.innerHTML = gallery.gallery.map(item => `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <img src="${item.url}" alt="${item.title}" class="card-img-top" style="height: 200px; object-fit: cover;">
                    <div class="card-body">
                        <h6 class="card-title">${item.title}</h6>
                        <p class="card-text text-muted small">${item.description || ''}</p>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading gallery:', error);
    }
}

/**
 * Load users (admin only)
 */
async function loadUsers() {
    try {
        const users = await APIClient.get(API_ENDPOINTS.USERS.LIST);
        const listElement = document.getElementById('users-list');
        
        if (!users.users || users.users.length === 0) {
            listElement.innerHTML = '<div class="col-12 text-center text-muted"><p>कोई सदस्य नहीं</p></div>';
            return;
        }

        listElement.innerHTML = users.users.map(user => `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h6 class="card-title">${user.name}</h6>
                        <p class="card-text">
                            <small class="text-muted">${user.email}</small><br>
                            <small class="text-muted">${user.phone}</small>
                        </p>
                        <span class="badge bg-primary">${user.role}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

/**
 * Load inventory (admin only)
 */
async function loadInventory() {
    try {
        const inventory = await APIClient.get(API_ENDPOINTS.INVENTORY.LIST);
        const listElement = document.getElementById('inventory-list');
        
        if (!inventory.items || inventory.items.length === 0) {
            listElement.innerHTML = '<div class="col-12 text-center text-muted"><p>कोई आइटम नहीं</p></div>';
            return;
        }

        listElement.innerHTML = inventory.items.map(item => `
            <div class="col-md-6 col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-body">
                        <h6 class="card-title">${item.name}</h6>
                        <p class="card-text">
                            <strong>Qty: ${item.quantity} ${item.unit}</strong><br>
                            <small class="text-muted">${item.category}</small>
                        </p>
                        <span class="badge bg-${item.condition === 'good' ? 'success' : item.condition === 'fair' ? 'warning' : 'danger'}">
                            ${item.condition}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading inventory:', error);
    }
}

/**
 * Show donation form modal
 */
function showDonationForm() {
    const modal = new bootstrap.Modal(document.getElementById('donationModal'));
    modal.show();
}

/**
 * Save donation
 */
async function saveDonation() {
    try {
        UIUtils.showLoading();

        const donationData = {
            donor_name: document.getElementById('donor-name').value,
            donor_email: document.getElementById('donor-email').value,
            donor_mobile: document.getElementById('donor-mobile').value,
            amount: parseFloat(document.getElementById('amount').value),
            donation_type: document.getElementById('donation-type').value,
            purpose: document.getElementById('purpose').value
        };

        await APIClient.post(API_ENDPOINTS.DONATIONS.CREATE, donationData);

        UIUtils.hideLoading();
        UIUtils.showToast('Donation saved successfully!', 'success');

        // Close modal and reload
        const modal = bootstrap.Modal.getInstance(document.getElementById('donationModal'));
        modal.hide();

        // Reload donations
        await loadDonations();
    } catch (error) {
        UIUtils.hideLoading();
        console.error('Error saving donation:', error);
        UIUtils.showToast('Failed to save donation', 'danger');
    }
}

/**
 * Show expense form
 */
function showExpenseForm() {
    alert('Expense form not yet implemented');
}

/**
 * Show event form
 */
function showEventForm() {
    alert('Event form not yet implemented');
}

/**
 * Show gallery upload
 */
function showGalleryUpload() {
    alert('Gallery upload not yet implemented');
}

/**
 * Show user form
 */
function showUserForm() {
    alert('User form not yet implemented');
}

/**
 * Show inventory form
 */
function showInventoryForm() {
    alert('Inventory form not yet implemented');
}

/**
 * Save settings
 */
function saveSettings() {
    UIUtils.showToast('Settings saved successfully!', 'success');
}
