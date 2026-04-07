/**
 * Sahakar Mandal - Landing Page
 */

document.addEventListener('DOMContentLoaded', async () => {
    // If user is already logged in, redirect to dashboard
    if (AuthManager.isAuthenticated()) {
        window.location.href = 'dashboard.html';
        return;
    }

    // Load gallery preview
    await loadGalleryPreview();

    // Setup language toggle
    setupLanguageToggle();

    // Smooth scroll for anchor links
    setupSmoothScroll();
});

/**
 * Load gallery preview on landing page
 */
async function loadGalleryPreview() {
    try {
        const gallery = await APIClient.get(API_ENDPOINTS.GALLERY.LIST);
        const galleryContainer = document.getElementById('gallery-preview');

        if (!gallery.gallery || gallery.gallery.length === 0) {
            galleryContainer.innerHTML = `
                <div class="col-12 text-center text-muted">
                    <p>कोई छवि अभी उपलब्ध नहीं / No images available yet</p>
                </div>
            `;
            return;
        }

        // Show only first 6 images
        const items = gallery.gallery.slice(0, 6);
        galleryContainer.innerHTML = items.map(item => `
            <div class="col-md-4 mb-4">
                <a href="${item.url}" class="gallery-item d-block overflow-hidden rounded shadow-sm" style="aspect-ratio: 1/1;">
                    <img src="${item.url}" alt="${item.title}" class="w-100 h-100 object-fit-cover" style="transition: transform 0.3s;">
                </a>
            </div>
        `).join('');

        // Add hover effect
        document.querySelectorAll('.gallery-item img').forEach(img => {
            img.addEventListener('mouseover', () => {
                img.style.transform = 'scale(1.1)';
            });
            img.addEventListener('mouseout', () => {
                img.style.transform = 'scale(1)';
            });
        });
    } catch (error) {
        console.error('Error loading gallery preview:', error);
    }
}

/**
 * Setup language toggle
 */
function setupLanguageToggle() {
    const langToggle = document.getElementById('lang-toggle');
    if (langToggle) {
        langToggle.addEventListener('click', () => {
            const currentLang = localStorage.getItem('language') || 'en';
            const newLang = currentLang === 'en' ? 'hi' : 'en';
            localStorage.setItem('language', newLang);
            
            // Reload page or update language
            window.location.reload();
        });
    }
}

/**
 * Setup smooth scroll for anchor links
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}
