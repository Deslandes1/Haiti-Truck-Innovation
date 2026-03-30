import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Simulator PRO", layout="wide")

# --- FULL VISUAL REPAIR ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: 'Arial', sans-serif; }}
        
        /* OVERLAY UI */
        #gui {{
            position: absolute; top: 10px; right: 10px; 
            display: flex; flex-direction: column; gap: 10px; z-index: 100;
        }}
        .btn {{
            padding: 12px 20px; background: #D21034; color: white; border: none;
            cursor: pointer; font-weight: bold; border-radius: 5px; text-transform: uppercase;
        }}
        .btn:hover {{ background: #00209F; }}

        #dashboard {{
            position: absolute; bottom: 0; width: 100%; height: 150px;
            background: #111; border-top: 3px solid #444;
            display: flex; justify-content: center; align-items: center; gap: 50px;
            color: #00FF41; z-index: 10;
        }}

        #start-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9); display: flex; flex-direction: column;
            justify-content: center; align-items: center; color: white; z-index: 200;
        }}
    </style>
</head>
<body>

    <div id="start-overlay" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:45px;">🇭🇹 {COMPANY}</h1>
        <p>REPAIRING VISUALS... CLICK TO LOAD ROAD & TRUCK</p>
        <div style="background:#444; padding:15px; border-radius:10px; margin-top:20px;">
            USE [UP ARROW] TO DRIVE | [LEFT/RIGHT] TO STEER
        </div>
    </div>

    <div id="gui">
        <button class="btn" onclick="toggleView()">Change View (V)</button>
        <button class="btn" onclick="toggleTime()">Day / Night (N)</button>
    </div>

    <div id="dashboard">
        <div style="text-align:center;">
            <small>SPEED</small><br>
            <span id="speed-val" style="font-size:35px; font-weight:bold;">0</span> MPH
        </div>
        <div style="color:white; opacity:0.5; font-size:12px;">
            {OWNER}<br>{COMPANY}
        </div>
        <div style="text-align:center;">
            <small>STATUS</small><br>
            <span id="mode-txt" style="font-size:20px;">CABIN MODE</span>
        </div>
    </div>

    <script>
        let scene, camera, renderer, wheel, truckGroup, roadSegments = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let isNight = true, isCabin = true;

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000814);
            scene.fog = new THREE.Fog(0x000814, 1000, 5000);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 15000);
            
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // LIGHTING
            const ambient = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambient);
            const sun = new THREE.DirectionalLight(0xffffff, 1.0);
            sun.position.set(500, 1000, 500);
            scene.add(sun);
            scene.sun = sun;

            // --- THE TRUCK EXTERIOR ---
            truckGroup = new THREE.Group();
            let bodyMat = new THREE.MeshPhongMaterial({{color: 0x00209F}});
            let cabin = new THREE.Mesh(new THREE.BoxGeometry(8, 10, 12), bodyMat);
            cabin.position.y = 5;
            truckGroup.add(cabin);

            let trailer = new THREE.Mesh(new THREE.BoxGeometry(8.5, 12, 45), new THREE.MeshPhongMaterial({{color: 0xeeeeee}}));
            trailer.position.set(0, 6, 30);
            truckGroup.add(trailer);
            scene.add(truckGroup);

            // --- THE STEERING WHEEL ---
            wheel = new THREE.Group();
            let ring = new THREE.Mesh(new THREE.TorusGeometry(3.5, 0.5, 16, 100), new THREE.MeshPhongMaterial({{color: 0x222222}}));
            let spoke = new THREE.Mesh(new THREE.BoxGeometry(7, 0.6, 0.6), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            wheel.add(ring); wheel.add(spoke);
            wheel.position.set(0, 8.5, -4);
            wheel.rotation.x = Math.PI/3;
            scene.add(wheel);

            // --- THE ROAD ---
            const roadMat = new THREE.MeshPhongMaterial({{color: 0x151515}});
            for(let i=0; i<250; i++) {{
                let seg = new THREE.Group();
                let road = new THREE.Mesh(new THREE.PlaneGeometry(250, 80), roadMat);
                road.rotation.x = -Math.PI/2;
                seg.add(road);

                // Street Lights
                let pole = new THREE.Group();
                let pMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 45), new THREE.MeshPhongMaterial({{color: 0x333333}}));
                let bulb = new THREE.Mesh(new THREE.SphereGeometry(2), new THREE.MeshBasicMaterial({{color: 0xffffaa}}));
                bulb.position.set(-10, 22, 0);
                pole.add(pMesh); pole.add(bulb);
                pole.position.set(120, 22, 0);
                pole.visible = false;
                seg.add(pole);
                seg.light = pole;

                seg.position.z = -i * 80;
                scene.add(seg);
                roadSegments.push(seg);
            }}

            window.addEventListener('keydown', e => {{ 
                keys[e.code] = true; 
                if(e.code === 'KeyV') toggleView();
                if(e.code === 'KeyN') toggleTime();
            }});
            window.addEventListener('keyup', e => keys[e.code] = false);

            animate();
        }}

        function toggleView() {{
            isCabin = !isCabin;
            document.getElementById('mode-txt').innerText = isCabin ? "CABIN MODE" : "TRUCK MODE";
        }}

        function toggleTime() {{
            isNight = !isNight;
            scene.background = new THREE.Color(isNight ? 0x000814 : 0x87CEEB);
            scene.fog.color = new THREE.Color(isNight ? 0x000814 : 0x87CEEB);
            scene.sun.intensity = isNight ? 0.2 : 1.3;
        }}

        function animate() {{
            requestAnimationFrame(animate);
            
            // Progressive Drive
            if (keys['ArrowUp']) speed += 0.0004;
            else speed *= 0.993; // Slow down step-by-step
            if (speed < 0) speed = 0;

            // Steering
            if (keys['ArrowLeft']) targetX -= 1.8;
            if (keys['ArrowRight']) targetX += 1.8;
            truckX += (targetX - truckX) * 0.06;
            
            wheel.rotation.z = (targetX - truckX) * -0.4;
            time += speed * 6;

            // Camera Setup
            if(isCabin) {{
                camera.position.set(truckX, 11, 0);
                camera.lookAt(truckX, 10, -100);
                wheel.position.x = truckX;
                wheel.visible = true;
                truckGroup.visible = false;
            }} else {{
                camera.position.set(truckX, 50, 180);
                camera.lookAt(truckX, 15, -100);
                wheel.visible = false;
                truckGroup.visible = true;
                truckGroup.position.x = truckX;
            }}

            // Road & Curve Limits
            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 1000; 
                if(seg.position.z > 800) seg.position.z -= 250 * 80;
                
                let zPos = seg.position.z - (time * 50);
                let curveX = 0;
                let isCurve = false;

                // Turn every 15000 units
                if (zPos < -12000 && zPos > -20000) {{
                    curveX = Math.sin((zPos + 12000) * 0.0003) * 700;
                    isCurve = true;
                }}
                seg.position.x = curveX;
                seg.light.visible = isCurve && isNight;
            }});

            document.getElementById('speed-val').innerText = Math.round(speed * 9000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
