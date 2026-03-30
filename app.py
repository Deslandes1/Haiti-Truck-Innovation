import streamlit as st
import streamlit.components.v1 as components

# --- SYSTEM CONFIG & CREDENTIALS ---
COMPANY = "EduHumanity"
GAME_NAME = "Haiti Truck Innovation"
OWNER = "Gesner Deslandes"
VERSION = "2026.11 PRO"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- THE STURDY 3D SIMULATION ENGINE ---
# This uses Three.js for robust rendering of textures, lighting, and heavy environments.
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #hud {{ 
            position: absolute; bottom: 30px; left: 30px; 
            background: rgba(0,0,0,0.8); padding: 25px; border-radius: 12px; 
            color: white; border-top: 8px solid #D21034; pointer-events: none;
            min-width: 250px;
        }}
        #start-btn {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.9);
            color: white; display: flex; flex-direction: column; justify-content: center;
            align-items: center; z-index: 9999; cursor: pointer; text-align: center;
        }}
    </style>
</head>
<body>
    <div id="start-btn" onclick="startEngine();">
        <h1 style="color:#00209F; font-size: 60px;">🇭🇹 {GAME_NAME}</h1>
        <p>[ CLICK TO DEPLOY FULL USA LANDSCAPE & IGNITE EXHAUSTS ]</p>
    </div>

    <div id="hud">
        <div style="font-size: 14px; letter-spacing: 2px; color:#aaa;">GROUND SPEED</div>
        <div style="font-size: 60px; color: #00FF41; line-height:1; text-shadow: 2px 2px #000;">
            <span id="sp">00</span> <span style="font-size: 16px;">MPH</span>
        </div>
        <div style="margin-top:20px; color:#D21034; border-top: 1px solid #333; padding-top:10px; font-size: 12px;">
            OPERATOR: {OWNER}
        </div>
    </div>

    <script>
        let scene, camera, renderer, truck, speed = 0, angle = 0, keys = {{}}, attached = false;
        let roadSegments = [], worldSegments = [], exhaustParticles = [];
        let audioCtx, oscillator, gainNode;

        function startEngine() {{
            document.getElementById('start-btn').style.display='none';
            initAudio();
            init();
        }}

        function initAudio() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            gainNode = audioCtx.createGain();
            oscillator.type = 'sawtooth';
            oscillator.frequency.setValueAtTime(45, audioCtx.currentTime); 
            gainNode.gain.setValueAtTime(0.04, audioCtx.currentTime);
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
        }}

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB); 
            scene.fog = new THREE.Fog(0x87CEEB, 150, 900);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 1, 3000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            const ambient = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambient);
            const sun = new THREE.DirectionalLight(0xffffff, 1);
            sun.position.set(100, 200, 100);
            scene.add(sun);

            // --- THE FULL ENVIRONMENTAL LANDSCAPE ---
            worldSegments = new THREE.Group();
            
            // Endless Grass Land
            const grass = new THREE.Mesh(new THREE.PlaneGeometry(10000, 10000), new THREE.MeshPhongMaterial({{color: 0x348C31}}));
            grass.rotation.x = -Math.PI / 2;
            worldSegments.add(grass);

            // The Highway (Textured Asphalt)
            const roadGeo = new THREE.PlaneGeometry(50, 20000);
            const roadMat = new THREE.MeshPhongMaterial({{color: 0x1A1A1B}});
            const road = new THREE.Mesh(roadGeo, roadMat);
            road.rotation.x = -Math.PI / 2;
            road.position.y = 0.1;
            worldSegments.add(road);

            // Road Markings (Yellow USA centerline)
            for(let i=0; i<400; i++) {{
                const line = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 12), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                line.rotation.x = -Math.PI / 2;
                line.position.set(0, 0.15, -i * 50);
                worldSegments.add(line);
            }}

            // passing by Community States & mountains with Trees
            for(let i=0; i<150; i++) {{
                // COMMUNITY STATE (Housing Block)
                if (i % 8 === 0) {{
                    let community = new THREE.Group();
                    let color = i % 16 === 0 ? 0xD21034 : 0xEEEEEE;
                    let building = new THREE.Mesh(new THREE.BoxGeometry(10, 8, 15), new THREE.MeshPhongMaterial({{color: color}}));
                    community.add(building);
                    community.position.set(i % 16 === 0 ? 60 : -60, 4, -i * 80);
                    worldSegments.add(community);
                }}
                
                // MOUNTAINS WITH TREES (Passable horizon)
                if (i % 2 === 0) {{
                    let foliage = new THREE.Group();
                    let trunkMat = new THREE.MeshPhongMaterial({{color: 0x4d2926}});
                    let leavesMat = new THREE.MeshPhongMaterial({{color: 0x143306}});
                    
                    let trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 6), trunkMat);
                    let leaves = new THREE.Mesh(new THREE.ConeGeometry(5, 12, 8), leavesMat); leaves.position.y = 6;
                    foliage.add(trunk); foliage.add(leaves);
                    
                    let range = i % 4 === 0 ? 80 : -80;
                    foliage.position.set(range + (Math.random()*10 - 5), 3, -i * 100);
                    worldSegments.add(foliage);
                }}
            }}
            scene.add(worldSegments);

            // --- THE 18-WHEELER (Conventional USA Style) ---
            truck = new THREE.Group();
            const bodyMat = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 90}});
            
            // Long Nose Cab
            const nose = new THREE.Mesh(new THREE.BoxGeometry(3.5, 3.2, 5.5), bodyMat);
            nose.position.set(0, 1.6, 6);
            truck.add(nose);

            const cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), bodyMat);
            cab.position.set(0, 2.75, 1.5);
            truck.add(cab);

            // Chrome Details
            const chrome = new THREE.MeshPhongMaterial({{color: 0xEEEEEE, shininess: 150}});
            const grill = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.8, 0.2), chrome);
            grill.position.set(0, 1.4, 8.8);
            truck.add(grill);

            // DUAL EXHAUST STACKS (mounted on the front cab)
            const stackGeo = new THREE.CylinderGeometry(0.2, 0.2, 8);
            const s1 = new THREE.Mesh(stackGeo, chrome); s1.position.set(1.8, 5, 0.5);
            const s2 = new THREE.Mesh(stackGeo, chrome); s2.position.set(-1.8, 5, 0.5);
            truck.add(s1); truck.add(s2);

            // HAITIAN FLAG
            const flagGeo = new THREE.PlaneGeometry(1.5, 1);
            // Simulating a flag texture with color bands
            const flagMat = new THREE.MeshBasicMaterial({{color: 0x00209F, emissive: 0xD21034, emissiveIntensity: 0.2}});
            const flagHT = new THREE.Mesh(flagGeo, flagMat);
            flagHT.position.set(2.11, 4.5, 2);
            flagHT.rotation.y = Math.PI / 2;
            truck.add(flagHT);

            // Trailer (Standard 53ft)
            const trailer = new THREE.Mesh(new THREE.BoxGeometry(4, 5.5, 26), new THREE.MeshPhongMaterial({{color: 0xD21034}}));
            trailer.position.set(0, 2.75, -14);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        // Healthy Smoke Particle System
        function updateExhaust() {{
            if (speed > 0.005) {{
                // Create new particle
                const smokeGeo = new THREE.CylinderGeometry(0.2, 0.6, 1, 8);
                const smokeMat = new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.5}});
                const particle = new THREE.Mesh(smokeGeo, smokeMat);
                
                // Position at top of stacks
                let pos = truck.position.clone();
                let direction = new THREE.Vector3(1.8, 8, 0.5); // stack position
                if(Math.random()>0.5) direction.x *= -1; // other stack
                direction.applyEuler(truck.rotation);
                particle.position.addVectors(pos, direction);
                
                particle.userData = {{ age: 0 }};
                scene.add(particle);
                exhaustParticles.push(particle);
            }}

            // Update existing particles
            for(let i=exhaustParticles.length-1; i>=0; i--) {{
                let p = exhaustParticles[i];
                p.position.y += 0.2 + (speed * 0.5); // healthy smoke rises
                p.scale.addScalar(0.01);
                p.material.opacity *= 0.96; // dissipate
                p.userData.age++;
                if(p.userData.age > 80 || p.material.opacity < 0.01) {{
                    scene.remove(p);
                    exhaustParticles.splice(i, 1);
                }}
            }}
        }}

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // Heavy Rig Physics
            if (keys['ArrowUp'] || keys['KeyW']) speed += 0.0007; 
            if (keys['ArrowDown'] || keys['KeyS']) speed -= 0.001;
            if (keys['Enter']) speed *= 0.94; // Air Brakes

            speed *= 0.996; // Rolling Friction
            if (Math.abs(speed) > 0.001) {{
                if (keys['ArrowLeft'] || keys['KeyA']) angle += 0.008;
                if (keys['ArrowRight'] || keys['KeyD']) angle -= 0.008;
            }}

            truck.rotation.y = angle;
            truck.position.x += Math.sin(angle) * speed * 75;
            truck.position.z += Math.cos(angle) * speed * 75;

            // Recycle world Group (Infinity Loop)
            // No void, the world just continues.
            worldSegments.position.copy(truck.position);
            worldSegments.position.x = 0; // Lock to road
            worldSegments.rotation.y = 0; // No spinning road

            // update Exhaust smoke
            updateExhaust();

            // Engine Audio Sync
            if(oscillator) {{
                let pitch = 45 + (Math.abs(speed) * 900);
                oscillator.frequency.setTargetAtTime(pitch, audioCtx.currentTime, 0.1);
            }}

            // Follow Camera (Console Game Style)
            camera.position.x = truck.position.x - Math.sin(angle) * 60;
            camera.position.z = truck.position.z - Math.cos(angle) * 60;
            camera.position.y = 22;
            camera.lookAt(truck.position.x, 5, truck.position.z);

            document.getElementById('sp').innerText = Math.round(Math.abs(speed * 1600));
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
