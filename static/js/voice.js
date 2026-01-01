// Voice Module with Audio Visualization
class VoiceModule {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.visualizer = document.getElementById('audio-visualizer');
        this.visualizerCtx = this.visualizer.getContext('2d');
        this.animationId = null;

        this.transcribedText = '';

        this.setupEventListeners();
        this.initSpeechRecognition();
    }

    setupEventListeners() {
        const voiceBtn = document.getElementById('btn-voice');
        voiceBtn.addEventListener('click', () => {
            this.toggle();
        });
    }

    initSpeechRecognition() {
        // Check for Web Speech API support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            // Enable continuous mode for "Always On" experience
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = CONFIG.voice.language;

            this.recognition.onstart = () => {
                console.log('🎤 Speech recognition started');
                this.isRecording = true;
                this.updateUI(true);
            };

            this.recognition.onresult = (event) => {
                let interimTranscript = '';

                // Keep track of the latest final result to avoid sending duplicates loops
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        const finalText = transcript.trim();
                        if (finalText) {
                            console.log('✅ Final result:', finalText);
                            this.transcribedText = finalText; // Store for fallback

                            // Send query immediately
                            const customEvent = new CustomEvent('voiceTranscribed', {
                                detail: { text: finalText }
                            });
                            console.log('🚀 Dispatching voiceTranscribed event');
                            document.dispatchEvent(customEvent);
                        }
                    } else {
                        interimTranscript += transcript;
                    }
                }

                if (interimTranscript) {
                    console.log('⏳ Interim transcript:', interimTranscript);
                }
            };

            this.recognition.onerror = (event) => {
                console.error('❌ Speech recognition error:', event.error);
                // Don't stop on no-speech, just keep listening
                if (event.error !== 'no-speech') {
                    // For other errors, we might need to restart or stop
                    if (event.error === 'aborted' || event.error === 'not-allowed') {
                        this.stop();
                    }
                }
            };

            this.recognition.onend = () => {
                console.log('🎤 Speech recognition ended');
                // Auto-restart if we are supposed to be recording
                if (this.isRecording) {
                    console.log('🔄 Auto-restarting speech recognition...');
                    // Add small delay to prevent rapid-fire restart loops if error occurred
                    setTimeout(() => {
                        if (this.isRecording) {
                            try {
                                this.recognition.start();
                            } catch (e) {
                                console.error("Failed to restart recognition:", e);
                                this.stop();
                            }
                        }
                    }, 300);
                } else {
                    this.stop();
                }
            };
        } else {
            console.warn('Web Speech API not supported');
        }
    }

    async start() {
        try {
            // Reset transcript
            this.transcribedText = '';

            // Start speech recognition
            if (this.recognition) {
                this.recognition.start();
            }

            // Start audio visualizer
            await this.startAudioVisualizer();

        } catch (error) {
            console.error('Error starting voice recording:', error);
            alert('无法访问麦克风。请检查权限设置。');
            this.stop();
        }
    }

    stop() {
        if (this.recognition) {
            this.recognition.stop();
        }

        this.stopAudioVisualizer();
        this.isRecording = false;
        this.updateUI(false);
    }

    toggle() {
        if (this.isRecording) {
            this.stop();
        } else {
            this.start();
        }
    }

    async startAudioVisualizer() {
        try {
            // Show visualizer container
            const container = document.getElementById('visualizer-container');
            if (container) {
                container.style.display = 'block';
            }

            // Get microphone stream
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;

            this.microphone = this.audioContext.createMediaStreamSource(stream);
            this.microphone.connect(this.analyser);

            // Start visualization
            this.visualize();

        } catch (error) {
            console.error('Error starting audio visualizer:', error);
        }
    }

    stopAudioVisualizer() {
        // Hide visualizer container
        const container = document.getElementById('visualizer-container');
        if (container) {
            container.style.display = 'none';
        }

        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }

        if (this.microphone) {
            this.microphone.disconnect();
            this.microphone = null;
        }

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }

        // Clear canvas
        this.visualizerCtx.clearRect(0, 0, this.visualizer.width, this.visualizer.height);
    }

    visualize() {
        if (!this.analyser) return;

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            this.animationId = requestAnimationFrame(draw);

            this.analyser.getByteFrequencyData(dataArray);

            const ctx = this.visualizerCtx;
            const width = this.visualizer.width;
            const height = this.visualizer.height;

            // Clear canvas
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.fillRect(0, 0, width, height);

            // Draw bars
            const barWidth = (width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                barHeight = (dataArray[i] / 255) * height * 0.8;

                // Gradient color based on frequency
                const hue = (i / bufferLength) * 200 + 200; // Blue to cyan
                ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;

                // Draw bar
                ctx.fillRect(x, height - barHeight, barWidth, barHeight);

                x += barWidth + 1;
            }
        };

        // Set canvas size
        this.visualizer.width = this.visualizer.offsetWidth;
        this.visualizer.height = this.visualizer.offsetHeight;

        draw();
    }

    updateUI(isActive) {
        const voiceBtn = document.getElementById('btn-voice');
        if (!voiceBtn) return;

        if (isActive) {
            voiceBtn.classList.add('active');
        } else {
            voiceBtn.classList.remove('active');
        }

        // Optional: Update text if element exists
        const voiceText = voiceBtn.querySelector('.voice-text');
        if (voiceText) {
            voiceText.textContent = isActive ? 'Listening...' : 'Click to speak';
        }
    }
}

// Export
window.VoiceModule = VoiceModule;
