import streamlit as st
import streamlit.components.v1 as components

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Circular Steering", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }}
        #hud {{ position: absolute; bottom: 0; width: 100%; height: 100px; background: #080808; color: #00FF41; display: flex; justify-content: space-around; align-items: center; border-top: 4px solid #333; z-index: 50; }}
        #start {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
        #crash {{ position: absolute; width: 100%; height: 100%; background: rgba(210, 16, 52, 0.95); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 300; }}
        .btn {{ padding: 10px 20px; background: #D21034; color: white; border: 2px solid #fff; cursor: pointer; font-weight: bold; border-radius: 5px; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>HD CIRCULAR STEERING WHEEL | LHD CENTERED</p>
        <h2 style="background:#00209F; padding:10px 40px; border-radius:5px;">START ENGINE</h2>
    </div>

    <div id="crash">
        <h1>💥 ACCIDENT DETECTED</h1>
        <button class="btn" onclick="location.reload()">RESTART SIMULATION</button>
    </div>

    <div id="hud">
        <div>DRIVER: <b>{OWNER}</b></div>
        <div style="font-size:22px;">SPEED: <span id="sp">0</span> MPH</div>
        <div style="font-size:22px;">GEAR: <span style="color:#fff;">[D]</span></div>
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
            scene.fog = new THREE.Fog(0x87CEEB, 1, 10000);
            
            camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 30000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 1.2); scene.add(amb);

            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            
            // Dashboard
            let dash = new THREE.Mesh(new THREE.BoxGeometry(220, 35, 60), cMat);
            dash.position.set(0, 5, -30);
            cabin.add(dash);

            // --- THE PERFECT CIRCLE STEERING WHEEL ---
            wheel = new THREE.Group();
            // High resolution segments (128) for a perfect circle
            let wGeom = new THREE.TorusGeometry(11, 1.9, 24, 128); 
            let wMat = new THREE.MeshPhongMaterial({{color: 0x050505}});
            let wRing = new THREE.Mesh(wGeom, wMat);
            wheel.add(wRing);

            // Center Hub & Spokes
            let hub = new THREE.Mesh(new THREE.CylinderGeometry(2.5, 2.5, 3), wMat);
            hub.rotation.x = Math.PI/2;
            wheel.add(hub);

            // Hands/Grip positions
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(4, 12, 4), hM); L.position.set(-11, 0, 1);
            let R = L.clone(); R.position.set(11, 0, 1);
            wheel.add(L); wheel.add(R);

            // Vertical angle (1.5) makes it look round from the camera's tilt
            wheel.position.set(-38, 22, -40); wheel.rotation.x = 1.5; 
            cabin.add(wheel);

            // Gear Console
            let gear = new THREE.Group();
            let gB = new THREE.Mesh(new THREE.BoxGeometry(14, 10, 22), new THREE.MeshPhongMaterial({{color: 0x0a0a0a}}));
            let gS = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 14), new THREE.MeshPhongMaterial({{color: 0x999}}));
            gS.position.y = 7; gS.rotation.x = -0.4;
            gear.add(gB); gear.add(gS);
            gear.position.set(15, 12, -40);
            cabin.add(gear);

            // Symmetrical Window Frame
            let pL = new THREE.Mesh(new THREE.BoxGeometry(6, 140, 6), cMat);
            pL.position.set(-95, 60, -25); pL.rotation.z = 0.1;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 95; pR.rotation.z = -0.1;
            cabin.add(pR);

            scene.add(cabin);

            // Environment setup
            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(12000, 600), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(500, 600), new THREE.MeshPhongMaterial({{color: 0x151515}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(20, 250), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(160, 110, 160), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                    let side = (i%20==0)? 1000 : -1000;
                    house.position.set(side, 55, 0); s.add(house); s.houseX = side;
                }}
                s.position.z = -i * 600; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.003; 
                if(e.key=='ArrowLeft') targetX -= 12; 
                if(e.key=='ArrowRight') targetX += 12;
            }});
            animate();
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            speed *= 0.996; tx += (targetX - tx) * 0.1;
            
            road.forEach(seg => {{ 
                seg.position.z += speed * 12000; 
                if(seg.position.z > 2000) seg.position.z -= 100 * 600; 
                if(Math.abs(seg.position.z) < 150 && seg.houseX && Math.abs(tx - seg.houseX) < 250) {{
                    isCrashed = true;
                    document.getElementById('crash').style.display = 'flex';
                    if(osc) osc.stop();
                }}
            }});

            cabin.position.x = tx; 
            wheel.rotation.z = (targetX - tx) * -0.2;
            
            // Position camera exactly behind the circular wheel (-38)
            camera.position.set(tx - 38, 42, 65); 
            camera.lookAt(tx - 38, 30, -600);

            document.getElementById('sp').innerText = Math.round(speed * 70000);
            if(osc) osc.frequency.value = 25 + (speed * 20000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
