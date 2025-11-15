const API_BASE_URL = '/travel-assistant';

// DOM elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newConversationBtn = document.getElementById('newConversationBtn');

let isWaitingForResponse = false;
let loadingIndicator = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showWelcomeMessage();
    setupEventListeners();
    autoResizeTextarea();
    updateSendButtonState();
});

function setupEventListeners() {
    sendBtn.addEventListener('click', handleSendMessage);
    newConversationBtn.addEventListener('click', handleNewConversation);
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isWaitingForResponse && messageInput.value.trim()) {
                handleSendMessage();
            }
        }
    });
    
    messageInput.addEventListener('input', () => {
        // Allow typing even when waiting, but send button is disabled
        autoResizeTextarea();
        updateSendButtonState();
    });
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
}

function showWelcomeMessage() {
    const welcomeText = `🌟 Welcome!

I'm NIR, your intelligent travel recommender. I can help you with:

📍 Destination recommendations based on your preferences
📦 Packing suggestions tailored to your trip
🎯 Local attractions and things to do

What would you like to know about your next trip?`;
    
    addMessage(welcomeText, 'assistant');
}

function handleNewConversation() {
    if (isWaitingForResponse) {
        return; // Don't allow new conversation while waiting
    }
    
    if (confirm('Start a new conversation? This will clear the current chat history.')) {
        resetConversation();
    }
}

async function resetConversation() {
    try {
        const response = await fetch(`${API_BASE_URL}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (response.ok) {
            chatContainer.innerHTML = '';
            showWelcomeMessage();
        } else {
            console.error('Failed to reset conversation');
        }
    } catch (error) {
        console.error('Error resetting conversation:', error);
    }
}

async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isWaitingForResponse) {
        return;
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    autoResizeTextarea();
    
    // Disable input and send button
    setWaitingState(true);
    
    // Show loading animation
    showLoadingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `HTTP error! status: ${response.status}`);
        }
        
        // Hide loading and add assistant response
        hideLoadingIndicator();
        
        if (data.response) {
            addMessage(data.response, 'assistant');
        } else {
            throw new Error('Invalid response format from server');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        hideLoadingIndicator();
        let errorMessage = 'Sorry, I encountered an error. Please try again.';
        if (error.message && !error.message.includes('HTTP error')) {
            errorMessage = `Sorry, I encountered an error: ${error.message}`;
        }
        addMessage(errorMessage, 'assistant');
    } finally {
        setWaitingState(false);
    }
}

function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-content">${formatMarkdown(text)}</div>
        <div class="message-time">${time}</div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function formatMarkdown(text) {
    // First escape HTML to prevent XSS
    const div = document.createElement('div');
    div.textContent = text;
    let html = div.innerHTML;
    
    // Convert markdown bold **text** to <strong>text</strong>
    // Handle both single-line and multi-line bold text
    html = html.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
    
    // Remove extra newlines after bold titles (reduce spacing)
    // Pattern: </strong>\n\n becomes </strong>\n
    html = html.replace(/(<\/strong>)\n\n+/g, '$1\n');
    
    // Convert remaining newlines to <br>
    html = html.replace(/\n/g, '<br>');
    
    return html;
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function updateSendButtonState() {
    const hasText = messageInput.value.trim().length > 0;
    sendBtn.disabled = isWaitingForResponse || !hasText;
}

function setWaitingState(waiting) {
    isWaitingForResponse = waiting;
    updateSendButtonState();
}

function showLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading-indicator';
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.innerHTML = `
        <div class="message-content">
            <div class="plane-loader">
                <svg class="plane-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
                </svg>
            </div>
        </div>
    `;
    chatContainer.appendChild(loadingDiv);
    loadingIndicator = loadingDiv;
    scrollToBottom();
}

function hideLoadingIndicator() {
    if (loadingIndicator) {
        loadingIndicator.remove();
        loadingIndicator = null;
    }
}

