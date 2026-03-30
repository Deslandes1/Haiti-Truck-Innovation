import streamlit as st
import streamlit.components.v1 as components

# --- MANDATORY CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
EMAIL = "deslandes78@gmail.com"
PHONE = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- RACING WORLD ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #050505; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #info-panel {{ 
            position: absolute; top: 15px; left: 15px; 
            background: rgba(0,32,159,0.9); padding: 15px; border-radius: 5px; 
            color: white; border-bottom: 4px solid #D21034; z-index: 10;
        }}
        #speed-hud {{
            position: absolute; bottom: 30px; right: 30px;
            color: #00FF41; font-size: 80px; text-shadow: 2px 2px #000;
        }}
        #click-to-play {{
            position: absolute; width:100%; height:100%; background: rgba(0,0,0,0.8);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="click-to-play" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY} RACING</h1>
        <p>CLICK TO DEPLOY TRUCK & START ENGINE SOUND</p>
    </div>

    <div id="info-panel">
        <div style="font-size: 18px; font-weight: bold;">{OWNER}</div>
        <div style="font-size: 12px; color: #ccc;">Founder of {COMPANY}</div>
        <div style="font-size: 12px;">{EMAIL}</div>
        <div style="font-size: 12px;">WhatsApp: {PHONE}</div>
    </div>

    <div id="speed-hud"><span id="sp">00</span><span style="font-size:20px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], speed = 0, angle = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            // Audio setup for diesel engine
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(45, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a); // Dark racing sky
            scene.fog = new THREE.Fog(0x0a0a0a, 50, 500);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 1000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.5));
            let sun = new THREE.DirectionalLight(0xffffff, 1);
            sun.position.set(10, 50, 10);
            scene.add(sun);

            // --- THE RACING LANDSCAPE ---
            for(let i=0; i<40; i++) {{
                let seg = new THREE.Group();
                // Asphalt
                let road = new THREE.Mesh(new THREE.PlaneGeometry(60, 40), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Racing Curbs (Red/White)
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(8, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-34, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(34, 0.2, 0);
                seg.add(curbR);

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE SEMI-TRUCK ---
            truck = new THREE.Group();
            let bodyMat = new THREE.MeshPhongMaterial({{color: 0x00209F}}); // Blue Cab
            
            // Long Nose
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.5, 3, 6), bodyMat);
            nose.position.set(0, 1.5, 5);
            truck.add(nose);

            let cab = new THREE.Mesh(new THREE.BoxGeometry(4, 5.5, 5), bodyMat);
            cab.position.set(0, 2.75, 0);
            truck.add(cab);

            // Haitian Flag (Side of Cab)
            let flag = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flag.position.set(2.05, 4.5, 1);
            flag.rotation.y = Math.PI/2;
            truck.add(flag);

            // Visible tires
            let tireGeo = new THREE.CylinderGeometry(1.2, 1.2, 1, 12);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x000000}});
            [[-2,1,4],[2,1,4], [-2,1,0],[2,1,0], [-2,1,-12],[2,1,-12]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            // White Trailer
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.2, 6, 28), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 4, -13);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp']) speed += 0.0015; 
            if (keys['ArrowDown']) speed -= 0.002;
            speed *= 0.992; // Friction

            // Ground movement logic
            roadSegments.forEach(seg => {{
                seg.position.z += speed * 150; 
                if(seg.position.z > 100) seg.position.z -= 40 * 40;
            }});

            // Wheel Spin
            wheels.forEach(w => w.rotation.x += speed * 5);

            // Engine Pitch
            if(osc) osc.frequency.setTargetAtTime(45 + (speed * 1200), audioCtx.currentTime, 0.1);

            camera.position.set(0, 20, 60);
            camera.lookAt(0, 5, 0);

            document.getElementById('sp').innerText = Math.round(speed * 2000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
