import streamlit as st
import streamlit.components.v1 as components

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Master Fix", layout="wide")

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
        <p>CABIN RE-CENTERED | EXPRESSIVE ENVIRONMENT LOADED</p>
        <h2 style="background:#00209F; padding:10px 40px; border-radius:5px;">ENGAGE MISSION</h2>
    </div>

    <div id="crash">
        <h1>💥 ACCIDENT DETECTED</h1>
        <button style="padding:15px; font-weight:bold; cursor:pointer;" onclick="location.reload()">REPAIR & RESTART</button>
    </div>

    <div id="hud">
        <div><b>{OWNER}</b></div>
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
            engineOsc.type = 'triangle'; engineGain.gain.value = 0.1;
            engineOsc.connect(engineGain); engineGain.connect(audioCtx.destination); engineOsc.start();

            // --- 3D SETUP ---
            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 18000);
            
            camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 50000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 1.5); scene.add(amb);

            // --- THE CABIN (STATIONARY ANCHOR) ---
            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            
            // Dashboard
            let dash = new THREE.Mesh(new THREE.BoxGeometry(350, 45, 100), cMat);
            dash.position.set(0, -25, -60);
            cabin.add(dash);

            // Large Circular Steering Wheel
            wheel = new THREE.Group();
            let wRing = new THREE.Mesh(new THREE.TorusGeometry(15, 3, 32, 128), new THREE.MeshPhongMaterial({{color: 0x000}}));
            wheel.add(wRing);
            wheel.position.set(-55, 15, -80); wheel.rotation.x = 1.55; 
            cabin.add(wheel);

            // A-Pillars (Symmetry Check)
            let pL = new THREE.Mesh(new THREE.BoxGeometry(8, 200, 8), cMat);
            pL.position.set(-150, 50, -40); pL.rotation.z = 0.05;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 150; pR.rotation.z = -0.05;
            cabin.add(pR);

            scene.add(cabin);

            // --- THE MOVING WORLD ---
            roadGroup = new THREE.Group();
            scene.add(roadGroup);

            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(20000, 1000), new THREE.MeshPhongMaterial({{color: 0x228B22}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(700, 1000), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                gr.rotation.x = rd.rotation.x = -Math.PI/2;
                s.add(gr); s.add(rd);

                // Add Expressive Objects
                if(i % 6 == 0) {{
                    let side = (i % 12 == 0) ? 800 : -800;
                    if(i % 18 == 0) {{ // Restaurant
                        let res = new THREE.Mesh(new THREE.BoxGeometry(300, 150, 250), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                        res.position.set(side * 1.5, 75, 0); s.add(res);
                    }} else if (i % 12 == 0) {{ // Stop Sign
                        let sign = new THREE.Mesh(new THREE.CylinderGeometry(30, 30, 5, 8), new THREE.MeshPhongMaterial({{color: 0xFF0000}}));
                        sign.position.set(side, 100, 0); sign.rotation.x = Math.PI/2;
                        s.add(sign);
                    }} else {{ // Speed Sign
                        let board = new THREE.Mesh(new THREE.BoxGeometry(40, 60, 5), new THREE.MeshPhongMaterial({{color: 0xFFFFFF}}));
                        board.position.set(side, 80, 0); s.add(board);
                    }}
                }}

                s.position.z = -i * 1000; roadGroup.add(s); roadSegments.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.006; 
                if(e.key=='ArrowLeft') targetRoadX += 35; 
                if(e.key=='ArrowRight') targetRoadX -= 35;
            }});
            animate();
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            speed *= 0.994; roadX += (targetRoadX - roadX) * 0.1;
            
            roadSegments.forEach(seg => {{ 
                seg.position.z += speed * 20000; 
                if(seg.position.z > 4000) seg.position.z -= 100 * 1000; 
            }});

            roadGroup.position.x = roadX; 
            wheel.rotation.z = (roadX - targetRoadX) * 0.03;
            
            // Hard Lock Camera & Cabin to center
            camera.position.set(-55, 65, 120); 
            camera.lookAt(-55, 45, -1000);
            
            // Re-sync Cabin position to Camera
            cabin.position.copy(camera.position);
            cabin.rotation.copy(camera.rotation);
            cabin.translateZ(-150); cabin.translateY(-50);

            document.getElementById('sp').innerText = Math.round(speed * 110000);
            if(engineOsc) engineOsc.frequency.setTargetAtTime(20 + (speed * 25000), audioCtx.currentTime, 0.1);

            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
