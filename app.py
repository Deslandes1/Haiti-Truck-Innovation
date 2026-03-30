import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- REALISTIC SEGMENT ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #000814; overflow: hidden; font-family: sans-serif; }}
        #hud {{ 
            position: absolute; top: 20px; left: 20px; 
            background: rgba(0,32,159,0.95); padding: 20px; border-radius: 10px; 
            color: white; border-bottom: 5px solid #D21034; z-index: 10;
        }}
        #speedo {{
            position: absolute; bottom: 40px; right: 40px;
            color: #00FF41; font-size: 90px; font-weight: bold; text-shadow: 4px 4px #000;
        }}
        #start {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.98);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer; text-align: center;
        }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <h2 style="color:#fff;">FIXED STRAIGHT ROAD & CURVE GUIDANCE</h2>
        <p>NO MORE "S" CURVES | STREET LIGHTS GUIDE THE TURNS</p>
        <p style="font-size:12px; margin-top:20px;">[ CLICK TO START TRUCKING ]</p>
    </div>

    <div id="hud">
        <div style="font-size: 22px; font-weight: bold;">{OWNER}</div>
        <div style="font-size: 12px; color: #FFD700; letter-spacing: 2px;">{COMPANY} FOUNDER</div>
        <div style="font-size: 12px; margin-top:5px;">{CONTACT}</div>
    </div>

    <div id="speedo"><span id="sp">00</span><span style="font-size:30px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], lights = [], smokeParticles = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(18, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000814); // Night drive for visibility of lights
            scene.fog = new THREE.Fog(0x000814, 1200, 5000);

            camera = new THREE.PerspectiveCamera(40, window.innerWidth/window.innerHeight, 1, 10000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.4));
            let moon = new THREE.DirectionalLight(0xaaaaFF, 0.8);
            moon.position.set(500, 1000, 100);
            scene.add(moon);

            // --- THE FIXED ROAD (LONG STRAIGHTS) ---
            for(let i=0; i<300; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(180, 50), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Shoulder Markings
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(6, 50), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-93, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(93, 0.2, 0);
                seg.add(curbR);

                // Street Light Poles (Hidden by default)
                let pole = new THREE.Group();
                let pMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.8, 35), new THREE.MeshPhongMaterial({{color: 0x444444}}));
                let head = new THREE.Mesh(new THREE.BoxGeometry(8, 1, 2), new THREE.MeshPhongMaterial({{color: 0x222222}}));
                head.position.set(-4, 17.5, 0);
                let bulb = new THREE.Mesh(new THREE.SphereGeometry(1.5), new THREE.MeshBasicMaterial({{color: 0xffffaa}}));
                bulb.position.set(-7, 17, 0);
                pole.add(pMesh); pole.add(head); pole.add(bulb);
                pole.position.set(105, 17.5, 0);
                pole.visible = false; // Turned off on straight road
                seg.add(pole);
                seg.light = pole;

                seg.position.z = -i * 50;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE TRUCK ---
            truck = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 120}});
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.8, 3.4, 6), blue);
            nose.position.set(0, 1.7, -12); 
            truck.add(nose);
            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.8, 6.2, 6), blue);
            cab.position.set(0, 3.1, -6);
            truck.add(cab);

            let chrome = new THREE.MeshPhongMaterial({{color: 0xffffff, shininess: 300}});
            let s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 12), chrome); 
            s1.position.set(2.2, 6.5, -4.5); 
            let s2 = s1.clone(); s2.position.x = -2.2;
            truck.add(s1); truck.add(s2);

            let flagHT = new THREE.Mesh(new THREE.PlaneGeometry(2, 1.2), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flagHT.position.set(2.5, 5, -6); flagHT.rotation.y = Math.PI/2;
            truck.add(flagHT);

            let tireGeo = new THREE.CylinderGeometry(2, 2, 2, 24);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x050505}});
            [[-2.6,2,-10], [2.6,2,-10], [-2.6,2,0], [2.6,2,0], [-2.6,2,18], [2.6,2,18], [-2.6,2,24], [2.6,2,24]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            let trailer = new THREE.Mesh(new THREE.BoxGeometry(5, 8.5, 45), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 6.2, 24);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp']) {{ speed += 0.0003; }} 
            else {{ speed *= 0.993; }} // Progressive slow down
            
            if (keys['ArrowDown']) speed -= 0.002; 
            if (speed < 0) speed = 0;

            if (keys['ArrowLeft']) targetX -= 1.2;
            if (keys['ArrowRight']) targetX += 1.2;
            truckX += (targetX - truckX) * 0.05;
            
            if(truckX < -85) {{ truckX = -85; targetX = -85; }}
            if(truckX > 85) {{ truckX = 85; targetX = 85; }}
            
            truck.position.x = truckX;
            truck.rotation.y = (targetX - truckX) * 0.01;

            time += speed * 6;

            // --- LOGIC FOR STRAIGHT VS TURNS ---
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 600; 
                if(seg.position.z > 500) seg.position.z -= 300 * 50;
                
                let zPos = seg.position.z - (time * 40);
                
                // NO "S" CURVE: Logic for discrete curve blocks
                // The road is 100% straight unless zPos falls into a "Curve Zone"
                let curveX = 0;
                let isCurve = false;

                // Turn 1: Wide Left at 5000 units
                if (zPos < -4000 && zPos > -9000) {{
                    curveX = Math.pow((zPos + 4000) * 0.05, 2) * -0.1;
                    isCurve = true;
                }}
                // Turn 2: Wide Right at 15000 units
                if (zPos < -14000 && zPos > -19000) {{
                    curveX = Math.pow((zPos + 14000) * 0.05, 2) * 0.1;
                    isCurve = true;
                }}

                seg.position.x = curveX;
                
                // STREET LIGHTS ACTIVATE ONLY DURING TURNS
                if (isCurve) {{
                    seg.light.visible = true;
                }} else {{
                    seg.light.visible = false;
                }}
            }});

            // Smoke
            if(keys['ArrowUp'] && Math.random() > 0.3) {{
                let sm = new THREE.Mesh(new THREE.SphereGeometry(0.6, 8, 8), new THREE.MeshBasicMaterial({{color: 0x444444, transparent: true, opacity: 0.4}}));
                sm.position.set(truckX + (Math.random()>0.5?2.3:-2.3), 12, -4);
                scene.add(sm);
                smokeParticles.push({{m: sm, l: 1.2}});
            }}
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.m.position.z += speed * 70 + 0.5;
                p.m.position.y += 0.18; p.l -= 0.02;
                p.m.material.opacity = p.l;
                if(p.l <= 0) {{ scene.remove(p.m); smokeParticles.splice(i,1); }}
            }}

            wheels.forEach(w => w.rotation.x -= speed * 30);
            if(osc) osc.frequency.setTargetAtTime(18 + (speed * 5000), audioCtx.currentTime, 0.1);

            camera.position.set(truckX * 0.6, 45, 180);
            camera.lookAt(truckX, 18, -80);

            document.getElementById('sp').innerText = Math.round(speed * 7000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
