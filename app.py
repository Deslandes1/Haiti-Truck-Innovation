import streamlit as st
import streamlit.components.v1 as components

# --- OWNER & PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"
EMAIL = "deslandes78@gmail.com"

st.set_page_config(page_title="Haiti Truck Innovation - Dash View", layout="wide")

# --- COCKPIT ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #00050a; overflow: hidden; font-family: 'Arial', sans-serif; }}
        #ui-overlay {{
            position: absolute; bottom: 0; width: 100%; height: 250px;
            background: linear-gradient(0deg, #111 0%, #222 50%, rgba(0,0,0,0) 100%);
            z-index: 10; display: flex; justify-content: space-around; align-items: center;
            border-top: 4px solid #444;
        }}
        .gauge {{
            width: 150px; height: 150px; border-radius: 50%;
            border: 5px solid #555; background: #000;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: #00FF41; box-shadow: inset 0 0 20px #00FF41;
        }}
        #speed-val {{ font-size: 40px; font-weight: bold; }}
        #start-screen {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.95);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer; text-align: center;
        }}
        #brand {{ position: absolute; top: 20px; left: 20px; color: white; z-index: 20; }}
    </style>
</head>
<body>
    <div id="start-screen" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:60px; margin-bottom:0;">{COMPANY}</h1>
        <p style="letter-spacing:5px;">DASHBOARD VIEW SIMULATION</p>
        <p>HOLD [UP] TO ACCELERATE | RELEASE TO SLOW | [LEFT/RIGHT] TO STEER</p>
        <h2 style="color:#FFD700;">CLICK TO ENTER CABIN</h2>
    </div>

    <div id="brand">
        <h2 style="margin:0;">{OWNER}</h2>
        <small>{COMPANY} | {CONTACT}</small>
    </div>

    <div id="ui-overlay">
        <div class="gauge">
            <small>RPM</small>
            <div id="rpm-val">0</div>
        </div>
        <div style="text-align:center; color:white;">
            <div style="font-size:20px; color:#D21034;">🇭🇹 HAITI TRUCK</div>
            <div style="font-size:12px;">INNOVATION 2026</div>
        </div>
        <div class="gauge">
            <small>SPEED</small>
            <div id="speed-val">0</div>
            <small>MPH</small>
        </div>
    </div>

    <script>
        let scene, camera, renderer, roadSegments = [], smokeParticles = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(15, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000a1a);
            scene.fog = new THREE.Fog(0x000a1a, 500, 4000);

            // CAMERA POSITIONED INSIDE THE TRUCK
            camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 0.1, 10000);
            camera.position.set(0, 12, 0); // Inside the cabin height

            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.5));
            let headlights = new THREE.SpotLight(0xffffaa, 2);
            headlights.position.set(0, 5, -10);
            headlights.angle = Math.PI / 4;
            scene.add(headlights);

            // --- THE ROAD (INFINITE STRAIGHT) ---
            for(let i=0; i<250; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(200, 60), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(8, 60), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-104, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(104, 0.2, 0);
                seg.add(curbR);

                // Street Light Pole
                let pole = new THREE.Group();
                let pMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.8, 40), new THREE.MeshPhongMaterial({{color: 0x333333}}));
                let bulb = new THREE.Mesh(new THREE.SphereGeometry(2), new THREE.MeshBasicMaterial({{color: 0xffffaa}}));
                bulb.position.set(-8, 20, 0);
                pole.add(pMesh); pole.add(bulb);
                pole.position.set(120, 20, 0);
                pole.visible = false; 
                seg.add(pole);
                seg.light = pole;

                seg.position.z = -i * 60;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            
            // PROGRESSIVE MOVEMENT
            if (keys['ArrowUp']) {{ speed += 0.0004; }} 
            else {{ speed *= 0.992; }} // Release to slow down step-by-step
            
            if (keys['ArrowDown']) speed -= 0.002; 
            if (speed < 0) speed = 0;

            if (keys['ArrowLeft']) targetX -= 1.5;
            if (keys['ArrowRight']) targetX += 1.5;
            truckX += (targetX - truckX) * 0.05;
            
            time += speed * 5;

            // Update Camera position based on steering
            camera.position.x = truckX;
            camera.rotation.y = (targetX - truckX) * -0.01;

            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 800; 
                if(seg.position.z > 500) seg.position.z -= 250 * 60;
                
                let zPos = seg.position.z - (time * 50);
                let curveX = 0;
                let isCurve = false;

                // Turn logic (Every 15000 units)
                if (zPos < -10000 && zPos > -16000) {{
                    curveX = Math.sin((zPos + 10000) * 0.0005) * 500;
                    isCurve = true;
                }}

                seg.position.x = curveX;
                seg.light.visible = isCurve; // Only show lights during the turns
            }});

            // Sound & UI Updates
            if(osc) osc.frequency.setTargetAtTime(15 + (speed * 6000), audioCtx.currentTime, 0.1);
            document.getElementById('speed-val').innerText = Math.round(speed * 8000);
            document.getElementById('rpm-val').innerText = Math.round(speed * 12000);

            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
