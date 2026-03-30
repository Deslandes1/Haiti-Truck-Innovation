import streamlit as st
import streamlit.components.v1 as components

# --- OWNER DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
EMAIL = "deslandes78@gmail.com"
PHONE = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- THE PROGRESSIVE MOTION ENGINE ---
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
        #overlay {{
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.9);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <p>RE-ORIENTED FORWARD MOTION: CLICK TO IGNITE</p>
    </div>

    <div id="hud">
        <div style="font-size: 18px;">{OWNER}</div>
        <div style="font-size: 11px; color: #FFD700;">{COMPANY} FOUNDER</div>
        <div style="font-size: 11px;">{PHONE}</div>
    </div>

    <div id="speedo"><span id="sp">00</span><span style="font-size:25px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], smokeParticles = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(35, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 300, 1200);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 4000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.8));
            let sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(100, 500, 100);
            scene.add(sun);

            // --- THE FORWARD-FLOWING ENVIRONMENT ---
            for(let i=0; i<120; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(100, 40), new THREE.MeshPhongMaterial({{color: 0x222222}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Progressive Racing Curbs
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(10, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-55, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(55, 0.2, 0);
                seg.add(curbR);

                // Community Landscape & Mountains
                if(i % 8 == 0) {{
                    let mt = new THREE.Mesh(new THREE.ConeGeometry(40, 80, 5), new THREE.MeshPhongMaterial({{color: 0x1b301b}}));
                    mt.position.set(i%16==0?200:-200, 35, 0);
                    seg.add(mt);
                    
                    let tree = new THREE.Group();
                    let tTrunk = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 10), new THREE.MeshPhongMaterial({{color: 0x4d2926}}));
                    let tTop = new THREE.Mesh(new THREE.SphereGeometry(6, 8, 8), new THREE.MeshPhongMaterial({{color: 0x2d5d2d}}));
                    tTop.position.y = 8; tree.add(tTrunk); tree.add(tTop);
                    tree.position.set(i%16==0?-85:85, 5, 0);
                    seg.add(tree);
                }}

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE CORRECTLY ORIENTED 18-WHEELER ---
            truck = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 90}});
            
            // Re-oriented: Nose is at the FRONT (Positive Z)
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3, 6), blue);
            nose.position.set(0, 1.5, -6); // Positioned forward
            truck.add(nose);

            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), blue);
            cab.position.set(0, 2.75, -1);
            truck.add(cab);

            // Haitian Flag
            let flag = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flag.position.set(2.15, 4.5, -1); flag.rotation.y = Math.PI/2;
            truck.add(flag);

            // DUAL EXHAUSTS (Now facing forward into the wind)
            let chrome = new THREE.MeshPhongMaterial({{color: 0xeeeeee, shininess: 150}});
            let s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 8), chrome); s1.position.set(1.8, 5, -0.5);
            let s2 = s1.clone(); s2.position.x = -1.8;
            truck.add(s1); truck.add(s2);

            // Wheels
            let tireGeo = new THREE.CylinderGeometry(1.2, 1.2, 1.2, 16);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            [[-2.1,1,-4], [2.1,1,-4], [-2.1,1,0], [2.1,1,0], [-2.1,1,12], [2.1,1,12]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            // Trailer (Longer 53ft representation)
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.3, 6.2, 32), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 4.1, 15);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // Progressive Acceleration
            if (keys['ArrowUp']) speed += 0.003; 
            if (keys['ArrowDown']) speed -= 0.004;
            speed *= 0.994;

            // Progressive Steering (Inertia)
            if (keys['ArrowLeft']) targetX -= 1.2;
            if (keys['ArrowRight']) targetX += 1.2;
            truckX += (targetX - truckX) * 0.1; // Smooth movement
            
            if(truckX < -40) {{ truckX = -40; targetX = -40; }}
            if(truckX > 40) {{ truckX = 40; targetX = 40; }}
            
            truck.position.x = truckX;
            truck.rotation.y = (targetX - truckX) * 0.05; // Lean into turn
            truck.rotation.z = (targetX - truckX) * 0.02; // Suspension lean

            time += speed * 5;

            // Curved Road Logic
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 250; // Road moves TOWARD camera
                if(seg.position.z > 200) seg.position.z -= 120 * 40;

                // Sine-curve for turns
                let curve = Math.sin((seg.position.z - time * 60) * 0.004) * 60;
                seg.position.x = curve;
            }});

            // Healthy Smoke particles drifting AWAY
            if(speed > 0.01 && Math.random() > 0.4) {{
                let sm = new THREE.Mesh(new THREE.SphereGeometry(0.5, 6, 6), new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.5}}));
                sm.position.set(truckX + (Math.random()>0.5?1.8:-1.8), 9, -5);
                scene.add(sm);
                smokeParticles.push({{m: sm, l: 1.0}});
            }}
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.m.position.z += speed * 50; // Drifts toward back of trailer
                p.m.position.y += 0.1; p.l -= 0.02;
                p.m.material.opacity = p.l;
                p.m.scale.multiplyScalar(1.02);
                if(p.l <= 0) {{ scene.remove(p.m); smokeParticles.splice(i,1); }}
            }}

            wheels.forEach(w => w.rotation.x -= speed * 10);
            if(osc) osc.frequency.setTargetAtTime(35 + (speed * 2000), audioCtx.currentTime, 0.1);

            // Camera Setup
            camera.position.set(truckX * 0.4, 25, 100);
            camera.lookAt(truckX, 8, -50);

            document.getElementById('sp').innerText = Math.round(speed * 3500);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
