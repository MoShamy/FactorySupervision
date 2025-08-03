/**
 * Dashboard Chat Integration
 * Cute and user-friendly chat interface for the dashboard
 */

class DashboardChat {
  constructor() {
    this.messages = [];
    this.isTyping = false;
    
    // Configuration
    this.config = {
      chatEndpoint: "http://localhost:3000/chat",
      retryAttempts: 3,
      timeout: 30000
    };
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupQuickActions();
    this.initializeCharCounter();
    this.testConnection();
  }

  setupEventListeners() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    
    if (chatInput && sendButton) {
      // Input handling
      chatInput.addEventListener('input', (e) => this.handleInputChange(e));
      chatInput.addEventListener('keypress', (e) => this.handleKeyPress(e));
      
      // Send button
      sendButton.addEventListener('click', () => this.sendMessage());
      
      // Auto-resize textarea
      chatInput.addEventListener('input', () => this.autoResizeTextarea(chatInput));
    }
  }

  setupQuickActions() {
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const message = btn.getAttribute('data-message');
        if (message) {
          this.sendMessage(message);
        }
      });
    });
  }

  initializeCharCounter() {
    const chatInput = document.getElementById('chatInput');
    const charCount = document.getElementById('charCount');
    
    if (chatInput && charCount) {
      chatInput.addEventListener('input', () => {
        const count = chatInput.value.length;
        charCount.textContent = count;
        
        // Change color based on character count
        if (count > 800) {
          charCount.style.color = '#ef4444';
        } else if (count > 600) {
          charCount.style.color = '#f59e0b';
        } else {
          charCount.style.color = '#a0aec0';
        }
      });
    }
  }

  handleInputChange(e) {
    const sendBtn = document.getElementById('sendButton');
    if (e.target.value.trim()) {
      sendBtn.style.opacity = '1';
      sendBtn.style.transform = 'scale(1)';
    } else {
      sendBtn.style.opacity = '0.7';
      sendBtn.style.transform = 'scale(0.95)';
    }
  }

  handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.sendMessage();
    }
  }

  autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  }

  async sendMessage(customMessage = null) {
    const chatInput = document.getElementById('chatInput');
    const message = customMessage || chatInput.value.trim();
    
    if (!message || this.isTyping) return;

    // Add user message
    this.addMessage('user', message);
    
    // Clear input if not using custom message
    if (!customMessage) {
      chatInput.value = '';
      chatInput.style.height = 'auto';
      this.updateCharCounter(0);
    }

    // Show typing indicator
    this.showTypingIndicator();
    
    try {
      const response = await fetch(this.config.chatEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: message,
          timestamp: new Date().toISOString(),
          context: "dashboard_chat"
        }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Hide typing indicator
      this.hideTypingIndicator();
      
      // Add AI response
      if (data.reply) {
        this.addMessage('assistant', data.reply);
      } else {
        this.addMessage('assistant', "I received your message but couldn't generate a proper response. Please try again.", true);
      }

    } catch (error) {
      this.hideTypingIndicator();
      
      let errorMessage = "Sorry, I'm having trouble connecting right now. ";
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        errorMessage += "The request timed out. Please try again.";
      } else if (error.message.includes('404')) {
        errorMessage += "The chat service is not available.";
      } else if (error.message.includes('500')) {
        errorMessage += "There's an issue with my processing. Please try again.";
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage += "Can't reach the server. Make sure it's running.";
      } else {
        errorMessage += `Error: ${error.message}`;
      }
      
      this.addMessage('assistant', errorMessage, true);
      console.error("Chat API Error:", error);
    }
  }

  addMessage(sender, content, isError = false) {
    const messagesContainer = document.getElementById('chatMessages');
    const welcomeMessage = messagesContainer.querySelector('.welcome-message');
    
    // Remove welcome message on first user message
    if (sender === 'user' && welcomeMessage) {
      welcomeMessage.style.opacity = '0';
      setTimeout(() => welcomeMessage.remove(), 300);
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    if (isError) {
      messageContent.style.background = 'linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%)';
      messageContent.style.color = '#c53030';
    }
    messageContent.textContent = content;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom with smooth animation
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
    
    // Store message
    this.messages.push({
      sender,
      content,
      timestamp: new Date().toISOString(),
      isError
    });
  }

  showTypingIndicator() {
    this.isTyping = true;
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
      indicator.style.display = 'flex';
    }
  }

  hideTypingIndicator() {
    this.isTyping = false;
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
      indicator.style.display = 'none';
    }
  }

  updateCharCounter(count) {
    const charCount = document.getElementById('charCount');
    if (charCount) {
      charCount.textContent = count;
    }
  }

  async testConnection() {
    try {
      const response = await fetch(this.config.chatEndpoint.replace('/chat', '/health'), {
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      });
      
      if (response.ok) {
        const health = await response.json();
        console.log('🟢 Dashboard chat connection healthy:', health);
        
        // Update status indicator
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) {
          statusDot.classList.add('online');
        }
        
        return true;
      } else {
        console.warn('🟡 Server returned non-OK status:', response.status);
        return false;
      }
    } catch (error) {
      console.error('🔴 Dashboard chat connection failed:', error);
      
      // Update status to offline
      const statusDot = document.querySelector('.status-dot');
      if (statusDot) {
        statusDot.classList.remove('online');
        statusDot.style.background = '#ef4444';
      }
      
      // Update status text
      const statusText = document.querySelector('.status-text');
      if (statusText) {
        statusText.innerHTML = '<span class="status-dot offline"></span>Connection issues detected';
      }
      
      return false;
    }
  }

  clearChat() {
    const messagesContainer = document.getElementById('chatMessages');
    if (messagesContainer) {
      messagesContainer.innerHTML = `
        <div class="welcome-message">
          <div class="welcome-card">
            <div class="welcome-icon">👋</div>
            <h4>Chat cleared! How can I help you?</h4>
            <p>Ask me anything about your factory operations, analytics, or system status.</p>
          </div>
        </div>
      `;
    }
    this.messages = [];
  }

  getDebugInfo() {
    return {
      messagesCount: this.messages.length,
      isTyping: this.isTyping,
      config: this.config,
      lastMessage: this.messages[this.messages.length - 1]
    };
  }
}

// Initialize dashboard chat when page loads
document.addEventListener('DOMContentLoaded', () => {
  // Only initialize if we're on the dashboard page with chat elements
  if (document.getElementById('chatMessages') && document.getElementById('chatInput')) {
    try {
      const dashboardChat = new DashboardChat();
      
      // Make available globally for debugging
      window.dashboardChat = dashboardChat;
      window.clearChat = () => dashboardChat.clearChat();
      window.debugDashboardChat = () => console.log('📋 Dashboard Chat Debug:', dashboardChat.getDebugInfo());
      
      console.log('✅ Dashboard chat initialized successfully');
    } catch (error) {
      console.error('❌ Dashboard chat initialization failed:', error);
    }
  }
});
