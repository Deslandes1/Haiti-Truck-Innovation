import streamlit as st
import streamlit.components.v1 as components

# --- OWNER DATA (EDUHUNANITY CREDENTIALS) ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
EMAIL = "deslandes78@gmail.com"
PHONE = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- RACING WORLD WITH STEERING ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #001021; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #credentials {{ 
            position: absolute; top: 20px; left: 20px; 
            background: rgba(0,32,159,0.9); padding: 15px; border-radius: 5px; 
            color: white; border-left: 10px solid #D21034; z-index: 10;
        }}
        #speedo {{
            position: absolute; bottom: 30px; right: 30px;
            color: #00FF41; font-size: 80px; font-style: italic;
        }}
        #start-gate {{
            position: absolute; width:100%; height:100%; background: rgba(0,0,0,0.9);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer;
        }}
        .label {{ color: #FFD700; font-size: 10px; text-transform: uppercase; }}
    </style>
</head>
<body>
    <div id="start-gate" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:60px;">🇭🇹 {COMPANY}</h1>
        <h2 style="margin-top:0;">TRUCK INNOVATION 2026</h2>
        <p>[ CLICK TO DEPLOY TRUCK & ACTIVATE STEERING ]</p>
    </div>

    <div id="credentials">
        <div class="label">Founder & Operator</div>
        <div style="font-size: 20px; margin-bottom:5px;">{OWNER}</div>
        <div class="label">Contact Information</div>
        <div style="font-size: 13px;">{EMAIL}</div>
        <div style="font-size: 13px;">WhatsApp: {PHONE}</div>
    </div>

    <div id="speedo"><span id="sp">00</span><span style="font-size:25px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], speed = 0, angle = 0, truckX = 0, keys = {{}};
        let audioCtx, osc, gain;

        function init() {{
            // Engine Audio
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(40, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB); // Blue Sky Landscape
            scene.fog = new THREE.Fog(0x87CEEB, 100, 800);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 2000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            let sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(50, 200, 50);
            scene.add(sun);

            // --- THE RACING LANDSCAPE (Road & Environment) ---
            const ground = new THREE.Mesh(new THREE.PlaneGeometry(5000, 5000), new THREE.MeshPhongMaterial({{color: 0x1a3306}}));
            ground.rotation.x = -Math.PI / 2;
            scene.add(ground);

            for(let i=0; i<50; i++) {{
                let seg = new THREE.Group();
                // Asphalt Racing Surface
                let road = new THREE.Mesh(new THREE.PlaneGeometry(80, 40), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Racing Stripes (Red/White Vibration)
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(8, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-44, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(44, 0.2, 0);
                seg.add(curbR);

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE 18-WHEELER (Conventional USA Style) ---
            truck = new THREE.Group();
            let paint = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 100}});
            
            // Nose & Cab
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.2, 6), paint);
            nose.position.set(0, 1.6, 6);
            truck.add(nose);

            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), paint);
            cab.position.set(0, 2.75, 1);
            truck.add(cab);

            // HAITIAN FLAG
            let flag = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flag.position.set(2.15, 4.5, 1);
            flag.rotation.y = Math.PI/2;
            truck.add(flag);

            // TIRES (Visible & Spinning)
            let tireGeo = new THREE.CylinderGeometry(1.2, 1.2, 1.1, 16);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x000000}});
            [[-2.1,1,4.5], [2.1,1,4.5], [-2.1,1,1], [2.1,1,1], [-2.1,1,-12], [2.1,1,-12]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            // White Trailer
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.2, 6, 28), new THREE.MeshPhongMaterial({{color: 0xEEEEEE}}));
            trailer.position.set(0, 4.1, -12);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // Movement & Physics
            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0018; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.0025;
            
            // --- STEERING CONTROL ---
            if (keys['ArrowLeft'] || keys['KeyA']) truckX -= 0.8;
            if (keys['ArrowRight'] || keys['KeyD']) truckX += 0.8;
            
            // Keep truck on the racing track
            if (truckX < -38) truckX = -38;
            if (truckX > 38) truckX = 38;
            
            speed *= 0.993; // Rolling Friction
            truck.position.x = truckX;

            // Loop the road segments
            roadSegments.forEach(seg => {{
                seg.position.z += speed * 120; 
                if(seg.position.z > 80) seg.position.z -= 50 * 40;
            }});

            // Visual Wheel Spin
            wheels.forEach(w => w.rotation.x += speed * 6);

            // Audio Sync
            if(osc) osc.frequency.setTargetAtTime(40 + (speed * 1500), audioCtx.currentTime, 0.1);

            // Camera follow (locks behind truck but allows steering view)
            camera.position.set(truckX * 0.5, 22, 65);
            camera.lookAt(truckX, 6, -10);

            document.getElementById('sp').innerText = Math.round(speed * 2200);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
