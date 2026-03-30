import streamlit as st
import streamlit.components.v1 as components

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Diesel Power", layout="wide")

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
        <p>DIESEL ENGINE SOUND ACTIVATED | BIG TRUCK MODE</p>
        <h2 style="background:#00209F; padding:10px 40px; border-radius:5px;">START ENGINE</h2>
    </div>

    <div id="crash">
        <h1>💥 TRUCK DAMAGED</h1>
        <button class="btn" onclick="location.reload()">REPAIR TRUCK</button>
    </div>

    <div id="hud">
        <div>DRIVER: <b>{OWNER}</b></div>
        <div style="font-size:22px;">SPEED: <span id="sp">0</span> MPH</div>
        <div style="font-size:22px;">GEAR: <span style="color:#fff;">[D]</span></div>
    </div>

    <script>
        let scene, camera, renderer, cabin, wheel, road = [], speed = 0, tx = 0, targetX = 0;
        let isCrashed = false, audioCtx, engineOsc, engineGain, noiseNode;

        function init() {{
            // --- DIESEL ENGINE AUDIO ENGINE ---
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            
            // Base Engine Rumble
            engineOsc = audioCtx.createOscillator();
            engineGain = audioCtx.createGain();
            engineOsc.type = 'triangle'; // Smoother, deeper rumble than sawtooth
            engineGain.gain.value = 0.15;
            
            // Add Engine Noise (Combustion sound)
            let bufferSize = 2 * audioCtx.sampleRate,
                noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate),
                output = noiseBuffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {{
                output[i] = Math.random() * 2 - 1;
            }}
            noiseNode = audioCtx.createBufferSource();
            noiseNode.buffer = noiseBuffer;
            noiseNode.loop = true;
            let noiseGain = audioCtx.createGain();
            noiseGain.gain.value = 0.05;

            // Filter for deep bass
            let filter = audioCtx.createBiquadFilter();
            filter.type = "lowpass";
            filter.frequency.value = 150;

            engineOsc.connect(filter);
            noiseNode.connect(filter);
            filter.connect(engineGain);
            engineGain.connect(audioCtx.destination);

            engineOsc.start();
            noiseNode.start();

            // --- 3D SCENE ---
            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 12000);
            
            camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 35000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 1.3); scene.add(amb);

            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            
            let dash = new THREE.Mesh(new THREE.BoxGeometry(220, 35, 60), cMat);
            dash.position.set(0, 5, -30);
            cabin.add(dash);

            // Circular Wheel (128 segments)
            wheel = new THREE.Group();
            let wRing = new THREE.Mesh(new THREE.TorusGeometry(12, 2.2, 24, 128), new THREE.MeshPhongMaterial({{color: 0x050505}}));
            wheel.add(wRing);
            let hM = new THREE.MeshPhongMaterial({{color: 0x5c4033}});
            let L = new THREE.Mesh(new THREE.BoxGeometry(4, 14, 4), hM); L.position.set(-12, 0, 1);
            let R = L.clone(); R.position.set(12, 0, 1);
            wheel.add(L); wheel.add(R);
            wheel.position.set(-40, 24, -45); wheel.rotation.x = 1.55; 
            cabin.add(wheel);

            // Gear Shifter
            let gear = new THREE.Group();
            let gB = new THREE.Mesh(new THREE.BoxGeometry(14, 10, 22), new THREE.MeshPhongMaterial({{color: 0x0a0a0a}}));
            let gS = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 14), new THREE.MeshPhongMaterial({{color: 0x999}}));
            gS.position.y = 7; gS.rotation.x = -0.4;
            gear.add(gB); gear.add(gS);
            gear.position.set(18, 12, -45);
            cabin.add(gear);

            let pL = new THREE.Mesh(new THREE.BoxGeometry(6, 140, 6), cMat);
            pL.position.set(-95, 60, -25); pL.rotation.z = 0.1;
            cabin.add(pL);
            let pR = pL.clone(); pR.position.x = 95; pR.rotation.z = -0.1;
            cabin.add(pR);

            scene.add(cabin);

            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(12000, 600), new THREE.MeshPhongMaterial({{color: 0x2d5a27}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(500, 600), new THREE.MeshPhongMaterial({{color: 0x151515}}));
                let ln = new THREE.Mesh(new THREE.PlaneGeometry(20, 250), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                gr.rotation.x = rd.rotation.x = ln.rotation.x = -Math.PI/2;
                rd.position.y = 0.1; ln.position.y = 0.2; s.add(gr); s.add(rd); s.add(ln);

                if(i%10==0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(180, 120, 180), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                    let side = (i%20==0)? 1100 : -1100;
                    house.position.set(side, 60, 0); s.add(house); s.houseX = side;
                }}
                s.position.z = -i * 600; scene.add(s); road.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.0035; 
                if(e.key=='ArrowLeft') targetX -= 14; 
                if(e.key=='ArrowRight') targetX += 14;
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
                if(Math.abs(seg.position.z) < 150 && seg.houseX && Math.abs(tx - seg.houseX) < 280) {{
                    isCrashed = true;
                    document.getElementById('crash').style.display = 'flex';
                    if(engineOsc) engineOsc.stop();
                    if(noiseNode) noiseNode.stop();
                }}
            }});

            cabin.position.x = tx; 
            wheel.rotation.z = (targetX - tx) * -0.2;
            
            camera.position.set(tx - 40, 45, 75); 
            camera.lookAt(tx - 40, 32, -600);

            document.getElementById('sp').innerText = Math.round(speed * 80000);
            
            // ENGINE AUDIO DYNAMICS
            if(engineOsc) {{
                // Base idle starts at 30Hz, increases with speed
                engineOsc.frequency.setTargetAtTime(30 + (speed * 15000), audioCtx.currentTime, 0.1);
                // Engine gets louder as you accelerate
                engineGain.gain.setTargetAtTime(0.15 + (speed * 20), audioCtx.currentTime, 0.1);
            }}

            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
