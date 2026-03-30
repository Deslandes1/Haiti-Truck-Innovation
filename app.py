import streamlit as st
import streamlit.components.v1 as components

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Master Center", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }}
        #ui {{ position: absolute; top: 20px; left: 20px; z-index: 100; }}
        .btn {{ padding: 10px 20px; background: #D21034; color: white; border: 2px solid #fff; cursor: pointer; font-weight: bold; border-radius: 5px; }}
        #hud {{ position: absolute; bottom: 0; width: 100%; height: 100px; background: #080808; color: #00FF41; display: flex; justify-content: space-around; align-items: center; border-top: 4px solid #333; z-index: 50; }}
        #start {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
        #crash {{ position: absolute; width: 100%; height: 100%; background: rgba(210, 16, 52, 0.95); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 300; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>MASTER CABIN ALIGNMENT | LHD & AUTOMATIC</p>
        <h2 style="background:#00209F; padding:10px 40px; border-radius:5px;">ENGAGE ENGINE</h2>
    </div>

    <div id="crash">
        <h1>💥 CABIN CRUSHED</h1>
        <button class="btn" onclick="location.reload()">RESTART SIMULATION</button>
    </div>

    <div id="ui"><button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button></div>

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
            scene.fog = new THREE.Fog(0x87CEEB, 1, 8000);
            
            // Wider FOV (80) to see the whole centered cabin
            camera = new THREE.PerspectiveCamera(80, window.innerWidth/window.innerHeight, 0.1, 25000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 1.0); scene.add(amb); scene.amb = amb;

            // --- THE MASTER CENTERED CABIN ---
            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x151515}});
            
            // Dashboard - centered at 0
            let dash = new THREE.Mesh(new THREE.BoxGeometry(200, 30, 50), cMat);
            dash.position.set(0, 5, -25);
            cabin.add(dash);

            // Left-Hand Steering Wheel (Shifted left to -35)
            wheel = new THREE.Group();
            let wR = new THREE.Mesh(new THREE.TorusGeometry(7, 1.4, 12, 40), new THREE.MeshPhongMaterial({{color: 0x000}}));
            wheel.add(wR);
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(3, 10, 3), hM); L.position.set(-7, 0, 1);
            let R = L.clone(); R.position.set(7, 0, 1);
            wheel.add(L); wheel.add(R);
            wheel.position.set(-35, 20, -35); wheel.rotation.x = 1.4;
            cabin.add(wheel);

            // Automatic Transmission Shifter (Shifted right to +15)
            let gear = new THREE.Group();
            let gB = new THREE.Mesh(new THREE.BoxGeometry(12, 8, 20), new THREE.MeshPhongMaterial({{color: 0x080808}}));
            let gS = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 12), new THREE.MeshPhongMaterial({{color: 0x888}}));
            gS.position.y = 6; gS.rotation.x = -0.4;
            gear.add(gB); gear.add(gS);
            gear.position.set(15, 12, -35);
            cabin.add(gear);

            // Symmetrical Window Pillars
            let pL = new THREE.Mesh(new THREE.BoxGeometry(6, 120, 6), cMat);
            pL.position.set(-85, 50, -20); pL.rotation.z = 0.12;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 85; pR.rotation.z = -0.12;
            cabin.add(pR);

            scene.add(cabin);

            // Infinite Road
            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(10000, 500), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(450, 500), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(18, 200), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(140, 100, 140), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                    let side = (i%20==0)? 900 : -900;
                    house.position.set(side, 50, 0); s.add(house); s.houseX = side;
                }}
                s.position.z = -i * 500; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.0028; 
                if(e.key=='ArrowLeft') targetX -= 10; 
                if(e.key=='ArrowRight') targetX += 10;
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
                seg.position.z += speed * 10000; 
                if(seg.position.z > 1500) seg.position.z -= 100 * 500; 
                if(Math.abs(seg.position.z) < 120 && seg.houseX && Math.abs(tx - seg.houseX) < 220) {{
                    isCrashed = true;
                    document.getElementById('crash').style.display = 'flex';
                    if(osc) osc.stop();
                }}
            }});

            // The Cabin group moves with the center of the road (tx)
            cabin.position.x = tx; 
            wheel.rotation.z = (targetX - tx) * -0.2;
            
            // Eyes are behind the Left-Hand steering wheel (-35)
            camera.position.set(tx - 35, 38, 55); 
            camera.lookAt(tx - 35, 25, -500);

            document.getElementById('sp').innerText = Math.round(speed * 60000);
            if(osc) osc.frequency.value = 25 + (speed * 18000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
