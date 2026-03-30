import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM SETTINGS ---
OWNER = "Gesner Deslandes"
SYSTEM_KEY = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- LOGIN GATE ---
if 'active' not in st.session_state:
    st.session_state.active = False

if not st.session_state.active:
    st.title("🇭🇹 EDUHUMANITY: TRUCK SIMULATOR 2026")
    with st.form("gate"):
        key = st.text_input("IGNITION KEY:", type="password")
        if st.form_submit_button("ACTIVATE ENGINE"):
            if key == SYSTEM_KEY:
                st.session_state.active = True
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

# --- THE REALISTIC 3D WORLD ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #000; overflow: hidden; font-family: 'Impact', sans-serif; }}
        #hud {{ position: absolute; bottom: 40px; left: 40px; background: rgba(0,0,0,0.8); padding: 25px; border-radius: 10px; border-left: 10px solid #D21034; color: white; pointer-events: none; }}
        .speed-val {{ font-size: 70px; color: #00FF41; line-height: 1; }}
        #boot-screen {{ position: absolute; width:100%; height:100%; background: #000; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; cursor: pointer; }}
    </style>
</head>
<body>
    <div id="boot-screen" onclick="this.style.display='none'; init();">
        <h1 style="color:#00209F; font-size: 50px;">HAITI TRUCK INNOVATION</h1>
        <p style="font-size: 20px;">[ CLICK TO INITIALIZE WORLD & START ENGINE ]</p>
    </div>

    <div id="hud">
        <div style="font-size: 15px; letter-spacing: 3px; color: #aaa;">USA HIGHWAY PATROL</div>
        <div class="speed-val" id="sp">00</div><span style="color:#00FF41; font-size: 20px;">MPH</span>
        <div style="margin-top:20px; border-top: 1px solid #444; padding-top: 10px; font-size: 18px;">{OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, worldGroup;
        let speed = 0, angle = 0, keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB); 
            scene.fog = new THREE.Fog(0x87CEEB, 200, 1200);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 3000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.5));
            const sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(100, 300, 100);
            scene.add(sun);

            // --- THE LANDSCAPE (The Perfect Road) ---
            worldGroup = new THREE.Group();
            
            // Endless Grass
            const grass = new THREE.Mesh(new THREE.PlaneGeometry(10000, 10000), new THREE.MeshPhongMaterial({{color: 0x143306}}));
            grass.rotation.x = -Math.PI / 2;
            worldGroup.add(grass);

            // Asphalt Highway
            const road = new THREE.Mesh(new THREE.PlaneGeometry(60, 20000), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            road.rotation.x = -Math.PI / 2;
            road.position.y = 0.2;
            worldGroup.add(road);

            // Road Markings (USA Style)
            for(let i=0; i<400; i++) {{
                const yellowLine = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 15), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                yellowLine.rotation.x = -Math.PI / 2;
                yellowLine.position.set(0, 0.3, -i * 60);
                worldGroup.add(yellowLine);
            }}
            scene.add(worldGroup);

            // --- THE SEMI-TRUCK (USA DESIGN) ---
            truck = new THREE.Group();
            const paint = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 90}});
            
            // The "Nose" (Long Front)
            const nose = new THREE.Mesh(new THREE.BoxGeometry(3.8, 3.5, 6), paint);
            nose.position.set(0, 1.75, 6);
            truck.add(nose);

            // The Sleeper Cab
            const cab = new THREE.Mesh(new THREE.BoxGeometry(4.5, 5.8, 5), paint);
            cab.position.set(0, 2.9, 1);
            truck.add(cab);

            // Chrome Details
            const grill = new THREE.Mesh(new THREE.BoxGeometry(3.5, 3, 0.2), new THREE.MeshPhongMaterial({{color: 0xCCCCCC, shininess: 200}}));
            grill.position.set(0, 1.5, 9.1);
            truck.add(grill);

            const stackGeo = new THREE.CylinderGeometry(0.25, 0.25, 10);
            const chrome = new THREE.MeshPhongMaterial({{color: 0xFFFFFF, shininess: 250}});
            const s1 = new THREE.Mesh(stackGeo, chrome); s1.position.set(2, 5, 0);
            const s2 = new THREE.Mesh(stackGeo, chrome); s2.position.set(-2, 5, 0);
            truck.add(s1); truck.add(s2);

            // Flags
            const flagHT = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.8), new THREE.MeshBasicMaterial({{color: 0x00209F}})); 
            flagHT.position.set(2.3, 4.5, 2); flagHT.rotation.y = Math.PI/2;
            truck.add(flagHT);

            const flagUS = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.8), new THREE.MeshBasicMaterial({{color: 0xBF0A30}})); 
            flagUS.position.set(-2.3, 4.5, 2); flagUS.rotation.y = -Math.PI/2;
            truck.add(flagUS);

            scene.add(truck);

            // 53' RED TRAILER
            const trailer = new THREE.Mesh(new THREE.BoxGeometry(4.5, 6, 30), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 3, -16);
            truck.add(trailer);

            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.001; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.0015;
            if (keys['Enter']) speed *= 0.94; // Air Brakes

            speed *= 0.996; 
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.01;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.01;
            }}

            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 90;
            truck.position.z += Math.cos(angle) * speed * 90;

            camera.position.x = truck.position.x - Math.sin(angle) * 75;
            camera.position.z = truck.position.z - Math.cos(angle) * 75;
            camera.position.y = 25;
            camera.lookAt(truck.position.x, 6, truck.position.z);

            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 2000));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
