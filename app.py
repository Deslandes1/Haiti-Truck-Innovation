import streamlit as st
import streamlit.components.v1 as components

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Centered LHD", layout="wide")

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
        <p>CENTERED CABIN | LEFT-HAND DRIVE FIXED</p>
        <h2 style="background:#00209F; padding:10px 30px; border-radius:5px;">START TRUCK</h2>
    </div>

    <div id="crash-screen">
        <h1>💥 ACCIDENT DETECTED</h1>
        <button class="btn" onclick="location.reload()">START OVER</button>
    </div>

    <div id="ui"><button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button></div>

    <div id="hud">
        <div><b>{OWNER}</b></div>
        <div style="font-size:20px;">SPEED: <span id="sp">0</span> MPH</div>
        <div style="font-size:20px;">GEAR: <span style="color:#fff;">[D]</span></div>
    </div>

    <script>
        let scene, camera, renderer, cabin, wheel, road = [], speed = 0, tx = 0, targetX = 0;
        let isNight = false, isCrashed = false, osc;

        function init() {{
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

            // --- THE CABIN SYSTEM (CENTERED) ---
            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x1a1a1a}});
            
            // Dashboard (Centered horizontally at 0)
            let dash = new THREE.Mesh(new THREE.BoxGeometry(150, 25, 40), cMat);
            dash.position.set(0, 5, -20);
            cabin.add(dash);

            // Left Steering Wheel (Shifted to the left -25)
            wheel = new THREE.Group();
            let wR = new THREE.Mesh(new THREE.TorusGeometry(6, 1.2, 12, 40), new THREE.MeshPhongMaterial({{color: 0x000}}));
            wheel.add(wR);
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(2.5, 8, 2.5), hM); L.position.set(-6, 0, 1);
            let R = L.clone(); R.position.set(6, 0, 1);
            wheel.add(L); wheel.add(R);
            wheel.position.set(-25, 18, -30); wheel.rotation.x = 1.35;
            cabin.add(wheel);

            // Automatic Shifter (Shifted to center-right +15)
            let gear = new THREE.Group();
            let gB = new THREE.Mesh(new THREE.BoxGeometry(10, 6, 15), new THREE.MeshPhongMaterial({{color: 0x111}}));
            let gS = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 10), new THREE.MeshPhongMaterial({{color: 0x777}}));
            gS.position.y = 5; gS.rotation.x = -0.3;
            gear.add(gB); gear.add(gS);
            gear.position.set(15, 12, -30);
            cabin.add(gear);

            // Frame Pillars (Equally spaced from 0)
            let pL = new THREE.Mesh(new THREE.BoxGeometry(5, 100, 5), cMat);
            pL.position.set(-60, 40, -15); pL.rotation.z = 0.15;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 60; pR.rotation.z = -0.15;
            cabin.add(pR);

            scene.add(cabin);

            // Road & Houses
            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(8000, 450), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(400, 450), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(15, 180), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(120, 90, 120), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                    let side = (i%20==0)? 750 : -750;
                    house.position.set(side, 45, 0); s.add(house); s.houseX = side;
                }}
                s.position.z = -i * 450; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.0025; 
                if(e.key=='ArrowLeft') targetX -= 8; 
                if(e.key=='ArrowRight') targetX += 8;
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
            
            road.forEach(seg => {{ 
                seg.position.z += speed * 9000; 
                if(seg.position.z > 1500) seg.position.z -= 100 * 450; 
                if(Math.abs(seg.position.z) < 100 && seg.houseX && Math.abs(tx - seg.houseX) < 180) {{
                    isCrashed = true;
                    document.getElementById('crash-screen').style.display = 'flex';
                    if(osc) osc.stop();
                }}
            }});

            // Align the Cabin to the truck's steering (tx)
            cabin.position.x = tx; 
            wheel.rotation.z = (targetX - tx) * -0.2;
            
            // Set Camera to the Driver's eye level, offset left (-25)
            camera.position.set(tx - 25, 32, 45); 
            camera.lookAt(tx - 25, 22, -400);

            document.getElementById('sp').innerText = Math.round(speed * 55000);
            if(osc) osc.frequency.value = 25 + (speed * 16000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
