import streamlit as st
import streamlit.components.v1 as components

# --- PRO credentials & System Info ---
COMPANY = "EduHumanity"
GAME_NAME = "Haiti Truck Innovation"
OWNER = "Gesner Deslandes"
EMAIL = "deslandes78@gmail.com"
PHONE = "(509)-47385663"
VERSION = "2026.10 PRO"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- THE STURDY 3D SIMULATION ENGINE ---
# We use a refined Three.js setup to handle complex geometry like text textures.
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #hud {{ 
            position: absolute; top: 20px; right: 20px; 
            background: rgba(0,0,0,0.85); padding: 25px; border-radius: 12px; 
            color: white; border-top: 8px solid #D21034; pointer-events: none;
            min-width: 250px;
        }}
        #start-btn {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.95);
            color: white; display: flex; flex-direction: column; justify-content: center;
            align-items: center; z-index: 9999; cursor: pointer; text-align: center;
        }}
        .stat {{ color: #00FF41; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="start-btn" onclick="this.style.display='none'; init();">
        <h1 style="color:#00209F; font-size: 60px;">🇭🇹 {GAME_NAME}</h1>
        <p style="font-size: 20px; margin-top:0;">[ CLICK TO IGNITE DIESEL ENGINE & DEPLOY ]</p>
        <p style="font-size: 10px; color: #555;">Version {VERSION}</p>
    </div>

    <div id="hud">
        <div style="font-size: 18px; border-bottom: 2px solid #444; padding-bottom: 8px; margin-bottom: 12px; letter-spacing: 1px;">
            OPERATOR: <b>{OWNER}</b>
        </div>
        <div>System: <span class="stat">{GAME_NAME}</span></div>
        <div>Credentials: <span class="stat">{EMAIL}</span></div>
        <div>WhatsApp: <span class="stat">{PHONE}</span></div>
        <hr>
        <div style="font-size: 35px; text-align: center; color: #fff; text-shadow: 2px 2px #000;">
            <span id="sp">0</span> <span style="font-size: 16px;">MPH</span>
        </div>
    </div>

    <script>
        let scene, camera, renderer, truck, tires = [], speed = 0, angle = 0, keys = {{}};
        let audioCtx, oscillator, gainNode;

        function initAudio() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();
            oscillator.type = 'sawtooth'; // Heavy diesel rumble shape
            oscillator.frequency.setValueAtTime(38, audioCtx.currentTime); 
            gainNode.gain.setValueAtTime(0.06, audioCtx.currentTime);
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
        }}

        function init() {{
            initAudio();
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 100, 750);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 1, 2500);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
            const sun = new THREE.DirectionalLight(0xffffff, 1.3);
            sun.position.set(150, 200, 100);
            scene.add(sun);

            // --- THE LANDSCAPE (End the Void) ---
            // Grass Plains
            const grass = new THREE.Mesh(new THREE.PlaneGeometry(10000, 10000), new THREE.MeshPhongMaterial({{color: 0x348C31}}));
            grass.rotation.x = -Math.PI / 2;
            scene.add(grass);

            // Asphalt Road with Markings
            const road = new THREE.Mesh(new THREE.PlaneGeometry(60, 20000), new THREE.MeshPhongMaterial({{color: 0x222222}}));
            road.rotation.x = -Math.PI / 2;
            road.position.y = 0.1;
            scene.add(road);

            for(let i=0; i<300; i++) {{
                const line = new THREE.Mesh(new THREE.PlaneGeometry(2.5, 14), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                line.rotation.x = -Math.PI / 2;
                line.position.set(0, 0.2, -i * 60);
                scene.add(line);
            }}

            // --- THE HIGH-DETAIL 18-WHEELER ---
            truck = new THREE.Group();
            
            // The Conventional "Long Nose" Cab (Blue)
            const bodyMat = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 90}});
            
            const nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.2, 5.5), bodyMat);
            nose.position.set(0, 1.6, 6);
            truck.add(nose);

            const cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), bodyMat);
            cab.position.set(0, 2.75, 1);
            truck.add(cab);

            // Chrome Details (Grill, Pipes)
            const grillMat = new THREE.MeshPhongMaterial({{color: 0xaaaaaa, shininess:120}});
            const grill = new THREE.Mesh(new THREE.BoxGeometry(3.4, 3, 0.2), grillMat);
            grill.position.set(0, 1.5, 8.8);
            truck.add(grill);

            const stackGeo = new THREE.CylinderGeometry(0.2, 0.2, 8);
            const chromeMat = new THREE.MeshPhongMaterial({{color: 0xeeeeee, shininess:150}});
            const s1 = new THREE.Mesh(stackGeo, chromeMat); s1.position.set(1.7, 5, 0.5);
            const s2 = new THREE.Mesh(stackGeo, chromeMat); s2.position.set(-1.7, 5, 0.5);
            truck.add(s1); truck.add(s2);

            // HAITIAN FLAG
            const flagGeo = new THREE.PlaneGeometry(1.5, 0.9);
            // Simulating flag with red/blue bands and center coat of arms
            const flagMat = new THREE.MeshBasicMaterial({{color: 0x00209F, emissive: 0xD21034, emissiveIntensity: 0.2}});
            const flag = new THREE.Mesh(flagGeo, flagMat);
            flag.position.set(2.11, 4.5, 2);
            flag.rotation.y = Math.PI / 2;
            truck.add(flag);

            // WHEELS (Tires) with Visible Structure
            const tireGeo = new THREE.CylinderGeometry(1.2, 1.2, 1, 16);
            const tireMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            const hubMat = new THREE.MeshPhongMaterial({{color: 0x777777, shininess:100}});
            
            // Function to build a wheel assembly
            function createWheel(pos) {{
                let tire = new THREE.Mesh(tireGeo, tireMat);
                let hub = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 1.1, 8), hubMat);
                tire.add(hub); // Hub spins with tire
                tire.rotation.z = Math.PI / 2;
                tire.position.set(pos[0], pos[1], pos[2]);
                truck.add(tire);
                tires.push(tire); // Add to spin animation list
            }}

            const tirePositions = [
                [2, 1, 3.5], [-2, 1, 3.5], // Front
                [2, 1, 0], [-2, 1, 0],     // Drive 1
                [2, 1, -2.5], [-2, 1, -2.5], // Drive 2
                [2, 1, -13], [-2, 1, -13], // Trailer 1
                [2, 1, -15.5], [-2, 1, -15.5] // Trailer 2
            ];
            tirePositions.forEach(pos => createWheel(pos));

            // THE TRAILER (With Text Branding)
            const trailerGroup = new THREE.Group();
            
            // Standard 53' Reefer Box (White for best text contrast)
            const trailerMat = new THREE.MeshPhongMaterial({{color: 0xEEEEEE, shininess: 40}});
            const trailer = new THREE.Mesh(new THREE.BoxGeometry(4.2, 6, 28), trailerMat);
            trailerGroup.add(trailer);

            // text BRANDING (Haiti Truck Innovation)
            // We use a canvas texture because browsers handle rendering text onto textures efficiently.
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 1024; canvas.height = 256;
            context.fillStyle = '#EEEEEE'; context.fillRect(0, 0, canvas.width, canvas.height); // Matches trailer
            context.font = 'Bold 80px Impact'; context.fillStyle = '#00209F'; // Haiti Blue Text
            context.textAlign = 'center'; context.fillText("HAITI TRUCK INNOVATION", 512, 128);
            
            const textTexture = new THREE.CanvasTexture(canvas);
            const textMat = new THREE.MeshBasicMaterial({{map: textTexture, transparent: true}});
            
            const brandingGeo = new THREE.PlaneGeometry(16, 4);
            // Driver side text
            const brandingL = new THREE.Mesh(brandingGeo, textMat);
            brandingL.position.set(2.11, 0, -2); brandingL.rotation.y = Math.PI / 2;
            trailerGroup.add(brandingL);
            
            // Passenger side text
            const brandingR = new THREE.Mesh(brandingGeo, textMat);
            brandingR.position.set(-2.11, 0, -2); brandingR.rotation.y = -Math.PI / 2;
            trailerGroup.add(brandingR);

            trailerGroup.position.set(0, 4.25, -12);
            truck.add(trailerGroup);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // HEAVY TRUCK PHYSICS
            // Start slow (inertia) and need space to stop.
            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0007; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.001;
            if (keys['Enter']) speed *= 0.94; // Air Brakes

            speed *= 0.995; // Rolling Resistance
            
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.012;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.012;
            }}

            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 75;
            truck.position.z += Math.cos(angle) * speed * 75;

            // SPIN TIRES
            tires.forEach(t => t.rotation.x += speed * 1.5);

            // ENGINE AUDIO SYNC
            if(oscillator) {{
                let pitch = 38 + (Math.abs(speed) * 850);
                oscillator.frequency.setTargetAtTime(pitch, audioCtx.currentTime, 0.1);
            }}

            // FOLLOW CAMERA (Console Game Style)
            camera.position.set(truck.position.x - Math.sin(angle)*60, 25, truck.position.z - Math.cos(angle)*60);
            camera.lookAt(truck.position.x, 6, truck.position.z);

            // UPDATE HUD
            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 1600));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
