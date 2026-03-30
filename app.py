import streamlit as st
import streamlit.components.v1 as components

# --- OWNER & PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - LHD & Automatic", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }}
        #ui {{ position: absolute; top: 20px; left: 20px; z-index: 100; }}
        .btn {{ padding: 10px 20px; background: #D21034; color: white; border: 2px solid #fff; cursor: pointer; font-weight: bold; border-radius: 5px; }}
        #hud {{ position: absolute; bottom: 0; width: 100%; height: 90px; background: #050505; color: #00FF41; display: flex; justify-content: space-around; align-items: center; border-top: 2px solid #444; z-index: 50; }}
        #start {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
        #crash-screen {{ position: absolute; width: 100%; height: 100%; background: rgba(210, 16, 52, 0.9); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 300; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>LEFT-HAND DRIVE & AUTOMATIC GEARS</p>
        <h2 style="background:#00209F; padding:10px 30px; border-radius:5px;">START MISSION</h2>
    </div>

    <div id="crash-screen">
        <h1>💥 ACCIDENT!</h1>
        <button class="btn" onclick="location.reload()">RELOAD TRUCK</button>
    </div>

    <div id="ui"><button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button></div>

    <div id="hud">
        <div><b>{OWNER}</b></div>
        <div style="font-size:25px;">SPEED: <span id="sp">0</span> MPH</div>
        <div style="color:white;">GEAR: <span style="color:#00FF41;">D</span></div>
    </div>

    <script>
        let scene, camera, renderer, cabin, wheel, gear, road = [], speed = 0, tx = 0, targetX = 0, isNight = false, isCrashed = false, osc;

        function init() {{
            let ctx = new (window.AudioContext || window.webkitAudioContext)();
            osc = ctx.createOscillator(); let g = ctx.createGain();
            osc.type = 'sawtooth'; g.gain.value = 0.03; osc.connect(g); g.connect(ctx.destination); osc.start();

            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 6000);
            
            camera = new THREE.PerspectiveCamera(70, window.innerWidth/window.innerHeight, 0.1, 15000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 0.9); scene.add(amb); scene.amb = amb;

            // --- CABIN INTERIOR ---
            cabin = new THREE.Group();
            let cabMat = new THREE.MeshPhongMaterial({{color: 0x222222}});
            
            // Dashboard
            let dash = new THREE.Mesh(new THREE.BoxGeometry(80, 18, 25), cabMat);
            dash.position.set(0, 5, -15);
            cabin.add(dash);

            // Left-Hand Steering Wheel
            wheel = new THREE.Group();
            let wRing = new THREE.Mesh(new THREE.TorusGeometry(4.5, 0.8, 12, 40), new THREE.MeshPhongMaterial({{color: 0x050505}}));
            wheel.add(wRing);
            let hMat = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(2, 6, 2), hMat); L.position.set(-4.5, 0, 1);
            let R = L.clone(); R.position.set(4.5, 0, 1);
            wheel.add(L); wheel.add(R);
            wheel.position.set(-15, 14, -18); wheel.rotation.x = 1.3; // POSITIONED LEFT
            cabin.add(wheel);

            // Automatic Gear Selector (Console)
            gear = new THREE.Group();
            let gBase = new THREE.Mesh(new THREE.BoxGeometry(6, 4, 10), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            let gStick = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 6), new THREE.MeshPhongMaterial({{color: 0x444444}}));
            let gKnob = new THREE.Mesh(new THREE.SphereGeometry(1.2), new THREE.MeshPhongMaterial({{color: 0x000}}));
            gStick.position.y = 3; gKnob.position.y = 6;
            gear.add(gBase); gear.add(gStick); gear.add(gKnob);
            gear.position.set(10, 12, -18); // POSITIONED TO THE RIGHT OF WHEEL
            cabin.add(gear);

            // A-Pillars
            let pL = new THREE.Mesh(new THREE.BoxGeometry(3, 60, 3), cabMat);
            pL.position.set(-35, 25, -10); pL.rotation.z = 0.25;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 35; pR.rotation.z = -0.25;
            cabin.add(pR);

            scene.add(cabin);

            // World setup
            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(6000, 300), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(280, 300), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(10, 120), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(90, 70, 90), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                    let side = (i%20==0)? 500 : -500;
                    house.position.set(side, 35, 0); s.add(house); s.houseX = side;
                }}
                s.position.z = -i * 300; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.002; 
                if(e.key=='ArrowLeft') targetX -= 6; 
                if(e.key=='ArrowRight') targetX += 6;
                if(e.key.toLowerCase()=='n') toggleTime();
            }});
            animate();
        }}

        function toggleTime() {{
            isNight = !isNight;
            let c = isNight ? 0x00050a : 0x87CEEB;
            scene.background = new THREE.Color(c); scene.fog.color = new THREE.Color(c);
            scene.amb.intensity = isNight ? 0.05 : 0.9;
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            speed *= 0.995; tx += (targetX - tx) * 0.1;
            let onRoad = Math.abs(tx) < 140;
            
            road.forEach(s => {{ 
                s.position.z += speed * 7000; 
                if(s.position.z > 1200) s.position.z -= 100 * 300; 
                if(Math.abs(s.position.z) < 60 && s.houseX && Math.abs(tx - s.houseX) < 120) {{
                    isCrashed = true;
                    document.getElementById('crash-screen').style.display = 'flex';
                    if(osc) osc.stop();
                }}
            }});

            cabin.position.x = tx;
            wheel.rotation.z = (targetX - tx) * -0.2;
            
            // Driver is sitting on the left (tx - 15)
            camera.position.set(tx - 15, 25, 25); 
            camera.lookAt(tx - 15, 18, -250);

            document.getElementById('sp').innerText = Math.round(speed * 45000);
            if(osc) osc.frequency.value = 25 + (speed * 14000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
