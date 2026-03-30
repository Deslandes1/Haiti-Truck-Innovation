import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- MANUAL TORQUE ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: sans-serif; }}
        #hud {{ 
            position: absolute; top: 20px; left: 20px; 
            background: rgba(0,32,159,0.9); padding: 20px; border-radius: 10px; 
            color: white; border-bottom: 5px solid #D21034; z-index: 10;
        }}
        #speedo {{
            position: absolute; bottom: 40px; right: 40px;
            color: #00FF41; font-size: 90px; font-weight: bold; text-shadow: 4px 4px #000;
        }}
        #start {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.95);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer; text-align: center;
        }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <h2 style="color:#fff;">MANUAL THROTTLE SIMULATION</h2>
        <p>RELEASE ARROW TO SLOW DOWN | ADJUST FOR WIDE CURVES</p>
        <p style="font-size:12px; margin-top:20px;">[ CLICK TO BEGIN ]</p>
    </div>

    <div id="hud">
        <div style="font-size: 22px; font-weight: bold;">{OWNER}</div>
        <div style="font-size: 12px; color: #FFD700; letter-spacing: 2px;">{COMPANY} FOUNDER</div>
        <div style="font-size: 12px; margin-top:5px;">{CONTACT}</div>
    </div>

    <div id="speedo"><span id="sp">00</span><span style="font-size:30px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], smokeParticles = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(20, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 600, 2500);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 1, 6000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.8));
            let sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(200, 500, 100);
            scene.add(sun);

            // --- THE ROAD SYSTEM (WIDE CURVES) ---
            for(let i=0; i<160; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(140, 40), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Side Markings
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(10, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-75, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(75, 0.2, 0);
                seg.add(curbR);

                // Environment (Mountains and states)
                if(i % 15 == 0) {{
                    let mt = new THREE.Mesh(new THREE.ConeGeometry(80, 180, 4), new THREE.MeshPhongMaterial({{color: 0x1a2b1a}}));
                    mt.position.set(i%30==0?350:-350, 90, 0);
                    seg.add(mt);
                }}

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE TRUCK ---
            truck = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 100}});
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.2, 6), blue);
            nose.position.set(0, 1.6, -8.5); 
            truck.add(nose);
            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.4, 6, 6), blue);
            cab.position.set(0, 3, -3);
            truck.add(cab);

            let chrome = new THREE.MeshPhongMaterial({{color: 0xdddddd, shininess: 200}});
            let s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 10), chrome); 
            s1.position.set(2.0, 5.5, -2); 
            let s2 = s1.clone(); s2.position.x = -2.0;
            truck.add(s1); truck.add(s2);

            let flagHT = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 1.1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flagHT.position.set(2.25, 4.8, -3); flagHT.rotation.y = Math.PI/2;
            truck.add(flagHT);

            let tireGeo = new THREE.CylinderGeometry(1.5, 1.5, 1.5, 18);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x080808}});
            [[-2.3,1.5,-6.5], [2.3,1.5,-6.5], [-2.3,1.5,0], [2.3,1.5,0], [-2.3,1.5,14], [2.3,1.5,14], [-2.3,1.5,18], [2.3,1.5,18]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.5, 7, 38), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 4.8, 18);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // --- PROGRESSIVE THROTTLE & RELEASE ---
            if (keys['ArrowUp']) {{
                speed += 0.00025; // Gain speed slowly (Progressive)
            }} else {{
                speed *= 0.994; // Release to slow down (Engine Braking)
            }}
            
            if (keys['ArrowDown']) speed -= 0.001; // Active Brakes
            if (speed < 0) speed = 0;

            if (keys['ArrowLeft']) targetX -= 0.8;
            if (keys['ArrowRight']) targetX += 0.8;
            truckX += (targetX - truckX) * 0.04;
            
            if(truckX < -65) {{ truckX = -65; targetX = -65; }}
            if(truckX > 65) {{ truckX = 65; targetX = 65; }}
            
            truck.position.x = truckX;
            truck.rotation.y = (targetX - truckX) * 0.015;

            time += speed * 3.5;

            // --- WIDE ROAD CURVES ---
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 400; 
                if(seg.position.z > 200) seg.position.z -= 160 * 40;
                
                // Reduced frequency (0.002) for long straights and gentle turns
                let curve = Math.sin((seg.position.z - time * 50) * 0.002) * 90;
                seg.position.x = curve;
            }});

            // Smoke
            if(keys['ArrowUp'] && Math.random() > 0.3) {{
                let sm = new THREE.Mesh(new THREE.SphereGeometry(0.5, 8, 8), new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.4}}));
                sm.position.set(truckX + (Math.random()>0.5?2.0:-2.0), 10, -3);
                scene.add(sm);
                smokeParticles.push({{m: sm, l: 1.0}});
            }}
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.m.position.z += speed * 60 + 0.4;
                p.m.position.y += 0.15; p.l -= 0.015;
                p.m.material.opacity = p.l;
                if(p.l <= 0) {{ scene.remove(p.m); smokeParticles.splice(i,1); }}
            }}

            wheels.forEach(w => w.rotation.x -= speed * 20);
            if(osc) osc.frequency.setTargetAtTime(20 + (speed * 4000), audioCtx.currentTime, 0.1);

            camera.position.set(truckX * 0.5, 32, 130);
            camera.lookAt(truckX, 12, -50);

            document.getElementById('sp').innerText = Math.round(speed * 6000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
