import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com | (509)-4738-5663"
PASSWORD_REQUIRED = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation 3D", layout="wide")

# --- LOGIN GATE ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"<h1 style='text-align:center; color:#00209F;'>🇭🇹 {COMPANY}</h1>", unsafe_allow_html=True)
    pwd = st.text_input("ENTER SYSTEM ACCESS KEY:", type="password")
    if st.button("IGNITION"):
        if pwd == PASSWORD_REQUIRED:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- THE 3D ENGINE (THREE.JS) ---
# This creates a 3D world with lighting, textures, and physics.
game_3d_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #000; color: white; font-family: 'Arial', sans-serif; overflow: hidden; }}
        #ui {{ position: absolute; top: 20px; left: 20px; background: rgba(0,0,0,0.7); padding: 20px; border-left: 5px solid #D21034; }}
        .gauge {{ font-size: 24px; color: #00FF41; font-family: monospace; }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
    <div id="ui">
        <div style="color:#00209F; font-weight:bold;">{GAME_NAME if 'GAME_NAME' in locals() else "HAITI TRUCK INNOVATION"}</div>
        <div class="gauge" id="speedDisplay">0 MPH</div>
        <div id="status">STATUS: DRIVE TO THE LOAD</div>
        <div style="font-size:10px; margin-top:10px;">ARROWS: Drive | ENTER: Air Brakes | SHIFT: Clutch</div>
    </div>

    <script>
        let scene, camera, renderer, truck, road, trailer;
        let speed = 0, angle = 0;
        let keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.fog = new THREE.Fog(0x222222, 10, 100);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Lighting
            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(5, 10, 7.5);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0x404040));

            // Road
            const roadGeo = new THREE.PlaneGeometry(20, 2000);
            const roadMat = new THREE.MeshPhongMaterial({{ color: 0x111111 }});
            road = new THREE.Mesh(roadGeo, roadMat);
            road.rotation.x = -Math.PI / 2;
            scene.add(road);

            // High-Detail Truck (Composite Group)
            truck = new THREE.Group();
            
            // Main Chassis (Haiti Blue)
            const bodyGeo = new THREE.BoxGeometry(2, 1.5, 4);
            const bodyMat = new THREE.MeshPhongMaterial({{ color: 0x00209F }});
            const body = new THREE.Mesh(bodyGeo, bodyMat);
            truck.add(body);

            // The Cab (Chrome/Glass Look)
            const cabGeo = new THREE.BoxGeometry(1.9, 1.2, 1.5);
            const cabMat = new THREE.MeshPhongMaterial({{ color: 0x555555, shininess: 100 }});
            const cab = new THREE.Mesh(cabGeo, cabMat);
            cab.position.set(0, 0.8, 1);
            truck.add(cab);

            // Smoke Stacks (Big Truck Style)
            const stackGeo = new THREE.CylinderGeometry(0.1, 0.1, 2);
            const stackMat = new THREE.MeshPhongMaterial({{ color: 0xaaaaaa }});
            const stackL = new THREE.Mesh(stackGeo, stackMat);
            stackL.position.set(-0.9, 1.2, 0);
            truck.add(stackL);
            
            scene.add(truck);

            // Trailer (Haiti Red) - Placed down the road
            trailer = new THREE.Mesh(new THREE.BoxGeometry(2.2, 2.5, 8), new THREE.MeshPhongMaterial({{ color: 0xD21034 }}));
            trailer.position.set(0, 1.25, -20);
            scene.add(trailer);

            camera.position.set(0, 5, 10);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);

            // Physics Logic
            if (keys['ArrowUp']) speed += 0.005;
            if (keys['ArrowDown']) speed -= 0.005;
            if (keys['Enter']) speed *= 0.9; // Air Brakes
            
            if (Math.abs(speed) > 0.01) {{
                if (keys['ArrowLeft']) truck.rotation.y += 0.02;
                if (keys['ArrowRight']) truck.rotation.y -= 0.02;
            }}

            speed *= 0.98; // Friction
            truck.position.x += Math.sin(truck.rotation.y) * speed * -10;
            truck.position.z += Math.cos(truck.rotation.y) * speed * -10;

            // Camera follow (Video Game Style)
            camera.position.x = truck.position.x + Math.sin(truck.rotation.y) * 12;
            camera.position.z = truck.position.z + Math.cos(truck.rotation.y) * 12;
            camera.lookAt(truck.position);

            // HUD update
            document.getElementById('speedDisplay').innerText = Math.abs(Math.round(speed * 500)) + " MPH";

            renderer.render(scene, camera);
        }}

        init();
    </script>
</body>
</html>
"""

# Render full screen
components.html(game_3d_html, height=800)

# --- CREDENTIALS FOOTER ---
st.markdown("---")
st.write(f"**Developer:** {OWNER} | **Company:** {COMPANY} | **Contact:** {CONTACT}")
