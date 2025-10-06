// Multimodal AI Web Interface JavaScript
class MultimodalAI {
    constructor() {
        this.ws = null;
        this.isRecording = false;
        this.recordingTimeout = null;
        this.voices = {};
        this.currentVoice = '';
        
        this.initializeElements();
        this.attachEventListeners();
        this.loadVoices();
        this.initializeWebSocket();
    }
    
    initializeElements() {
        // Main elements
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.imageBtn = document.getElementById('imageBtn');
        this.imageUpload = document.getElementById('imageUpload');
        this.chatMessages = document.getElementById('chatMessages');
        this.clearBtn = document.getElementById('clearBtn');
        this.settingsBtn = document.getElementById('settingsBtn');
        
        // Voice controls
        this.voiceControls = document.getElementById('voiceControls');
        this.stopRecordingBtn = document.getElementById('stopRecordingBtn');
        
        // Settings modal
        this.settingsModal = document.getElementById('settingsModal');
        this.autoSpeakCheckbox = document.getElementById('autoSpeak');
        this.autoPlayAudioCheckbox = document.getElementById('autoPlayAudio');
        this.voiceSelect = document.getElementById('voiceSelect');
        this.themeSelect = document.getElementById('themeSelect');
        this.saveSettingsBtn = document.getElementById('saveSettings');
    }
    
    attachEventListeners() {
        // Message sending
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
        
        // Voice input
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceRecording());
        this.stopRecordingBtn.addEventListener('click', () => this.stopVoiceRecording());
        
        // Image upload
        this.imageBtn.addEventListener('click', () => this.imageUpload.click());
        this.imageUpload.addEventListener('change', (e) => this.handleImageUpload(e));
        
        // Clear conversation
        this.clearBtn.addEventListener('click', () => this.clearConversation());
        
        // Settings
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        
        // Modal close
        document.querySelector('.close-btn').addEventListener('click', () => this.closeSettings());
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettings();
            }
        });
    }
    
    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.initializeWebSocket(), 3000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'response':
                this.addMessage(data.message, 'assistant');
                break;
            case 'voice_response':
                this.addMessage(`Transcribed: ${data.transcribed}`, 'system');
                this.addMessage(data.response, 'assistant');
                break;
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        const imageFile = this.imageUpload.files[0];
        
        if (!message && !imageFile) return;
        
        // Add user message to chat
        if (message) {
            this.addMessage(message, 'user');
        }
        
        // Show image preview if uploaded
        if (imageFile) {
            this.addImagePreview(imageFile);
        }
        
        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.imageUpload.value = '';
        
        try {
            const formData = new FormData();
            if (message) formData.append('message', message);
            if (imageFile) formData.append('image', imageFile);
            formData.append('voice_id', this.currentVoice);
            formData.append('speak_response', this.autoSpeakCheckbox.checked);
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            
            const result = await response.json();
            
            // Add AI response
            this.addMessage(result.response, 'assistant');
            
            // Play audio if available
            if (result.audio_path && this.autoPlayAudioCheckbox.checked) {
                this.playAudio(result.audio_path);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    addImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.maxWidth = '200px';
            img.style.borderRadius = '0.5rem';
            img.style.marginTop = '0.5rem';
            
            contentDiv.textContent = 'Image uploaded:';
            contentDiv.appendChild(img);
            messageDiv.appendChild(contentDiv);
            this.chatMessages.appendChild(messageDiv);
            
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        };
        reader.readAsDataURL(file);
    }
    
    toggleVoiceRecording() {
        if (this.isRecording) {
            this.stopVoiceRecording();
        } else {
            this.startVoiceRecording();
        }
    }
    
    startVoiceRecording() {
        this.isRecording = true;
        this.voiceBtn.classList.add('recording');
        this.voiceControls.style.display = 'flex';
        
        // Send voice input request via WebSocket
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'voice_input',
                duration: 5
            }));
        }
        
        // Auto-stop after 10 seconds
        this.recordingTimeout = setTimeout(() => {
            this.stopVoiceRecording();
        }, 10000);
    }
    
    stopVoiceRecording() {
        this.isRecording = false;
        this.voiceBtn.classList.remove('recording');
        this.voiceControls.style.display = 'none';
        
        if (this.recordingTimeout) {
            clearTimeout(this.recordingTimeout);
            this.recordingTimeout = null;
        }
    }
    
    handleImageUpload(event) {
        const file = event.target.files[0];
        if (file) {
            // Image will be handled in sendMessage()
            console.log('Image selected:', file.name);
        }
    }
    
    async clearConversation() {
        if (confirm('Are you sure you want to clear the conversation?')) {
            try {
                const response = await fetch('/api/conversation', {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    this.chatMessages.innerHTML = `
                        <div class="message system-message">
                            <div class="message-content">
                                <i class="fas fa-info-circle"></i>
                                Welcome! I'm your multimodal AI assistant. You can:
                                <ul>
                                    <li>Type messages and I'll respond</li>
                                    <li>Upload images for analysis</li>
                                    <li>Use voice input by clicking the microphone</li>
                                    <li>I'll speak my responses aloud</li>
                                </ul>
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Error clearing conversation:', error);
            }
        }
    }
    
    openSettings() {
        this.settingsModal.style.display = 'block';
    }
    
    closeSettings() {
        this.settingsModal.style.display = 'none';
    }
    
    async saveSettings() {
        try {
            // Save settings to localStorage
            const settings = {
                autoSpeak: this.autoSpeakCheckbox.checked,
                autoPlayAudio: this.autoPlayAudioCheckbox.checked,
                voice: this.voiceSelect.value,
                theme: this.themeSelect.value
            };
            
            localStorage.setItem('aiSettings', JSON.stringify(settings));
            
            // Apply theme
            document.body.className = `theme-${settings.theme}`;
            
            this.closeSettings();
            
            // Show success message
            this.addMessage('Settings saved successfully!', 'system');
            
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }
    
    async loadVoices() {
        try {
            const response = await fetch('/api/voices');
            const data = await response.json();
            
            this.voices = data.voices;
            this.voiceSelect.innerHTML = '<option value="">Default Voice</option>';
            
            Object.entries(this.voices).forEach(([id, voice]) => {
                const option = document.createElement('option');
                option.value = voice.id;
                option.textContent = voice.name;
                this.voiceSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading voices:', error);
        }
    }
    
    playAudio(audioPath) {
        const audio = new Audio(audioPath);
        audio.play().catch(error => {
            console.error('Error playing audio:', error);
        });
    }
    
    loadSettings() {
        const saved = localStorage.getItem('aiSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            this.autoSpeakCheckbox.checked = settings.autoSpeak;
            this.autoPlayAudioCheckbox.checked = settings.autoPlayAudio;
            this.voiceSelect.value = settings.voice || '';
            this.themeSelect.value = settings.theme || 'dark';
            
            // Apply theme
            document.body.className = `theme-${settings.theme}`;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new MultimodalAI();
    app.loadSettings();
});