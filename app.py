import streamlit as st
import streamlit.components.v1 as components

# --- 1. CREDENTIALS & SYSTEM CONFIG ---
COMPANY = "GlobalInternet.py"
OWNER = "Gesner Deslandes"
CONTACT = "deslandes78@gmail.com | (509)-4738-5663"
PASSWORD_REQUIRED = "20082010"

st.set_page_config(page_title="Haiti Truck Innovation", layout="wide")

# --- 2. LOGIN GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(f"<h1 style='text-align:center; color:#00209F;'>🇭🇹 {COMPANY}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; color:#D21034;'>Haiti Truck Innovation - Login</h3>", unsafe_allow_html=True)
    
    pwd = st.text_input("Enter Access Code:", type="password")
    if st.button("START ENGINE"):
        if pwd == PASSWORD_REQUIRED:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid Code")
    st.stop()

# --- 3. THE LIVE GAME ENGINE (HTML5/CANVAS) ---
# This section handles the real-time movement, arrows, and enter key.
game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: #222; color: white; font-family: sans-serif; text-align: center; margin: 0; overflow: hidden; }}
        canvas {{ background-color: #444; border: 5px solid #00209F; display: block; margin: 0 auto; }}
        .dash {{ background: #111; padding: 10px; border-bottom: 4px solid #D21034; display: flex; justify-content: space-around; }}
        .stat {{ font-size: 20px; font-weight: bold; color: #00FF41; }}
    </style>
</head>
<body>
    <div class="dash">
        <div id="sp">SPEED: 0 MPH</div>
        <div id="st">STATUS: LOCATE TRAILER</div>
        <div style="color: #FFD700;">{COMPANY}</div>
    </div>
    <canvas id="truckCanvas" width="800" height="500"></canvas>
    <p>USE ARROWS TO DRIVE | ENTER TO BRAKE | SHIFT FOR CLUTCH</p>

    <script>
        const canvas = document.getElementById('truckCanvas');
        const ctx = canvas.getContext('2d');

        let truck = {{ x: 400, y: 400, angle: 0, speed: 0, attached: false }};
        let trailer = {{ x: 400, y: 100, attached: false }};
        let keys = {{}};

        window.addEventListener('keydown', e => {{ keys[e.code] = true; }});
        window.addEventListener('keyup', e => {{ keys[e.code] = false; }});

        function update() {{
            // 1. Driving Logic
            if (keys['ArrowUp']) truck.speed += 0.1;
            if (keys['ArrowDown']) truck.speed -= 0.1;
            if (keys['Enter']) truck.speed *= 0.8; // Air Brakes
            
            if (Math.abs(truck.speed) > 0.1) {{
                if (keys['ArrowLeft']) truck.angle -= 0.05;
                if (keys['ArrowRight']) truck.angle += 0.05;
            }}

            truck.speed *= 0.99; // Friction
            truck.x += Math.cos(truck.angle) * truck.speed;
            truck.y += Math.sin(truck.angle) * truck.speed;

            // 2. Attachment Logic (Fifth Wheel)
            let dist = Math.sqrt((truck.x-trailer.x)**2 + (truck.y-trailer.y)**2);
            if (dist < 30 && !truck.attached && Math.abs(truck.speed) < 1) {{
                truck.attached = True;
                document.getElementById('st').innerText = "STATUS: LOAD ATTACHED - HEAD NORTH";
            }}

            draw();
            document.getElementById('sp').innerText = "SPEED: " + Math.round(truck.speed * 10) + " MPH";
            requestAnimationFrame(update);
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw Road Marks
            ctx.strokeStyle = "yellow"; ctx.setLineDash([20, 20]);
            ctx.beginPath(); ctx.moveTo(400,0); ctx.lineTo(400,500); ctx.stroke();

            // Draw Trailer (Haiti Red)
            if (!truck.attached) {{
                ctx.fillStyle = "#D21034";
                ctx.fillRect(trailer.x-20, trailer.y-40, 40, 80);
            }}

            // Draw Truck (Haiti Blue)
            ctx.save();
            ctx.translate(truck.x, truck.y);
            ctx.rotate(truck.angle);
            ctx.fillStyle = "#00209F";
            ctx.fillRect(-15, -25, 30, 50); // Cab
            ctx.fillStyle = "black";
            ctx.fillRect(-18, -20, 5, 10); ctx.fillRect(13, -20, 5, 10); // Tires
            ctx.restore();
        }}

        update();
    </script>
</body>
</html>
"""

# Render the game
components.html(game_html, height=650)

# --- 4. FOOTER ---
st.markdown("---")
st.write(f"**Owner:** {OWNER} | **Email:** {CONTACT}")
st.write(f"**Instruction:** Click the game screen once to activate the keyboard controls.")
