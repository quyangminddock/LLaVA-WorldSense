// Enhanced Chat Module - Real-Time Streaming Support
class ChatModule {
    constructor() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.clearButton = document.getElementById('btn-clear-chat');

        // Streaming state
        this.currentStreamingMessage = null;
        this.streamingElement = null;

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Clear chat button
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => {
                this.clearMessages();
            });
        }
    }

    addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = isUser ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';

        // Support markdown
        if (typeof marked !== 'undefined') {
            textDiv.innerHTML = marked.parse(message);
        } else {
            const p = document.createElement('p');
            p.textContent = message;
            textDiv.appendChild(p);
        }

        content.appendChild(textDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    startStreamingMessage() {
        // Start a new streaming message from AI
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message streaming';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = '<p><span class="streaming-cursor">▋</span></p>';

        content.appendChild(textDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        this.messagesContainer.appendChild(messageDiv);

        this.currentStreamingMessage = '';
        this.streamingElement = textDiv.querySelector('p');

        this.scrollToBottom();

        return messageDiv;
    }

    appendToStreamingMessage(text) {
        // Append text to the currently streaming message
        if (!this.streamingElement) return;

        this.currentStreamingMessage += text;

        // Update the display with cursor
        this.streamingElement.innerHTML = this.currentStreamingMessage + '<span class="streaming-cursor">▋</span>';

        this.scrollToBottom();
    }

    finishStreamingMessage(audioUrl = null) {
        // Complete the streaming message and optionally play audio
        if (!this.streamingElement) return;

        // Remove cursor
        this.streamingElement.innerHTML = this.currentStreamingMessage;

        // Add audio player if available
        if (audioUrl && this.streamingElement.parentElement) {
            const audioContainer = document.createElement('div');
            audioContainer.className = 'message-audio';

            const audioPlayer = document.createElement('audio');
            audioPlayer.controls = true;
            audioPlayer.src = audioUrl;
            audioPlayer.className = 'jarvis-audio';

            // Auto-play if configured
            if (CONFIG.jarvis?.autoPlayAudio) {
                audioPlayer.autoplay = true;
            }

            const playIcon = document.createElement('span');
            playIcon.textContent = '🔊 ';

            audioContainer.appendChild(playIcon);
            audioContainer.appendChild(audioPlayer);
            this.streamingElement.parentElement.appendChild(audioContainer);
        }

        // Clean up
        this.currentStreamingMessage = null;
        this.streamingElement = null;

        this.scrollToBottom();
    }

    showTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'block';
            this.scrollToBottom();
        }
    }

    hideTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }

    clearMessages() {
        // Keep welcome message
        const messages = this.messagesContainer.querySelectorAll('.message');
        messages.forEach((msg, index) => {
            if (index > 0) { // Skip first welcome message
                msg.remove();
            }
        });
    }

    addSystemMessage(text, type = 'info') {
        // Add a system status message
        const messageDiv = document.createElement('div');
        messageDiv.className = `message system-message ${type}`;

        const content = document.createElement('div');
        content.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text system';
        textDiv.innerHTML = `<p><em>${text}</em></p>`;

        content.appendChild(textDiv);
        messageDiv.appendChild(content);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// Export
window.ChatModule = ChatModule;
