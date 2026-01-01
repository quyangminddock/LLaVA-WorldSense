// AR HUD Module - Iron Man Style Interface Renderer
class ARHUDModule {
    constructor(canvasCtx, canvasElement) {
        this.canvasCtx = canvasCtx;
        this.canvasElement = canvasElement;

        // Animation state
        this.rotation = 0;
        this.pulse = 0;
        this.lastTime = 0;

        // Right eye landmark indices (approximate center and contour)
        // 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398
        this.rightEyeIndices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398];

        // Start animation loop for consistent rotation speed
        requestAnimationFrame(this.animate.bind(this));
    }

    animate(timestamp) {
        if (!this.lastTime) this.lastTime = timestamp;
        // Update animation parameters independently of frame rate
        this.rotation += 0.02;
        this.pulse += 0.1;

        requestAnimationFrame(this.animate.bind(this));
    }

    draw(landmarks) {
        if (!landmarks) return;

        const width = this.canvasElement.width;
        const height = this.canvasElement.height;

        // Calculate Right Eye Center
        let cx = 0, cy = 0;

        // Use iris landmark if available (index 473 for right iris)
        if (landmarks[473]) {
            cx = landmarks[473].x * width;
            cy = landmarks[473].y * height;
        } else {
            // Fallback: average of eye contour
            let sumX = 0, sumY = 0;
            this.rightEyeIndices.forEach(idx => {
                sumX += landmarks[idx].x;
                sumY += landmarks[idx].y;
            });
            cx = (sumX / this.rightEyeIndices.length) * width;
            cy = (sumY / this.rightEyeIndices.length) * height;
        }

        // Draw Iron Man Target Widget
        // Scale based on face size or screen size (simplified to screen size for now)
        const scale = Math.max(width, height) / 1920;

        this.drawSciFiCircle(cx, cy, 50 * scale);
        this.drawDataTicks(cx, cy, 90 * scale);

        // Draw Connecting Lines to edge - FIXED: only if coordinates valid
        this.canvasCtx.strokeStyle = 'rgba(0, 255, 255, 0.4)';
        this.canvasCtx.lineWidth = 2;
        this.canvasCtx.beginPath(); // Ensure new path
        // Use logic to detect which side is closer or just fixed direction
        // Mirroring issue: if canvas is mirrored, drawing logic needs to account for visual reversal?
        // Actually CSS transform scaleX(-1) mirrors the drawing too. 
        // So drawing at x=100 appears at x=width-100 visually.
        // User said: "Long thin line connected to screen outside". 
        // This usually happens when moving from (0,0) or undefined.

        if (cx > 0 && cy > 0) {
            this.canvasCtx.moveTo(cx + 80 * scale, cy);
            this.canvasCtx.lineTo(cx + 150 * scale, cy); // Short horizontal line instead of to edge
            this.canvasCtx.stroke();

            // Add a small data block at the end of line
            this.canvasCtx.fillStyle = 'rgba(0, 255, 255, 0.3)';
            this.canvasCtx.fillRect(cx + 152 * scale, cy - 5, 20 * scale, 10);
        }

        // Draw HUD Corner Elements
        this.drawCorners();
    }

    drawCorners() {
        const ctx = this.canvasCtx;
        const w = this.canvasElement.width;
        const h = this.canvasElement.height;
        const padding = 40;
        const len = 80;

        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 2;
        ctx.shadowColor = '#00ffff';
        ctx.shadowBlur = 10;

        // Top Left
        ctx.beginPath();
        ctx.moveTo(padding, padding + len);
        ctx.lineTo(padding, padding);
        ctx.lineTo(padding + len, padding);
        ctx.stroke();

        // Top Right
        ctx.beginPath();
        ctx.moveTo(w - padding - len, padding);
        ctx.lineTo(w - padding, padding);
        ctx.lineTo(w - padding, padding + len);
        ctx.stroke();

        // Bottom Left
        ctx.beginPath();
        ctx.moveTo(padding, h - padding - len);
        ctx.lineTo(padding, h - padding);
        ctx.lineTo(padding + len, h - padding);
        ctx.stroke();

        // Bottom Right
        ctx.beginPath();
        ctx.moveTo(w - padding - len, h - padding);
        ctx.lineTo(w - padding, h - padding);
        ctx.lineTo(w - padding, h - padding - len);
        ctx.stroke();

        ctx.shadowBlur = 0;
    }

    drawSciFiCircle(x, y, radius) {
        const ctx = this.canvasCtx;

        // Enhance Glow
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#00ffff';

        // Support Ring (Thicker)
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(this.rotation);

        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 4; // Thicker line
        ctx.setLineDash([15, 25, 10, 25]);
        ctx.beginPath();
        ctx.arc(0, 0, radius, 0, Math.PI * 2);
        ctx.stroke();

        // Counter-rotating Inner Ring
        ctx.rotate(-this.rotation * 2.5);
        ctx.strokeStyle = 'rgba(0, 255, 255, 0.8)';
        ctx.lineWidth = 2; // Slightly thicker
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.arc(0, 0, radius * 0.7, 0, Math.PI * 2);
        ctx.stroke();

        ctx.restore();

        // Center Core (Brighter Pulse)
        ctx.shadowBlur = 20;
        ctx.shadowColor = '#00ffff';
        ctx.fillStyle = `rgba(0, 255, 255, ${0.7 + Math.sin(this.pulse * 2) * 0.3})`;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();

        // Reset Shadow
        ctx.shadowBlur = 0;
    }

    drawDataTicks(x, y, radius) {
        const ctx = this.canvasCtx;
        ctx.strokeStyle = 'rgba(0, 255, 255, 0.8)'; // More opacity
        ctx.lineWidth = 3; // Thicker

        for (let i = 0; i < 8; i++) { // Fewer, bolder ticks
            const angle = (i / 8) * Math.PI * 2 + this.rotation * 0.5;
            const sx = x + Math.cos(angle) * (radius - 5);
            const sy = y + Math.sin(angle) * (radius - 5);
            const ex = x + Math.cos(angle) * (radius + 20);
            const ey = y + Math.sin(angle) * (radius + 20);

            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.lineTo(ex, ey);
            ctx.stroke();
        }
    }
}

// Export
window.ARHUDModule = ARHUDModule;
