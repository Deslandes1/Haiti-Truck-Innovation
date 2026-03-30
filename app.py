import streamlit as st
import streamlit.components.v1 as components

# --- OWNER DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck Innovation - Recovery", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #87CEEB; font-family: sans-serif; }}
        #ui-layer {{
            position: absolute; top: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 10;
        }}
        .hud-box {{
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.8); color: #00FF41; padding: 15px 40px;
            border-radius: 50px; border: 2px solid #D21034; pointer-events: auto;
            text-align: center;
        }}
        #start-gate {{
            position: absolute; width: 100%; height: 100%; background: #000;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer;
        }}
    </style>
</head>
<body>

    <div id="start-gate" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>SCREEN RECOVERY MODE: ACTIVE</p>
        <h2 style="background:#D21034; padding:10px 20px; border-radius:5px;">CLICK TO START ENGINE</h2>
    </div>

    <div id="ui-layer">
        <div class="hud-box">
            <small>{OWNER} | {COMPANY}</small><br>
            SPEED: <span id="speedo" style="font-size:30px; font-weight:bold;">0</span> MPH
        </div>
    </div>

    <script>
        let scene, camera, renderer, wheel, truck, roadSegments = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            // Audio setup
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let g = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(20, audioCtx.currentTime);
            g.gain.setValueAtTime(0.04, audioCtx.currentTime);
            osc.connect(g); g.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 10000);
            
            renderer = new THREE.WebGLRenderer({{ antialias: false }}); // Disabled antialias for speed
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 1));

            // --- THE TRUCK (Simplified to prevent lag) ---
            truck = new THREE.Group();
            let cab = new THREE.Mesh(new THREE.BoxGeometry(10, 10, 10), new THREE.MeshBasicMaterial({{color: 0x00209F}}));
            truck.add(cab);
            scene.add(truck);

            // --- THE WHEEL & HANDS ---
            wheel = new THREE.Group();
            let wMesh = new THREE.Mesh(new THREE.TorusGeometry(3, 0.4, 8, 24), new THREE.MeshBasicMaterial({{color: 0x111111}}));
            wheel.add(wMesh);
            
            // Two Hands
            let handMat = new THREE.MeshBasicMaterial({{color: 0x5c4033}});
            let LHand = new THREE.Mesh(new THREE.BoxGeometry(1.5, 3, 1), handMat);
            LHand.position.set(-3, 0, 0.5);
            let RHand = LHand.clone(); RHand.position.set(3, 0, 0.5);
            wheel.add(LHand); wheel.add(RHand);
            
            wheel.position.set(0, 7, -5);
            wheel.rotation.x = Math.PI/3;
            scene.add(wheel);

            // --- THE ROAD & LANDSCAPE ---
            for(let i=0; i<100; i++) {{
                let seg = new THREE.Group();
                // Grass
                let grass = new THREE.Mesh(new THREE.PlaneGeometry(1000, 200), new THREE.MeshBasicMaterial({{color: 0x3d7a33}}));
                grass.rotation.x = -Math.PI/2;
                seg.add(grass);
                // Road
                let road = new THREE.Mesh(new THREE.PlaneGeometry(120, 200), new THREE.MeshBasicMaterial({{color: 0x222222}}));
                road.rotation.x = -Math.PI/2;
                road.position.y = 0.05;
                seg.add(road);
                // Line
                let line = new THREE.Mesh(new THREE.PlaneGeometry(4, 50), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                line.rotation.x = -Math.PI/2;
                line.position.set(0, 0.1, 0);
                seg.add(line);

                seg.position.z = -i * 200;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            window.addEventListener('keydown', e => keys[e.code] = true);
            window.addEventListener('keyup', e => keys[e.code] = false);
            animate();
        }}

        function animate() {{
            requestAnimationFrame(animate);
            
            if (keys['ArrowUp']) speed += 0.0008;
            else speed *= 0.992;
            if (speed < 0) speed = 0;

            if (keys['ArrowLeft']) targetX -= 3;
            if (keys['ArrowRight']) targetX += 3;
            truckX += (targetX - truckX) * 0.1;

            wheel.rotation.z = (targetX - truckX) * -0.1;
            wheel.position.x = truckX;
            
            // Fixed Dashboard Camera
            camera.position.set(truckX, 10, 0);
            camera.lookAt(truckX, 8, -100);

            roadSegments.forEach(seg => {{
                seg.position.z += speed * 2000;
                if(seg.position.z > 400) seg.position.z -= 100 * 200;
            }});

            document.getElementById('speedo').innerText = Math.round(speed * 15000);
            if(osc) osc.frequency.setTargetAtTime(20 + (speed * 8000), audioCtx.currentTime, 0.1);
            
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
