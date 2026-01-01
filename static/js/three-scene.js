// Three.js Background Scene
class ThreeScene {
    constructor() {
        this.canvas = document.getElementById('bg-canvas');
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = null;
        this.geometries = [];
        this.animationId = null;
    }

    init() {
        // Check if THREE is available
        if (typeof THREE === 'undefined') {
            console.warn('⚠️  THREE.js not loaded, skipping 3D background');
            return;
        }

        try {
            this.setupScene();
            this.createParticles();
            this.createGeometries();
            this.addLights();
            this.animate();
            this.handleResize();
            console.log('✨ Three.js scene initialized successfully');
        } catch (error) {
            console.error('Error initializing Three.js:', error);
        }
    }

    setupScene() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x0a0a0f, 0.0008);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.z = 50;

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    }

    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        const colors = [];

        const particleCount = CONFIG.three.particleCount;

        // Create particles
        for (let i = 0; i < particleCount; i++) {
            // Random position
            const x = (Math.random() - 0.5) * 200;
            const y = (Math.random() - 0.5) * 200;
            const z = (Math.random() - 0.5) * 200;
            positions.push(x, y, z);

            // Color gradient from purple to blue
            const colorMix = Math.random();
            const color = new THREE.Color();
            color.setRGB(
                0.4 + colorMix * 0.2,  // R
                0.5 + colorMix * 0.2,  // G
                0.9                     // B
            );
            colors.push(color.r, color.g, color.b);
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

        // Material
        const material = new THREE.PointsMaterial({
            size: CONFIG.three.particleSize,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });

        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    createGeometries() {
        // Create floating geometric shapes
        const geometryConfigs = [
            { type: 'torus', color: 0x667eea, position: [30, 0, -10] },
            { type: 'torusKnot', color: 0x764ba2, position: [-30, 20, -20] },
            { type: 'octahedron', color: 0x00f2fe, position: [0, -30, -15] }
        ];

        geometryConfigs.forEach(config => {
            let geometry;
            switch (config.type) {
                case 'torus':
                    geometry = new THREE.TorusGeometry(5, 2, 16, 100);
                    break;
                case 'torusKnot':
                    geometry = new THREE.TorusKnotGeometry(5, 1.5, 100, 16);
                    break;
                case 'octahedron':
                    geometry = new THREE.OctahedronGeometry(6);
                    break;
            }

            const material = new THREE.MeshPhongMaterial({
                color: config.color,
                wireframe: true,
                transparent: true,
                opacity: 0.3
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(...config.position);
            this.geometries.push(mesh);
            this.scene.add(mesh);
        });
    }

    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        // Point lights
        const pointLight1 = new THREE.PointLight(0x667eea, 1, 100);
        pointLight1.position.set(50, 50, 50);
        this.scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x00f2fe, 1, 100);
        pointLight2.position.set(-50, -50, 50);
        this.scene.add(pointLight2);
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        const time = Date.now() * CONFIG.three.particleSpeed;

        // Rotate particles
        if (this.particles) {
            this.particles.rotation.y = time * 0.5;
            this.particles.rotation.x = time * 0.3;
        }

        // Rotate geometries
        this.geometries.forEach((mesh, index) => {
            mesh.rotation.x += 0.002 * (index + 1);
            mesh.rotation.y += 0.003 * (index + 1);

            // Floating motion
            mesh.position.y += Math.sin(time * 2 + index) * 0.02;
        });

        // Render
        this.renderer.render(this.scene, this.camera);
    }

    handleResize() {
        window.addEventListener('resize', () => {
            // Update camera
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();

            // Update renderer
            this.renderer.setSize(window.innerWidth, window.innerHeight);
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        });
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        // Dispose geometries and materials
        this.scene.traverse((object) => {
            if (object.geometry) {
                object.geometry.dispose();
            }
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });

        this.renderer.dispose();
    }
}

// Export
window.ThreeScene = ThreeScene;
