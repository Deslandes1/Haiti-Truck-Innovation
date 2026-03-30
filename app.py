import streamlit as st
import streamlit.components.v1 as components

# --- OWNER & PROJECT DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Pro - Realistic Driver", layout="wide")

# --- REAL-WORLD SIMULATION ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #87CEEB; font-family: 'Arial', sans-serif; }}
        
        #gui {{
            position: absolute; top: 20px; left: 20px; 
            display: flex; flex-direction: column; gap: 10px; z-index: 100;
        }}
        .btn {{
            padding: 12px 20px; background: #D21034; color: white; border: 2px solid #fff;
            cursor: pointer; font-weight: bold; border-radius: 5px; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        }}
        #dashboard {{
            position: absolute; bottom: 0; width: 100%; height: 160px;
            background: #1a1a1a; border-top: 5px solid #333;
            display: flex; justify-content: space-around; align-items: center;
            color: #00FF41; z-index: 10;
        }}
        #start-screen {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.95); display: flex; flex-direction: column;
            justify-content: center; align-items: center; color: white; z-index: 200;
            text-align: center; cursor: pointer;
        }}
    </style>
</head>
<body>

    <div id="start-screen" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px; margin:0;">🇭🇹 {COMPANY}</h1>
        <h2 style="color:#FFD700;">REALISTIC DRIVER & SOUND SIMULATOR</h2>
        <p style="font-size:18px;">CLICK TO START THE DIESEL ENGINE</p>
    </div>

    <div id="gui">
        <button class="btn" onclick="toggleView()">TOGGLE VIEW (V)</button>
        <button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button>
    </div>

    <div id="dashboard">
        <div style="text-align:center;">SPEED<br><span id="speed-val" style="font-size:40px;">0</span> MPH</div>
        <div style="text-align:center; color:white;"><b>{OWNER}</b><br><span id="mode-txt">CABIN MODE</span></div>
        <div style="text-align:center;">GEAR<br><span id="gear-val" style="font-size:30px;">N</span></div>
    </div>

    <script>
        let scene, camera, renderer, truck, steeringWheel, hands, roadSegments = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let isNight = false, isCabin = true;
        let audioCtx, osc, gainNode;

        function init() {{
            // AUDIO SYSTEM
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(20, audioCtx.currentTime);
            gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
            osc.connect(gainNode); gainNode.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 1000, 5000);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 1, 10000);
            
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            const sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(100, 1000, 100);
            scene.add(sun);
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));

            // --- TRUCK MODEL ---
            truck = new THREE.Group();
            let bodyMat = new THREE.MeshPhongMaterial({{color: 0x00209F}});
            let cab = new THREE.Mesh(new THREE.BoxGeometry(12, 14, 15), bodyMat);
            cab.position.y = 7;
            truck.add(cab);
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(12, 16, 55), new THREE.MeshPhongMaterial({{color: 0xeeeeee}}));
            trailer.position.set(0, 8, 40);
            truck.add(trailer);
            scene.add(truck);

            // --- STEERING WHEEL & HANDS ---
            steeringWheel = new THREE.Group();
            let wheelRing = new THREE.Mesh(new THREE.TorusGeometry(4.5, 0.7, 16, 100), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            steeringWheel.add(wheelRing);
            
            // SIMULATED HANDS
            hands = new THREE.Group();
            let handMat = new THREE.MeshPhongMaterial({{color: 0x5c4033}}); // Driver skin tone
            let leftHand = new THREE.Mesh(new THREE.CapsuleGeometry(1, 4, 4, 8), handMat);
            leftHand.position.set(-4.5, 0, 1);
            let rightHand = leftHand.clone();
            rightHand.position.set(4.5, 0, 1);
            hands.add(leftHand); hands.add(rightHand);
            steeringWheel.add(hands);

            steeringWheel.position.set(0, 10, -8);
            steeringWheel.rotation.x = Math.PI/3.5;
            scene.add(steeringWheel);

            // --- LANDSCAPE GENERATION ---
            const roadMat = new THREE.MeshPhongMaterial({{color: 0x222222}});
            for(let i=0; i<150; i++) {{
                let seg = new THREE.Group();
                
                // Grass
                let grass = new THREE.Mesh(new THREE.PlaneGeometry(3000, 150), new THREE.MeshPhongMaterial({{color: 0x3d7a33}}));
                grass.rotation.x = -Math.PI/2;
                seg.add(grass);

                // Road
                let road = new THREE.Mesh(new THREE.PlaneGeometry(180, 150), roadMat);
                road.rotation.x = -Math.PI/2;
                road.position.y = 0.1;
                seg.add(road);

                // Yellow Center Line
                let line = new THREE.Mesh(new THREE.PlaneGeometry(5, 60), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                line.rotation.x = -Math.PI/2;
                line.position.set(0, 0.2, 0);
                seg.add(line);

                // Buildings & Palms (The Landscape)
                if(i % 10 == 0) {{
                    let house = new THREE.Mesh(new THREE.BoxGeometry(30, 20, 30), new THREE.MeshPhongMaterial({{color: i%20==0?0xD21034:0x00209F}}));
                    house.position.set(i%20==0?200:-200, 10, 0);
                    seg.add(house);
                    
                    let palm = new THREE.Mesh(new THREE.CylinderGeometry(1, 2, 40), new THREE.MeshPhongMaterial({{color: 0x4d3319}}));
                    palm.position.set(i%20==0?150:-150, 20, 40);
                    seg.add(palm);
                }}

                seg.position.z = -i * 150;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            window.addEventListener('keydown', e => keys[e.code] = true);
            window.addEventListener('keyup', e => keys[e.code] = false);
            animate();
        }}

        function toggleView() {{
            isCabin = !isCabin;
            document.getElementById('mode-txt').innerText = isCabin ? "CABIN MODE" : "TRUCK MODE";
        }}

        function toggleTime() {{
            isNight = !isNight;
            scene.background = new THREE.Color(isNight ? 0x000814 : 0x87CEEB);
            scene.fog.color = new THREE.Color(isNight ? 0x000814 : 0x87CEEB);
        }}

        function animate() {{
            requestAnimationFrame(animate);
            
            if (keys['ArrowUp']) speed += 0.0006;
            else speed *= 0.993; // Release to slow down naturally
            if (speed < 0) speed = 0;

            if (keys['ArrowLeft']) targetX -= 2.5;
            if (keys['ArrowRight']) targetX += 2.5;
            truckX += (targetX - truckX) * 0.08;
            
            // Hands move with wheel
            steeringWheel.rotation.z = (targetX - truckX) * -0.5;
            time += speed * 10;

            // Camera Lockdown (No swinging)
            if(isCabin) {{
                camera.position.set(truckX, 15, -2);
                camera.lookAt(truckX, 12, -200);
                steeringWheel.position.x = truckX;
                steeringWheel.visible = true;
                truck.visible = false;
            }} else {{
                camera.position.set(truckX, 70, 300);
                camera.lookAt(truckX, 20, -100);
                steeringWheel.visible = false;
                truck.visible = true;
                truck.position.x = truckX;
            }}

            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 1500; 
                if(seg.position.z > 1000) seg.position.z -= 150 * 150;
                
                let zPos = seg.position.z - (time * 80);
                let curveX = 0;
                if (zPos < -20000 && zPos > -35000) {{
                    curveX = Math.sin((zPos + 20000) * 0.0002) * 1000;
                }}
                seg.position.x = curveX;
            }});

            // RPM / Sound Update
            if(osc) {{
                let enginePitch = 20 + (speed * 6000);
                osc.frequency.setTargetAtTime(enginePitch, audioCtx.currentTime, 0.1);
                gainNode.gain.setTargetAtTime(speed > 0 ? 0.08 : 0.02, audioCtx.currentTime, 0.1);
            }}

            document.getElementById('speed-val').innerText = Math.round(speed * 12000);
            document.getElementById('gear-val').innerText = speed > 0.008 ? "D" : (speed > 0 ? "1" : "N");
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
