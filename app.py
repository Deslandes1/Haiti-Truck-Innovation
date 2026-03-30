import streamlit as st
import streamlit.components.v1 as components

# --- OWNER DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
EMAIL = "deslandes78@gmail.com"
PHONE = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- THE UNIFIED RACING ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: 'Arial Black', sans-serif; }}
        #hud {{ 
            position: absolute; top: 20px; left: 20px; 
            background: rgba(0,32,159,0.9); padding: 15px; border-radius: 5px; 
            color: white; border-left: 10px solid #D21034; z-index: 10;
        }}
        #speedo {{
            position: absolute; bottom: 40px; right: 40px;
            color: #00FF41; font-size: 80px; text-shadow: 3px 3px #000;
        }}
        #start-screen {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.9);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="start-screen" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <p>CLICK TO START RACING & IGNITE EXHAUST SMOKE</p>
    </div>

    <div id="hud">
        <div style="font-size: 18px;">{OWNER}</div>
        <div style="font-size: 11px; color: #FFD700;">{COMPANY} FOUNDER</div>
        <div style="font-size: 11px;">{EMAIL}</div>
        <div style="font-size: 11px;">{PHONE}</div>
    </div>

    <div id="speedo"><span id="sp">00</span><span style="font-size:25px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], smokeParticles = [], speed = 0, truckX = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            // Engine Sound
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(42, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 100, 800);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 2000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
            let sun = new THREE.DirectionalLight(0xffffff, 1);
            sun.position.set(50, 200, 50);
            scene.add(sun);

            // --- THE RACING ROAD & ENVIRONMENT ---
            for(let i=0; i<60; i++) {{
                let seg = new THREE.Group();
                
                // Asphalt
                let road = new THREE.Mesh(new THREE.PlaneGeometry(80, 40), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Racing Stripes (Red/White Curbs)
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(10, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-45, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(45, 0.2, 0);
                seg.add(curbR);

                // MOUNTAINS AND TREES ON SIDES
                if(i % 5 == 0) {{
                    let mt = new THREE.Mesh(new THREE.ConeGeometry(20, 40, 4), new THREE.MeshPhongMaterial({{color: 0x3d4d3d}}));
                    mt.position.set(i%10==0?90:-90, 15, 0);
                    seg.add(mt);
                }}

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE TRUCK MODEL ---
            truck = new THREE.Group();
            let paint = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 80}});
            
            // Nose & Cab
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3, 6), paint);
            nose.position.set(0, 1.5, 6);
            truck.add(nose);

            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), paint);
            cab.position.set(0, 2.75, 1);
            truck.add(cab);

            // HAITIAN FLAG
            let flag = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flag.position.set(2.15, 4.5, 1); flag.rotation.y = Math.PI/2;
            truck.add(flag);

            // DUAL EXHAUST STACKS
            let stackGeo = new THREE.CylinderGeometry(0.2, 0.2, 8);
            let chrome = new THREE.MeshPhongMaterial({{color: 0xaaaaaa, shininess: 150}});
            let s1 = new THREE.Mesh(stackGeo, chrome); s1.position.set(1.8, 5, 0.5);
            let s2 = new THREE.Mesh(stackGeo, chrome); s2.position.set(-1.8, 5, 0.5);
            truck.add(s1); truck.add(s2);

            // Visible tires
            let tireGeo = new THREE.CylinderGeometry(1.2, 1.2, 1, 16);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x000000}});
            [[-2.1,1,4.5], [2.1,1,4.5], [-2.1,1,1], [2.1,1,1], [-2.1,1,-12], [2.1,1,-12]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            // White Trailer
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.2, 6, 28), new THREE.MeshPhongMaterial({{color: 0xEEEEEE}}));
            trailer.position.set(0, 4.1, -12);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function createSmoke() {{
            if(speed < 0.005) return;
            let pGeo = new THREE.SphereGeometry(0.3, 4, 4);
            let pMat = new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.6}});
            let p = new THREE.Mesh(pGeo, pMat);
            
            // Set start at exhaust top
            let side = Math.random() > 0.5 ? 1.8 : -1.8;
            p.position.set(truckX + side, 9, -speed * 10);
            scene.add(p);
            smokeParticles.push({{ mesh: p, life: 1.0 }});
        }}

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp']) speed += 0.002; 
            if (keys['ArrowDown']) speed -= 0.003;
            if (keys['ArrowLeft']) truckX -= 0.8;
            if (keys['ArrowRight']) truckX += 0.8;
            
            speed *= 0.992;
            if(truckX < -38) truckX = -38; if(truckX > 38) truckX = 38;
            truck.position.x = truckX;

            // Loop road segments
            roadSegments.forEach(seg => {{
                seg.position.z += speed * 180; 
                if(seg.position.z > 80) seg.position.z -= 60 * 40;
            }});

            // Smoke logic
            createSmoke();
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.mesh.position.z += speed * 90; // Smoke drifts back
                p.mesh.position.y += 0.1;
                p.life -= 0.02;
                p.mesh.material.opacity = p.life;
                if(p.life <= 0) {{
                    scene.remove(p.mesh);
                    smokeParticles.splice(i, 1);
                }}
            }}

            wheels.forEach(w => w.rotation.x += speed * 6);
            if(osc) osc.frequency.setTargetAtTime(42 + (speed * 1600), audioCtx.currentTime, 0.1);

            camera.position.set(truckX * 0.3, 22, 65);
            camera.lookAt(truckX, 6, 0);

            document.getElementById('sp').innerText = Math.round(speed * 2500);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
