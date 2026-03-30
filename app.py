import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Haiti Truck - Iron Cabin", layout="wide")

sim_html = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body { margin: 0; overflow: hidden; font-family: sans-serif; }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            color: white;
            background: rgba(0,0,0,0.6);
            padding: 10px;
            border-radius: 8px;
            z-index: 100;
            pointer-events: none;
        }
        #controls {
            position: absolute;
            bottom: 20px;
            left: 20px;
            color: white;
            background: rgba(0,0,0,0.6);
            padding: 10px;
            border-radius: 8px;
            z-index: 100;
            font-family: monospace;
        }
        #start {
            position: absolute;
            width: 100%;
            height: 100%;
            background: #000;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 200;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; startGame();">
        <h1 style="color:#D21034;">🇭🇹 EduHumanity</h1>
        <p>IRON-CLAD CABIN LOCK | EXPRESSIVE SIGNS</p>
        <h2 style="background:#00209F; padding:10px 40px; border-radius:5px;">START ENGINE</h2>
    </div>
    <div id="info">
        <b>DRIVER: Gesner Deslandes</b><br>
        Speed: <span id="speed">0</span> mph
    </div>
    <div id="controls">
        ↑ Accelerate<br>
        ← → Steer
    </div>

    <script>
        let scene, camera, renderer, cabin, wheel, roadGroup, roadSegments = [];
        let speed = 0, roadX = 0, targetRoadX = 0;
        let animId = null;

        function startGame() {
            // --- 3D SETUP ---
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 500, 15000);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 20000);
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Lights
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 1);
            dirLight.position.set(100, 200, 100);
            scene.add(dirLight);

            // --- CABIN (driver's view) ---
            cabin = new THREE.Group();
            const darkMat = new THREE.MeshPhongMaterial({ color: 0x222222 });

            // Dashboard
            const dash = new THREE.Mesh(new THREE.BoxGeometry(400, 50, 100), darkMat);
            dash.position.set(0, -35, -80);
            cabin.add(dash);

            // Steering wheel
            wheel = new THREE.Group();
            const wheelRing = new THREE.Mesh(new THREE.TorusGeometry(18, 3.5, 32, 64), new THREE.MeshPhongMaterial({ color: 0x111111 }));
            wheel.add(wheelRing);
            // Add spokes
            for (let i = 0; i < 3; i++) {
                const spoke = new THREE.Mesh(new THREE.BoxGeometry(25, 3, 3), new THREE.MeshPhongMaterial({ color: 0x888888 }));
                spoke.rotation.z = (i * Math.PI * 2 / 3);
                wheel.add(spoke);
            }
            wheel.position.set(-60, 20, -100);
            wheel.rotation.x = 1.55;
            cabin.add(wheel);

            // Pillars
            const leftPillar = new THREE.Mesh(new THREE.BoxGeometry(10, 250, 10), darkMat);
            leftPillar.position.set(-180, 80, -60);
            leftPillar.rotation.z = 0.04;
            cabin.add(leftPillar);
            const rightPillar = leftPillar.clone();
            rightPillar.position.x = 180;
            rightPillar.rotation.z = -0.04;
            cabin.add(rightPillar);

            scene.add(cabin);

            // --- ROAD (moving world) ---
            roadGroup = new THREE.Group();
            scene.add(roadGroup);

            const segmentLength = 1200;
            const numSegments = 100;
            const roadWidth = 800;
            const grassWidth = 25000;

            for (let i = 0; i < numSegments; i++) {
                const segment = new THREE.Group();

                // Grass
                const grass = new THREE.Mesh(new THREE.PlaneGeometry(grassWidth, segmentLength), new THREE.MeshPhongMaterial({ color: 0x3c9e3c }));
                grass.rotation.x = -Math.PI / 2;
                segment.add(grass);

                // Road
                const road = new THREE.Mesh(new THREE.PlaneGeometry(roadWidth, segmentLength), new THREE.MeshPhongMaterial({ color: 0x2c2c2c }));
                road.rotation.x = -Math.PI / 2;
                segment.add(road);

                // Add simple trees or signs
                if (i % 8 === 0) {
                    const side = (i % 16 === 0) ? 900 : -900;
                    const treeTrunk = new THREE.Mesh(new THREE.CylinderGeometry(20, 25, 60, 6), new THREE.MeshPhongMaterial({ color: 0x8B5A2B }));
                    treeTrunk.position.set(side, 30, 0);
                    segment.add(treeTrunk);
                    const treeTop = new THREE.Mesh(new THREE.ConeGeometry(35, 80, 8), new THREE.MeshPhongMaterial({ color: 0x2c8c2c }));
                    treeTop.position.set(side, 80, 0);
                    segment.add(treeTop);
                }

                segment.position.z = -i * segmentLength;
                roadGroup.add(segment);
                roadSegments.push(segment);
            }

            // --- Controls ---
            window.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowUp') speed = Math.min(speed + 0.02, 0.45);
                if (e.key === 'ArrowLeft') targetRoadX = Math.min(targetRoadX + 35, 350);
                if (e.key === 'ArrowRight') targetRoadX = Math.max(targetRoadX - 35, -350);
            });
            window.addEventListener('keyup', (e) => {
                if (e.key === 'ArrowUp') speed = Math.max(speed - 0.015, 0);
            });

            // Start animation loop
            animate();
        }

        function animate() {
            if (!scene) return;
            requestAnimationFrame(animate);

            // Physics
            speed *= 0.995;
            roadX += (targetRoadX - roadX) * 0.12;

            // Move road segments
            const move = speed * 25000;
            for (let seg of roadSegments) {
                seg.position.z += move;
                if (seg.position.z > 5000) seg.position.z -= roadSegments.length * 1200;
            }

            // Steer the world
            roadGroup.position.x = roadX;

            // Steering wheel visual
            if (wheel) wheel.rotation.z = -roadX * 0.006;

            // Camera position (driver's view)
            camera.position.set(-60, 70, 150);
            camera.lookAt(-60, 50, -1000);

            // Cabin must follow camera (so it stays in view)
            cabin.position.copy(camera.position);
            cabin.rotation.copy(camera.rotation);
            cabin.translateZ(-180);
            cabin.translateY(-60);

            // Update speed display
            const mph = Math.floor(speed * 1600);
            document.getElementById('speed').innerText = mph;

            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
