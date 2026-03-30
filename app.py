import streamlit as st
import streamlit.components.v1 as components

# --- 1. CREDENTIALS & INFO ---
COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com"
VERSION = "2026.03 PRO"
SYSTEM_KEY = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- 2. SECURITY GATE ---
if 'active' not in st.session_state:
    st.session_state.active = False

if not st.session_state.active:
    st.markdown(f"<h1 style='text-align:center; color:#00209F;'>🇭🇹 {COMPANY}</h1>", unsafe_allow_html=True)
    st.subheader("Heavy Vehicle Simulation Interface")
    key = st.text_input("Enter Ignition Key:", type="password")
    if st.button("ENGAGE SYSTEM"):
        if key == SYSTEM_KEY:
            st.session_state.active = True
            st.rerun()
    st.stop()

# --- 3. THE 3D SIMULATION ENGINE ---
# This uses Three.js to handle 3D models and NumPy-style physics logic in JavaScript
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #111; font-family: 'Segoe UI', sans-serif; overflow: hidden; }}
        #dashboard {{ 
            position: absolute; bottom: 20px; left: 20px; right: 20px;
            display: flex; justify-content: space-between; align-items: flex-end;
            pointer-events: none;
        }}
        .gauge-box {{ background: rgba(0,0,0,0.8); border: 2px solid #00209F; padding: 15px; border-radius: 10px; color: white; }}
        .big-text {{ font-size: 40px; font-weight: bold; color: #00FF41; }}
        .warning {{ color: #D21034; font-weight: bold; animation: blink 1s infinite; }}
        @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div id="dashboard">
        <div class="gauge-box">
            <div style="font-size: 12px;">VELOCITY</div>
            <div class="big-text" id="speedText">00</div><span style="color:#00FF41"> MPH</span>
            <div style="margin-top:10px;">FUEL: <span id="fuelText">100</span>%</div>
        </div>
        <div style="text-align: center; color: white; text-shadow: 2px 2px #000;">
            <h2 style="margin:0;">{COMPANY}</h2>
            <div>MISSION: FLORIDA → NEW YORK</div>
        </div>
        <div class="gauge-box" style="border-color: #D21034;">
            <div style="font-size: 12px;">LOAD STATUS</div>
            <div id="loadStatus" class="warning">UNATTACHED</div>
            <div style="margin-top:10px; font-size: 10px;">DRIVER: {OWNER}</div>
        </div>
    </div>

    <script>
        let scene, camera, renderer, truck, trailer, road;
        let velocity = 0, acceleration = 0.0005, friction = 0.985;
        let angle = 0, steerSpeed = 0;
        let fuel = 100, attached = false;
        let keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x050505);
            scene.fog = new THREE.Fog(0x050505, 50, 250);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 0.1, 1000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Lighting (High Contrast for Pro Look)
            const sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(50, 100, 50);
            scene.add(sun);
            scene.add(new THREE.AmbientLight(0xffffff, 0.3));

            // Infinite Highway
            const roadGeo = new THREE.PlaneGeometry(60, 10000);
            const roadMat = new THREE.MeshPhongMaterial({{ color: 0x151515 }});
            road = new THREE.Mesh(roadGeo, roadMat);
            road.rotation.x = -Math.PI / 2;
            scene.add(road);

            // THE TRUCK (Blue High-Detail Rig)
            truck = new THREE.Group();
            
            // Chassis
            const body = new THREE.Mesh(new THREE.BoxGeometry(3, 2, 6), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            body.position.y = 1.5;
            truck.add(body);

            // Cab (Upper)
            const cab = new THREE.Mesh(new THREE.BoxGeometry(2.8, 2, 2.5), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            cab.position.set(0, 3, 1.5);
            truck.add(cab);

            // Chrome Pipes
            const pipeGeo = new THREE.CylinderGeometry(0.15, 0.15, 5);
            const chrome = new THREE.MeshPhongMaterial({{color: 0xaaaaaa, shininess: 100}});
            const p1 = new THREE.Mesh(pipeGeo, chrome); p1.position.set(1.3, 3, -0.5);
            const p2 = new THREE.Mesh(pipeGeo, chrome); p2.position.set(-1.3, 3, -0.5);
            truck.add(p1); truck.add(p2);

            scene.add(truck);

            // THE LOAD (Red Trailer)
            trailer = new THREE.Mesh(new THREE.BoxGeometry(3.2, 4.5, 18), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.25, -30);
            scene.add(trailer);

            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);

            // Realistic "Heavy" Physics Logic
            if (keys['KeyW'] || keys['ArrowUp']) {{
                if (fuel > 0) velocity += acceleration;
                fuel -= 0.005;
            }}
            if (keys['KeyS'] || keys['ArrowDown']) velocity -= acceleration * 1.5;
            if (keys['Enter']) velocity *= 0.94; // Air Brakes

            // Steering Sensitivity based on Speed
            if (Math.abs(velocity) > 0.001) {{
                let turnFactor = 0.02 / (1 + velocity * 5); // Faster = Harder to turn
                if (keys['KeyA'] || keys['ArrowLeft']) angle += turnFactor;
                if (keys['KeyD'] || keys['ArrowRight']) angle -= turnFactor;
            }}

            velocity *= friction;
            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * velocity * 100;
            truck.position.z += Math.cos(angle) * velocity * 100;

            // Load Coupling Logic
            let dist = truck.position.distanceTo(trailer.position);
            if (dist < 10 && !attached && Math.abs(velocity) < 0.05) {{
                attached = true;
                document.getElementById('loadStatus').innerText = "LOCKED";
                document.getElementById('loadStatus').className = "";
                document.getElementById('loadStatus').style.color = "#00FF41";
            }}
            if (attached) {{
                trailer.position.copy(truck.position);
                trailer.rotation.copy(truck.rotation);
                trailer.translateZ(-13);
            }}

            // Camera Following (Professional View)
            let camDist = 30 + (velocity * 50); // Camera pulls back at high speed
            camera.position.x = truck.position.x - Math.sin(angle) * camDist;
            camera.position.z = truck.position.z - Math.cos(angle) * camDist;
            camera.position.y = 12;
            camera.lookAt(truck.position.x, 3, truck.position.z);

            // Update Dashboard
            document.getElementById('speedText').innerText = Math.round(Math.abs(velocity * 800));
            document.getElementById('fuelText').innerText = Math.max(0, Math.floor(fuel));

            renderer.render(scene, camera);
        }}
        init();
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)

# --- 4. GITHUB DEPLOYMENT FILES ---
st.sidebar.header("📂 Deployment Files")
st.sidebar.info("To put this on GitHub/Streamlit Cloud, you need these 2 files:")

st.sidebar.code("""
# requirements.txt
streamlit
""", language="text")

st.sidebar.code(f"""
# README.md
# {COMPANY}
Project Lead: {OWNER}
Simulation: Big Truck v{VERSION}
""", language="markdown")
