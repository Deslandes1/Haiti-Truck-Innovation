import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM SETTINGS ---
OWNER = "Gesner Deslandes"
SYSTEM_KEY = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- LOGIN GATE (Bright & Visible) ---
if 'active' not in st.session_state:
    st.session_state.active = False

if not st.session_state.active:
    st.markdown("<h1 style='color:#00209F;'>🇭🇹 EDUHUMANITY CONTROL CENTER</h1>", unsafe_allow_html=True)
    with st.container():
        st.info("System Locked. Please enter the Ignition Key to deploy the 18-Wheeler.")
        key = st.text_input("IGNITION KEY:", type="password")
        if st.button("START SYSTEM"):
            if key == SYSTEM_KEY:
                st.session_state.active = True
                st.rerun()
            else:
                st.error("Invalid Key.")
    st.stop()

# --- THE HIGH-DETAIL 3D WORLD ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #001021; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #gui {{ position: absolute; top: 20px; left: 20px; color: white; background: rgba(0,0,0,0.7); padding: 15px; border-radius: 5px; border-bottom: 4px solid #D21034; }}
        #start-prompt {{ position: absolute; width:100%; height:100%; background: rgba(0,0,0,0.9); z-index: 999; display: flex; justify-content: center; align-items: center; color: white; cursor: pointer; }}
    </style>
</head>
<body>
    <div id="start-prompt" onclick="this.style.display='none'; init();">
        <h1>CLICK TO INITIALIZE USA LANDSCAPE</h1>
    </div>

    <div id="gui">
        <div style="font-size: 10px; color: #888;">UNIT ID: HT-2026</div>
        <div style="font-size: 24px; color: #00FF41;"><span id="speedo">0</span> MPH</div>
        <div style="font-size: 12px; margin-top: 5px;">DRIVER: {OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, world;
        let speed = 0, angle = 0, keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB); // Realistic Sky Blue
            scene.fog = new THREE.Fog(0x87CEEB, 100, 1000);

            camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 1, 3000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Realistic Lighting
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            const sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(200, 500, 200);
            scene.add(sun);

            // --- THE LANDSCAPE (The Perfect Road) ---
            const worldGroup = new THREE.Group();
            
            // Ground
            const floor = new THREE.Mesh(new THREE.PlaneGeometry(10000, 10000), new THREE.MeshPhongMaterial({{color: 0x1b4d1b}}));
            floor.rotation.x = -Math.PI / 2;
            worldGroup.add(floor);

            // Highway
            const road = new THREE.Mesh(new THREE.PlaneGeometry(60, 20000), new THREE.MeshPhongMaterial({{color: 0x222222}}));
            road.rotation.x = -Math.PI / 2;
            road.position.y = 0.2;
            worldGroup.add(road);

            // Road Lines (Yellow & White)
            for(let i=0; i<300; i++) {{
                const line = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 15), new THREE.MeshBasicMaterial({{color: 0xffd700}}));
                line.rotation.x = -Math.PI / 2;
                line.position.set(0, 0.3, -i * 60);
                worldGroup.add(line);
            }}
            scene.add(worldGroup);

            // --- THE SEMI-TRUCK (USA DESIGN) ---
            truck = new THREE.Group();
            
            // Main Chassis
            const bodyMat = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 80}});
            
            // The "Nose" (Engine Compartment)
            const nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.2, 5.5), bodyMat);
            nose.position.set(0, 1.6, 6);
            truck.add(nose);

            // The Cab & Sleeper
            const cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), bodyMat);
            cab.position.set(0, 2.75, 1);
            truck.add(cab);

            // Chrome Front Grill
            const grill = new THREE.Mesh(new THREE.BoxGeometry(3.4, 2.8, 0.2), new THREE.MeshPhongMaterial({{color: 0xaaaaaa, shininess: 120}}));
            grill.position.set(0, 1.4, 8.7);
            truck.add(grill);

            // Dual Chrome Exhaust Pipes (Tall)
            const stackGeo = new THREE.CylinderGeometry(0.2, 0.2, 10);
            const chrome = new THREE.MeshPhongMaterial({{color: 0xeeeeee, shininess: 200}});
            const s1 = new THREE.Mesh(stackGeo, chrome); s1.position.set(1.9, 5, 0);
            const s2 = new THREE.Mesh(stackGeo, chrome); s2.position.set(-1.9, 5, 0);
            truck.add(s1); truck.add(s2);

            // THE FLAGS (Haiti & USA)
            const flagGeo = new THREE.PlaneGeometry(1.2, 0.8);
            const flagH = new THREE.Mesh(flagGeo, new THREE.MeshBasicMaterial({{color: 0x00209F}})); 
            flagH.position.set(2.11, 4, 1.5); flagH.rotation.y = Math.PI/2;
            truck.add(flagH);

            const flagU = new THREE.Mesh(flagGeo, new THREE.MeshBasicMaterial({{color: 0xBF0A30}})); 
            flagU.position.set(-2.11, 4, 1.5); flagU.rotation.y = -Math.PI/2;
            truck.add(flagU);

            scene.add(truck);

            // THE TRAILER (USA 53' Standard)
            const trailer = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.8, 28), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.9, -15);
            truck.add(trailer);

            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0009; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.0015;
            if (keys['Enter']) speed *= 0.94; // Brakes

            speed *= 0.995; 
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.008;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.008;
            }}

            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 80;
            truck.position.z += Math.cos(angle) * speed * 80;

            // Follow Camera (Cinematic)
            camera.position.x = truck.position.x - Math.sin(angle) * 70;
            camera.position.z = truck.position.z - Math.cos(angle) * 70;
            camera.position.y = 25;
            camera.lookAt(truck.position.x, 5, truck.position.z);

            document.getElementById('speedo').innerText = Math.round(Math.abs(speed * 1800));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
