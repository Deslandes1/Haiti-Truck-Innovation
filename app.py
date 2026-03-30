import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="GlobalInternet.py - Heavy-Duty Simulation", layout="wide")

sim_html = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { margin: 0; overflow: hidden; font-family: 'Courier New', monospace; }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #00ff41;
            background: rgba(0,0,0,0.7);
            padding: 12px;
            border-radius: 8px;
            z-index: 100;
            pointer-events: none;
            font-size: 14px;
        }
        #controls {
            position: absolute;
            bottom: 20px;
            left: 20px;
            color: #00ff41;
            background: rgba(0,0,0,0.7);
            padding: 12px;
            border-radius: 8px;
            z-index: 100;
            font-family: monospace;
            font-size: 12px;
        }
        #startScreen {
            position: absolute;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            color: white;
            z-index: 200;
            cursor: pointer;
            font-family: sans-serif;
        }
        .flag { font-size: 4rem; margin-bottom: 1rem; }
        button {
            background: #00209F;
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1.2rem;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
            transition: 0.2s;
        }
        button:hover { background: #D21034; transform: scale(1.05); }
        #resources {
            position: absolute;
            top: 20px;
            right: 20px;
            color: #ffcc44;
            background: rgba(0,0,0,0.7);
            padding: 12px;
            border-radius: 8px;
            z-index: 100;
            font-family: monospace;
            text-align: right;
        }
    </style>
</head>
<body>
    <div id="startScreen">
        <div class="flag">🇭🇹</div>
        <h1 style="color:#D21034;">GlobalInternet.py</h1>
        <p>HEAVY-DUTY SIMULATION ENGINE | IRON-CLAD CABIN</p>
        <button id="startBtn">START ENGINE</button>
    </div>
    <div id="info">
        🚛 DRIVER: Gesner Deslandes<br>
        SPEED: <span id="speed">0</span> km/h &nbsp;|&nbsp;
        GEAR: D
    </div>
    <div id="resources">
        💎 RESOURCES COLLECTED: <span id="score">0</span>
    </div>
    <div id="controls">
        ↑ Accelerate &nbsp;&nbsp; ↓ Brake &nbsp;&nbsp; ← → Steer
    </div>

    <script>
        // ========================
        // 3D Driving Simulator (Cabin View) with Resource Collection
        // ========================

        let scene, camera, renderer, cabin, wheel, roadGroup, roadSegments = [];
        let speed = 0, targetSpeed = 0, roadX = 0, targetRoadX = 0;
        let score = 0;
        let resources = [];      // resources placed on the road
        let resourceSpawnTimer = 0;
        let gameRunning = false;
        let animId = null;

        // Controls
        let leftPressed = false, rightPressed = false, accelPressed = false, brakePressed = false;

        // Constants
        const ROAD_WIDTH = 800;
        const GRASS_WIDTH = 25000;
        const SEGMENT_LENGTH = 1200;
        const NUM_SEGMENTS = 100;
        const MAX_SPEED = 45;
        const STEER_SPEED = 0.12;
        const ACCEL_RATE = 0.025;
        const BRAKE_RATE = 0.04;

        // Helper: random range
        function randomRange(min, max) { return min + Math.random() * (max - min); }

        // Create a resource (a glowing gold cube)
        function createResource(x, z) {
            const group = new THREE.Group();
            const geometry = new THREE.BoxGeometry(40, 40, 40);
            const material = new THREE.MeshPhongMaterial({ color: 0xffaa33, emissive: 0x442200 });
            const cube = new THREE.Mesh(geometry, material);
            group.add(cube);
            // Add a small glow effect using a point light? Not necessary.
            group.position.set(x, 20, z);
            return group;
        }

        // Add resource to the road segment
        function addResourceToSegment(segment, zOffset) {
            const x = randomRange(-ROAD_WIDTH/2 + 100, ROAD_WIDTH/2 - 100);
            const resource = createResource(x, zOffset);
            segment.add(resource);
            resources.push({ obj: resource, x: x, z: zOffset });
        }

        function init() {
            // --- 3D Setup ---
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a2f3f);
            scene.fog = new THREE.Fog(0x0a2f3f, 500, 20000);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 30000);
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Lights
            const ambientLight = new THREE.AmbientLight(0x404040);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 1);
            dirLight.position.set(100, 300, 100);
            scene.add(dirLight);
            const backLight = new THREE.DirectionalLight(0x88aaff, 0.5);
            backLight.position.set(-50, 150, -200);
            scene.add(backLight);

            // --- CABIN (driver's view) ---
            cabin = new THREE.Group();
            const darkMat = new THREE.MeshPhongMaterial({ color: 0x222222 });
            const redMat = new THREE.MeshPhongMaterial({ color: 0xD21034 });
            const blueMat = new THREE.MeshPhongMaterial({ color: 0x00209F });

            // Dashboard
            const dash = new THREE.Mesh(new THREE.BoxGeometry(400, 50, 100), darkMat);
            dash.position.set(0, -35, -80);
            cabin.add(dash);

            // Steering wheel
            wheel = new THREE.Group();
            const wheelRing = new THREE.Mesh(new THREE.TorusGeometry(22, 4, 32, 80), new THREE.MeshPhongMaterial({ color: 0x111111, roughness: 0.5 }));
            wheel.add(wheelRing);
            // Spokes
            for (let i = 0; i < 3; i++) {
                const spoke = new THREE.Mesh(new THREE.BoxGeometry(40, 5, 5), new THREE.MeshPhongMaterial({ color: 0x888888 }));
                spoke.rotation.z = (i * Math.PI * 2 / 3);
                wheel.add(spoke);
            }
            // Center cap
            const cap = new THREE.Mesh(new THREE.SphereGeometry(6, 16, 16), new THREE.MeshPhongMaterial({ color: 0xCCCCCC }));
            wheel.add(cap);
            wheel.position.set(-60, 20, -100);
            wheel.rotation.x = 1.55;
            cabin.add(wheel);

            // Dashboard instruments
            const speedo = new THREE.Mesh(new THREE.BoxGeometry(50, 40, 10), new THREE.MeshPhongMaterial({ color: 0x111111 }));
            speedo.position.set(30, -20, -85);
            cabin.add(speedo);
            const tacho = new THREE.Mesh(new THREE.BoxGeometry(50, 40, 10), new THREE.MeshPhongMaterial({ color: 0x111111 }));
            tacho.position.set(-30, -20, -85);
            cabin.add(tacho);

            // Pillars
            const leftPillar = new THREE.Mesh(new THREE.BoxGeometry(15, 280, 15), darkMat);
            leftPillar.position.set(-200, 80, -60);
            leftPillar.rotation.z = 0.04;
            cabin.add(leftPillar);
            const rightPillar = leftPillar.clone();
            rightPillar.position.x = 200;
            rightPillar.rotation.z = -0.04;
            cabin.add(rightPillar);

            // Steering column
            const column = new THREE.Mesh(new THREE.CylinderGeometry(10, 12, 40, 8), darkMat);
            column.position.set(-60, -5, -105);
            column.rotation.x = 0.2;
            cabin.add(column);

            scene.add(cabin);

            // --- ROAD (moving world) ---
            roadGroup = new THREE.Group();
            scene.add(roadGroup);

            for (let i = 0; i < NUM_SEGMENTS; i++) {
                const segment = new THREE.Group();

                // Grass
                const grass = new THREE.Mesh(new THREE.PlaneGeometry(GRASS_WIDTH, SEGMENT_LENGTH), new THREE.MeshPhongMaterial({ color: 0x3c9e3c }));
                grass.rotation.x = -Math.PI / 2;
                segment.add(grass);

                // Road
                const roadMat = new THREE.MeshPhongMaterial({ color: 0x2c2c2c });
                const road = new THREE.Mesh(new THREE.PlaneGeometry(ROAD_WIDTH, SEGMENT_LENGTH), roadMat);
                road.rotation.x = -Math.PI / 2;
                segment.add(road);

                // Road markings (dashed line)
                const dashMat = new THREE.MeshPhongMaterial({ color: 0xffdd88 });
                for (let j = -SEGMENT_LENGTH/2 + 100; j < SEGMENT_LENGTH/2; j += 200) {
                    const mark = new THREE.Mesh(new THREE.BoxGeometry(20, 20, 30), dashMat);
                    mark.position.set(0, 5, j);
                    road.add(mark);
                }

                // Trees and signs
                if (i % 8 === 0) {
                    const side = (i % 16 === 0) ? 1400 : -1400;
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(30, 40, 100, 6), new THREE.MeshPhongMaterial({ color: 0x8B5A2B }));
                    trunk.position.set(side, 50, 0);
                    segment.add(trunk);
                    const top = new THREE.Mesh(new THREE.ConeGeometry(50, 120, 8), new THREE.MeshPhongMaterial({ color: 0x2c8c2c }));
                    top.position.set(side, 110, 0);
                    segment.add(top);
                }

                // Add a restaurant sign every 20 segments
                if (i % 20 === 0 && i !== 0) {
                    const signBase = new THREE.Mesh(new THREE.BoxGeometry(80, 200, 20), new THREE.MeshPhongMaterial({ color: 0xD21034 }));
                    signBase.position.set(1200, 100, 0);
                    segment.add(signBase);
                    const textCanvas = document.createElement('canvas');
                    textCanvas.width = 256;
                    textCanvas.height = 128;
                    const ctx2 = textCanvas.getContext('2d');
                    ctx2.fillStyle = '#FFFFFF';
                    ctx2.fillRect(0, 0, textCanvas.width, textCanvas.height);
                    ctx2.fillStyle = '#D21034';
                    ctx2.font = 'Bold 30px Arial';
                    ctx2.fillText("RESTAURANT", 20, 60);
                    const texture = new THREE.CanvasTexture(textCanvas);
                    const signBoard = new THREE.Mesh(new THREE.BoxGeometry(150, 80, 5), new THREE.MeshPhongMaterial({ map: texture }));
                    signBoard.position.set(1200, 180, 5);
                    segment.add(signBoard);
                }

                segment.position.z = -i * SEGMENT_LENGTH;
                roadGroup.add(segment);
                roadSegments.push(segment);
            }

            // Spawn initial resources
            for (let i = 0; i < 10; i++) {
                const segIndex = Math.floor(Math.random() * NUM_SEGMENTS);
                const segment = roadSegments[segIndex];
                const zOffset = randomRange(-SEGMENT_LENGTH/2 + 100, SEGMENT_LENGTH/2 - 100);
                addResourceToSegment(segment, zOffset);
            }

            // --- Controls ---
            window.addEventListener('keydown', (e) => {
                if (!gameRunning) return;
                if (e.key === 'ArrowUp') accelPressed = true;
                if (e.key === 'ArrowDown') brakePressed = true;
                if (e.key === 'ArrowLeft') leftPressed = true;
                if (e.key === 'ArrowRight') rightPressed = true;
            });
            window.addEventListener('keyup', (e) => {
                if (e.key === 'ArrowUp') accelPressed = false;
                if (e.key === 'ArrowDown') brakePressed = false;
                if (e.key === 'ArrowLeft') leftPressed = false;
                if (e.key === 'ArrowRight') rightPressed = false;
            });

            // Start animation
            animate();
        }

        function update() {
            if (!gameRunning) return;

            // Acceleration & braking
            if (accelPressed) targetSpeed = Math.min(targetSpeed + ACCEL_RATE, MAX_SPEED);
            else if (brakePressed) targetSpeed = Math.max(targetSpeed - BRAKE_RATE, 0);
            else targetSpeed *= 0.995;

            speed = targetSpeed;

            // Steering
            let steer = 0;
            if (leftPressed) steer = -STEER_SPEED;
            if (rightPressed) steer = STEER_SPEED;
            targetRoadX += steer * speed * 0.2;
            targetRoadX = Math.max(Math.min(targetRoadX, 450), -450);
            roadX += (targetRoadX - roadX) * 0.08;

            // Move road segments
            const move = speed * 0.6;
            for (let seg of roadSegments) {
                seg.position.z += move;
                if (seg.position.z > 3000) {
                    seg.position.z -= NUM_SEGMENTS * SEGMENT_LENGTH;
                    // Move resources that belong to this segment? They are attached to the segment, so they move with it.
                    // No need to update manually.
                }
            }

            // Steer the world
            roadGroup.position.x = roadX;

            // Steering wheel rotation
            if (wheel) wheel.rotation.z = -roadX * 0.004;

            // Camera (driver's view)
            camera.position.set(-60, 80, 150);
            camera.lookAt(-60, 50, -500);

            // Cabin follows camera (so it stays in view)
            cabin.position.copy(camera.position);
            cabin.rotation.copy(camera.rotation);
            cabin.translateZ(-180);
            cabin.translateY(-60);

            // Resource collection detection (simple distance check)
            // Since resources are in the world, we need to check the distance from the truck position.
            // The truck position is basically at camera position with some offset? Actually, the truck's location in world coordinates is (0,0,0)? 
            // Better: we define the truck's world position as (roadX, 0, something). But with moving world, it's simpler to check relative to camera.
            // For simplicity, we'll check distance from the camera's forward direction.
            // We'll iterate resources and see if they are within a certain area in front of the camera.
            const truckWorldPos = new THREE.Vector3(0, 0, 0); // not used
            // Since resources are children of roadSegments, their world position changes. We'll compute their world position and check if within collision box of truck.
            for (let i = 0; i < resources.length; i++) {
                const res = resources[i];
                const worldPos = res.obj.getWorldPosition(new THREE.Vector3());
                // The truck's approximate collision area is around (0, 0, -400 to -100) in world coordinates? Let's approximate.
                // The camera is at (-60, 80, 150) but the truck is in front of camera? Better to set a fixed collision zone.
                // Since the road moves relative to the truck, the truck's world position is effectively fixed? Actually, the world moves, so the truck's position in world coordinates is the negative of roadGroup.position. Let's compute truck world x = -roadX, truck world z = (some offset). We'll keep it simple: we assume the truck is at (0,0,0) in world space? No.
                // Instead, we'll check if the resource is within a bounding box in front of the camera.
                // The camera's forward vector is (0,0,-1) in camera local space. In world space, it's the direction camera is looking.
                // But this is getting complex. For a simpler approach, we'll check if the resource is within a certain distance from the road center at the truck's z position.
                // The truck's z position in world coordinates is not constant, but we can approximate using the road segment's z offset.
                // Since the road moves, the truck's world Z is actually the negative of the road's Z? Let's not overcomplicate: we'll use a simple distance check from the camera's position.
                const dx = worldPos.x;
                const dz = worldPos.z - camera.position.z;
                if (Math.abs(dx) < 100 && dz > -200 && dz < 50) {
                    // Collect resource
                    res.obj.parent.remove(res.obj);
                    resources.splice(i,1);
                    score++;
                    document.getElementById('score').innerText = score;
                    // Spawn a new resource somewhere else
                    const segIndex = Math.floor(Math.random() * NUM_SEGMENTS);
                    const segment = roadSegments[segIndex];
                    const zOffset = randomRange(-SEGMENT_LENGTH/2 + 100, SEGMENT_LENGTH/2 - 100);
                    addResourceToSegment(segment, zOffset);
                    i--; // adjust index
                }
            }

            // Update UI
            document.getElementById('speed').innerText = Math.floor(speed * 3.6); // convert to km/h
        }

        function startGame() {
            gameRunning = true;
            targetSpeed = 0;
            speed = 0;
            score = 0;
            document.getElementById('score').innerText = "0";
            // Reset resources (clear all)
            for (let r of resources) {
                r.obj.parent.remove(r.obj);
            }
            resources = [];
            // Spawn fresh resources
            for (let i = 0; i < 10; i++) {
                const segIndex = Math.floor(Math.random() * NUM_SEGMENTS);
                const segment = roadSegments[segIndex];
                const zOffset = randomRange(-SEGMENT_LENGTH/2 + 100, SEGMENT_LENGTH/2 - 100);
                addResourceToSegment(segment, zOffset);
            }
            targetRoadX = 0;
            roadX = 0;
            leftPressed = false; rightPressed = false; accelPressed = false; brakePressed = false;
        }

        function animate() {
            requestAnimationFrame(animate);
            if (gameRunning) {
                update();
            }
            renderer.render(scene, camera);
        }

        // Start after start screen
        const startBtn = document.getElementById('startBtn');
        const startScreen = document.getElementById('startScreen');
        startBtn.onclick = () => {
            startScreen.style.display = 'none';
            init();
            startGame();
        };
        // Initial static scene (optional)
    </script>
</body>
</html>
"""

components.html(sim_html, height=700)
