/**
 * Simple Page Loader for Single Page Application
 * Fetches pages and loads them into content container without changing content
 */

// Configuration
const pageMap = {
    'dashboard': 'Dashboard.html',
    'predict': 'predict demand.html',
    'reports': 'reports.html',
    'data': 'manage-data.html',
    'profile': 'profile.html'
};

let currentPage = 'dashboard';

/**
 * Manage dashboard-specific elements visibility
 */
function manageDashboardElements(pageKey) {
    // Find the graphs by looking for specific text content
    const cards = document.querySelectorAll('.card');
    let demandCard = null;
    let wastageCard = null;
    
    cards.forEach(card => {
        const text = card.textContent;
        if (text.includes('Past 7 Days Food Demand')) {
            demandCard = card;
        }
        if (text.includes('Wastage Trend')) {
            wastageCard = card;
        }
    });
    
    // Show graphs only for dashboard, hide for other pages
    if (pageKey === 'dashboard') {
        if (demandCard) demandCard.style.display = 'block';
        if (wastageCard) wastageCard.style.display = 'block';
    } else {
        if (demandCard) demandCard.style.display = 'none';
        if (wastageCard) wastageCard.style.display = 'none';
    }
}

/**
 * Load page content from HTML file
 * Fetches the entire page and extracts the .content div
 */
function loadPage(pageKey) {
    console.log('Loading page:', pageKey);
    
    // Check authentication
    const isAuthenticated = localStorage.getItem('isAuthenticated');
    if (!isAuthenticated || isAuthenticated !== 'true') {
        window.location.href = 'login.html';
        return;
    }

    const fileName = pageMap[pageKey];
    if (!fileName) {
        console.error('Page not found:', pageKey);
        return;
    }

    const contentContainer = document.querySelector('.content');
    if (!contentContainer) {
        console.error('Content container not found');
        return;
    }

    // Show loading state
    contentContainer.style.opacity = '0.6';
    contentContainer.style.pointerEvents = 'none';

    // Fetch the page HTML
    fetch(fileName)
        .then(response => response.text())
        .then(html => {
            // Parse HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Extract styles
            const styleElements = doc.querySelectorAll('style');
            const styles = [];
            styleElements.forEach(style => {
                styles.push(style.innerHTML);
            });
            
            // Extract .content div
            const contentDiv = doc.querySelector('.content');
            let contentHTML = '';
            
            if (contentDiv) {
                contentHTML = contentDiv.innerHTML;
            }
            
            if (!contentHTML) {
                throw new Error('No .content div found in page');
            }
            
            // Fade out
            contentContainer.style.opacity = '0';
            
            setTimeout(() => {
                // Remove old page styles
                const oldStyles = document.querySelectorAll('style[data-page-style]');
                oldStyles.forEach(style => style.remove());
                
                // Add new styles to document head
                styles.forEach(styleContent => {
                    const styleTag = document.createElement('style');
                    styleTag.setAttribute('data-page-style', pageKey);
                    styleTag.innerHTML = styleContent;
                    document.head.appendChild(styleTag);
                });
                
                // Insert content
                contentContainer.innerHTML = contentHTML;
                contentContainer.style.opacity = '1';
                contentContainer.style.pointerEvents = 'auto';
                
                // Manage dashboard-specific elements visibility
                manageDashboardElements(pageKey);
                
                // Re-attach menu events since DOM changed
                setupMenuEvents();
                
                // Update current page
                currentPage = pageKey;
                updateActiveMenu(pageKey);
            }, 200);
            
            // Update browser history
            window.history.pushState({ page: pageKey }, '', `#${pageKey}`);
        })
        .catch(error => {
            console.error('Error loading page:', error);
            contentContainer.style.opacity = '1';
            contentContainer.style.pointerEvents = 'auto';
            contentContainer.innerHTML = `<div style="padding:40px; text-align:center; color:#ef4444;"><h3>Error Loading Page</h3><p>${error.message}</p></div>`;
        });
}

/**
 * Update active menu item
 */
function updateActiveMenu(pageKey) {
    const menuItems = document.querySelectorAll('nav a');
    menuItems.forEach(item => {
        item.classList.remove('active');
    });

    const activeItem = Array.from(menuItems).find(item => {
        const text = item.textContent.toLowerCase();
        if (pageKey === 'dashboard') return text.includes('dashboard');
        if (pageKey === 'predict') return text.includes('predict');
        if (pageKey === 'reports') return text.includes('report');
        if (pageKey === 'data') return text.includes('data');
        if (pageKey === 'profile') return text.includes('profile');
        return false;
    });

    if (activeItem) {
        activeItem.classList.add('active');
    }
}

/**
 * Setup menu click events
 */
function setupMenuEvents() {
    const menuItems = document.querySelectorAll('nav a');
    
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            const text = item.textContent.toLowerCase().trim();
            let pageKey = null;

            if (text.includes('dashboard')) pageKey = 'dashboard';
            else if (text.includes('predict')) pageKey = 'predict';
            else if (text.includes('report')) pageKey = 'reports';
            else if (text.includes('data')) pageKey = 'data';
            else if (text.includes('profile')) pageKey = 'profile';

            if (pageKey) {
                loadPage(pageKey);
            }
        });
    });
}

/**
 * Setup logout button
 */
function setupLogout() {
    // Look for Sign Out button in profile section
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase().includes('sign out') || 
            btn.textContent.toLowerCase().includes('logout')) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.setItem('isAuthenticated', 'false');
                window.location.href = 'login.html';
            });
        }
    });
}

/**
 * Handle back/forward buttons
 */
function handlePopState() {
    window.addEventListener('popstate', (event) => {
        if (event.state && event.state.page) {
            loadPage(event.state.page);
        }
    });
}

/**
 * Initialize when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing page loader');
    
    // Check authentication
    const isAuthenticated = localStorage.getItem('isAuthenticated');
    if (!isAuthenticated || isAuthenticated !== 'true') {
        window.location.href = 'login.html';
        return;
    }

    // Setup navigation
    setTimeout(() => {
        setupMenuEvents();
        setupLogout();
        handlePopState();
        console.log('Page loader ready');
    }, 100);
});

/**
 * Global navigation function
 */
function navigateTo(pageKey) {
    loadPage(pageKey);
}

/**
 * Get current page
 */
function getCurrentPage() {
    return currentPage;
}
