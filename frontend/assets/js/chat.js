/**
 * Factory Supervision Dashboard - Chat System
 * Enhanced chat functionality with AI integration
 */

class ChatSystem {
  constructor() {
    this.messageList = new MessageLinkedList();
    this.isTyping = false;
    this.scrollButton = null;
    this.typingTimer = null;
    
    // DOM Elements
    this.input = document.getElementById("chatInput");
    this.chatBox = document.getElementById("chatMessages");
    this.sendButton = document.getElementById("sendButton");
    this.chatPanel = document.getElementById("chatPanel");
    this.chatToggle = document.getElementById("chatToggle");
    this.chatToggleCollapsed = document.getElementById("chatToggleCollapsed");
    
    // Configuration
    this.config = {
      chatEndpoint: "http://localhost:3000/chat",
      retryAttempts: 3,
      timeout: 30000
    };
    
    this.init();
  }

  /**
   * Initialize the chat system
   */
  init() {
    this.setupEventListeners();
    this.addAnimationStyles();
    this.initializeChat();
  }

  /**
   * Setup all event listeners
   */
  setupEventListeners() {
    // Chat toggle functionality
    this.chatToggle.addEventListener('click', () => this.toggleChat());
    this.chatToggleCollapsed.addEventListener('click', () => this.toggleChat());

    // Input handling
    this.input.addEventListener('input', (e) => this.handleInputChange(e));
    this.input.addEventListener("keypress", (e) => this.handleKeyPress(e));
    this.sendButton.addEventListener("click", () => this.handleSendClick());

    // Scroll detection for scroll-to-bottom button
    this.chatBox.addEventListener('scroll', () => this.handleScroll());
    
    // Drag functionality
    this.setupDragFunctionality();
  }

  /**
   * Toggle chat panel between collapsed and expanded states
   */
  toggleChat() {
    const isCollapsed = this.chatPanel.classList.contains('collapsed');
    
    if (isCollapsed) {
      // Expand chat
      this.chatPanel.classList.remove('collapsed');
      this.chatToggle.style.display = 'flex';
      this.chatToggleCollapsed.style.display = 'none';
      
      // Focus input when expanded
      setTimeout(() => {
        this.input.focus();
      }, 300);
    } else {
      // Collapse chat
      this.chatPanel.classList.add('collapsed');
      this.chatToggle.style.display = 'none';
      this.chatToggleCollapsed.style.display = 'flex';
    }
  }

  /**
   * Handle input field changes
   */
  handleInputChange(e) {
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    
    // Enable/disable send button based on content
    if (e.target.value.trim()) {
      this.sendButton.style.opacity = '1';
      this.sendButton.style.transform = 'scale(1)';
    } else {
      this.sendButton.style.opacity = '0.7';
      this.sendButton.style.transform = 'scale(0.95)';
    }

    // Enhanced typing detection
    clearTimeout(this.typingTimer);
    
    // Show user is typing (visual feedback)
    e.target.style.borderColor = '#667eea';
    e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
    
    this.typingTimer = setTimeout(() => {
      e.target.style.borderColor = '#e5e7eb';
      e.target.style.boxShadow = 'none';
    }, 1000);
  }

  /**
   * Handle key press events
   */
  handleKeyPress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      
      // Add visual feedback for enter press
      this.sendButton.style.transform = 'scale(0.95)';
      setTimeout(() => {
        this.sendButton.style.transform = 'scale(1)';
      }, 150);
      
      this.handleUserInput();
    }
  }

  /**
   * Handle send button click
   */
  handleSendClick() {
    // Add click animation
    this.sendButton.style.transform = 'scale(0.95)';
    setTimeout(() => {
      this.sendButton.style.transform = 'scale(1)';
    }, 150);
    
    this.handleUserInput();
  }

  /**
   * Handle scroll events for scroll-to-bottom button
   */
  handleScroll() {
    const isAtBottom = this.chatBox.scrollTop >= (this.chatBox.scrollHeight - this.chatBox.clientHeight - 50);
    
    if (!isAtBottom && !this.scrollButton) {
      this.scrollButton = document.createElement('button');
      this.scrollButton.innerHTML = '↓ New messages';
      this.scrollButton.style.cssText = `
        position: absolute;
        bottom: 80px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        z-index: 10;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        animation: bounceIn 0.3s ease-out;
      `;
      
      this.scrollButton.onclick = () => {
        this.chatBox.scrollTo({
          top: this.chatBox.scrollHeight,
          behavior: 'smooth'
        });
      };
      
      this.chatBox.parentElement.appendChild(this.scrollButton);
    } else if (isAtBottom && this.scrollButton) {
      this.scrollButton.style.animation = 'bounceOut 0.3s ease-out';
      setTimeout(() => {
        if (this.scrollButton && this.scrollButton.parentElement) {
          this.scrollButton.parentElement.removeChild(this.scrollButton);
          this.scrollButton = null;
        }
      }, 300);
    }
  }

  /**
   * Setup drag functionality for chat panel
   */
  setupDragFunctionality() {
    const header = this.chatPanel.querySelector('.chat-header');
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    const dragStart = (e) => {
      if (this.chatPanel.classList.contains('collapsed')) return;
      
      // Only allow dragging from header
      if (!header.contains(e.target) || e.target.closest('.chat-toggle')) return;
      
      isDragging = true;
      
      if (e.type === "touchstart") {
        initialX = e.touches[0].clientX - xOffset;
        initialY = e.touches[0].clientY - yOffset;
      } else {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
      }

      header.style.cursor = 'grabbing';
      this.chatPanel.style.transition = 'none';
    };

    const dragEnd = () => {
      if (!isDragging) return;
      
      isDragging = false;
      header.style.cursor = 'grab';
      this.chatPanel.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
      
      // Keep chat panel within viewport bounds
      const rect = this.chatPanel.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      
      let newX = xOffset;
      let newY = yOffset;
      
      // Constrain to viewport
      if (rect.left < 0) newX = xOffset - rect.left;
      if (rect.right > viewportWidth) newX = xOffset - (rect.right - viewportWidth);
      if (rect.top < 0) newY = yOffset - rect.top;
      if (rect.bottom > viewportHeight) newY = yOffset - (rect.bottom - viewportHeight);
      
      if (newX !== xOffset || newY !== yOffset) {
        xOffset = newX;
        yOffset = newY;
        this.chatPanel.style.transform = `translate(${xOffset}px, ${yOffset}px)`;
      }
    };

    const drag = (e) => {
      if (!isDragging) return;
      
      e.preventDefault();
      
      if (e.type === "touchmove") {
        currentX = e.touches[0].clientX - initialX;
        currentY = e.touches[0].clientY - initialY;
      } else {
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
      }

      xOffset = currentX;
      yOffset = currentY;

      this.chatPanel.style.transform = `translate(${currentX}px, ${currentY}px)`;
    };

    // Mouse events
    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);

    // Touch events for mobile
    header.addEventListener('touchstart', dragStart, { passive: true });
    document.addEventListener('touchmove', drag, { passive: false });
    document.addEventListener('touchend', dragEnd);
  }

  /**
   * Create DOM element for message
   */
  createMessageElement(messageNode) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${messageNode.sender.toLowerCase()}`;
    messageDiv.id = messageNode.id;
    
    const timeString = messageNode.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    if (messageNode.sender === "System") {
      messageDiv.innerHTML = `
        <div class="message-bubble ${messageNode.isError ? 'error' : ''}">
          ${messageNode.content}
        </div>
        <div class="message-time">${timeString}</div>
      `;
    } else {
      const senderLabel = messageNode.sender === "You" ? "You" : "AI Assistant";
      messageDiv.innerHTML = `
        <div class="message-sender">${senderLabel}</div>
        <div class="message-bubble ${messageNode.isError ? 'error' : ''}">
          ${messageNode.content}
        </div>
        <div class="message-time">${timeString}</div>
      `;
    }
    
    return messageDiv;
  }

  /**
   * Add message to chat with enhanced animations
   */
  addMessage(sender, content, isError = false) {
    // Add to linked list
    const messageNode = this.messageList.append(sender, content, isError);
    
    // Create DOM element
    const messageElement = this.createMessageElement(messageNode);
    messageNode.element = messageElement;
    
    // Add to chat box with enhanced animation
    messageElement.style.opacity = '0';
    messageElement.style.transform = 'translateY(20px) scale(0.95)';
    this.chatBox.appendChild(messageElement);
    
    // Trigger staggered animation
    requestAnimationFrame(() => {
      messageElement.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
      messageElement.style.opacity = '1';
      messageElement.style.transform = 'translateY(0) scale(1)';
    });
    
    // Smooth scroll to bottom with improved behavior
    setTimeout(() => {
      this.chatBox.scrollTo({
        top: this.chatBox.scrollHeight,
        behavior: 'smooth'
      });
    }, 100);
    
    // Add fun sound effect simulation (visual feedback)
    if (sender === "You") {
      messageElement.style.animation = 'messageGlow 0.6s ease-out';
    }
    
    return messageNode;
  }

  /**
   * Show typing indicator
   */
  showTypingIndicator() {
    if (this.isTyping) return null; // Prevent multiple typing indicators
    
    this.isTyping = true;
    const typingNode = this.messageList.append("AI", "", false);
    
    const typingDiv = document.createElement("div");
    typingDiv.className = "message ai typing";
    typingDiv.id = typingNode.id;
    typingDiv.innerHTML = `
      <div class="message-sender">AI Assistant is thinking...</div>
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    
    typingNode.element = typingDiv;
    this.chatBox.appendChild(typingDiv);
    
    // Smooth scroll to show typing indicator
    setTimeout(() => {
      this.chatBox.scrollTo({
        top: this.chatBox.scrollHeight,
        behavior: 'smooth'
      });
    }, 100);
    
    return typingNode;
  }

  /**
   * Remove typing indicator
   */
  removeTypingIndicator(typingNode) {
    if (typingNode && typingNode.element) {
      // Remove from linked list properly
      if (typingNode.prev) {
        typingNode.prev.next = typingNode.next;
      } else {
        this.messageList.head = typingNode.next;
      }
      
      if (typingNode.next) {
        typingNode.next.prev = typingNode.prev;
      } else {
        this.messageList.tail = typingNode.prev;
      }
      
      // Remove DOM element
      if (typingNode.element.parentNode) {
        typingNode.element.parentNode.removeChild(typingNode.element);
      }
      
      this.messageList.length--;
    }
    this.isTyping = false;
  }

  /**
   * Send message to AI API
   */
  async sendMessageToAI(message) {
    const typingIndicator = this.showTypingIndicator();
    this.sendButton.disabled = true;
    
    try {
      const response = await fetch(this.config.chatEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: message,
          timestamp: new Date().toISOString(),
          context: "factory_supervision_dashboard"
        }),
        signal: AbortSignal.timeout(this.config.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Remove typing indicator
      this.removeTypingIndicator(typingIndicator);
      
      // Add AI response
      if (data.reply) {
        this.addMessage("AI", data.reply);
      } else {
        this.addMessage("AI", "I received your message but couldn't generate a proper response. Please try again.", true);
      }

    } catch (error) {
      // Remove typing indicator
      this.removeTypingIndicator(typingIndicator);
      
      // Handle different error types
      let errorMessage = "Sorry, I'm having trouble connecting right now. ";
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        errorMessage += "The request timed out. Please try a shorter question.";
      } else if (error.message.includes('404')) {
        errorMessage += "The chat service is not available.";
      } else if (error.message.includes('500')) {
        errorMessage += "There's an issue with my processing. Please try again.";
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage += "Can't reach the server. Make sure it's running.";
      } else {
        errorMessage += `Error: ${error.message}`;
      }
      
      this.addMessage("AI", errorMessage, true);
      console.error("Chat API Error:", error);
    } finally {
      this.sendButton.disabled = false;
    }
  }

  /**
   * Handle user input
   */
  handleUserInput() {
    const message = this.input.value.trim();
    if (message && !this.sendButton.disabled) {
      // Add user message to linked list
      this.addMessage("You", message);
      this.input.value = "";
      
      // Auto-resize textarea
      this.input.style.height = 'auto';
      
      // Send to AI
      this.sendMessageToAI(message);
    }
  }

  /**
   * Check server connection
   */
  async checkServerConnection() {
    try {
      const response = await fetch('http://localhost:3000/health');
      if (response.ok) {
        const health = await response.json();
        const backendStatus = health.services?.fastapi_backend === 'connected' ? '✅' : '⚠️';
        this.addMessage("System", `${backendStatus} Connected to Factory Supervision System`);
      }
    } catch (error) {
      this.addMessage("System", "⚠️ System offline - Please start the servers");
    }
  }

  /**
   * Add interactive quick action buttons
   */
  addQuickActions() {
    const quickActionsDiv = document.createElement("div");
    quickActionsDiv.style.cssText = `
      margin: 20px 0;
      padding: 16px;
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
      border-radius: 16px;
      border: 1px solid rgba(102, 126, 234, 0.2);
      animation: slideInUp 0.5s ease-out;
    `;
    
    const quickActions = [
      { text: "📊 Production Status", action: "What's the current production status?" },
      { text: "🎥 Camera Feeds", action: "Show me the camera feeds" },
      { text: "🚨 Recent Alerts", action: "Any recent alerts or issues?" },
      { text: "📈 Performance Metrics", action: "How is the system performing today?" }
    ];
    
    quickActionsDiv.innerHTML = `
      <div style="font-size: 12px; font-weight: 600; margin-bottom: 12px; color: #667eea; text-align: center;">
        ⚡ QUICK ACTIONS ⚡
      </div>
      ${quickActions.map((action, index) => `
        <button data-action="${action.action}" class="quick-action-btn"
                style="display: block; width: 100%; margin: 6px 0; padding: 10px 16px; 
                       background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(248,250,252,0.8) 100%);
                       border: 1px solid rgba(102, 126, 234, 0.3); 
                       border-radius: 12px; color: #374151; font-size: 13px; 
                       cursor: pointer; text-align: left; font-weight: 500;
                       transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                       animation: slideInUp 0.5s ease-out ${index * 0.1}s both;">
          ${action.text}
        </button>
      `).join('')}
    `;
    
    // Add event listeners to quick action buttons
    quickActionsDiv.querySelectorAll('.quick-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = e.target.getAttribute('data-action');
        this.input.value = action;
        
        // Add visual feedback
        this.input.style.transform = 'scale(1.02)';
        setTimeout(() => {
          this.input.style.transform = 'scale(1)';
          this.handleUserInput();
        }, 200);
      });
    });
    
    this.chatBox.appendChild(quickActionsDiv);
    
    // Smooth scroll to show quick actions
    setTimeout(() => {
      this.chatBox.scrollTo({
        top: this.chatBox.scrollHeight,
        behavior: 'smooth'
      });
    }, 100);
  }

  /**
   * Initialize chat with welcome message
   */
  initializeChat() {
    const welcomeMsg = `🎉 Welcome to the Factory Supervision System! 🏭✨

I'm your friendly AI assistant, here to make factory management fun and efficient! 

🔍 **Production Monitoring**
• Real-time system status 📊
• Machine diagnostics 🔧
• Performance metrics 📈

📊 **Analytics & Reports**  
• Production trends 📉
• Quality analysis ✅
• Efficiency insights 💡

⚙️ **System Management**
• Computer vision status 👁️
• Alert management 🚨
• File access 📁

💬 **Pro Tips:**
• Try asking "What's happening on the factory floor?"
• Say "Show me today's performance" for quick stats
• Type "Help" anytime for assistance

What would you like to explore today? 🚀`;
    
    setTimeout(() => {
      this.addMessage("AI", welcomeMsg);
      
      // Add some fun quick action buttons after welcome
      setTimeout(() => {
        this.addQuickActions();
      }, 1500);
      
      setTimeout(() => this.checkServerConnection(), 2000);
    }, 800);
  }

  /**
   * Add dynamic animation styles
   */
  addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes bounceIn {
        0% { transform: scale(0.3) translateY(20px); opacity: 0; }
        50% { transform: scale(1.05) translateY(-5px); opacity: 0.8; }
        100% { transform: scale(1) translateY(0); opacity: 1; }
      }
      @keyframes bounceOut {
        0% { transform: scale(1) translateY(0); opacity: 1; }
        100% { transform: scale(0.3) translateY(20px); opacity: 0; }
      }
      @keyframes slideInUp {
        from {
          opacity: 0;
          transform: translateY(30px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Get debug information about the chat system
   */
  getDebugInfo() {
    return {
      messageStats: this.messageList.getStats(),
      isTyping: this.isTyping,
      hasScrollButton: !!this.scrollButton,
      chatCollapsed: this.chatPanel.classList.contains('collapsed')
    };
  }
}

// Global chat system instance
let chatSystem = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  try {
    console.log('🤖 Initializing chat system...');
    chatSystem = new ChatSystem();
    
    // Make available globally for debugging
    window.chatSystem = chatSystem;
    window.debugMessages = () => console.log('📋 Chat Debug:', chatSystem.getDebugInfo());
    
    console.log('✅ Chat system initialized successfully');
  } catch (error) {
    console.error('❌ Chat system initialization failed:', error);
    
    // Create minimal fallback chat
    window.chatSystem = {
      initialized: false,
      error: error.message,
      addMessage: (sender, content) => {
        console.log(`Fallback chat - ${sender}: ${content}`);
      }
    };
  }
});
