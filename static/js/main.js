// Main Application - Real-Time Jarvis System
class App {
    constructor() {
        this.threeScene = null;
        this.camera = null;
        this.voice = null;
        this.chat = null;
        this.ws = null;
        this.isInitialized = false;

        // Monitoring state
        this.isMonitoring = false;
        this.frameIntervalId = null;
        this.lastVisionUpdate = null;
    }

    async init() {
        try {
            console.log('🚀 Initializing Real-Time Jarvis WorldSense...');

            // Initialize modules
            this.threeScene = new ThreeScene();
            this.camera = new CameraModule();
            this.voice = new VoiceModule();
            this.chat = new ChatModule();

            // Start Three.js scene (non-critical)
            if (this.threeScene) {
                this.threeScene.init();
            }

            // Setup event listeners
            this.setupEventListeners();

            // Connect WebSocket
            await this.connectWebSocket();

            // Check API health
            await this.checkHealth();

            // Hide loading overlay
            this.hideLoading();

            this.isInitialized = true;
            console.log('✅ JARVIS WorldSense initialized successfully');

        } catch (error) {
            console.error('❌ Initialization error:', error);
            // Hide loading anyway to show the UI
            this.hideLoading();
        }
    }

    setupEventListeners() {
        // Send button
        document.getElementById('btn-send').addEventListener('click', () => {
            this.sendMessage();
        });

        // Text input - Enter to send
        const textInput = document.getElementById('text-input');
        textInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Monitoring toggle (optional button)
        const monitoringToggle = document.getElementById('btn-monitoring');
        if (monitoringToggle) {
            monitoringToggle.addEventListener('click', () => {
                this.toggleMonitoring();
            });
        }

        // Voice transcribed event
        document.addEventListener('voiceTranscribed', (e) => {
            console.log('📨 Voice transcribed event received:', e.detail.text);
            this.sendVoiceQuery(e.detail.text);
        });
    }

    async connectWebSocket() {
        try {
            this.ws = new WebSocket(CONFIG.api.websocket);

            this.ws.onopen = () => {
                console.log('✅ WebSocket connected');
                const aiStatus = document.getElementById('ai-status');
                aiStatus.classList.add('active');

                // Auto-start monitoring if configured
                if (CONFIG.jarvis.continuousVision) {
                    this.startMonitoring();
                }
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
            };

            this.ws.onclose = () => {
                console.log('❌ WebSocket disconnected');
                const aiStatus = document.getElementById('ai-status');
                aiStatus.classList.remove('active');

                // Stop monitoring
                this.stopMonitoring();

                // Attempt reconnection after 3 seconds
                setTimeout(() => {
                    if (this.isInitialized) {
                        console.log('🔄 Attempting to reconnect...');
                        this.connectWebSocket();
                    }
                }, 3000);
            };

        } catch (error) {
            console.error('❌ WebSocket connection error:', error);
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message:', data);

        switch (data.type) {
            case 'pong':
                // Heartbeat response
                break;

            case 'llava_start':
                // LLaVA processing started
                this.chat.startStreamingMessage();
                break;

            case 'response_chunk':
                // Streaming text chunk
                this.chat.appendToStreamingMessage(data.text);
                break;

            case 'response_complete':
                // Response finished with audio
                this.chat.finishStreamingMessage(data.audio_url);
                break;

            case 'vision_update':
                // Continuous monitoring update
                this.handleVisionUpdate(data);
                break;

            case 'monitoring_status':
                // Monitoring status changed
                console.log('👁️ Monitoring:', data.active);
                if (data.active) {
                    this.chat.addSystemMessage('🔍 Continuous vision monitoring active', 'info');
                } else {
                    this.chat.addSystemMessage('⏸️ Continuous vision monitoring stopped', 'info');
                }
                break;

            case 'error':
                // Error message
                this.chat.addSystemMessage(`❌ Error: ${data.message}`, 'error');
                break;
        }
    }

    handleVisionUpdate(data) {
        // Handle continuous vision monitoring update
        this.lastVisionUpdate = data.observation;

        // Update HUD with latest observation (optional)
        const visionStatus = document.getElementById('vision-status');
        if (visionStatus) {
            visionStatus.textContent = data.observation;
        }

        console.log('👁️ Vision Update:', data.observation);
    }

    async checkHealth() {
        try {
            const response = await fetch(CONFIG.api.base + CONFIG.api.health);
            const data = await response.json();
            console.log('Health check:', data);

            if (!data.llava_loaded) {
                console.warn('⚠️ LLaVA model not loaded');
                this.chat.addSystemMessage('⚠️ LLaVA model not loaded. Some features may be unavailable.', 'warning');
            }

        } catch (error) {
            console.error('❌ Health check failed:', error);
        }
    }

    startMonitoring() {
        // Start continuous vision monitoring
        if (this.isMonitoring || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        // Send start monitoring command
        this.ws.send(JSON.stringify({
            type: 'start_monitoring'
        }));

        this.isMonitoring = true;

        // Start sending frames periodically
        this.frameIntervalId = setInterval(() => {
            this.sendCameraFrame();
        }, CONFIG.jarvis.frameInterval);

        console.log('🔍 Monitoring started');
    }

    stopMonitoring() {
        // Stop continuous vision monitoring
        if (!this.isMonitoring) {
            return;
        }

        // Clear frame interval
        if (this.frameIntervalId) {
            clearInterval(this.frameIntervalId);
            this.frameIntervalId = null;
        }

        // Send stop monitoring command
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'stop_monitoring'
            }));
        }

        this.isMonitoring = false;
        console.log('⏸️ Monitoring stopped');
    }

    toggleMonitoring() {
        // Toggle continuous vision monitoring
        if (this.isMonitoring) {
            this.stopMonitoring();
        } else {
            this.startMonitoring();
        }
    }

    sendCameraFrame() {
        // Send current camera frame to server for monitoring
        if (!this.camera.isActive) {
            return;
        }

        const imageData = this.camera.getCurrentFrame();
        if (!imageData) {
            return;
        }

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'camera_frame',
                image: imageData
            }));
        }
    }

    async sendMessage() {
        const textInput = document.getElementById('text-input');
        const question = textInput.value.trim();

        if (!question) {
            return;
        }

        // Capture current frame
        const imageData = this.camera.getCapturedImage() || this.camera.getCurrentFrame();

        if (!imageData) {
            this.chat.addSystemMessage('⚠️ Please capture an image first or start camera', 'warning');
            return;
        }

        // Add user message to chat
        this.chat.addMessage(question, true);

        // Clear input
        textInput.value = '';

        // Send via WebSocket for streaming response
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'llava_query',
                image: imageData,
                question: question
            }));
        } else {
            this.chat.addSystemMessage('❌ WebSocket not connected. Please wait...', 'error');
        }
    }

    async sendVoiceQuery(text) {
        // Send voice-transcribed query
        console.log('🗣️ sendVoiceQuery called with text:', text);

        if (!text || !text.trim()) {
            console.warn('⚠️ Empty text, aborting');
            return;
        }

        // Capture current frame
        console.log('📷 Getting image data...');
        console.log('Camera active:', this.camera.isActive);
        const imageData = this.camera.getCapturedImage() || this.camera.getCurrentFrame();

        if (!imageData) {
            console.warn('⚠️ No image data available');
            this.chat.addSystemMessage('⚠️ Please capture an image first or start camera', 'warning');
            return;
        }

        console.log('✅ Image data obtained');

        // Add user message to chat
        this.chat.addMessage(text, true);

        // Send via WebSocket
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.log('📤 Sending voice query via WebSocket');
            this.ws.send(JSON.stringify({
                type: 'voice_query',
                image: imageData,
                text: text
            }));
            console.log('✅ Voice query sent');
        } else {
            console.error('❌ WebSocket not ready. State:', this.ws?.readyState);
            this.chat.addSystemMessage('❌ WebSocket not connected. Please wait...', 'error');
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');

        if (typeof gsap !== 'undefined') {
            gsap.to(loadingOverlay, {
                opacity: 0,
                duration: 0.5,
                onComplete: () => {
                    loadingOverlay.classList.add('hidden');
                }
            });
        } else {
            loadingOverlay.classList.add('hidden');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    window.app = app; // Make it global for debugging
    app.init();
});
