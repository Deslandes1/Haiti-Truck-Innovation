import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- HEAVY PROGRESSIVE ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; background: #87CEEB; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
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
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.9);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer; text-align: center;
        }}
    </style>
</head>
<body>
    <div id="start" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <h2 style="color:#fff;">HEAVY TORQUE SIMULATION</h2>
        <p>HOLD [UP ARROW] TO BUILD PROGRESSIVE POWER</p>
    </div>

    <div id="hud">
        <div style="font-size: 22px; font-weight: bold;">{OWNER}</div>
        <div style="font-size: 12px; color: #FFD700; letter-spacing: 2px;">{COMPANY} FOUNDER</div>
        <div style="font-size: 12px; margin-top:5px;">WhatsApp: {CONTACT}</div>
    </div>

    <div id="speedo"><span id="sp">00</span><span style="font-size:30px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], smokeParticles = [];
        let speed = 0, targetSpeed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(25, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.07, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 500, 2000);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth/window.innerHeight, 1, 5000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.8));
            let sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(100, 500, 100);
            scene.add(sun);

            // --- THE CURVED WORLD ---
            for(let i=0; i<150; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(130, 40), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Racing Borders
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(12, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-71, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(71, 0.2, 0);
                seg.add(curbR);

                // Passing Mountains & Community Buildings
                if(i % 12 == 0) {{
                    let mt = new THREE.Mesh(new THREE.ConeGeometry(70, 150, 4), new THREE.MeshPhongMaterial({{color: 0x1b2b1b}}));
                    mt.position.set(i%24==0?300:-300, 75, 0);
                    seg.add(mt);
                    
                    let bld = new THREE.Mesh(new THREE.BoxGeometry(20, 25, 20), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
                    bld.position.set(i%24==0?-100:100, 12.5, 0);
                    seg.add(bld);
                }}

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE HEAVY 18-WHEELER (FORWARD FACING) ---
            truck = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 100}});
            
            // Nose & Cab
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3.2, 6), blue);
            nose.position.set(0, 1.6, -8); 
            truck.add(nose);

            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.3, 5.8, 5.5), blue);
            cab.position.set(0, 2.9, -2.5);
            truck.add(cab);

            // Chrome Stacks (Dual Exhaust)
            let chrome = new THREE.MeshPhongMaterial({{color: 0xdddddd, shininess: 200}});
            let s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 9.5), chrome); 
            s1.position.set(1.9, 5.5, -1.5); 
            let s2 = s1.clone(); s2.position.x = -1.9;
            truck.add(s1); truck.add(s2);

            // Haitian Flag
            let flagHT = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flagHT.position.set(2.2, 4.8, -2.5); flagHT.rotation.y = Math.PI/2;
            truck.add(flagHT);

            // 10 Heavy Wheels
            let tireGeo = new THREE.CylinderGeometry(1.4, 1.4, 1.4, 18);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x050505}});
            [[-2.2,1.4,-6], [2.2,1.4,-6], [-2.2,1.4,-1], [2.2,1.4,-1], [-2.2,1.4,12], [2.2,1.4,12], [-2.2,1.4,16], [2.2,1.4,16]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            // White Trailer
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.4, 6.8, 36), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 4.5, 16);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // --- HEAVY PROGRESSIVE ACCELERATION ---
            // The truck gains speed based on a "Torque Curve"
            if (keys['ArrowUp']) {{
                // Very slow increment (step by step)
                speed += 0.0003; 
            }} else {{
                // Natural deceleration (Inertia)
                speed *= 0.998; 
            }}
            
            if (keys['ArrowDown']) speed -= 0.0008; // Heavy Brakes
            if (speed < 0) speed = 0;

            // Heavy Rig Steering (Slow Response)
            if (keys['ArrowLeft']) targetX -= 0.9;
            if (keys['ArrowRight']) targetX += 0.9;
            truckX += (targetX - truckX) * 0.05;
            
            if(truckX < -55) {{ truckX = -55; targetX = -55; }}
            if(truckX > 55) {{ truckX = 55; targetX = 55; }}
            
            truck.position.x = truckX;
            truck.rotation.y = (targetX - truckX) * 0.02;

            time += speed * 4;

            // Curved World Logic
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 350; 
                if(seg.position.z > 200) seg.position.z -= 150 * 40;
                let curve = Math.sin((seg.position.z - time * 60) * 0.004) * 80;
                seg.position.x = curve;
            }});

            // Healthy Exhaust Smoke (Intensifies when pedaling the gas)
            if(keys['ArrowUp'] && Math.random() > 0.2) {{
                let sm = new THREE.Mesh(new THREE.SphereGeometry(0.5, 8, 8), new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.5}}));
                sm.position.set(truckX + (Math.random()>0.5?1.9:-1.9), 10, -3);
                scene.add(sm);
                smokeParticles.push({{m: sm, l: 1.0}});
            }}
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.m.position.z += speed * 50 + 0.3;
                p.m.position.y += 0.12; p.l -= 0.012;
                p.m.material.opacity = p.l;
                p.m.scale.multiplyScalar(1.04);
                if(p.l <= 0) {{ scene.remove(p.m); smokeParticles.splice(i,1); }}
            }}

            wheels.forEach(w => w.rotation.x -= speed * 15);
            if(osc) osc.frequency.setTargetAtTime(25 + (speed * 3500), audioCtx.currentTime, 0.1);

            camera.position.set(truckX * 0.5, 30, 120);
            camera.lookAt(truckX, 12, -40);

            document.getElementById('sp').innerText = Math.round(speed * 5000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
