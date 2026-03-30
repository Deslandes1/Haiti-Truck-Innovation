import streamlit as st
import streamlit.components.v1 as components

# --- PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"

st.set_page_config(page_title="Haiti Truck - Expressive World", layout="wide")

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
        .label {{ position: absolute; color: white; background: rgba(0,0,0,0.5); padding: 2px 5px; font-size: 12px; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034;">🇭🇹 {COMPANY}</h1>
        <p>EXPRESSIVE WORLD: SIGNS & RESTAURANTS</p>
        <h2 style="background:#00209F; padding:10px 40px; border-radius:5px;">START ENGINE</h2>
    </div>

    <div id="crash">
        <h1>💥 COLLISION!</h1>
        <button style="padding:10px; cursor:pointer;" onclick="location.reload()">RESTART</button>
    </div>

    <div id="hud">
        <div>DRIVER: <b>{OWNER}</b></div>
        <div style="font-size:22px;">SPEED: <span id="sp">0</span> MPH</div>
        <div style="color:#FFD700;">LOCATION: <span id="loc">ON ROAD</span></div>
    </div>

    <script>
        let scene, camera, renderer, cabin, wheel, roadGroup, roadSegments = [], speed = 0, roadX = 0, targetRoadX = 0;
        let isCrashed = false, audioCtx, engineOsc, engineGain;

        function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            engineOsc = audioCtx.createOscillator(); engineGain = audioCtx.createGain();
            engineOsc.type = 'triangle'; engineGain.gain.value = 0.1;
            engineOsc.connect(engineGain); engineGain.connect(audioCtx.destination); engineOsc.start();

            scene = new THREE.Scene(); 
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1, 15000);
            
            camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 40000);
            renderer = new THREE.WebGLRenderer({{antialias: true}});
            renderer.setSize(window.innerWidth, window.innerHeight); document.body.appendChild(renderer.domElement);
            
            let amb = new THREE.AmbientLight(0xffffff, 1.4); scene.add(amb);

            // --- FIXED CABIN ---
            cabin = new THREE.Group();
            let cMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            let dash = new THREE.Mesh(new THREE.BoxGeometry(300, 40, 80), cMat);
            dash.position.set(0, -20, -50);
            cabin.add(dash);

            wheel = new THREE.Group();
            let wRing = new THREE.Mesh(new THREE.TorusGeometry(14, 2.8, 24, 128), new THREE.MeshPhongMaterial({{color: 0x000}}));
            wheel.add(wRing);
            wheel.position.set(-50, 10, -70); wheel.rotation.x = 1.55; 
            cabin.add(wheel);
            scene.add(cabin);

            // --- EXPRESSIVE WORLD ---
            roadGroup = new THREE.Group();
            scene.add(roadGroup);

            for(let i=0; i<100; i++) {{
                let s = new THREE.Group();
                let gr = new THREE.Mesh(new THREE.PlaneGeometry(15000, 800), new THREE.MeshPhongMaterial({{color: 0x228B22}}));
                let rd = new THREE.Mesh(new THREE.PlaneGeometry(600, 800), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                gr.rotation.x = rd.rotation.x = -Math.PI/2;
                s.add(gr); s.add(rd);

                // Add Objects on Grass
                if(i % 5 == 0) {{
                    let side = (i % 10 == 0) ? 600 : -600;
                    let type = i % 15;
                    
                    if(type == 0) {{ // RESTAURANT
                        let b = new THREE.Mesh(new THREE.BoxGeometry(250, 120, 200), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
                        let roof = new THREE.Mesh(new THREE.ConeGeometry(180, 80, 4), new THREE.MeshPhongMaterial({{color: 0x333}}));
                        roof.position.y = 100; roof.rotation.y = Math.PI/4;
                        let res = new THREE.Group(); res.add(b); res.add(roof);
                        res.position.set(side * 1.5, 60, 0); s.add(res);
                        s.label = "RESTAURANT";
                    }} else if (type == 5) {{ // STOP SIGN
                        let pole = new THREE.Mesh(new THREE.CylinderGeometry(2, 2, 100), new THREE.MeshPhongMaterial({{color: 0x777}}));
                        let sign = new THREE.Mesh(new THREE.CylinderGeometry(25, 25, 5, 8), new THREE.MeshPhongMaterial({{color: 0xFF0000}}));
                        sign.position.y = 50; sign.rotation.x = Math.PI/2;
                        let stop = new THREE.Group(); stop.add(pole); stop.add(sign);
                        stop.position.set(side * 0.8, 50, 0); s.add(stop);
                        s.label = "STOP";
                    }} else if (type == 10) {{ // SPEED LIMIT
                        let pole = new THREE.Mesh(new THREE.CylinderGeometry(2, 2, 80), new THREE.MeshPhongMaterial({{color: 0x777}}));
                        let board = new THREE.Mesh(new THREE.BoxGeometry(40, 50, 5), new THREE.MeshPhongMaterial({{color: 0xFFFFFF}}));
                        board.position.y = 40;
                        let limit = new THREE.Group(); limit.add(pole); limit.add(board);
                        limit.position.set(side * 0.8, 40, 0); s.add(limit);
                        s.label = "SPEED 45";
                    }}
                }}

                s.position.z = -i * 800; roadGroup.add(s); roadSegments.push(s);
            }}

            window.addEventListener('keydown', e => {{ 
                if(isCrashed) return;
                if(e.key=='ArrowUp') speed += 0.005; 
                if(e.key=='ArrowLeft') targetRoadX += 25; 
                if(e.key=='ArrowRight') targetRoadX -= 25;
            }});
            animate();
        }}

        function animate() {{
            if(isCrashed) return;
            requestAnimationFrame(animate);
            speed *= 0.995; roadX += (targetRoadX - roadX) * 0.1;
            
            roadSegments.forEach(seg => {{ 
                seg.position.z += speed * 18000; 
                if(seg.position.z > 3000) seg.position.z -= 100 * 800; 
            }});

            roadGroup.position.x = roadX; 
            wheel.rotation.z = (roadX - targetRoadX) * 0.05;
            
            camera.position.set(-50, 60, 100); 
            camera.lookAt(-50, 40, -800);
            cabin.position.copy(camera.position);
            cabin.rotation.copy(camera.rotation);
            cabin.translateZ(-130); cabin.translateY(-40);

            document.getElementById('sp').innerText = Math.round(speed * 95000);
            document.getElementById('loc').innerText = Math.abs(roadX + 50) < 300 ? "ON ROAD" : "OFF ROAD (GRASS)";
            if(engineOsc) engineOsc.frequency.setTargetAtTime(20 + (speed * 20000), audioCtx.currentTime, 0.1);

            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
