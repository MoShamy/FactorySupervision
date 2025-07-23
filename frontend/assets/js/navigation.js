/**
 * Factory Supervision Dashboard - Navigation System
 * Handles page routing and dynamic content loading
 */

class NavigationSystem {
  constructor() {
    this.currentPage = 'dashboard';
    this.pages = {
      dashboard: { title: 'Dashboard', icon: '🏭', file: 'dashboard.html' },
      cameras: { title: 'Camera Feeds', icon: '📹', file: 'cameras.html' },
      alerts: { title: 'Alerts', icon: '🚨', file: 'alerts.html' },
      analytics: { title: 'Analytics', icon: '📊', file: 'analytics.html' },
      files: { title: 'File Manager', icon: '📁', file: 'files.html' },
      settings: { title: 'Settings', icon: '⚙️', file: 'settings.html' }
    };
    
    this.contentArea = document.getElementById('mainContent');
    this.init();
  }

  /**
   * Initialize navigation system
   */
  init() {
    this.setupEventListeners();
    this.updateActiveNavItem();
    this.loadPage(this.currentPage);
  }

  /**
   * Setup navigation event listeners
   */
  setupEventListeners() {
    // Navigation item clicks
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.getAttribute('data-page');
        if (page && page !== this.currentPage) {
          this.navigateTo(page);
        }
      });
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', (e) => {
      if (e.state && e.state.page) {
        this.loadPage(e.state.page, false);
      }
    });
  }

  /**
   * Navigate to a specific page
   */
  navigateTo(page) {
    if (!this.pages[page]) {
      console.error(`Page "${page}" not found`);
      return;
    }

    // Add to browser history
    const state = { page: page };
    const url = `#${page}`;
    history.pushState(state, '', url);

    this.loadPage(page);
  }

  /**
   * Load page content
   */
  async loadPage(page, updateHistory = true) {
    if (!this.pages[page]) {
      console.error(`Page "${page}" not found`);
      return;
    }

    try {
      // Show loading state
      this.showLoadingState();

      // Update current page
      this.currentPage = page;
      this.updateActiveNavItem();

      // Load page content from separate HTML file
      const pageData = this.pages[page];
      const response = await fetch(`pages/${pageData.file}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load page: ${response.status}`);
      }
      
      const content = await response.text();
      
      // Animate content change
      await this.animateContentChange(content);

      // Update document title
      document.title = `Factory Supervision - ${pageData.title}`;

      console.log(`📄 Loaded page: ${pageData.title}`);

    } catch (error) {
      console.error('Error loading page:', error);
      this.showErrorState(error.message);
    }
  }

  /**
   * Show loading state
   */
  showLoadingState() {
    this.contentArea.innerHTML = `
      <div class="loading-container" style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
        color: #6b7280;
      ">
        <div class="loading-spinner" style="
          width: 40px;
          height: 40px;
          border: 3px solid #e5e7eb;
          border-top: 3px solid #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 16px;
        "></div>
        <p style="font-size: 16px; font-weight: 500;">Loading...</p>
      </div>
    `;
  }

  /**
   * Show error state
   */
  showErrorState(message) {
    this.contentArea.innerHTML = `
      <div class="error-container" style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
        color: #ef4444;
      ">
        <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
        <h3 style="margin-bottom: 8px;">Error Loading Page</h3>
        <p style="color: #6b7280; margin-bottom: 16px;">${message}</p>
        <button onclick="navigation.loadPage('dashboard')" style="
          background: #667eea;
          color: white;
          border: none;
          border-radius: 8px;
          padding: 8px 16px;
          cursor: pointer;
        ">Return to Dashboard</button>
      </div>
    `;
  }

  /**
   * Animate content change
   */
  async animateContentChange(newContent) {
    return new Promise((resolve) => {
      // Fade out current content
      this.contentArea.style.opacity = '0';
      this.contentArea.style.transform = 'translateY(20px)';

      setTimeout(() => {
        // Update content
        this.contentArea.innerHTML = newContent;

        // Fade in new content
        this.contentArea.style.opacity = '1';
        this.contentArea.style.transform = 'translateY(0)';

        resolve();
      }, 150);
    });
  }

  /**
   * Update active navigation item
   */
  updateActiveNavItem() {
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
    });

    // Add active class to current page nav item
    const activeNavItem = document.querySelector(`[data-page="${this.currentPage}"]`);
    if (activeNavItem) {
      activeNavItem.classList.add('active');
    }
  }

  /**
   * Utility methods for page interactions
   */
  refreshDashboard() {
    console.log('🔄 Refreshing dashboard...');
    this.loadPage('dashboard');
  }

  refreshCameras() {
    console.log('🔄 Refreshing camera feeds...');
    // Add camera refresh logic
  }

  refreshAlerts() {
    console.log('🔄 Refreshing alerts...');
    // Add alerts refresh logic
  }

  refreshAnalytics() {
    console.log('🔄 Refreshing analytics...');
    // Add analytics refresh logic
  }

  refreshFiles() {
    console.log('🔄 Refreshing file list...');
    // Add file refresh logic
  }

  saveSettings() {
    console.log('💾 Saving settings...');
    // Add settings save logic
  }
}

// Global navigation instance
let navigation = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  navigation = new NavigationSystem();
  
  // Make available globally
  window.navigation = navigation;
  
  // Handle initial page load from URL hash
  const hash = window.location.hash.replace('#', '');
  if (hash && navigation.pages[hash]) {
    navigation.loadPage(hash);
  }
});
