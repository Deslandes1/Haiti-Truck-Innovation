import streamlit as st
import streamlit.components.v1 as components

# --- OWNER & PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck Pro - Off-Road Edition", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }}
        #ui {{ position: absolute; top: 20px; left: 20px; z-index: 100; }}
        .btn {{ padding: 12px 24px; background: #D21034; color: white; border: 2px solid #fff; cursor: pointer; font-weight: bold; border-radius: 5px; }}
        #dash {{ position: absolute; bottom: 0; width: 100%; height: 140px; background: #111; color: #00FF41; display: flex; justify-content: space-around; align-items: center; border-top: 4px solid #444; z-index: 50; }}
        #overlay {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
        #crash-screen {{ position: absolute; width: 100%; height: 100%; background: rgba(210, 16, 52, 0.9); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 300; }}
    </style>
</head>
<body>
    <div id="overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>DRIVE ANYWHERE. JUST DON'T HIT THE HOUSES.</p>
        <h2 style="background:#00209F; padding:10px 30px; border-radius:5px;">START ENGINE</h2>
    </div>

    <div id="crash-screen">
        <h1>💥 ACCIDENT!</h1>
        <p>YOU HIT A STRUCTURE. TRUCK DESTROYED.</p>
        <button class="btn" onclick="location.reload()">CLICK TO START OVER</button>
    </div>

    <div id="ui"><button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button></div>

    <div id="dash">
        <div style="text-align:center;">SPEED<br><span id="sp" style="font-size:35px;">0</span> MPH</div>
        <div style="color:white; text-align:center;"><b>{OWNER}</b></div>
        <div style="text-align:center;">TERRAIN<br><span id="ter" style="color:#FFD700;">ASPHALT</span></div>
    </div>

    <script>
        let scene, camera, renderer, wheel, headLight, road = [], speed = 0, tx = 0, targetX = 0, isNight = false, isCrashed = false, osc;

        function init() {{
            let ctx = new (window.AudioContext || window.webkitAudioContext)();
            osc = ctx.createOscillator(); let g = ctx.createGain();
            osc.type = 'sawtooth'; g.gain.value = 0.03; osc.connect(g); g.connect(ctx.destination); osc.start();

            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 5000);
            
            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 15000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 0.8); scene.add(amb); scene.amb = amb;
            headLight = new THREE.SpotLight(0xffffff, 0); headLight.distance = 3000; scene.add(headLight); scene.add(headLight.target);

            // Cockpit
            wheel = new THREE.Group();
            let wM = new THREE.Mesh(new THREE.TorusGeometry(3.5, 0.6, 12, 40), new THREE.MeshPhongMaterial({{color: 0x222222}}));
            wheel.add(wM);
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(1.5, 4, 1.2), hM); L.position.set(-3.8, 0, 1);
            let R = L.clone(); R.position.set(3.8, 0, 1); wheel.add(L); wheel.add(R);
            wheel.position.set(0, 9, -7); wheel.rotation.x = 1.1; scene.add(wheel);

            for(let i=0; i<120; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(5000, 200), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(180, 200), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(5, 80), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                // Houses are the ONLY things that cause a crash
                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(60, 40, 60), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                    let side = (i % 20 == 0) ? 350 : -350;
                    house.position.set(side, 20, 0);
                    s.add(house);
                    s.houseX = side; // Store for collision check
                }}
                s.position.z = -i * 200; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.0012; 
                if(e.key=='ArrowLeft') targetX -= 4; 
                if(e.key=='ArrowRight') targetX += 4;
            }});
            animate();
        }}

        function toggleTime() {{
            isNight = !isNight;
            let c = isNight ? 0x00050a : 0x87CEEB;
            scene.background = new THREE.Color(c); scene.fog.color = new THREE.Color(c);
            scene.amb.intensity = isNight ? 0.05 : 0.8;
            headLight.intensity = isNight ? 5.0 : 0;
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            
            speed *= 0.994; tx += (targetX - tx) * 0.1;
            
            // Terrain Detection
            let onRoad = Math.abs(tx) < 90;
            document.getElementById('ter').innerText = onRoad ? "ASPHALT" : "GRASS / DIRT";
            document.getElementById('ter').style.color = onRoad ? "#00FF41" : "#FFD700";

            // Collision Logic with Objects (Houses)
            road.forEach(s => {{ 
                s.position.z += speed * 4500; 
                if(s.position.z > 800) s.position.z -= 120 * 200; 
                
                // If truck is close to a segment with a house (Z-axis) 
                // AND truck X matches house X (within range) -> CRASH
                if(Math.abs(s.position.z) < 30 && s.houseX) {{
                    if(Math.abs(tx - s.houseX) < 50) {{
                        isCrashed = true;
                        document.getElementById('crash-screen').style.display = 'flex';
                        if(osc) osc.stop();
                    }}
                }}
            }});

            wheel.position.x = tx; 
            wheel.rotation.z = (targetX - tx) * -0.2 + (onRoad ? 0 : Math.sin(Date.now()*0.02)*0.05);
            camera.position.set(tx, 14 + (onRoad ? 0 : Math.sin(Date.now()*0.05)*0.3), 0); 
            camera.lookAt(tx, 12, -200);
            
            headLight.position.set(tx, 10, -5);
            headLight.target.position.set(tx, 0, -1000);

            document.getElementById('sp').innerText = Math.round(speed * 32000);
            if(osc) osc.frequency.value = 25 + (speed * 11000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)
