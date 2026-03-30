import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck Pro", layout="wide")

# Optimized lightweight engine to prevent Syntax Errors
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #87CEEB; font-family: sans-serif; }}
        #dash {{ position: absolute; bottom: 0; width: 100%; height: 120px; background: #111; color: #00FF41; display: flex; justify-content: center; align-items: center; gap: 40px; border-top: 4px solid #D21034; z-index: 100; }}
        #start {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>CLICK TO START ENGINE & ENABLE SOUND</p>
    </div>
    <div id="dash">
        <div>{OWNER}</div>
        <div style="font-size:24px;">SPEED: <span id="sp">0</span> MPH</div>
    </div>
    <script>
        let scene, camera, renderer, wheel, hands, road = [], speed = 0, tx = 0, targetX = 0, osc;
        function init() {{
            let ctx = new (window.AudioContext || window.webkitAudioContext)();
            osc = ctx.createOscillator(); let g = ctx.createGain();
            osc.type = 'sawtooth'; g.gain.value = 0.03; osc.connect(g); g.connect(ctx.destination); osc.start();

            scene = new THREE.Scene(); scene.background = new THREE.Color(0x87CEEB);
            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 10000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            scene.add(new THREE.AmbientLight(0xffffff, 1));

            // Steering Wheel & Hands
            wheel = new THREE.Group();
            let wM = new THREE.Mesh(new THREE.TorusGeometry(3.5, 0.5, 10, 40), new THREE.MeshBasicMaterial({{color: 0x222222}}));
            wheel.add(wM);
            let hM = new THREE.MeshBasicMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(1.5, 3, 1), hM); L.position.set(-3.5, -0.5, 1);
            let R = L.clone(); R.position.set(3.5, -0.5, 1);
            wheel.add(L); wheel.add(R);
            wheel.position.set(0, 7, -6); wheel.rotation.x = 1.1; scene.add(wheel);

            // Road Segments
            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(2000, 200), new THREE.MeshBasicMaterial({{color: 0x3d7a33}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(120, 200), new THREE.MeshBasicMaterial({{color: 0x222222}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(4, 60), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);
                
                // Add simple houses on the landscape
                if(i%8==0) {{
                    let h = new THREE.Mesh(new THREE.BoxGeometry(30, 20, 30), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
                    h.position.set(i%16==0?150:-150, 10, 0); s.add(h);
                }}
                s.position.z = -i * 200; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ if(e.key=='ArrowUp') speed += 0.001; if(e.key=='ArrowLeft') targetX -= 3; if(e.key=='ArrowRight') targetX += 3; }});
            animate();
        }}

        function animate() {{
            requestAnimationFrame(animate);
            speed *= 0.99; tx += (targetX - tx) * 0.1;
            wheel.position.x = tx; wheel.rotation.z = (targetX - tx) * -0.1;
            camera.position.set(tx, 12, 0); camera.lookAt(tx, 10, -100);
            road.forEach(s => {{ s.position.z += speed * 2500; if(s.position.z > 400) s.position.z -= 100 * 200; }});
            document.getElementById('sp').innerText = Math.round(speed * 20000);
            if(osc) osc.frequency.value = 20 + (speed * 9000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=800)
