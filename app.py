import streamlit as st
import streamlit.components.v1 as components
import time

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Centered Cockpit", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }}
        #ui {{ position: absolute; top: 20px; left: 20px; z-index: 100; }}
        .btn {{ padding: 10px 20px; background: #D21034; color: white; border: 2px solid #fff; cursor: pointer; font-weight: bold; border-radius: 5px; }}
        #hud {{ position: absolute; bottom: 0; width: 100%; height: 100px; background: #050505; color: #00FF41; display: flex; justify-content: space-around; align-items: center; border-top: 3px solid #D21034; z-index: 50; }}
        #start {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
        #crash-screen {{ position: absolute; width: 100%; height: 100%; background: rgba(210, 16, 52, 0.9); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 300; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>CENTERED CHASSIS | LEFT-HAND DRIVE</p>
        <h2 style="background:#00209F; padding:10px 30px; border-radius:5px;">START ENGINE</h2>
    </div>

    <div id="crash-screen">
        <h1>💥 TOTAL LOSS</h1>
        <button class="btn" onclick="location.reload()">REDEPLOY TRUCK</button>
    </div>

    <div id="ui"><button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button></div>

    <div id="hud">
        <div><b>{OWNER}</b></div>
        <div style="font-size:20px;">SPEED: <span id="sp">0</span> MPH</div>
        <div style="font-size:20px;">GEAR: <span style="color:#fff;">[D]</span></div>
        <div style="font-size:20px;">TIME: <span id="clock">00:00</span></div>
    </div>

    <script>
        let scene, camera, renderer, cabin, wheel, road = [], speed = 0, tx = 0, targetX = 0;
        let isNight = false, isCrashed = false, osc, startTime;

        function init() {{
            startTime = Date.now();
            let ctx = new (window.AudioContext || window.webkitAudioContext)();
            osc = ctx.createOscillator(); let g = ctx.createGain();
            osc.type = 'sawtooth'; g.gain.value = 0.02; osc.connect(g); g.connect(ctx.destination); osc.start();

            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 7000);
            
            camera = new THREE.PerspectiveCamera(70, window.innerWidth/window.innerHeight, 0.1, 20000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 1.0); scene.add(amb); scene.amb = amb;

            // --- CENTERED CABIN SYSTEM ---
            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x222222}});
            
            // Dashboard (Centered)
            let dash = new THREE.Mesh(new THREE.BoxGeometry(100, 20, 30), cMat);
            dash.position.set(0, 5, -20);
            cabin.add(dash);

            // Left Steering Wheel (Offset -20 from center)
            wheel = new THREE.Group();
            let wR = new THREE.Mesh(new THREE.TorusGeometry(5, 1, 12, 40), new THREE.MeshPhongMaterial({{color: 0x0a0a0a}}));
            wheel.add(wR);
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(2, 7, 2), hM); L.position.set(-5, 0, 1);
            let R = L.clone(); R.position.set(5, 0, 1);
            wheel.add(L); wheel.add(R);
            wheel.position.set(-20, 15, -25); wheel.rotation.x = 1.3;
            cabin.add(wheel);

            // Automatic Gear Selector (Offset +10 from center)
            let gear = new THREE.Group();
            let gB = new THREE.Mesh(new THREE.BoxGeometry(8, 5, 12), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            let gS = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 8), new THREE.MeshPhongMaterial({{color: 0x666}}));
            gS.position.y = 4; gS.rotation.x = -0.2;
            gear.add(gB); gear.add(gS);
            gear.position.set(10, 10, -25);
            cabin.add(gear);

            // Cabin Frames (Pillars)
            let pL = new THREE.Mesh(new THREE.BoxGeometry(4, 80, 4), cMat);
            pL.position.set(-45, 30, -15); pL.rotation.z = 0.2;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 45; pR.rotation.z = -0.2;
            cabin.add(pR);

            scene.add(cabin);

            // Environment
            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(8000, 400), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(350, 400), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(12, 150), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(100, 80, 100), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                    let side = (i%20==0)? 650 : -650;
                    house.position.set(side, 40, 0); s.add(house); s.houseX = side;
                }}
                s.position.z = -i * 400; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.0022; 
                if(e.key=='ArrowLeft') targetX -= 7; 
                if(e.key=='ArrowRight') targetX += 7;
                if(e.key.toLowerCase()=='n') toggleTime();
            }});
            animate();
        }}

        function toggleTime() {{
            isNight = !isNight;
            let c = isNight ? 0x00050a : 0x87CEEB;
            scene.background = new THREE.Color(c); scene.fog.color = new THREE.Color(c);
            scene.amb.intensity = isNight ? 0.05 : 1.0;
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            speed *= 0.996; tx += (targetX - tx) * 0.1;
            let onRoad = Math.abs(tx) < 175;
            
            // Timer Logic
            let elapsed = Math.floor((Date.now() - startTime) / 1000);
            let m = Math.floor(elapsed / 60).toString().padStart(2, '0');
            let s = (elapsed % 60).toString().padStart(2, '0');
            document.getElementById('clock').innerText = m + ":" + s;

            road.forEach(seg => {{ 
                seg.position.z += speed * 8000; 
                if(seg.position.z > 1500) seg.position.z -= 100 * 400; 
                if(Math.abs(seg.position.z) < 80 && seg.houseX && Math.abs(tx - seg.houseX) < 150) {{
                    isCrashed = true;
                    document.getElementById('crash-screen').style.display = 'flex';
                    if(osc) osc.stop();
                }}
            }});

            cabin.position.x = tx; // Truck body stays centered on steering position
            wheel.rotation.z = (targetX - tx) * -0.2;
            
            // Camera sits on the LEFT seat (relative to truck center)
            camera.position.set(tx - 20, 28, 35); 
            camera.lookAt(tx - 20, 20, -300);

            document.getElementById('sp').innerText = Math.round(speed * 50000);
            if(osc) osc.frequency.value = 25 + (speed * 15000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
