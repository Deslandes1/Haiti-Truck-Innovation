import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM CONFIG ---
COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com"
PASSWORD_REQUIRED = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation 3D", layout="wide")

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"<h1 style='text-align:center; color:#00209F;'>🇭🇹 {COMPANY}</h1>", unsafe_allow_html=True)
    pwd = st.text_input("IGNITION KEY:", type="password")
    if st.button("START SYSTEM"):
        if pwd == PASSWORD_REQUIRED:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3D ENGINE ---
game_3d_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #000; overflow: hidden; font-family: 'Impact', sans-serif; }}
        #hud {{ position: absolute; bottom: 30px; left: 30px; color: #00FF41; text-shadow: 2px 2px #000; }}
        .speed {{ font-size: 50px; }}
        .label {{ font-size: 15px; color: white; }}
    </script>
</head>
<body>
    <div id="hud">
        <div class="label">VEHICLE SPEED</div>
        <div class="speed" id="sp">00</div><span style="font-size:20px;">MPH</span>
        <div class="label" style="margin-top:10px;">SYSTEM: ACTIVE</div>
        <div style="color:#D21034; font-size:12px;">{COMPANY} | {OWNER}</div>
    </div>

    <script>
        let scene, camera, renderer, truck, trailer, road;
        let speed = 0, wheelAngle = 0, truckAngle = 0;
        let keys = {{}};

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a);
            scene.fog = new THREE.Fog(0x0a0a0a, 20, 150);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Lights
            scene.add(new THREE.AmbientLight(0x404040, 2));
            const sun = new THREE.DirectionalLight(0xffffff, 1);
            sun.position.set(10, 20, 10);
            scene.add(sun);

            // Infinite Road
            const roadGeo = new THREE.PlaneGeometry(40, 5000);
            const roadMat = new THREE.MeshPhongMaterial({{ color: 0x111111 }});
            road = new THREE.Mesh(roadGeo, roadMat);
            road.rotation.x = -Math.PI / 2;
            scene.add(road);

            // THE RIG (Blue Cab)
            truck = new THREE.Group();
            const cab = new THREE.Mesh(new THREE.BoxGeometry(2.5, 3, 4), new THREE.MeshPhongMaterial({{color:0x00209F}}));
            cab.position.y = 1.5;
            truck.add(cab);

            // Chrome Exhaust Stacks
            const stack = new THREE.CylinderGeometry(0.15, 0.15, 4);
            const chrome = new THREE.MeshPhongMaterial({{color:0xaaaaaa, shininess: 100}});
            const s1 = new THREE.Mesh(stack, chrome); s1.position.set(1.1, 3, -1.5);
            const s2 = new THREE.Mesh(stack, chrome); s2.position.set(-1.1, 3, -1.5);
            truck.add(s1); truck.add(s2);

            // THE TRAILER (Red - 18 Wheeler Style)
            trailer = new THREE.Mesh(new THREE.BoxGeometry(2.5, 3.5, 12), new THREE.MeshPhongMaterial({{color:0xD21034}}));
            trailer.position.set(0, 2, -8.5);
            truck.add(trailer);
            
            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);

            // Realistic Acceleration (Heavy Mass)
            if (keys['ArrowUp']) speed += 0.002; 
            if (keys['ArrowDown']) speed -= 0.003;
            if (keys['Enter']) speed *= 0.96; // Air Brakes

            // Steering Logic
            if (keys['ArrowLeft']) wheelAngle += 0.001;
            if (keys['ArrowRight']) wheelAngle -= 0.001;
            wheelAngle *= 0.95; // Steering Centers itself
            truckAngle += wheelAngle * (speed * 5);

            speed *= 0.992; // Rolling Resistance
            
            truck.position.x += Math.sin(truckAngle) * speed * 20;
            truck.position.z += Math.cos(truckAngle) * speed * 20;
            truck.rotation.y = truckAngle;

            // Cinematic Camera (Follow + Smooth Lerp)
            let targetCamX = truck.position.x - Math.sin(truckAngle) * 25;
            let targetCamZ = truck.position.z - Math.cos(truckAngle) * 25;
            camera.position.x += (targetCamX - camera.position.x) * 0.05;
            camera.position.z += (targetCamZ - camera.position.z) * 0.05;
            camera.position.y = 8;
            camera.lookAt(truck.position.x, 2, truck.position.z);

            document.getElementById('sp').innerText = Math.abs(Math.round(speed * 600));
            renderer.render(scene, camera);
        }}
        init();
    </script>
</body>
</html>
"""

components.html(game_3d_html, height=800)
