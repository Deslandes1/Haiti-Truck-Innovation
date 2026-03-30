import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM SETTINGS ---
COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com"
VERSION = "2026.05 PRO"
SYSTEM_KEY = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- LOGIN GATE ---
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

# --- THE STURDY 3D ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #hud {{ position: absolute; bottom: 30px; left: 30px; background: rgba(0,0,0,0.85); padding: 25px; border-radius: 10px; border-left: 8px solid #D21034; color: white; pointer-events: none; min-width: 200px; }}
        .speed-val {{ font-size: 60px; color: #00FF41; line-height: 1; }}
        #start-overlay {{ 
            position: absolute; top:0; left:0; width:100%; height:100%; 
            background: rgba(0,0,0,0.8); display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 100; cursor: pointer;
        }}
        .hint {{ position: absolute; top: 20px; right: 20px; color: white; background: rgba(0,0,0,0.5); padding: 10px; font-size: 12px; }}
    </style>
</head>
<body>
    <div id="start-overlay" onclick="startSim();">
        <h1 style="color:#00209F">HAITI TRUCK INNOVATION</h1>
        <p>CLICK ANYWHERE TO SPAWN THE 18-WHEELER & START ENGINE</p>
    </div>

    <div class="hint">ARROWS/WASD: Drive | ENTER: Air Brakes | L: Headlights | T: Toggle Cam</div>

    <div id="hud">
        <div style="font-size: 14px; letter-spacing: 2px;">GROUND SPEED</div>
        <div class="speed-val" id="sp">00</div><span style="color:#00FF41">MPH</span>
        <div style="margin-top:20px; color:#D21034; font-size: 12px;">OPERATOR: {OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, trailer, road, grid, worldGroup;
        let speed = 0, angle = 0, keys = {{}}, attached = false, nightMode = false, camMode = 0;
        let audioCtx, oscillator, gainNode;

        function startSim() {{
            document.getElementById('start-overlay').style.display='none';
            initAudio();
            init();
        }}

        function initAudio() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();
            oscillator.type = 'sawtooth';
            oscillator.frequency.setValueAtTime(45, audioCtx.currentTime); 
            gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime);
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
        }}

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 150, 800);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 2000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Sunlight
            const ambient = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambient);
            const sun = new THREE.DirectionalLight(0xffffff, 1);
            sun.position.set(100, 200, 100);
            scene.add(sun);

            // --- THE LANDSCAPE ---
            worldGroup = new THREE.Group();
            
            // Grass Land
            const grass = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.MeshPhongMaterial({{color: 0x348C31}}));
            grass.rotation.x = -Math.PI / 2;
            worldGroup.add(grass);

            // Asphalt Road
            const roadGeo = new THREE.PlaneGeometry(50, 10000);
            const roadMat = new THREE.MeshPhongMaterial({{color: 0x1A1A1B}});
            road = new THREE.Mesh(roadGeo, roadMat);
            road.rotation.x = -Math.PI / 2;
            road.position.y = 0.1;
            worldGroup.add(road);

            // Road Lines
            for(let i=0; i<200; i++) {{
                const line = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 12), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                line.rotation.x = -Math.PI / 2;
                line.position.set(0, 0.15, -i * 50);
                worldGroup.add(line);
            }}

            // Scenery Activity
            for(let i=0; i<80; i++) {{
                const tree = new THREE.Mesh(new THREE.ConeGeometry(5, 15, 8), new THREE.MeshPhongMaterial({{color: 0x143306}}));
                tree.position.set(i % 2 === 0 ? 60 : -60, 7.5, -i * 90);
                worldGroup.add(tree);
            }}
            scene.add(worldGroup);

            // --- THE SEMI-TRUCK (Long Nose) ---
            truck = new THREE.Group();
            
            // Nose (Blue)
            const nose = new THREE.Mesh(new THREE.BoxGeometry(3.5, 3.2, 5), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            nose.position.set(0, 1.6, 6);
            truck.add(nose);

            // Sleeper Cab (Blue)
            const cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 4.5), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            cab.position.set(0, 2.75, 1.5);
            truck.add(cab);

            // Chrome Details
            const grill = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.5, 0.2), new THREE.MeshPhongMaterial({{color: 0xCCCCCC, shininess: 100}}));
            grill.position.set(0, 1.5, grill.getGeometry().parameters.depth / 2 + 8.5);
            truck.add(grill);

            const stackGeo = new THREE.CylinderGeometry(0.2, 0.2, 8);
            const chrome = new THREE.MeshPhongMaterial({{color: 0xEEEEEE, shininess: 150}});
            const s1 = new THREE.Mesh(stackGeo, chrome); s1.position.set(1.8, 5, 0.5);
            const s2 = new THREE.Mesh(stackGeo, chrome); s2.position.set(-1.8, 5, 0.5);
            truck.add(s1); truck.add(s2);

            // --- DUAL FLAGS (New!) ---
            const flagGeo = new THREE.PlaneGeometry(0.8, 0.5);
            
            // Haiti Flag (Blue/Red gradient is not simple, we approximate the shape)
            const htMat = new THREE.MeshPhongMaterial({{color: 0x00209F, emissive: 0xD21034, emissiveIntensity: 0.2}});
            const flagHT = new THREE.Mesh(flagGeo, htMat);
            flagHT.position.set(2.11, 3.5, 1.5); 
            flagHT.rotation.y = Math.PI / 2;
            truck.add(flagHT);
            
            // USA Flag (Star Spangled shape approximation)
            const usMat = new THREE.MeshPhongMaterial({{color: 0xffffff, emissive: 0xBF0A30, emissiveIntensity: 0.2}});
            const flagUS = new THREE.Mesh(flagGeo, usMat);
            flagUS.position.set(-2.11, 3.5, 1.5); 
            flagUS.rotation.y = -Math.PI / 2;
            truck.add(flagUS);

            scene.add(truck);

            // THE 53' TRAILER (Haiti Red)
            trailer = new THREE.Mesh(new THREE.BoxGeometry(4, 5.5, 26), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.75, -14);
            truck.add(trailer);

            animate();
        }}

        window.addEventListener('keydown', e => {{ keys[e.code] = true; }});
        window.addEventListener('keyup', e => {{ keys[e.code] = false; }});

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // Physics: Accelerate/Brake
            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0007; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.001;
            if (keys['Enter']) speed *= 0.94; // Air Brakes

            // Steering: Speed-dependent
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.008;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.008;
            }}

            speed *= 0.996; // Rolling Resistance
            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 75;
            truck.position.z += Math.cos(angle) * speed * 75;

            // Engine Sound Sync
            if(oscillator) {{
                let pitch = 40 + (Math.abs(speed) * 900);
                oscillator.frequency.setTargetAtTime(pitch, audioCtx.currentTime, 0.1);
            }}

            // Follow Camera
            camera.position.x = truck.position.x - Math.sin(angle) * 60;
            camera.position.z = truck.position.z - Math.cos(angle) * 60;
            camera.position.y = 22;
            camera.lookAt(truck.position.x, 5, truck.position.z);

            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 1600));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
