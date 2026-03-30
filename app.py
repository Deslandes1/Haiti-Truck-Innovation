import streamlit as st
import streamlit.components.v1 as components

# --- OWNER & COMPANY DATA ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
EMAIL = "deslandes78@gmail.com"
PHONE = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- HEAVY RIG PROGRESSIVE ENGINE ---
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
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.8);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div id="overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <p>HEAVY LOAD SIMULATION: PROGRESSIVE TORQUE ENABLED</p>
        <p style="font-size:12px;">[ CLICK TO IGNITE DIESEL ]</p>
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
            osc.frequency.setValueAtTime(30, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 400, 1500);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth/window.innerHeight, 1, 5000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.7));
            let sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(100, 500, 100);
            scene.add(sun);

            // --- THE PROGRESSIVE WORLD ---
            for(let i=0; i<150; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(120, 40), new THREE.MeshPhongMaterial({{color: 0x1a1a1a}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Racing Style Curbs (Still present for speed reference)
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(10, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-65, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(65, 0.2, 0);
                seg.add(curbR);

                // Environment: Mountains and Buildings
                if(i % 10 == 0) {{
                    let mt = new THREE.Mesh(new THREE.ConeGeometry(60, 120, 4), new THREE.MeshPhongMaterial({{color: 0x223322}}));
                    mt.position.set(i%20==0?250:-250, 60, 0);
                    seg.add(mt);
                    
                    let bld = new THREE.Mesh(new THREE.BoxGeometry(15, 20, 15), new THREE.MeshPhongMaterial({{color: 0xdddddd}}));
                    bld.position.set(i%20==0?-90:90, 10, 0);
                    seg.add(bld);
                }}

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- TRUCK MODEL (FORWARD FACING) ---
            truck = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 80}});
            
            // Nose is FORWARD (Negative Z in this camera setup)
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3, 6), blue);
            nose.position.set(0, 1.5, -8); 
            truck.add(nose);

            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), blue);
            cab.position.set(0, 2.75, -3);
            truck.add(cab);

            // Chrome Dual Exhausts
            let chrome = new THREE.MeshPhongMaterial({{color: 0xcccccc, shininess: 150}});
            let s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 9), chrome); 
            s1.position.set(1.8, 5, -2); 
            let s2 = s1.clone(); s2.position.x = -1.8;
            truck.add(s1); truck.add(s2);

            // Haitian Flag
            let flag = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flag.position.set(2.15, 4.5, -3); flag.rotation.y = Math.PI/2;
            truck.add(flag);

            // Heavy Wheels
            let tireGeo = new THREE.CylinderGeometry(1.3, 1.3, 1.3, 16);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x111111}});
            [[-2.1,1.3,-6], [2.1,1.3,-6], [-2.1,1.3,-2], [2.1,1.3,-2], [-2.1,1.3,10], [2.1,1.3,10]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            // 53ft Trailer
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.3, 6.5, 34), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 4.3, 15);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            // --- PROGRESSIVE ACCELERATION (HEAVY RIG) ---
            // Much lower increment values to simulate 40 tons of weight
            if (keys['ArrowUp']) speed += 0.0006; 
            if (keys['ArrowDown']) speed -= 0.0012; // Slowing down is hard
            
            speed *= 0.997; // High Rolling Resistance
            if (speed < 0) speed = 0;

            // Smooth Progressive Steering
            if (keys['ArrowLeft']) targetX -= 1.0;
            if (keys['ArrowRight']) targetX += 1.0;
            truckX += (targetX - truckX) * 0.08;
            
            if(truckX < -50) {{ truckX = -50; targetX = -50; }}
            if(truckX > 50) {{ truckX = 50; targetX = 50; }}
            
            truck.position.x = truckX;
            truck.rotation.y = (targetX - truckX) * 0.03;

            time += speed * 5;

            // World Flow (CURVED ROAD)
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 300; 
                if(seg.position.z > 200) seg.position.z -= 150 * 40;

                let curve = Math.sin((seg.position.z - time * 60) * 0.0045) * 70;
                seg.position.x = curve;
            }});

            // Healthy Exhaust Smoke (Scales with torque/acceleration)
            if(keys['ArrowUp'] && Math.random() > 0.3) {{
                let sm = new THREE.Mesh(new THREE.SphereGeometry(0.4, 6, 6), new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.4}}));
                sm.position.set(truckX + (Math.random()>0.5?1.8:-1.8), 9, -5);
                scene.add(sm);
                smokeParticles.push({{m: sm, l: 1.0}});
            }}
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.m.position.z += speed * 40 + 0.5;
                p.m.position.y += 0.15; p.l -= 0.015;
                p.m.material.opacity = p.l;
                p.m.scale.multiplyScalar(1.03);
                if(p.l <= 0) {{ scene.remove(p.m); smokeParticles.splice(i,1); }}
            }}

            wheels.forEach(w => w.rotation.x -= speed * 12);
            if(osc) osc.frequency.setTargetAtTime(30 + (speed * 2500), audioCtx.currentTime, 0.1);

            camera.position.set(truckX * 0.4, 28, 110);
            camera.lookAt(truckX, 10, -50);

            document.getElementById('sp').innerText = Math.round(speed * 4000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
