import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM SETTINGS ---
COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com"
VERSION = "2026.04"
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
        body {{ margin: 0; background: #050505; color: white; font-family: 'Arial Black', sans-serif; overflow: hidden; }}
        #hud {{ position: absolute; bottom: 40px; left: 40px; pointer-events: none; }}
        .speed-val {{ font-size: 70px; color: #00FF41; line-height: 1; }}
        #start-overlay {{ 
            position: absolute; top:0; left:0; width:100%; height:100%; 
            background: rgba(0,0,0,0.8); display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 100; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="start-overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#00209F">HAITI TRUCK INNOVATION</h1>
        <p>CLICK ANYWHERE TO SPAWN THE 18-WHEELER</p>
    </div>

    <div id="hud">
        <div style="font-size: 14px;">GROUND SPEED</div>
        <div class="speed-val" id="sp">00</div><span style="color:#00FF41">MPH</span>
        <div style="margin-top:20px; color:#D21034;">{COMPANY} | {OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, trailer, road;
        let speed = 0, angle = 0, keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.fog = new THREE.Fog(0x050505, 10, 300);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.5));
            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(10, 20, 10);
            scene.add(light);

            // Infinite Asphalt
            road = new THREE.Mesh(new THREE.PlaneGeometry(100, 20000), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            road.rotation.x = -Math.PI / 2;
            scene.add(road);

            // THE TRUCK (Blue High-Detail)
            truck = new THREE.Group();
            
            // Chassis
            const cab = new THREE.Mesh(new THREE.BoxGeometry(3.5, 4, 6), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            cab.position.y = 2;
            truck.add(cab);

            // Chrome Grill
            const grill = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.5, 0.5), new THREE.MeshPhongMaterial({{color: 0xaaaaaa, shininess: 100}}));
            grill.position.set(0, 1.5, 3);
            truck.add(grill);

            // Dual Exhaust Stacks
            const stackGeo = new THREE.CylinderGeometry(0.2, 0.2, 6);
            const chrome = new THREE.MeshPhongMaterial({{color: 0xcccccc, shininess: 120}});
            const s1 = new THREE.Mesh(stackGeo, chrome); s1.position.set(1.5, 4, -1);
            const s2 = new THREE.Mesh(stackGeo, chrome); s2.position.set(-1.5, 4, -1);
            truck.add(s1); truck.add(s2);

            scene.add(truck);

            // THE TRAILER (Red - Distance Spawn)
            trailer = new THREE.Mesh(new THREE.BoxGeometry(3.8, 5, 20), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.5, -40);
            scene.add(trailer);

            animate();
        }}

        window.addEventListener('keydown', e => {{ keys[e.code] = true; }});
        window.addEventListener('keyup', e => {{ keys[e.code] = false; }});

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // Physics: Accelerate/Brake
            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.001; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.002;
            if (keys['Enter']) speed *= 0.95; // Air Brakes

            // Steering: Speed-dependent
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.015;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.015;
            }}

            speed *= 0.993; // Friction
            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 40;
            truck.position.z += Math.cos(angle) * speed * 40;

            // Follow Camera (Console Style)
            camera.position.x = truck.position.x - Math.sin(angle) * 35;
            camera.position.z = truck.position.z - Math.cos(angle) * 35;
            camera.position.y = 12;
            camera.lookAt(truck.position.x, 3, truck.position.z);

            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 900));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)
