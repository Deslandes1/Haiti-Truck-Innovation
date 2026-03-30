import streamlit as st
import streamlit.components.v1 as components

# --- USER & SYSTEM DATA ---
OWNER = "Gesner Deslandes"
SYSTEM_KEY = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- CLEAR LOGIN GATE ---
if 'active' not in st.session_state:
    st.session_state.active = False

if not st.session_state.active:
    st.title("🇭🇹 EDUHUMANITY: TRUCK SIMULATOR")
    st.subheader("System Security Active")
    
    # This is the fix: A clear, bright login area
    with st.form("login_form"):
        key = st.text_input("ENTER IGNITION KEY (Password):", type="password")
        submit = st.form_submit_button("UNLOCK ENGINE")
        
        if submit:
            if key == SYSTEM_KEY:
                st.session_state.active = True
                st.rerun()
            else:
                st.error("Access Denied: Incorrect Key")
    st.stop()

# --- THE TRUCK ENGINE (Runs ONLY after login) ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #start-overlay {{ 
            position: absolute; top:0; left:0; width:100%; height:100%; 
            background: rgba(0,0,0,0.9); display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 1000; cursor: pointer; color: white;
        }}
        #hud {{ position: absolute; bottom: 30px; left: 30px; background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px; color: white; pointer-events: none; border-left: 5px solid #D21034; }}
    </style>
</head>
<body>
    <div id="start-overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#00209F; font-size:40px;">LOGIN SUCCESSFUL</h1>
        <p style="font-size:20px;">[ CLICK ANYWHERE TO DEPLOY THE TRUCK ]</p>
    </div>

    <div id="hud">
        <div style="font-size: 12px; color: #00FF41;">ENGINE: ACTIVE</div>
        <div style="font-size: 40px;" id="sp">00</div><span>MPH</span>
        <div style="margin-top:10px; font-size:14px;">DRIVER: {OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, world;
        let speed = 0, angle = 0, keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 200, 1000);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 2000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Sun & Environment
            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
            const sun = new THREE.DirectionalLight(0xffffff, 1);
            sun.position.set(50, 100, 50);
            scene.add(sun);

            // Landscape & Perfect Road
            const worldGroup = new THREE.Group();
            const grass = new THREE.Mesh(new THREE.PlaneGeometry(5000, 5000), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
            grass.rotation.x = -Math.PI / 2;
            worldGroup.add(grass);

            const road = new THREE.Mesh(new THREE.PlaneGeometry(50, 10000), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
            road.rotation.x = -Math.PI / 2;
            road.position.y = 0.1;
            worldGroup.add(road);

            // Road Markings
            for(let i=0; i<100; i++) {{
                const line = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 10), new THREE.MeshBasicMaterial({{color: 0xffd700}}));
                line.rotation.x = -Math.PI / 2;
                line.position.set(0, 0.2, -i * 100);
                worldGroup.add(line);
            }}
            scene.add(worldGroup);

            // --- THE REAL USA TRUCK ---
            truck = new THREE.Group();
            
            // Blue Long Nose Cab
            const cab = new THREE.Mesh(new THREE.BoxGeometry(4, 5, 8), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            cab.position.y = 2.5;
            truck.add(cab);

            // Chrome Exhausts
            const stackGeo = new THREE.CylinderGeometry(0.2, 0.2, 8);
            const chrome = new THREE.MeshPhongMaterial({{color: 0xcccccc, shininess: 100}});
            const s1 = new THREE.Mesh(stackGeo, chrome); s1.position.set(1.8, 5, -1);
            const s2 = new THREE.Mesh(stackGeo, chrome); s2.position.set(-1.8, 5, -1);
            truck.add(s1); truck.add(s2);

            // Flags
            const flagHT = new THREE.Mesh(new THREE.PlaneGeometry(1, 0.6), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flagHT.position.set(2.01, 4, 1); flagHT.rotation.y = Math.PI/2;
            truck.add(flagHT);

            // Red Trailer
            const trailer = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 25), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.75, -15);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0008; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.0012;
            if (keys['Enter']) speed *= 0.95;

            speed *= 0.996; 
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.01;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.01;
            }}

            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 70;
            truck.position.z += Math.cos(angle) * speed * 70;

            camera.position.x = truck.position.x - Math.sin(angle) * 50;
            camera.position.z = truck.position.z - Math.cos(angle) * 50;
            camera.position.y = 18;
            camera.lookAt(truck.position.x, 3, truck.position.z);

            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 1500));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)
