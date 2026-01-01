// Camera Module with MediaPipe Integration
class CameraModule {
    constructor() {
        this.video = document.getElementById('camera-video');
        this.canvas = document.getElementById('ar-overlay');
        this.ctx = this.canvas.getContext('2d');
        this.placeholder = document.getElementById('camera-placeholder');
        this.captureFlash = document.getElementById('capture-flash');

        this.stream = null;
        this.isActive = false;
        this.arEnabled = true;
        this.capturedImage = null;

        // MediaPipe
        this.hands = null;
        this.faceMesh = null;
        this.arHUD = null; // AR Renderer

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Camera toggle button
        document.getElementById('btn-camera-toggle').addEventListener('click', () => {
            this.toggle();
        });

        // AR toggle button
        document.getElementById('toggle-ar').addEventListener('click', () => {
            this.arEnabled = !this.arEnabled;
            const btn = document.getElementById('toggle-ar');
            btn.style.opacity = this.arEnabled ? '1' : '0.5';
        });

        // Capture button
        document.getElementById('btn-capture').addEventListener('click', () => {
            this.capture();
        });

        // Placeholder click
        this.placeholder.addEventListener('click', () => {
            if (!this.isActive) {
                this.start();
            }
        });
    }

    async start() {
        try {
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: CONFIG.camera.width,
                    height: CONFIG.camera.height,
                    frameRate: CONFIG.camera.fps
                },
                audio: false
            });

            this.video.srcObject = this.stream;
            this.video.play();

            // Hide placeholder
            this.placeholder.style.display = 'none';
            this.isActive = true;

            // Update button
            const btn = document.getElementById('btn-camera-toggle');
            btn.querySelector('span').textContent = '⏸️';
            btn.classList.add('active');

            // Update status indicator
            const cameraStatus = document.getElementById('camera-status');
            cameraStatus.classList.add('active');

            // Setup canvas size
            this.video.addEventListener('loadedmetadata', () => {
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;

                // Initialize AR HUD Renderer
                if (window.ARHUDModule) {
                    console.log('🛡️ Creating AR HUD Renderer');
                    this.arHUD = new ARHUDModule(this.ctx, this.canvas);
                }
            });

            // Initialize MediaPipe
            await this.initMediaPipe();

            console.log('Camera started successfully');

        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('无法访问摄像头。请检查权限设置。');
        }
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        this.video.srcObject = null;
        this.isActive = false;
        this.placeholder.style.display = 'flex';

        // Update button
        const btn = document.getElementById('btn-camera-toggle');
        btn.querySelector('span').textContent = '📹';
        btn.classList.remove('active');

        // Update status indicator
        const cameraStatus = document.getElementById('camera-status');
        cameraStatus.classList.remove('active');

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        console.log('Camera stopped');
    }

    toggle() {
        if (this.isActive) {
            this.stop();
        } else {
            this.start();
        }
    }

    async initMediaPipe() {
        try {
            // Wait for video to have proper dimensions
            await new Promise((resolve) => {
                const checkVideo = () => {
                    if (this.video.videoWidth > 0 && this.video.videoHeight > 0) {
                        resolve();
                    } else {
                        setTimeout(checkVideo, 100);
                    }
                };
                checkVideo();
            });

            console.log('Video ready, initializing MediaPipe...');
            console.log(`Video dimensions: ${this.video.videoWidth}x${this.video.videoHeight}`);

            // Initialize Hands
            if (typeof Hands !== 'undefined') {
                this.hands = new Hands({
                    locateFile: (file) => {
                        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
                    }
                });

                this.hands.setOptions({
                    maxNumHands: 2,
                    modelComplexity: 1,
                    minDetectionConfidence: 0.5,
                    minTrackingConfidence: 0.5
                });

                this.hands.onResults((results) => this.onHandsResults(results));
            }

            // Initialize FaceMesh
            if (typeof FaceMesh !== 'undefined') {
                this.faceMesh = new FaceMesh({
                    locateFile: (file) => {
                        return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
                    }
                });

                this.faceMesh.setOptions({
                    maxNumFaces: 1,
                    refineLandmarks: true,
                    minDetectionConfidence: 0.5,
                    minTrackingConfidence: 0.5
                });

                this.faceMesh.onResults((results) => this.onFaceMeshResults(results));
            }

            // Start processing frames
            this.processFrame();

            console.log('MediaPipe initialized successfully');

        } catch (error) {
            console.error('MediaPipe initialization error:', error);
            // Continue without MediaPipe - not critical for core functionality
        }
    }

    async processFrame() {
        if (!this.isActive) return;

        // Safety check: ensure video has dimensions
        if (this.video.videoWidth === 0 || this.video.videoHeight === 0) {
            requestAnimationFrame(() => this.processFrame());
            return;
        }

        try {
            if (this.arEnabled && this.hands) {
                await this.hands.send({ image: this.video });
            }

            if (this.arEnabled && this.faceMesh) {
                await this.faceMesh.send({ image: this.video });
            }
        } catch (error) {
            // Silently catch MediaPipe errors to prevent crashes
            console.warn('MediaPipe processing error (non-critical):', error.message);
        }

        requestAnimationFrame(() => this.processFrame());
    }

    onHandsResults(results) {
        if (!this.arEnabled) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            return;
        }

        this.ctx.save();
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        if (results.multiHandLandmarks) {
            for (const landmarks of results.multiHandLandmarks) {
                this.drawHand(landmarks);
            }
        }

        this.ctx.restore();
    }

    onFaceMeshResults(results) {
        if (!this.arEnabled) return;

        // Clear canvas if using native drawing here, but ARHUD handles clearing or drawing on top?
        // ARHUD.draw() clears? No, it looks like it draws on top.
        // Wait, ARHUD.onResults clears canvas in its own internal logic? 
        // No, current ARHUD.draw() does NOT clear. 
        // CameraModule clears in onHandsResults but not explicitly here if hands are off.

        // Ensure canvas is cleared if hands didn't clear it (if hands tracking is off or no hands)
        // If we want mixed AR (Hands + Face), we need shared clearing.
        // For now, let's assume Face AR is primary.

        if (this.arHUD && results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
            // Draw Iron Man HUD
            this.arHUD.draw(results.multiFaceLandmarks[0]);
        } else if (results.multiFaceLandmarks) {
            // Fallback
            for (const landmarks of results.multiFaceLandmarks) {
                this.drawFaceMesh(landmarks);
            }
        }
    }

    drawHand(landmarks) {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // Draw connections
        const connections = [
            [0, 1], [1, 2], [2, 3], [3, 4], // Thumb
            [0, 5], [5, 6], [6, 7], [7, 8], // Index
            [0, 9], [9, 10], [10, 11], [11, 12], // Middle
            [0, 13], [13, 14], [14, 15], [15, 16], // Ring
            [0, 17], [17, 18], [18, 19], [19, 20], // Pinky
            [5, 9], [9, 13], [13, 17] // Palm
        ];

        // Draw lines
        ctx.strokeStyle = '#00e5ff';
        ctx.lineWidth = 2;
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#00e5ff';

        for (const [start, end] of connections) {
            const startPoint = landmarks[start];
            const endPoint = landmarks[end];

            ctx.beginPath();
            ctx.moveTo(startPoint.x * w, startPoint.y * h);
            ctx.lineTo(endPoint.x * w, endPoint.y * h);
            ctx.stroke();
        }

        // Draw points
        ctx.fillStyle = '#00e5ff';
        for (const landmark of landmarks) {
            ctx.beginPath();
            ctx.arc(landmark.x * w, landmark.y * h, 4, 0, 2 * Math.PI);
            ctx.fill();
        }

        ctx.shadowBlur = 0;
    }

    drawFaceMesh(landmarks) {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // Draw a subset of face landmarks for performance
        ctx.fillStyle = '#00e5ff';
        ctx.shadowBlur = 5;
        ctx.shadowColor = '#00e5ff';

        // Draw key facial points
        const keyPoints = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
            397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127
        ];

        for (const idx of keyPoints) {
            if (landmarks[idx]) {
                const point = landmarks[idx];
                ctx.beginPath();
                ctx.arc(point.x * w, point.y * h, 2, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        ctx.shadowBlur = 0;
    }

    capture() {
        if (!this.isActive) {
            alert('请先启动摄像头');
            return null;
        }

        // Create a temporary canvas
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.video.videoWidth;
        tempCanvas.height = this.video.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');

        // Draw the current video frame
        tempCtx.drawImage(this.video, 0, 0);

        // Add AR overlay if enabled
        if (this.arEnabled) {
            tempCtx.drawImage(this.canvas, 0, 0);
        }

        // Convert to data URL
        this.capturedImage = tempCanvas.toDataURL('image/jpeg', 0.9);

        // Flash animation
        this.captureFlash.classList.add('active');
        setTimeout(() => {
            this.captureFlash.classList.remove('active');
        }, 300);

        console.log('Image captured');
        return this.capturedImage;
    }

    getCurrentFrame(includeAR = false) {
        // Get current video frame without flash animation
        if (!this.isActive) {
            return null;
        }

        // Create a temporary canvas
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.video.videoWidth;
        tempCanvas.height = this.video.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');

        // Draw the current video frame (clean)
        // Transform logic for mirroring if needed?
        // Note: The video input is raw. CSS mirrors it visually.
        // If we draw it to canvas, it will be raw (unmirrored).
        // If the user expects LLaVA to see what they "see" (mirrored), we might need to flip it.
        // But usually AI models expect standard orientation (left is left). 
        // Mirroring is for user self-view comfort.
        // So raw video is BETTER for AI (spatial reasoning: "on your left" means real left).
        // Let's keep it raw (unmirrored) for AI.

        tempCtx.drawImage(this.video, 0, 0);

        // Add AR overlay if enabled AND requested
        if (this.arEnabled && includeAR) {
            // AR overlay might be visually mirrored via CSS? 
            // In ar_hud.js, we draw based on landmarks.
            // If we composite it here, we need to match orientation.
            // But since we default includeAR=false for AI, this block won't run for AI.
            tempCtx.drawImage(this.canvas, 0, 0);
        }

        // Convert to data URL
        return tempCanvas.toDataURL('image/jpeg', 0.8);
    }

    getCapturedImage() {
        return this.capturedImage;
    }
}

// Export
window.CameraModule = CameraModule;
