/**
 * Factory Supervision Dashboard - Message Linked List Implementation
 * Efficient data structure for managing chat messages
 */

class MessageNode {
  constructor(id, sender, content, timestamp, isError = false) {
    this.id = id;
    this.sender = sender;
    this.content = content;
    this.timestamp = timestamp;
    this.isError = isError;
    this.next = null;
    this.prev = null;
    this.element = null; // DOM element reference
  }
}

class MessageLinkedList {
  constructor() {
    this.head = null;
    this.tail = null;
    this.length = 0;
    this.maxMessages = 100; // Limit to prevent memory issues
  }

  /**
   * Add message to the end (most recent)
   * @param {string} sender - Message sender (You, AI, System)
   * @param {string} content - Message content
   * @param {boolean} isError - Whether this is an error message
   * @returns {MessageNode} The created message node
   */
  append(sender, content, isError = false) {
    const timestamp = new Date();
    const id = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newNode = new MessageNode(id, sender, content, timestamp, isError);

    if (!this.head) {
      this.head = this.tail = newNode;
    } else {
      this.tail.next = newNode;
      newNode.prev = this.tail;
      this.tail = newNode;
    }

    this.length++;

    // Remove old messages if we exceed maxMessages
    if (this.length > this.maxMessages) {
      this.removeHead();
    }

    return newNode;
  }

  /**
   * Remove the oldest message (head)
   * @returns {MessageNode|null} The removed node
   */
  removeHead() {
    if (!this.head) return null;

    const removedNode = this.head;
    
    // Remove DOM element
    if (removedNode.element && removedNode.element.parentNode) {
      removedNode.element.parentNode.removeChild(removedNode.element);
    }

    if (this.head === this.tail) {
      this.head = this.tail = null;
    } else {
      this.head = this.head.next;
      this.head.prev = null;
    }

    this.length--;
    return removedNode;
  }

  /**
   * Get all messages as array (for iteration)
   * @returns {MessageNode[]} Array of message nodes
   */
  toArray() {
    const messages = [];
    let current = this.head;
    while (current) {
      messages.push(current);
      current = current.next;
    }
    return messages;
  }

  /**
   * Find message by ID
   * @param {string} id - Message ID to search for
   * @returns {MessageNode|null} Found message node or null
   */
  findById(id) {
    let current = this.head;
    while (current) {
      if (current.id === id) return current;
      current = current.next;
    }
    return null;
  }

  /**
   * Clear all messages
   */
  clear() {
    let current = this.head;
    while (current) {
      if (current.element && current.element.parentNode) {
        current.element.parentNode.removeChild(current.element);
      }
      current = current.next;
    }
    this.head = this.tail = null;
    this.length = 0;
  }

  /**
   * Get recent messages (last n)
   * @param {number} n - Number of recent messages to retrieve
   * @returns {MessageNode[]} Array of recent message nodes
   */
  getRecent(n = 10) {
    const messages = [];
    let current = this.tail;
    let count = 0;
    
    while (current && count < n) {
      messages.unshift(current);
      current = current.prev;
      count++;
    }
    
    return messages;
  }

  /**
   * Get statistics about the message list
   * @returns {object} Statistics object
   */
  getStats() {
    return {
      totalMessages: this.length,
      headContent: this.head?.content.slice(0, 30) + '...',
      tailContent: this.tail?.content.slice(0, 30) + '...',
      recentSenders: this.getRecent(5).map(m => m.sender)
    };
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MessageNode, MessageLinkedList };
}
