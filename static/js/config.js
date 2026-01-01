// Configuration
const CONFIG = {
    api: {
        base: '',
        health: '/api/health',
        llavaQuery: '/api/llava/query',
        whisperTranscribe: '/api/whisper/transcribe',
        websocket: `ws://${window.location.host}/ws`
    },
    camera: {
        width: 1280,
        height: 720,
        fps: 30
    },
    voice: {
        language: 'en-US'  // Speech recognition language (zh-CN or en-US)
    },
    // Jarvis real-time settings
    jarvis: {
        // Continuous monitoring
        continuousVision: false,        // Enable by default?
        visionInterval: 3000,           // ms between frame analyses

        // Streaming response
        streamingEnabled: true,
        typingSpeed: 50,                // ms per character

        // TTS
        ttsEnabled: true,
        ttsVoice: 'en-US-GuyNeural',    // Edge TTS voice
        autoPlayAudio: true,

        // Frame sending
        frameInterval: 3000             // Send frames every 3s when monitoring
    }
};

window.CONFIG = CONFIG;
