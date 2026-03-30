import streamlit as st
import streamlit.components.v1 as components

# --- CREDENTIALS ---
OWNER = "Gesner Deslandes"
COMPANY = "EduHumanity"
CONTACT = "(509)-47385663"

st.set_page_config(page_title="Haiti Truck Innovation PRO", layout="wide")

# --- HIGH-VISIBILITY LANDSCAPE ENGINE ---
sim_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #87CEEB; font-family: 'Arial', sans-serif; }}
        
        #gui {{
            position: absolute; top: 20px; left: 20px; 
            display: flex; flex-direction: column; gap: 12px; z-index: 100;
        }}
        .btn {{
            padding: 15px 25px; background: #00209F; color: white; border: 2px solid white;
            cursor: pointer; font-weight: bold; border-radius: 8px; text-shadow: 1px 1px #000;
        }}
        .btn:hover {{ background: #D21034; }}

        #dashboard {{
            position: absolute; bottom: 0; width: 100%; height: 160px;
            background: #222; border-top: 5px solid #444;
            display: flex; justify-content: space-around; align-items: center;
            color: #00FF41; font-family: monospace; z-index: 10;
        }}

        #start-screen {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.95); display: flex; flex-direction: column;
            justify-content: center; align-items: center; color: white; z-index: 200;
            text-align: center; cursor: pointer;
        }}
    </style>
</head>
<body>

    <div id="start-screen" onclick="this.style.display='none'; init();">
        <h1 style="color:#D21034; font-size:50px; margin:0;">🇭🇹 {COMPANY}</h1>
        <h2 style="color:#FFD700;">LANDSCAPE & TRUCK RESTORATION</h2>
        <p style="font-size:18px;">CLICK ANYWHERE TO ENTER THE WORLD</p>
        <p style="margin-top:20px;">[UP] GAS | [LEFT/RIGHT] STEER | [V] VIEW | [N] TIME</p>
    </div>

    <div id="gui">
        <button class="btn" onclick="toggleView()">SELECT VIEW (V)</button>
        <button class="btn" onclick="toggleTime()">DAY / NIGHT (N)</button>
    </div>

    <div id="dashboard">
        <div style="text-align:center;">
            SPEED<br><span id="speed-val" style="font-size:40px;">0</span> MPH
        </div>
        <div style="text-align:center; color:white;">
            <b>{OWNER}</b><br>
            <span id="mode-txt" style="color:#FFD700;">CABIN MODE</span>
        </div>
        <div style="text-align:center;">
            FUEL<br><span style="font-size:30px; color:#D21034;">100%</span>
        </div>
    </div>

    <script>
        let scene, camera, renderer, truck, steeringWheel, roadSegments = [];
        let speed = 0, truckX = 0, targetX = 0, time = 0, keys = {{}};
        let isNight = false, isCabin = true;

        function init() {{
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB); // Day Sky
            scene.fog = new THREE.Fog(0x87CEEB, 1000, 6000);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 15000);
            
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Lighting for visibility
            const ambient = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambient);
            const sun = new THREE.DirectionalLight(0xffffff, 1.2);
            sun.position.set(100, 1000, 100);
            scene.add(sun);
            scene.sun = sun;

            // --- THE TRUCK (REPAIRED) ---
            truck = new THREE.Group();
            let bodyMat = new THREE.MeshPhongMaterial({{color: 0x00209F}});
            let cab = new THREE.Mesh(new THREE.BoxGeometry(10, 12, 12), bodyMat);
            cab.position.y = 6;
            truck.add(cab);
            
            let trailer = new THREE.Mesh(new THREE.BoxGeometry(10, 14, 50), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
            trailer.position.set(0, 7, 35);
            truck.add(trailer);
            scene.add(truck);

            // --- THE STEERING WHEEL ---
            steeringWheel = new THREE.Group();
            let wheelRing = new THREE.Mesh(new THREE.TorusGeometry(4, 0.6, 16, 100), new THREE.MeshPhongMaterial({{color: 0x111111}}));
            steeringWheel.add(wheelRing);
            steeringWheel.position.set(0, 10, -5);
            steeringWheel.rotation.x = Math.PI/3;
            scene.add(steeringWheel);

            // --- THE LANDSCAPE & ROAD ---
            const grassMat = new THREE.MeshPhongMaterial({{color: 0x2d5a27}});
            const roadMat = new THREE.MeshPhongMaterial({{color: 0x333333}});
            
            for(let i=0; i<200; i++) {{
                let seg = new THREE.Group();
                
                // Grass Landscape (Left & Right)
                let grass = new THREE.Mesh(new THREE.PlaneGeometry(2000, 100), grassMat);
                grass.rotation.x = -Math.PI/2;
                seg.add(grass);

                // Central Road
                let road = new THREE.Mesh(new THREE.PlaneGeometry(160, 100), roadMat);
                road.rotation.x = -Math.PI/2;
                road.position.y = 0.1;
                seg.add(road);

                // Road Markings (Yellow Centers)
                if(i % 2 == 0) {{
                    let line = new THREE.Mesh(new THREE.PlaneGeometry(4, 40), new THREE.MeshBasicMaterial({{color: 0xFFD700}}));
                    line.rotation.x = -Math.PI/2;
                    line.position.set(0, 0.2, 0);
                    seg.add(line);
                }}

                // Street Lights for turns
                let pole = new THREE.Group();
                let pMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 50), new THREE.MeshPhongMaterial({{color: 0x222222}}));
                let bulb = new THREE.Mesh(new THREE.SphereGeometry(3), new THREE.MeshBasicMaterial({{color: 0xffffaa}}));
                bulb.position.set(-15, 25, 0);
                pole.add(pMesh); pole.add(bulb);
                pole.position.set(130, 25, 0);
                pole.visible = false;
                seg.add(pole);
                seg.light = pole;

                seg.position.z = -i * 100;
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
            document.getElementById('mode-txt').innerText = isCabin ? "CABIN MODE" : "FOLLOW MODE";
        }}

        function toggleTime() {{
            isNight = !isNight;
            let skyColor = isNight ? 0x000814 : 0x87CEEB;
            scene.background = new THREE.Color(skyColor);
            scene.fog.color = new THREE.Color(skyColor);
            scene.sun.intensity = isNight ? 0.1 : 1.2;
        }}

        function animate() {{
            requestAnimationFrame(animate);
            
            if (keys['ArrowUp']) speed += 0.0005;
            else speed *= 0.994;
            if (speed < 0) speed = 0;

            if (keys['ArrowLeft']) targetX -= 2.0;
            if (keys['ArrowRight']) targetX += 2.0;
            truckX += (targetX - truckX) * 0.07;
            
            steeringWheel.rotation.z = (targetX - truckX) * -0.4;
            time += speed * 8;

            if(isCabin) {{
                camera.position.set(truckX, 13, 0);
                camera.lookAt(truckX, 11, -200);
                steeringWheel.position.x = truckX;
                steeringWheel.visible = true;
                truck.visible = false;
            }} else {{
                camera.position.set(truckX, 60, 250);
                camera.lookAt(truckX, 20, -100);
                steeringWheel.visible = false;
                truck.visible = true;
                truck.position.x = truckX;
            }}

            roadSegments.forEach((seg, index) => {{
                seg.position.z += speed * 1200; 
                if(seg.position.z > 1000) seg.position.z -= 200 * 100;
                
                let zPos = seg.position.z - (time * 60);
                let curveX = 0;
                let isCurve = false;

                // REALISTIC LIMITS: Turn after long straight
                if (zPos < -15000 && zPos > -25000) {{
                    curveX = Math.sin((zPos + 15000) * 0.0003) * 800;
                    isCurve = true;
                }}
                seg.position.x = curveX;
                seg.light.visible = isCurve && isNight;
            }});

            document.getElementById('speed-val').innerText = Math.round(speed * 10000);
            renderer.render(scene, camera);
        }}
    </script>
</body>
</html>
"""

components.html(sim_html, height=850)
