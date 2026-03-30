import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Simulator PRO", layout="wide")

# --- MULTI-MODE ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #000; }}
        #ui {{
            position: absolute; top: 20px; left: 20px; 
            background: rgba(0,32,159,0.9); padding: 15px; border-radius: 8px; 
            color: white; border-left: 5px solid #D21034; z-index: 10;
        }}
        #controls-hint {{
            position: absolute; top: 20px; right: 20px; 
            background: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px; 
            color: #FFD700; font-size: 13px; z-index: 10;
        }}
        #dashboard {{
            position: absolute; bottom: 0; width: 100%; height: 180px;
            background: linear-gradient(0deg, #111 0%, #333 100%);
            border-top: 4px solid #444; display: flex; justify-content: space-around; align-items: center;
            color: #00FF41; font-family: monospace; z-index: 5;
        }}
        .gauge {{ text-align: center; border: 2px solid #444; padding: 10px; border-radius: 10px; min-width: 120px; }}
        #start-btn {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.98);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="start-btn" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <h2>HEAVY TRUCK PRO SIMULATOR</h2>
        <p>PRESS [V] TO CHANGE VIEW | [N] FOR DAY/NIGHT</p>
        <h3 style="color:#FFD700;">CLICK TO START ENGINE</h3>
    </div>

    <div id="ui">
        <div style="font-size: 18px; font-weight: bold;">{OWNER}</div>
        <div style="font-size: 11px;">{COMPANY} FOUNDER</div>
    </div>

    <div id="controls-hint">
        <b>[UP]</b> Gas (Progressive)<br>
        <b>[V]</b> Change View (In/Out)<br>
        <b>[N]</b> Day / Night Mode<br>
        <b>[SPACE]</b> Emergency Brake
    </div>

    <div id="dashboard">
        <div class="gauge">SPEED<br><span id="sp-val" style="font-size:30px;">0</span> MPH</div>
        <div style="color:white; text-align:center;">
             <span id="view-txt">CABIN VIEW</span><br>
             <span id="time-txt">NIGHT DRIVE</span>
        </div>
        <div class="gauge">GEAR<br><span id="gr-val" style="font-size:30px;">N</span></div>
    </div>

    <script>
        let scene, camera, renderer, wheel, truckBody, roadSegments = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let isNight = true, isCabinView = true;
        let audioCtx, osc;

        function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(20, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000814);
            scene.fog = new THREE.Fog(0x000814, 800, 4000);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 0.1, 10000);
            
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            const sun = new THREE.DirectionalLight(0xffffff, 0.8);
            sun.position.set(500, 1000, 200);
            scene.add(sun);
            scene.sun = sun;

            // --- THE 3D STEERING WHEEL ---
            wheel = new THREE.Group();
            let ring = new THREE.Mesh(new THREE.TorusGeometry(3, 0.4, 16, 100), new THREE.MeshPhongMaterial({{color: 0x222222}}));
            let spoke = new THREE.Mesh(new THREE.BoxGeometry(6, 0.5, 0.5), new THREE.MeshPhongMaterial({{color: 0x333333}}));
            wheel.add(ring); wheel.add(spoke);
            wheel.position.set(0, 8.5, -5); // Positioned in front of driver
            wheel.rotation.x = Math.PI / 3;
            scene.add(wheel);

            // --- TRUCK EXTERIOR (For Follow View) ---
            truckBody = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F}});
            let cab = new THREE.Mesh(new THREE.BoxGeometry(8, 10, 10), blue);
            cab.position.y = 5;
            truckBody.add(cab);
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(8, 12, 40), new THREE.MeshPhongMaterial({{color: 0xeeeeee}}));
            trailer.position.set(0, 6, 25);
            truckBody.add(trailer);
            scene.add(truckBody);

            // --- THE ROAD ---
            for(let i=0; i<200; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(200, 60), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);
                
                let pole = new THREE.Group();
                let pMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.6, 40), new THREE.MeshPhongMaterial({{color: 0x444444}}));
                let bulb = new THREE.Mesh(new THREE.SphereGeometry(1.5), new THREE.MeshBasicMaterial({{color: 0xffffaa}}));
                bulb.position.set(-8, 20, 0);
                pole.add(pMesh); pole.add(bulb);
                pole.position.set(110, 20, 0);
                pole.visible = false;
                seg.add(pole);
                seg.light = pole;

                seg.position.z = -i * 60;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            animate();
        }}

        window.addEventListener('keydown', e => {{
            keys[e.code] = true;
            if(e.code === 'KeyV') {{ isCabinView = !isCabinView; document.getElementById('view-txt').innerText = isCabinView ? "CABIN VIEW" : "FOLLOW VIEW"; }}
            if(e.code === 'KeyN') {{ 
                isNight = !isNight;
                scene.background = new THREE.Color(isNight ? 0x000814 : 0x87CEEB);
                scene.fog.color = new THREE.Color(isNight ? 0x000814 : 0x87CEEB);
                scene.sun.intensity = isNight ? 0.2 : 1.2;
                document.getElementById('time-txt').innerText = isNight ? "NIGHT DRIVE" : "DAY DRIVE";
            }}
        }});
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            
            // Progressive Gas
            if (keys['ArrowUp']) speed += 0.0004;
            else speed *= 0.994; // Slow down step-by-step
            
            if (keys['Space']) speed *= 0.95; // Brake
            if (speed < 0) speed = 0;

            // Steering Logic
            if (keys['ArrowLeft']) targetX -= 1.8;
            if (keys['ArrowRight']) targetX += 1.8;
            truckX += (targetX - truckX) * 0.06;
            
            // Turn Steering Wheel
            wheel.rotation.z = (targetX - truckX) * -0.5;

            time += speed * 6;

            // Camera Modes
            if(isCabinView) {{
                camera.position.set(truckX, 11, -1);
                camera.lookAt(truckX, 10, -100);
                wheel.visible = true;
                wheel.position.x = truckX;
                truckBody.visible = false;
            }} else {{
                camera.position.set(truckX, 40, 150);
                camera.lookAt(truckX, 15, -50);
                wheel.visible = false;
                truckBody.visible = true;
                truckBody.position.x = truckX;
            }}

            // Road & Turns
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 800; 
                if(seg.position.z > 500) seg.position.z -= 200 * 60;
                
                let zPos = seg.position.z - (time * 40);
                let curveX = 0;
                let isCurve = false;

                // Turn Limit Logic (Wide curve at specific distance)
                if (zPos < -12000 && zPos > -18000) {{
                    curveX = Math.sin((zPos + 12000) * 0.0004) * 600;
                    isCurve = true;
                }}
                seg.position.x = curveX;
                seg.light.visible = isCurve && isNight; // Guidance lights
            }});

            document.getElementById('sp-val').innerText = Math.round(speed * 8000);
            document.getElementById('gr-val').innerText = speed > 0.005 ? "D" : "N";
            if(osc) osc.frequency.setTargetAtTime(20 + (speed * 5000), audioCtx.currentTime, 0.1);

            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
