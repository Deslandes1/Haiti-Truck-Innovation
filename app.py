import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM SETTINGS ---
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

# --- THE REALISTIC 3D ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #hud {{ position: absolute; bottom: 30px; right: 30px; background: rgba(0,0,0,0.8); padding: 20px; border-radius: 15px; border: 2px solid #D21034; color: white; pointer-events: none; }}
        .speed-val {{ font-size: 50px; color: #00FF41; }}
        #start-screen {{ position: absolute; width: 100%; height: 100%; background: #000; z-index: 100; display: flex; justify-content: center; align-items: center; cursor: pointer; text-align:center; }}
    </style>
</head>
<body>
    <div id="start-screen" onclick="this.style.display='none'; init();">
        <h1 style="color:#00209F">HAITI TRUCK INNOVATION<br><span style="font-size:20px; color:white;">CLICK TO DEPLOY 18-WHEELER</span></h1>
    </div>

    <div id="hud">
        <div style="font-size: 12px;">USA HIGHWAY PATROL</div>
        <div class="speed-val" id="sp">00</div><span style="color:#00FF41"> MPH</span>
        <div style="margin-top:10px; font-size:10px;">DRIVER: {OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, trailer, road;
        let speed = 0, angle = 0, keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB); // Sky Blue
            scene.fog = new THREE.Fog(0x87CEEB, 50, 400);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 1500);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Sunlight
            const light = new THREE.DirectionalLight(0xffffff, 1.2);
            light.position.set(100, 100, 50);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0xffffff, 0.4));

            // THE ROAD (Asphalt with Markings)
            const roadGroup = new THREE.Group();
            const asphalt = new THREE.Mesh(new THREE.PlaneGeometry(50, 5000), new THREE.MeshPhongMaterial({{color: 0x222222}}));
            asphalt.rotation.x = -Math.PI / 2;
            roadGroup.add(asphalt);

            // Add Lane Stripes (Activity)
            for(let i=0; i<100; i++) {{
                const stripe = new THREE.Mesh(new THREE.PlaneGeometry(1, 10), new THREE.MeshPhongMaterial({{color: 0xffff00}}));
                stripe.rotation.x = -Math.PI / 2;
                stripe.position.set(0, 0.1, -i * 50);
                roadGroup.add(stripe);
            }}
            scene.add(roadGroup);

            // SCENERY (Buildings/Trees for speed reference)
            for(let i=0; i<50; i++) {{
                const building = new THREE.Mesh(new THREE.BoxGeometry(10, 20 + Math.random()*30, 10), new THREE.MeshPhongMaterial({{color: 0x555555}}));
                building.position.set(i % 2 === 0 ? 40 : -40, 10, -i * 80);
                scene.add(building);
            }}

            // THE AMERICAN TRUCK (Long Nose Style)
            truck = new THREE.Group();
            
            // Engine Bay (The "Nose")
            const nose = new THREE.Mesh(new THREE.BoxGeometry(3, 2.5, 4), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            nose.position.set(0, 1.25, 4);
            truck.add(nose);

            // The Sleeper Cab
            const cab = new THREE.Mesh(new THREE.BoxGeometry(3.5, 4, 3), new THREE.MeshPhongMaterial({{color: 0x00209F}}));
            cab.position.set(0, 2, 0.5);
            truck.add(cab);

            // Chrome Front Bumper & Grille
            const grill = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.5, 0.2), new THREE.MeshPhongMaterial({{color: 0xcccccc, shininess: 100}}));
            grill.position.set(0, 0.8, 6.1);
            truck.add(grill);

            // Exhaust Stacks (Tall Chrome)
            const stackGeo = new THREE.CylinderGeometry(0.15, 0.15, 7);
            const chromeMat = new THREE.MeshPhongMaterial({{color: 0xeeeeee, shininess: 150}});
            const s1 = new THREE.Mesh(stackGeo, chromeMat); s1.position.set(1.6, 3.5, -0.5);
            const s2 = new THREE.Mesh(stackGeo, chromeMat); s2.position.set(-1.6, 3.5, -0.5);
            truck.add(s1); truck.add(s2);

            scene.add(truck);

            // THE TRAILER (USA 53' Standard - Red)
            trailer = new THREE.Mesh(new THREE.BoxGeometry(3.5, 4.5, 22), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.25, -12);
            truck.add(trailer);

            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // HEAVY PHYSICS: Slow acceleration, High Inertia
            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0008; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.0015;
            if (keys['Enter']) speed *= 0.94; // Air Brakes

            // Friction & Speed Management
            speed *= 0.995; 
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.012;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.012;
            }}

            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 60;
            truck.position.z += Math.cos(angle) * speed * 60;

            // Follow Camera (Cinematic Chase)
            camera.position.x = truck.position.x - Math.sin(angle) * 45;
            camera.position.z = truck.position.z - Math.cos(angle) * 45;
            camera.position.y = 15;
            camera.lookAt(truck.position.x, 3, truck.position.z);

            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 1200));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)
