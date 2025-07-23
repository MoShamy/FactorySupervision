/**
 * Factory Supervision Dashboard - Main Application
 * Entry point and initialization for the dashboard application
 */

class FactoryDashboard {
  constructor() {
    this.version = '2.0.0';
    this.initialized = false;
    this.modules = {};
    this.config = {
      apiEndpoint: 'http://localhost:3000',
      refreshInterval: 30000, // 30 seconds
      debugMode: false
    };
    
    this.init();
  }

  /**
   * Initialize the dashboard application
   */
  async init() {
    try {
      console.log(`🏭 Factory Supervision Dashboard v${this.version} starting...`);
      
      // Add loading screen
      this.showLoadingScreen();
      
      // Initialize core systems
      await this.initializeModules();
      
      // Setup global event listeners
      this.setupGlobalEventListeners();
      
      // Start periodic updates
      this.startPeriodicUpdates();
      
      // Remove loading screen
      this.hideLoadingScreen();
      
      this.initialized = true;
      console.log('✅ Dashboard initialized successfully!');
      
      // Show welcome notification
      this.showWelcomeNotification();
      
    } catch (error) {
      console.error('❌ Dashboard initialization failed:', error);
      this.showErrorState(error);
    }
  }

  /**
   * Show loading screen during initialization
   */
  showLoadingScreen() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loadingOverlay';
    loadingOverlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      color: white;
    `;
    
    loadingOverlay.innerHTML = `
      <div class="loading-content">
        <div class="factory-icon" style="font-size: 64px; margin-bottom: 24px; animation: bounce 2s infinite;">🏭</div>
        <h1 style="font-size: 32px; font-weight: 700; margin-bottom: 16px;">Factory Supervision</h1>
        <p style="font-size: 18px; margin-bottom: 32px; opacity: 0.9;">Initializing dashboard systems...</p>
        <div class="loading-spinner" style="
          width: 40px;
          height: 40px;
          border: 3px solid rgba(255,255,255,0.3);
          border-top: 3px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        "></div>
        <p style="font-size: 14px; margin-top: 16px; opacity: 0.7;">v${this.version}</p>
      </div>
    `;
    
    document.body.appendChild(loadingOverlay);
    
    // Add animations
    const style = document.createElement('style');
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Hide loading screen
   */
  hideLoadingScreen() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
      loadingOverlay.style.opacity = '0';
      loadingOverlay.style.transform = 'scale(0.95)';
      setTimeout(() => {
        if (loadingOverlay.parentNode) {
          loadingOverlay.parentNode.removeChild(loadingOverlay);
        }
      }, 500);
    }
  }

  /**
   * Initialize all dashboard modules
   */
  async initializeModules() {
    // Wait for all modules to be available
    try {
      await this.waitForModules();
    } catch (error) {
      console.warn('⚠️ Some modules failed to load, initializing with fallbacks...');
      // Continue with partial initialization
    }
    
    // Initialize modules in order
    console.log('📋 Initializing modules...');
    
    // Navigation system
    if (window.navigation) {
      this.modules.navigation = window.navigation;
      console.log('✅ Navigation system ready');
    } else {
      console.warn('⚠️ Navigation system not found, creating fallback');
      this.createFallbackNavigation();
    }
    
    // Chat system
    if (window.chatSystem) {
      this.modules.chatSystem = window.chatSystem;
      console.log('✅ Chat system ready');
    } else {
      console.warn('⚠️ Chat system not found, creating fallback');
      this.createFallbackChat();
    }
    
    // Status monitoring
    this.modules.statusMonitor = new StatusMonitor();
    console.log('✅ Status monitor ready');
    
    // Performance tracker
    this.modules.performanceTracker = new PerformanceTracker();
    console.log('✅ Performance tracker ready');
  }

  /**
   * Wait for all required modules to load
   */
  async waitForModules() {
    const maxWait = 15000; // 15 seconds
    const startTime = Date.now();
    
    console.log('🔍 Waiting for modules to load...');
    
    while (Date.now() - startTime < maxWait) {
      const navigationReady = window.navigation || window.NavigationSystem;
      const chatReady = window.chatSystem || window.ChatSystem;
      const messageListReady = window.MessageLinkedList;
      
      console.log(`📋 Module status: Navigation=${!!navigationReady}, Chat=${!!chatReady}, MessageList=${!!messageListReady}`);
      
      if (navigationReady && chatReady && messageListReady) {
        console.log('✅ All modules loaded successfully');
        return;
      }
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    console.error('❌ Module loading failed. Available globals:', Object.keys(window).filter(k => k.includes('navigation') || k.includes('chat') || k.includes('Message')));
    throw new Error('Modules failed to load within timeout');
  }

  /**
   * Setup global event listeners
   */
  setupGlobalEventListeners() {
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K for chat focus
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (this.modules.chatSystem) {
          this.modules.chatSystem.input.focus();
        }
      }
      
      // Escape to close modals/panels
      if (e.key === 'Escape') {
        this.closeActiveModals();
      }
    });

    // Window resize handler
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        this.handleWindowResize();
      }, 250);
    });

    // Page visibility change
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.handlePageHidden();
      } else {
        this.handlePageVisible();
      }
    });

    // Network status
    window.addEventListener('online', () => this.handleNetworkOnline());
    window.addEventListener('offline', () => this.handleNetworkOffline());
  }

  /**
   * Start periodic system updates
   */
  startPeriodicUpdates() {
    // Status updates every 30 seconds
    this.statusUpdateInterval = setInterval(() => {
      if (this.modules.statusMonitor) {
        this.modules.statusMonitor.updateStatus();
      }
    }, this.config.refreshInterval);

    // Performance tracking every minute
    this.performanceUpdateInterval = setInterval(() => {
      if (this.modules.performanceTracker) {
        this.modules.performanceTracker.collectMetrics();
      }
    }, 60000);
  }

  /**
   * Handle window resize
   */
  handleWindowResize() {
    // Update chat layout if needed
    if (this.modules.chatSystem) {
      this.modules.chatSystem.handleResize?.();
    }
    
    // Update navigation layout
    if (this.modules.navigation) {
      this.modules.navigation.handleResize?.();
    }
  }

  /**
   * Handle page becoming hidden
   */
  handlePageHidden() {
    console.log('📱 Page hidden - reducing update frequency');
    // Reduce update frequency when page is hidden
    if (this.statusUpdateInterval) {
      clearInterval(this.statusUpdateInterval);
      this.statusUpdateInterval = setInterval(() => {
        if (this.modules.statusMonitor) {
          this.modules.statusMonitor.updateStatus();
        }
      }, this.config.refreshInterval * 4); // 4x slower
    }
  }

  /**
   * Handle page becoming visible
   */
  handlePageVisible() {
    console.log('👁️ Page visible - resuming normal updates');
    // Resume normal update frequency
    if (this.statusUpdateInterval) {
      clearInterval(this.statusUpdateInterval);
      this.statusUpdateInterval = setInterval(() => {
        if (this.modules.statusMonitor) {
          this.modules.statusMonitor.updateStatus();
        }
      }, this.config.refreshInterval);
    }
    
    // Immediate status update
    if (this.modules.statusMonitor) {
      this.modules.statusMonitor.updateStatus();
    }
  }

  /**
   * Handle network going online
   */
  handleNetworkOnline() {
    console.log('🌐 Network connection restored');
    this.showNotification('🌐 Connection restored', 'success');
    
    // Resume normal operations
    this.startPeriodicUpdates();
  }

  /**
   * Handle network going offline
   */
  handleNetworkOffline() {
    console.log('📡 Network connection lost');
    this.showNotification('📡 Connection lost - running in offline mode', 'warning');
    
    // Stop periodic updates
    if (this.statusUpdateInterval) {
      clearInterval(this.statusUpdateInterval);
    }
    if (this.performanceUpdateInterval) {
      clearInterval(this.performanceUpdateInterval);
    }
  }

  /**
   * Close any active modals or panels
   */
  closeActiveModals() {
    // Close any open modals, dropdowns, etc.
    document.querySelectorAll('.modal, .dropdown-open').forEach(element => {
      element.classList.remove('active', 'open', 'dropdown-open');
    });
  }

  /**
   * Show welcome notification
   */
  showWelcomeNotification() {
    setTimeout(() => {
      this.showNotification('🎉 Welcome back! Dashboard is ready for operation.', 'success');
    }, 1000);
  }

  /**
   * Show notification to user
   */
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : type === 'error' ? '#ef4444' : '#6366f1'};
      color: white;
      padding: 16px 24px;
      border-radius: 12px;
      font-weight: 500;
      box-shadow: 0 10px 25px rgba(0,0,0,0.15);
      z-index: 10000;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      max-width: 350px;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 4000);
  }

  /**
   * Show error state
   */
  showErrorState(error) {
    const errorContainer = document.createElement('div');
    errorContainer.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      color: white;
      text-align: center;
      padding: 40px;
    `;
    
    errorContainer.innerHTML = `
      <div class="error-content">
        <div style="font-size: 64px; margin-bottom: 24px;">⚠️</div>
        <h1 style="font-size: 32px; font-weight: 700; margin-bottom: 16px;">Initialization Failed</h1>
        <p style="font-size: 18px; margin-bottom: 32px; opacity: 0.9;">${error.message}</p>
        <button onclick="location.reload()" style="
          background: rgba(255,255,255,0.2);
          color: white;
          border: 2px solid white;
          border-radius: 8px;
          padding: 12px 24px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        " onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">
          🔄 Reload Dashboard
        </button>
      </div>
    `;
    
    document.body.appendChild(errorContainer);
  }

  /**
   * Get system information
   */
  getSystemInfo() {
    return {
      version: this.version,
      initialized: this.initialized,
      modules: Object.keys(this.modules),
      config: this.config,
      performance: this.modules.performanceTracker?.getMetrics() || null
    };
  }

  /**
   * Create fallback navigation if main module fails
   */
  createFallbackNavigation() {
    console.log('🔄 Creating fallback navigation...');
    const contentArea = document.getElementById('mainContent');
    if (contentArea) {
      contentArea.innerHTML = `
        <div class="fallback-content">
          <h1>🏭 Factory Dashboard</h1>
          <p>Loading full interface...</p>
          <div class="basic-nav">
            <button onclick="location.reload()">🔄 Reload</button>
          </div>
        </div>
      `;
    }
  }

  /**
   * Create fallback chat if main module fails
   */
  createFallbackChat() {
    console.log('🔄 Creating fallback chat...');
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
      chatMessages.innerHTML = `
        <div class="message ai">
          <div class="message-bubble">
            💭 Chat system is loading... Please wait a moment.
          </div>
        </div>
      `;
    }
  }
}

/**
 * Simple Status Monitor
 */
class StatusMonitor {
  constructor() {
    this.status = {
      backend: 'unknown',
      cameras: 'unknown',
      ai: 'unknown',
      lastUpdate: null
    };
  }

  async updateStatus() {
    try {
      // Check backend status
      const response = await fetch('http://localhost:3000/health');
      if (response.ok) {
        const health = await response.json();
        this.status = {
          backend: health.status === 'ok' ? 'online' : 'offline',
          cameras: health.services?.cameras || 'unknown',
          ai: health.services?.ai || 'unknown',
          lastUpdate: new Date()
        };
      }
    } catch (error) {
      this.status = {
        backend: 'offline',
        cameras: 'unknown',
        ai: 'unknown',
        lastUpdate: new Date()
      };
    }
    
    this.updateStatusDisplay();
  }

  updateStatusDisplay() {
    const statusElement = document.querySelector('.system-status');
    if (statusElement) {
      const statusIcon = this.status.backend === 'online' ? '🟢' : '🔴';
      statusElement.innerHTML = `${statusIcon} System ${this.status.backend}`;
    }
  }
}

/**
 * Simple Performance Tracker
 */
class PerformanceTracker {
  constructor() {
    this.metrics = {
      pageLoadTime: performance.now(),
      memoryUsage: null,
      networkRequests: 0,
      errors: 0
    };
  }

  collectMetrics() {
    // Collect performance metrics
    if (performance.memory) {
      this.metrics.memoryUsage = {
        used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
        total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024)
      };
    }
  }

  getMetrics() {
    return this.metrics;
  }
}

// Global dashboard instance
let dashboard = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  dashboard = new FactoryDashboard();
  
  // Make available globally for debugging
  window.dashboard = dashboard;
  window.getSystemInfo = () => dashboard.getSystemInfo();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
  if (dashboard) {
    // Cleanup intervals
    if (dashboard.statusUpdateInterval) {
      clearInterval(dashboard.statusUpdateInterval);
    }
    if (dashboard.performanceUpdateInterval) {
      clearInterval(dashboard.performanceUpdateInterval);
    }
    
    console.log('👋 Dashboard shutting down...');
  }
});
