import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM CONFIG ---
COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com"
SYSTEM_KEY = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- LOGIN ---
if 'active' not in st.session_state:
    st.session_state.active = False

if not st.session_state.active:
    st.markdown(f"<h1 style='text-align:center; color:#00209F;'>🇭🇹 {COMPANY}</h1>", unsafe_allow_html=True)
    key = st.text_input("Enter Ignition Key:", type="password")
    if st.button("ENGAGE SYSTEM"):
        if key == SYSTEM_KEY:
            st.session_state.active = True
            st.rerun()
    st.stop()

# --- THE FULL 3D ENGINE WITH SOUND, LIGHTS, AND LANDSCAPE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #000; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #hud {{ position: absolute; bottom: 30px; left: 30px; background: rgba(0,0,0,0.8); padding: 20px; border-radius: 15px; border: 2px solid #D21034; color: white; pointer-events: none; }}
        .speed-val {{ font-size: 50px; color: #00FF41; }}
        #start-screen {{ position: absolute; width: 100%; height: 100%; background: #000; z-index: 100; display: flex; justify-content: center; align-items: center; cursor: pointer; text-align:center; }}
        .controls-hint {{ position: absolute; top: 20px; right: 20px; color: white; background: rgba(0,0,0,0.5); padding: 10px; font-size: 12px; }}
    </style>
</head>
<body>
    <div id="start-screen" onclick="startSim();">
        <h1 style="color:#00209F">HAITI TRUCK INNOVATION<br><span style="font-size:20px; color:white;">CLICK TO START ENGINE</span></h1>
    </div>

    <div class="controls-hint">ARROWS: Drive | ENTER: Air Brakes | L: Headlights Toggle</div>

    <div id="hud">
        <div style="font-size: 12px;">NIGHT OPS: <span id="lightStatus">OFF</span></div>
        <div class="speed-val" id="sp">00</div><span style="color:#00FF41"> MPH</span>
        <div style="margin-top:10px; font-size:10px;">OPERATOR: {OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, headlights = [], sun;
        let speed = 0, angle = 0, keys = {{}}, nightMode = false;
        let audioCtx, oscillator, gainNode;

        function startSim() {{
            document.getElementById('start-screen').style.display = 'none';
            initAudio();
            init();
        }}

        function initAudio() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();
            oscillator.type = 'sawtooth';
            oscillator.frequency.setValueAtTime(40, audioCtx.currentTime); 
            gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime);
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
        }}

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 100, 700);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 0.1, 2000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(100, 200, 100);
            scene.add(sun);
            scene.add(new THREE.AmbientLight(0xffffff, 0.3));

            // LANDSCAPE
            const grass = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
            grass.rotation.x = -Math.PI / 2;
            scene.add(grass);

            const roadGeo = new THREE.PlaneGeometry(45, 10000);
            const road = new THREE.Mesh(roadGeo, new THREE.MeshPhongMaterial({{color: 0x222222}}));
            road.rotation.x = -Math.PI / 2;
            road.position.y = 0.05;
            scene.add(road);

            // SCENERY
            for(let i=0; i<80; i++) {{
                let tree = new THREE.Group();
                let trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 6), new THREE.MeshPhongMaterial({{color:0x4d2926}}));
                let leaves = new THREE.Mesh(new THREE.ConeGeometry(5, 12, 8), new THREE.MeshPhongMaterial({{color:0x1b3d17}}));
                leaves.position.y = 6;
                tree.add(trunk); tree.add(leaves);
                tree.position.set(i % 2 === 0 ? 60 : -60, 3, -i * 80);
                scene.add(tree);
            }}

            // TRUCK MODEL
            truck = new THREE.Group();
            const nose = new THREE.Mesh(new THREE.BoxGeometry(3.2, 3, 5), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            nose.position.set(0, 1.5, 5.5);
            truck.add(nose);

            const cab = new THREE.Mesh(new THREE.BoxGeometry(3.8, 4.8, 4.5), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            cab.position.set(0, 2.4, 1);
            truck.add(cab);

            // HEADLIGHT OBJECTS (Physical Bulbs)
            const bulbGeo = new THREE.CircleGeometry(0.5, 16);
            const bulbMat = new THREE.MeshBasicMaterial({{color: 0xffffff}});
            const h1 = new THREE.Mesh(bulbGeo, bulbMat); h1.position.set(1.2, 1.2, 8.01);
            const h2 = new THREE.Mesh(bulbGeo, bulbMat); h2.position.set(-1.2, 1.2, 8.01);
            truck.add(h1); truck.add(h2);

            // SPOTLIGHTS (Actual Light Casting)
            const spot1 = new THREE.SpotLight(0xffffff, 0, 150, Math.PI/4, 0.5, 1);
            spot1.position.set(1.2, 1.2, 8);
            const target1 = new THREE.Object3D(); target1.position.set(1.2, 0, 50);
            truck.add(spot1); truck.add(target1); spot1.target = target1;
            headlights.push(spot1);

            const spot2 = new THREE.SpotLight(0xffffff, 0, 150, Math.PI/4, 0.5, 1);
            spot2.position.set(-1.2, 1.2, 8);
            const target2 = new THREE.Object3D(); target2.position.set(-1.2, 0, 50);
            truck.add(spot2); truck.add(target2); spot2.target = target2;
            headlights.push(spot2);

            // TRAILER
            const trailer = new THREE.Mesh(new THREE.BoxGeometry(3.8, 5.2, 26), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.6, -14);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => {{
            keys[e.code] = true;
            if(e.code === 'KeyL') toggleLights();
        }});
        window.addEventListener('keyup', e => keys[e.code] = false);

        function toggleLights() {{
            nightMode = !nightMode;
            scene.background.set(nightMode ? 0x000105 : 0x87CEEB);
            scene.fog.color.set(nightMode ? 0x000105 : 0x87CEEB);
            sun.intensity = nightMode ? 0.05 : 1.2;
            headlights.forEach(h => h.intensity = nightMode ? 5 : 0);
            document.getElementById('lightStatus').innerText = nightMode ? "ON (HIGH BEAM)" : "OFF";
        }}

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0006; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.001;
            if (keys['Enter']) speed *= 0.94;

            speed *= 0.996; 
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.008;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.008;
            }}

            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 80;
            truck.position.z += Math.cos(angle) * speed * 80;

            if(oscillator) {{
                let pitch = 35 + (Math.abs(speed) * 900);
                oscillator.frequency.setTargetAtTime(pitch, audioCtx.currentTime, 0.1);
            }}

            camera.position.x = truck.position.x - Math.sin(angle) * 55;
            camera.position.z = truck.position.z - Math.cos(angle) * 55;
            camera.position.y = 20;
            camera.lookAt(truck.position.x, 3, truck.position.z);

            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 1800));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)
