import streamlit as st
import streamlit.components.v1 as components

# --- OWNER & PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck Pro - High Beams", layout="wide")

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
        #start {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; text-align: center; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>NIGHT HIGH-BEAMS ENABLED</p>
        <h2 style="background:#00209F; padding:10px 30px; border-radius:5px;">CLICK TO START</h2>
    </div>

    <div id="ui">
        <button class="btn" onclick="toggleTime()">TOGGLE DAY / NIGHT (N)</button>
    </div>

    <div id="dash">
        <div style="text-align:center;">SPEED<br><span id="sp" style="font-size:35px;">0</span> MPH</div>
        <div style="color:white; text-align:center;"><b>{OWNER}</b><br><small>EDUHUMANITY 2026</small></div>
        <div style="text-align:center;">LIGHTS<br><span id="lt" style="color:#FFD700;">OFF</span></div>
    </div>

    <script>
        let scene, camera, renderer, wheel, headLight, road = [], speed = 0, tx = 0, targetX = 0, isNight = false, osc;

        function init() {{
            let ctx = new (window.AudioContext || window.webkitAudioContext)();
            osc = ctx.createOscillator(); let g = ctx.createGain();
            osc.type = 'sawtooth'; g.gain.value = 0.03; osc.connect(g); g.connect(ctx.destination); osc.start();

            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 4000);
            
            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 15000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 0.8); scene.add(amb); scene.amb = amb;

            // --- THE HIGH-BEAM HEADLIGHT ---
            headLight = new THREE.SpotLight(0xffffff, 0); // Start off
            headLight.distance = 2500;
            headLight.angle = 0.4;
            headLight.penumbra = 0.3;
            headLight.decay = 1;
            scene.add(headLight);
            scene.add(headLight.target);

            // Cockpit: Wheel & Hands
            wheel = new THREE.Group();
            let wM = new THREE.Mesh(new THREE.TorusGeometry(3.5, 0.6, 12, 40), new THREE.MeshPhongMaterial({{color: 0x222222}}));
            wheel.add(wM);
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(1.5, 4, 1.2), hM); L.position.set(-3.8, 0, 1);
            let R = L.clone(); R.position.set(3.8, 0, 1);
            wheel.add(L); wheel.add(R);
            wheel.position.set(0, 9, -7); wheel.rotation.x = 1.1; scene.add(wheel);

            // Straight Road & Landscape
            for(let i=0; i<120; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(4000, 200), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(160, 200), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(5, 80), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%8==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(40, 30, 40), new THREE.MeshPhongMaterial({{color: i%16==0?0x00209F:0xD21034}}));
                    house.position.set(i%16==0?250:-250, 15, 0); s.add(house);
                    let palm = new THREE.Mesh(new THREE.CylinderGeometry(2,3,50), new THREE.MeshPhongMaterial({{color:0x4d3319}}));
                    palm.position.set(i%16==0?-220:220, 25, 0); s.add(palm);
                }}
                s.position.z = -i * 200; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(e.key=='ArrowUp') speed += 0.001; 
                if(e.key=='ArrowLeft') targetX -= 3; 
                if(e.key=='ArrowRight') targetX += 3;
                if(e.key.toLowerCase()=='n') toggleTime();
            }});
            animate();
        }}

        function toggleTime() {{
            isNight = !isNight;
            let c = isNight ? 0x00050a : 0x87CEEB;
            scene.background = new THREE.Color(c); scene.fog.color = new THREE.Color(c);
            scene.amb.intensity = isNight ? 0.05 : 0.8;
            headLight.intensity = isNight ? 3.5 : 0; // Turn on high beams at night
            document.getElementById('lt').innerText = isNight ? "HIGH BEAMS" : "OFF";
            document.getElementById('lt').style.color = isNight ? "#fff" : "#FFD700";
        }}

        function animate() {{
            requestAnimationFrame(animate);
            speed *= 0.992; tx += (targetX - tx) * 0.1;
            
            // Lock camera, wheel, and high-beams to steering
            wheel.position.x = tx; 
            wheel.rotation.z = (targetX - tx) * -0.15;
            camera.position.set(tx, 14, 0); camera.lookAt(tx, 12, -200);
            
            headLight.position.set(tx, 10, -5);
            headLight.target.position.set(tx, 0, -1000); // PROJECT FAR AHEAD

            road.forEach(s => {{ s.position.z += speed * 3500; if(s.position.z > 800) s.position.z -= 120 * 200; }});
            document.getElementById('sp').innerText = Math.round(speed * 28000);
            if(osc) osc.frequency.value = 25 + (speed * 9500);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)
