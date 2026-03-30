import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Haiti Truck Innovation", layout="wide")

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { margin: 0; overflow: hidden; font-family: monospace; }
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
        #scoreDisplay {
            position: absolute;
            top: 20px;
            right: 20px;
            color: #ffcc44;
            background: rgba(0,0,0,0.7);
            padding: 12px;
            border-radius: 8px;
            z-index: 100;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div id="startScreen">
        <div class="flag">🇭🇹</div>
        <h1 style="color:#D21034;">Haiti Truck Innovation</h1>
        <p>HEAVY-DUTY SIMULATION ENGINE | IRON-CLAD CABIN</p>
        <button id="startBtn">START ENGINE</button>
    </div>
    <div id="info">
        🚛 DRIVER: Gesner Deslandes<br>
        SPEED: <span id="speed">0</span> km/h &nbsp;|&nbsp;
        GEAR: D
    </div>
    <div id="scoreDisplay">
        💎 RESOURCES: <span id="score">0</span>
    </div>
    <div id="controls">
        ↑ Accelerate &nbsp;&nbsp; ↓ Brake &nbsp;&nbsp; ← → Steer
    </div>

    <script>
        // ========================
        // 3D Driving Simulator with Cabin View and Resource Collection
        // ========================

        let scene, camera, renderer, cabin, wheel, roadGroup, roadSegments = [];
        let speed = 0, targetSpeed = 0, roadX = 0, targetRoadX = 0;
        let score = 0;
        let resources = [];
        let gameRunning = false;
        let leftPressed = false, rightPressed = false, accelPressed = false, brakePressed = false;

        const ROAD_WIDTH = 800;
        const GRASS_WIDTH = 25000;
        const SEGMENT_LENGTH = 1200;
        const NUM_SEGMENTS = 100;
        const MAX_SPEED = 45;
        const STEER_SPEED = 0.12;
        const ACCEL_RATE = 0.025;
        const BRAKE_RATE = 0.04;

        function randomRange(min, max) { return min + Math.random() * (max - min); }

        function createResource(x, z) {
            const geometry = new THREE.BoxGeometry(40, 40, 40);
            const material = new THREE.MeshPhongMaterial({ color: 0xffaa33, emissive: 0x442200 });
            const cube = new THREE.Mesh(geometry, material);
            cube.position.set(x, 20, z);
            return cube;
        }

        function addResourceToSegment(segment, zOffset) {
            const x = randomRange(-ROAD_WIDTH/2 + 100, ROAD_WIDTH/2 - 100);
            const resource = createResource(x, zOffset);
            segment.add(resource);
            resources.push({ obj: resource, segment: segment, x: x, z: zOffset });
        }

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a2f3f);
            scene.fog = new THREE.Fog(0x0a2f3f, 500, 20000);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 30000);
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            const ambientLight = new THREE.AmbientLight(0x404040);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 1);
            dirLight.position.set(100, 300, 100);
            scene.add(dirLight);
            const backLight = new THREE.DirectionalLight(0x88aaff, 0.5);
            backLight.position.set(-50, 150, -200);
            scene.add(backLight);

            // --- CABIN ---
            cabin = new THREE.Group();
            const darkMat = new THREE.MeshPhongMaterial({ color: 0x222222 });
            const chromeMat = new THREE.MeshPhongMaterial({ color: 0xaaaaaa, shininess: 60 });

            // Dashboard base
            const dashBase = new THREE.Mesh(new THREE.BoxGeometry(400, 50, 100), darkMat);
            dashBase.position.set(0, -35, -80);
            cabin.add(dashBase);

            // Dashboard top
            const dashTop = new THREE.Mesh(new THREE.BoxGeometry(420, 20, 30), darkMat);
            dashTop.position.set(0, -10, -90);
            cabin.add(dashTop);

            // Steering wheel
            wheel = new THREE.Group();
            const wheelRing = new THREE.Mesh(new THREE.TorusGeometry(22, 4, 32, 80), new THREE.MeshPhongMaterial({ color: 0x111111, roughness: 0.5 }));
            wheel.add(wheelRing);
            for (let i = 0; i < 3; i++) {
                const spoke = new THREE.Mesh(new THREE.BoxGeometry(40, 5, 5), chromeMat);
                spoke.rotation.z = (i * Math.PI * 2 / 3);
                wheel.add(spoke);
            }
            const centerCap = new THREE.Mesh(new THREE.SphereGeometry(6, 16, 16), chromeMat);
            wheel.add(centerCap);
            wheel.position.set(-60, 20, -100);
            wheel.rotation.x = 1.55;
            cabin.add(wheel);

            // Steering column
            const column = new THREE.Mesh(new THREE.CylinderGeometry(10, 12, 40, 8), darkMat);
            column.position.set(-60, -5, -105);
            column.rotation.x = 0.2;
            cabin.add(column);

            // Instruments (simple circles)
            const instMat = new THREE.MeshPhongMaterial({ color: 0x111111 });
            const speedo = new THREE.Mesh(new THREE.CylinderGeometry(30, 30, 5, 32), instMat);
            speedo.rotation.x = Math.PI/2;
            speedo.position.set(30, -15, -85);
            cabin.add(speedo);
            const tacho = new THREE.Mesh(new THREE.CylinderGeometry(30, 30, 5, 32), instMat);
            tacho.rotation.x = Math.PI/2;
            tacho.position.set(-30, -15, -85);
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

            // Windshield frame
            const frameMat = new THREE.MeshPhongMaterial({ color: 0x888888 });
            const topFrame = new THREE.Mesh(new THREE.BoxGeometry(400, 15, 20), frameMat);
            topFrame.position.set(0, 130, -40);
            cabin.add(topFrame);
            const leftFrame = new THREE.Mesh(new THREE.BoxGeometry(20, 150, 20), frameMat);
            leftFrame.position.set(-195, 70, -40);
            cabin.add(leftFrame);
            const rightFrame = leftFrame.clone();
            rightFrame.position.x = 195;
            cabin.add(rightFrame);

            scene.add(cabin);

            // --- ROAD ---
            roadGroup = new THREE.Group();
            scene.add(roadGroup);

            for (let i = 0; i < NUM_SEGMENTS; i++) {
                const segment = new THREE.Group();

                const grassMat = new THREE.MeshPhongMaterial({ color: 0x3c9e3c });
                const grass = new THREE.Mesh(new THREE.PlaneGeometry(GRASS_WIDTH, SEGMENT_LENGTH), grassMat);
                grass.rotation.x = -Math.PI / 2;
                segment.add(grass);

                const roadMat = new THREE.MeshPhongMaterial({ color: 0x2c2c2c });
                const road = new THREE.Mesh(new THREE.PlaneGeometry(ROAD_WIDTH, SEGMENT_LENGTH), roadMat);
                road.rotation.x = -Math.PI / 2;
                segment.add(road);

                const dashMat = new THREE.MeshPhongMaterial({ color: 0xffdd88 });
                for (let j = -SEGMENT_LENGTH/2 + 100; j < SEGMENT_LENGTH/2; j += 200) {
                    const mark = new THREE.Mesh(new THREE.BoxGeometry(20, 20, 30), dashMat);
                    mark.position.set(0, 5, j);
                    road.add(mark);
                }

                if (i % 8 === 0) {
                    const side = (i % 16 === 0) ? 1400 : -1400;
                    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(30, 40, 100, 6), new THREE.MeshPhongMaterial({ color: 0x8B5A2B }));
                    trunk.position.set(side, 50, 0);
                    segment.add(trunk);
                    const top = new THREE.Mesh(new THREE.ConeGeometry(50, 120, 8), new THREE.MeshPhongMaterial({ color: 0x2c8c2c }));
                    top.position.set(side, 110, 0);
                    segment.add(top);
                }

                if (i % 20 === 0 && i !== 0) {
                    const signBase = new THREE.Mesh(new THREE.BoxGeometry(80, 200, 20), new THREE.MeshPhongMaterial({ color: 0xD21034 }));
                    signBase.position.set(1200, 100, 0);
                    segment.add(signBase);
                    const signBoardMat = new THREE.MeshPhongMaterial({ color: 0xffdd99 });
                    const signBoard = new THREE.Mesh(new THREE.BoxGeometry(150, 80, 5), signBoardMat);
                    signBoard.position.set(1200, 180, 5);
                    segment.add(signBoard);
                }

                segment.position.z = -i * SEGMENT_LENGTH;
                roadGroup.add(segment);
                roadSegments.push(segment);
            }

            // Spawn initial resources
            for (let i = 0; i < 12; i++) {
                const segIndex = Math.floor(Math.random() * NUM_SEGMENTS);
                const segment = roadSegments[segIndex];
                const zOffset = randomRange(-SEGMENT_LENGTH/2 + 100, SEGMENT_LENGTH/2 - 100);
                addResourceToSegment(segment, zOffset);
            }

            // Controls
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
        }

        function update() {
            if (!gameRunning) return;

            if (accelPressed) targetSpeed = Math.min(targetSpeed + ACCEL_RATE, MAX_SPEED);
            else if (brakePressed) targetSpeed = Math.max(targetSpeed - BRAKE_RATE, 0);
            else targetSpeed *= 0.995;
            speed = targetSpeed;

            let steer = 0;
            if (leftPressed) steer = -STEER_SPEED;
            if (rightPressed) steer = STEER_SPEED;
            targetRoadX += steer * speed * 0.2;
            targetRoadX = Math.max(Math.min(targetRoadX, 450), -450);
            roadX += (targetRoadX - roadX) * 0.08;

            const move = speed * 0.6;
            for (let seg of roadSegments) {
                seg.position.z += move;
                if (seg.position.z > 3000) {
                    seg.position.z -= NUM_SEGMENTS * SEGMENT_LENGTH;
                }
            }

            roadGroup.position.x = roadX;
            if (wheel) wheel.rotation.z = -roadX * 0.004;

            camera.position.set(-60, 80, 150);
            camera.lookAt(-60, 50, -500);
            cabin.position.copy(camera.position);
            cabin.rotation.copy(camera.rotation);
            cabin.translateZ(-180);
            cabin.translateY(-60);

            // Resource collection
            const camPos = camera.position;
            for (let i = 0; i < resources.length; i++) {
                const r = resources[i];
                const worldPos = r.obj.getWorldPosition(new THREE.Vector3());
                const dx = worldPos.x - camPos.x;
                const dz = worldPos.z - camPos.z;
                if (Math.abs(dx) < 100 && dz > -150 && dz < 50) {
                    r.obj.parent.remove(r.obj);
                    resources.splice(i,1);
                    score++;
                    document.getElementById('score').innerText = score;
                    const segIndex = Math.floor(Math.random() * NUM_SEGMENTS);
                    const segment = roadSegments[segIndex];
                    const zOffset = randomRange(-SEGMENT_LENGTH/2 + 100, SEGMENT_LENGTH/2 - 100);
                    addResourceToSegment(segment, zOffset);
                    i--;
                }
            }

            document.getElementById('speed').innerText = Math.floor(speed * 3.6);
        }

        function startGame() {
            gameRunning = true;
            targetSpeed = 0;
            speed = 0;
            score = 0;
            document.getElementById('score').innerText = "0";
            for (let r of resources) if (r.obj.parent) r.obj.parent.remove(r.obj);
            resources = [];
            for (let i = 0; i < 12; i++) {
                const segIndex = Math.floor(Math.random() * NUM_SEGMENTS);
                const segment = roadSegments[segIndex];
                const zOffset = randomRange(-SEGMENT_LENGTH/2 + 100, SEGMENT_LENGTH/2 - 100);
                addResourceToSegment(segment, zOffset);
            }
            targetRoadX = 0;
            roadX = 0;
        }

        function animate() {
            requestAnimationFrame(animate);
            if (gameRunning) update();
            renderer.render(scene, camera);
        }

        const startBtn = document.getElementById('startBtn');
        const startScreen = document.getElementById('startScreen');
        startBtn.onclick = () => {
            startScreen.style.display = 'none';
            init();
            startGame();
            animate();
        };
    </script>
</body>
</html>
"""

components.html(html_code, height=700)
