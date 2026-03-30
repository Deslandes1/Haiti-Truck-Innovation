import streamlit as st
import streamlit.components.v1 as components

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Iron Cabin", layout="wide")

sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }}
        #hud {{ position: absolute; bottom: 0; width: 100%; height: 100px; background: #080808; color: #00FF41; display: flex; justify-content: space-around; align-items: center; border-top: 4px solid #D21034; z-index: 50; }}
        #start {{ position: absolute; width: 100%; height: 100%; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 200; cursor: pointer; }}
        #crash {{ position: absolute; width: 100%; height: 100%; background: rgba(210, 16, 52, 0.9); color: white; display: none; flex-direction: column; justify-content: center; align-items: center; z-index: 300; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>IRON-CLAD CABIN LOCK | EXPRESSIVE SIGNS</p>
        <h2 style="background:#00209F; padding:10px 40px; border-radius:5px;">START ENGINE</h2>
    </div>

    <div id="crash">
        <h1>💥 CABIN INTACT - WORLD RESET</h1>
        <button style="padding:15px; cursor:pointer;" onclick="location.reload()">RESTART</button>
    </div>

    <div id="hud">
        <div>DRIVER: <b>{OWNER}</b></div>
        <div style="font-size:24px;">SPEED: <span id="sp">0</span> MPH</div>
        <div style="font-size:24px;">GEAR: <span style="color:#fff;">[D]</span></div>
    </div>

    <script>
        let scene, camera, renderer, cabin, wheel, roadGroup, roadSegments = [], speed = 0, roadX = 0, targetRoadX = 0;
        let isCrashed = false, audioCtx, engineOsc, engineGain;

        function init() {{
            // --- DIESEL AUDIO ---
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            engineOsc = audioCtx.createOscillator(); engineGain = audioCtx.createGain();
            engineOsc.type = 'triangle'; engineGain.gain.value = 0.12;
            engineOsc.connect(engineGain); engineGain.connect(audioCtx.destination); engineOsc.start();

            // --- 3D SETUP ---
            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 20000);
            
            camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 60000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 1.6); scene.add(amb);

            // --- THE IRON CABIN (STAYS STILL) ---
            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            
            // Dashboard (Centered)
            let dash = new THREE.Mesh(new THREE.BoxGeometry(400, 50, 100), cMat);
            dash.position.set(0, -35, -80);
            cabin.add(dash);

            // Big Circular Steering Wheel (Centered with driver seat at -60)
            wheel = new THREE.Group();
            let wRing = new THREE.Mesh(new THREE.TorusGeometry(18, 3.5, 32, 128), new THREE.MeshPhongMaterial({{color: 0x000}}));
            wheel.add(wRing);
            wheel.position.set(-60, 20, -100); wheel.rotation.x = 1.55; 
            cabin.add(wheel);

            // Symmetrical Pillars
            let pL = new THREE.Mesh(new THREE.BoxGeometry(10, 250, 10), cMat);
            pL.position.set(-180, 80, -60); pL.rotation.z = 0.04;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 180; pR.rotation.z = -0.04;
            cabin.add(pR);

            // This ensures the cabin is always in front of the camera
            scene.add(cabin);

            // --- THE MOVING WORLD ---
            roadGroup = new THREE.Group();
            scene.add(roadGroup);

            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(25000, 1200), new THREE.MeshPhongMaterial({{color: 0x228B22}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(800, 1200), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                gr.rotation.x = rd.rotation.x = -Math.PI/2;
                s.add(gr); s.add(rd);

                // Add Objects on Grass
                if(i % 7 == 0) {{
                    let side = (i % 14 == 0) ? 900 : -900;
                    if(i % 21 == 0) {{ // Restaurant
                        let res = new THREE.Mesh(new THREE.BoxGeometry(350, 180, 300), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                        res.position.set(side * 1.6, 90, 0); s.add(res);
                    }} else {{ // Signs
                        let sign = new THREE.Mesh(new THREE.CylinderGeometry(35, 35, 5, 8), new THREE.MeshPhongMaterial({{color: (i%2==0)? 0xFF0000 : 0xFFFFFF}}));
                        sign.position.set(side, 120, 0); sign.rotation.x = Math.PI/2;
                        s.add(sign);
                    }}
                }}

                s.position.z = -i * 1200; roadGroup.add(s); roadSegments.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.007; 
                if(e.key=='ArrowLeft') targetRoadX += 45; 
                if(e.key=='ArrowRight') targetRoadX -= 45;
            }});
            animate();
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            speed *= 0.993; roadX += (targetRoadX - roadX) * 0.1;
            
            roadSegments.forEach(seg => {{ 
                seg.position.z += speed * 25000; 
                if(seg.position.z > 5000) seg.position.z -= 100 * 1200; 
            }});

            // Move the world, NOT the cabin
            roadGroup.position.x = roadX; 
            wheel.rotation.z = (roadX - targetRoadX) * 0.025;
            
            // Lock Camera Position (Driver offset at -60)
            camera.position.set(-60, 80, 150); 
            camera.lookAt(-60, 50, -1200);
            
            // FORCE Cabin to stay stuck to the camera view
            cabin.position.copy(camera.position);
            cabin.rotation.copy(camera.rotation);
            cabin.translateZ(-180); cabin.translateY(-60);

            document.getElementById('sp').innerText = Math.round(speed * 120000);
            if(engineOsc) engineOsc.frequency.setTargetAtTime(22 + (speed * 28000), audioCtx.currentTime, 0.1);

            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
