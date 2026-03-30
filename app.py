import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- REAL-HIGHWAY ENGINE ---
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
        <h2 style="color:#fff;">REALISTIC HIGHWAY DRIVE</h2>
        <p>LONG STRAIGHTS | MANUAL SPEEDING | PROGRESSIVE SLOW DOWN</p>
        <p style="font-size:12px; margin-top:20px;">[ CLICK TO BEGIN YOUR SHIFT ]</p>
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
            scene.fog = new THREE.Fog(0x87CEEB, 1000, 4000);

            camera = new THREE.PerspectiveCamera(40, window.innerWidth/window.innerHeight, 1, 10000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 1.0));
            let sun = new THREE.DirectionalLight(0xffffff, 1.3);
            sun.position.set(400, 600, 100);
            scene.add(sun);

            // --- THE REALISTIC ROAD (STRAIGHTS WITH LIMITS) ---
            for(let i=0; i<250; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(160, 50), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Shoulder Markings
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(8, 50), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-84, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(84, 0.2, 0);
                seg.add(curbR);

                // Scenic Elements
                if(i % 15 == 0) {{
                    let mt = new THREE.Mesh(new THREE.ConeGeometry(100, 220, 4), new THREE.MeshPhongMaterial({{color: 0x1b2b1b}}));
                    mt.position.set(i%30==0?600:-600, 110, 0);
                    seg.add(mt);
                }}

                seg.position.z = -i * 50;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE TRUCK MODEL ---
            truck = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 120}});
            
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.2, 6), blue);
            nose.position.set(0, 1.6, -11); 
            truck.add(nose);
            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.6, 6, 6), blue);
            cab.position.set(0, 3, -5);
            truck.add(cab);

            let chrome = new THREE.MeshPhongMaterial({{color: 0xffffff, shininess: 250}});
            let s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 11), chrome); 
            s1.position.set(2.0, 6, -3.5); 
            let s2 = s1.clone(); s2.position.x = -2.0;
            truck.add(s1); truck.add(s2);

            let flagHT = new THREE.Mesh(new THREE.PlaneGeometry(2, 1.2), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flagHT.position.set(2.4, 5, -5); flagHT.rotation.y = Math.PI/2;
            truck.add(flagHT);

            let tireGeo = new THREE.CylinderGeometry(1.8, 1.8, 1.8, 24);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x050505}});
            [[-2.5,1.8,-9], [2.5,1.8,-9], [-2.5,1.8,0], [2.5,1.8,0], [-2.5,1.8,16], [2.5,1.8,16], [-2.5,1.8,22], [2.5,1.8,22]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.8, 7.8, 42), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 5.5, 22);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // --- PROGRESSIVE THROTTLE & HEAVY SLOW DOWN ---
            if (keys['ArrowUp']) {{
                speed += 0.00028; // Gain speed step-by-step
            }} else {{
                speed *= 0.996; // Naturally slow down (Inertia)
            }}
            
            if (keys['ArrowDown']) speed -= 0.0018; // Strong Brakes
            if (speed < 0) speed = 0;

            if (keys['ArrowLeft']) targetX -= 1.0;
            if (keys['ArrowRight']) targetX += 1.0;
            truckX += (targetX - truckX) * 0.06;
            
            if(truckX < -78) {{ truckX = -78; targetX = -78; }}
            if(truckX > 78) {{ truckX = 78; targetX = 78; }}
            
            truck.position.x = truckX;
            truck.rotation.y = (targetX - truckX) * 0.012;

            time += speed * 5;

            // --- REALISTIC ROAD LOGIC (LIMITS) ---
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 550; 
                if(seg.position.z > 250) seg.position.z -= 250 * 50;
                
                // FIXED LIMITS: The road stays straight (0) most of the time.
                // Every 10,000 units of Z distance, a turn occurs.
                let zPos = seg.position.z - (time * 30);
                
                // Curve factor is mostly 0 (straight) then rises for wide turns
                let curveFactor = Math.sin(zPos * 0.0005) * Math.cos(zPos * 0.0001);
                seg.position.x = curveFactor * 130;
            }});

            // Heavy Exhaust Smoke
            if(keys['ArrowUp'] && Math.random() > 0.35) {{
                let sm = new THREE.Mesh(new THREE.SphereGeometry(0.6, 8, 8), new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.5}}));
                sm.position.set(truckX + (Math.random()>0.5?2.1:-2.1), 11.5, -4.5);
                scene.add(sm);
                smokeParticles.push({{m: sm, l: 1.2}});
            }}
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.m.position.z += speed * 60 + 0.5;
                p.m.position.y += 0.16; p.l -= 0.016;
                p.m.material.opacity = p.l;
                if(p.l <= 0) {{ scene.remove(p.m); smokeParticles.splice(i,1); }}
            }}

            wheels.forEach(w => w.rotation.x -= speed * 28);
            if(osc) osc.frequency.setTargetAtTime(20 + (speed * 4800), audioCtx.currentTime, 0.1);

            camera.position.set(truckX * 0.6, 38, 160);
            camera.lookAt(truckX, 16, -70);

            document.getElementById('sp').innerText = Math.round(speed * 6800);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
