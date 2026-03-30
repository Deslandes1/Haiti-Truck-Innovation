import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck Pro - Full Cockpit", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }}
        #ui {{ position: absolute; top: 20px; left: 20px; z-index: 100; }}
        .btn {{ padding: 12px 24px; background: #D21034; color: white; border: 2px solid #fff; cursor: pointer; font-weight: bold; border-radius: 5px; }}
        #dash-ui {{ position: absolute; bottom: 0; width: 100%; height: 100px; background: #050505; color: #00FF41; display: flex; justify-content: space-around; align-items: center; border-top: 3px solid #333; z-index: 50; }}
        #overlay {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
        #crash-screen {{ position: absolute; width: 100%; height: 100%; background: rgba(210, 16, 52, 0.9); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 300; }}
    </style>
</head>
<body>
    <div id="overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>FULL COCKPIT MODE: ACTIVE</p>
        <h2 style="background:#00209F; padding:10px 30px; border-radius:5px;">ENTER CABIN</h2>
    </div>

    <div id="crash-screen">
        <h1>💥 ACCIDENT!</h1>
        <p>THE CABIN WAS DESTROYED IN THE COLLISION.</p>
        <button class="btn" onclick="location.reload()">REPAIR & START OVER</button>
    </div>

    <div id="ui"><button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button></div>

    <div id="dash-ui">
        <div><b>{OWNER}</b></div>
        <div style="font-size:25px;">SPEED: <span id="sp">0</span> MPH</div>
        <div id="ter" style="color:#FFD700;">ASPHALT</div>
    </div>

    <script>
        let scene, camera, renderer, cockpit, wheel, headLight, road = [], speed = 0, tx = 0, targetX = 0, isNight = false, isCrashed = false, osc;

        function init() {{
            let ctx = new (window.AudioContext || window.webkitAudioContext)();
            osc = ctx.createOscillator(); let g = ctx.createGain();
            osc.type = 'sawtooth'; g.gain.value = 0.03; osc.connect(g); g.connect(ctx.destination); osc.start();

            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 5000);
            
            camera = new THREE.PerspectiveCamera(65, window.innerWidth/window.innerHeight, 0.1, 15000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 0.8); scene.add(amb); scene.amb = amb;
            headLight = new THREE.SpotLight(0xffffff, 0); headLight.distance = 3500; scene.add(headLight); scene.add(headLight.target);

            // --- FULL COCKPIT DESIGN ---
            cockpit = new THREE.Group();
            let cabMat = new THREE.MeshPhongMaterial({{color: 0x1a1a1a}});
            
            // Dashboard
            let dashBoard = new THREE.Mesh(new THREE.BoxGeometry(40, 8, 15), cabMat);
            dashBoard.position.set(0, 7, -8);
            cockpit.add(dashBoard);

            // Side Pillars (A-Pillars)
            let pillarL = new THREE.Mesh(new THREE.BoxGeometry(2, 30, 2), cabMat);
            pillarL.position.set(-18, 20, -5); pillarL.rotation.z = 0.1;
            cockpit.add(pillarL);
            let pillarR = pillarL.clone(); pillarR.position.x = 18; pillarR.rotation.z = -0.1;
            cockpit.add(pillarR);

            // Roof Frame
            let roof = new THREE.Mesh(new THREE.BoxGeometry(40, 2, 10), cabMat);
            roof.position.set(0, 32, -5);
            cockpit.add(roof);

            // Steering Wheel & Hands
            wheel = new THREE.Group();
            let wM = new THREE.Mesh(new THREE.TorusGeometry(3.5, 0.6, 12, 40), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            wheel.add(wM);
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let LHand = new THREE.Mesh(new THREE.BoxGeometry(1.5, 4, 1.5), hM); LHand.position.set(-3.5, 0, 1);
            let RHand = LHand.clone(); RHand.position.set(3.5, 0, 1);
            wheel.add(LHand); wheel.add(RHand);
            wheel.position.set(0, 10, -10); wheel.rotation.x = 1.2;
            cockpit.add(wheel);

            scene.add(cockpit);

            // World Generation
            for(let i=0; i<120; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(5000, 200), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshPhongMaterial({{color: 0x222222}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(6, 90), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(70, 50, 70), new THREE.MeshPhongMaterial({{color: i%20==0?0x00209F:0xD21034}}));
                    let side = (i % 20 == 0) ? 400 : -400;
                    house.position.set(side, 25, 0); s.add(house);
                    s.houseX = side;
                }}
                s.position.z = -i * 200; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.0015; 
                if(e.key=='ArrowLeft') targetX -= 4.5; 
                if(e.key=='ArrowRight') targetX += 4.5;
                if(e.key.toLowerCase()=='n') toggleTime();
            }});
            animate();
        }}

        function toggleTime() {{
            isNight = !isNight;
            let c = isNight ? 0x00050a : 0x87CEEB;
            scene.background = new THREE.Color(c); scene.fog.color = new THREE.Color(c);
            scene.amb.intensity = isNight ? 0.05 : 0.8;
            headLight.intensity = isNight ? 6.0 : 0;
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            
            speed *= 0.994; tx += (targetX - tx) * 0.1;
            let onRoad = Math.abs(tx) < 100;
            
            document.getElementById('ter').innerText = onRoad ? "ASPHALT" : "OFF-ROAD DIRT";
            document.getElementById('ter').style.color = onRoad ? "#00FF41" : "#FFD700";

            road.forEach(s => {{ 
                s.position.z += speed * 5000; 
                if(s.position.z > 1000) s.position.z -= 120 * 200; 
                if(Math.abs(s.position.z) < 40 && s.houseX) {{
                    if(Math.abs(tx - s.houseX) < 60) {{
                        isCrashed = true;
                        document.getElementById('crash-screen').style.display = 'flex';
                        if(osc) osc.stop();
                    }}
                }}
            }});

            // Lock everything to Cockpit
            cockpit.position.x = tx;
            wheel.rotation.z = (targetX - tx) * -0.2;
            
            // Cockpit vibration when off-road
            let vib = onRoad ? 0 : Math.sin(Date.now()*0.05)*0.4;
            cockpit.position.y = vib;
            
            camera.position.set(tx, 16 + vib, 5); 
            camera.lookAt(tx, 14, -200);
            
            headLight.position.set(tx, 12, -5);
            headLight.target.position.set(tx, 0, -1500);

            document.getElementById('sp').innerText = Math.round(speed * 35000);
            if(osc) osc.frequency.value = 25 + (speed * 12000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
