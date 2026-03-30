import streamlit as st
import streamlit.components.v1 as components

# --- OWNER & COMPANY CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
EMAIL = "deslandes78@gmail.com"
PHONE = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- THE CURVED WORLD ENGINE ---
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
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.85);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 100; cursor: pointer; text-align: center;
        }}
    </style>
</head>
<body>
    <div id="overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px;">🇭🇹 {COMPANY}</h1>
        <p>CLICK TO START: THE ROAD NOW TURNS AND CURVES</p>
    </div>

    <div id="hud">
        <div style="font-size: 18px;">{OWNER}</div>
        <div style="font-size: 11px; color: #FFD700;">{COMPANY} FOUNDER</div>
        <div style="font-size: 11px;">{EMAIL}</div>
        <div style="font-size: 11px;">{PHONE}</div>
    </div>

    <div id="speedo"><span id="sp">00</span><span style="font-size:25px;"> MPH</span></div>

    <script>
        let scene, camera, renderer, truck, wheels = [], roadSegments = [], smokeParticles = [];
        let speed = 0, truckX = 0, time = 0, keys = {{}};
        let audioCtx, osc;

        function init() {{
            // Audio setup
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(40, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start();

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 200, 1000);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 1, 3000);
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            scene.add(new THREE.AmbientLight(0xffffff, 0.8));
            let sun = new THREE.DirectionalLight(0xffffff, 1);
            sun.position.set(100, 200, 50);
            scene.add(sun);

            // --- THE CURVING ROAD & ENVIRONMENT ---
            for(let i=0; i<100; i++) {{
                let seg = new THREE.Group();
                
                // Asphalt
                let road = new THREE.Mesh(new THREE.PlaneGeometry(80, 40), new THREE.MeshPhongMaterial({{color: 0x111111}}));
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Racing Stripes (Red/White Curbs)
                let curbL = new THREE.Mesh(new THREE.PlaneGeometry(12, 40), new THREE.MeshBasicMaterial({{color: i%2==0 ? 0xD21034 : 0xffffff}}));
                curbL.rotation.x = -Math.PI/2;
                curbL.position.set(-46, 0.2, 0);
                seg.add(curbL);

                let curbR = curbL.clone();
                curbR.position.set(46, 0.2, 0);
                seg.add(curbR);

                // Mountains & Community (Passing Horizon)
                if(i % 6 == 0) {{
                    let mt = new THREE.Mesh(new THREE.ConeGeometry(25, 50, 4), new THREE.MeshPhongMaterial({{color: 0x2d4d2d}}));
                    mt.position.set(i%12==0?120:-120, 20, 0);
                    seg.add(mt);
                    
                    let house = new THREE.Mesh(new THREE.BoxGeometry(10, 10, 10), new THREE.MeshPhongMaterial({{color: 0xeeeeee}}));
                    house.position.set(i%12==0?-80:80, 5, 0);
                    seg.add(house);
                }}

                seg.position.z = -i * 40;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            // --- THE 18-WHEELER ---
            truck = new THREE.Group();
            let blue = new THREE.MeshPhongMaterial({{color: 0x00209F, shininess: 80}});
            
            let nose = new THREE.Mesh(new THREE.BoxGeometry(3.6, 3, 6), blue);
            nose.position.set(0, 1.5, 6);
            truck.add(nose);

            let cab = new THREE.Mesh(new THREE.BoxGeometry(4.2, 5.5, 5), blue);
            cab.position.set(0, 2.75, 1);
            truck.add(cab);

            // Haitian Flag
            let flag = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1), new THREE.MeshBasicMaterial({{color: 0xD21034}}));
            flag.position.set(2.15, 4.5, 1); flag.rotation.y = Math.PI/2;
            truck.add(flag);

            // Chrome Stacks
            let chrome = new THREE.MeshPhongMaterial({{color: 0xaaaaaa, shininess: 150}});
            let s1 = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 8), chrome); s1.position.set(1.8, 5, 0.5);
            let s2 = s1.clone(); s2.position.x = -1.8;
            truck.add(s1); truck.add(s2);

            // Tires
            let tireGeo = new THREE.CylinderGeometry(1.2, 1.2, 1.2, 16);
            let tireMat = new THREE.MeshPhongMaterial({{color: 0x000000}});
            [[-2.1,1,4], [2.1,1,4], [-2.1,1,0], [2.1,1,0], [-2.1,1,-12], [2.1,1,-12]].forEach(p => {{
                let t = new THREE.Mesh(tireGeo, tireMat);
                t.rotation.z = Math.PI/2;
                t.position.set(p[0], p[1], p[2]);
                truck.add(t);
                wheels.push(t);
            }});

            // White Trailer
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(4.2, 6, 28), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 4, -13);
            truck.add(trailer);

            scene.add(truck);
            animate();
        }}

        window.addEventListener('keydown', e => keys[e.code] = true);
        window.addEventListener('keyup', e => keys[e.code] = false);

        function animate() {{
            requestAnimationFrame(animate);
            if(!truck) return;

            if (keys['ArrowUp']) speed += 0.0025; 
            if (keys['ArrowDown']) speed -= 0.003;
            if (keys['ArrowLeft']) truckX -= 0.9;
            if (keys['ArrowRight']) truckX += 0.9;
            
            speed *= 0.992;
            time += speed * 5; // Global world time based on speed

            // Physics bounds
            if(truckX < -35) truckX = -35; if(truckX > 35) truckX = 35;
            truck.position.x = truckX;

            // --- CURVED ROAD LOGIC ---
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 200; // Forward movement
                
                // If segment passes the camera, put it back at the horizon
                if(seg.position.z > 100) seg.position.z -= 100 * 40;

                // Mathematical Curve (Sine wave)
                // The X position depends on the Z distance and the time elapsed
                let curveStrength = Math.sin((seg.position.z - time * 50) * 0.005) * 40;
                seg.position.x = curveStrength;
            }});

            // Smoke
            if(speed > 0.005 && Math.random() > 0.5) {{
                let sm = new THREE.Mesh(new THREE.SphereGeometry(0.4, 4, 4), new THREE.MeshBasicMaterial({{color: 0xffffff, transparent: true, opacity: 0.6}}));
                sm.position.set(truckX + (Math.random()>0.5?1.8:-1.8), 9, 0);
                scene.add(sm);
                smokeParticles.push({{m: sm, l: 1.0}});
            }}
            for(let i=smokeParticles.length-1; i>=0; i--) {{
                let p = smokeParticles[i];
                p.m.position.z += speed * 100; p.m.position.y += 0.1; p.l -= 0.03;
                p.m.material.opacity = p.l;
                if(p.l <= 0) {{ scene.remove(p.m); smokeParticles.splice(i,1); }}
            }}

            wheels.forEach(w => w.rotation.x += speed * 8);
            if(osc) osc.frequency.setTargetAtTime(40 + (speed * 1800), audioCtx.currentTime, 0.1);

            // Follow Camera
            camera.position.set(truckX * 0.5, 22, 70);
            camera.lookAt(truckX, 6, -20);

            document.getElementById('sp').innerText = Math.round(speed * 3000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
