import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Haiti Truck - Iron Cabin", layout="wide")

game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            background: #0a0a0a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Courier New', monospace;
        }
        canvas {
            border: 3px solid #D21034;
            box-shadow: 0 0 20px rgba(210,16,52,0.3);
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: #00ff41;
            background: rgba(0,0,0,0.7);
            padding: 8px 15px;
            border-radius: 5px;
            font-family: monospace;
            z-index: 10;
        }
        #controls {
            position: absolute;
            bottom: 10px;
            left: 10px;
            color: #00ff41;
            background: rgba(0,0,0,0.7);
            padding: 8px 15px;
            border-radius: 5px;
            font-family: monospace;
            z-index: 10;
        }
        #startScreen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            color: white;
            z-index: 20;
            cursor: pointer;
        }
        .flag {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        button {
            background: #00209F;
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 1.2rem;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
            transition: 0.2s;
        }
        button:hover {
            background: #D21034;
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div id="startScreen">
        <div class="flag">🇭🇹</div>
        <h1 style="color:#D21034;">EduHumanity</h1>
        <p>IRON-CLAD CABIN LOCK | EXPRESSIVE SIGNS</p>
        <button id="startBtn">START ENGINE</button>
    </div>
    <canvas id="gameCanvas" width="900" height="650"></canvas>
    <div id="info">
        🚛 DRIVER: Gesner Deslandes<br>
        📊 SPEED: <span id="speed">0</span> km/h &nbsp;|&nbsp;
        🎯 SCORE: <span id="score">0</span>
    </div>
    <div id="controls">
        ← → Steer | ↑ Accelerate | ↓ Brake
    </div>

    <script>
        // ========================
        // 2D Driving Simulator (Cabin View)
        // ========================

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const startScreen = document.getElementById('startScreen');
        const startBtn = document.getElementById('startBtn');

        // Game state
        let gameRunning = false;
        let speed = 0;
        let baseSpeed = 0;
        let score = 0;
        let truckX = canvas.width / 2;
        const truckWidth = 70;
        const truckHeight = 100;
        const laneWidth = 400;
        const laneLeft = (canvas.width - laneWidth) / 2;
        const laneRight = laneLeft + laneWidth;

        // Obstacles
        let obstacles = [];
        let obstacleSpawnTimer = 0;

        // Controls
        let leftPressed = false;
        let rightPressed = false;
        let accelPressed = false;
        let brakePressed = false;

        // Dashboard animation
        let steeringAngle = 0;
        let speedometerNeedle = 0;

        // Start game
        startBtn.onclick = () => {
            startScreen.style.display = 'none';
            startGame();
        };

        function startGame() {
            gameRunning = true;
            speed = 0;
            baseSpeed = 0;
            score = 0;
            obstacles = [];
            obstacleSpawnTimer = 0;
            truckX = canvas.width / 2;
            updateUI();
            requestAnimationFrame(gameLoop);
        }

        function updateUI() {
            document.getElementById('speed').innerText = Math.floor(speed);
            document.getElementById('score').innerText = score;
        }

        function spawnObstacle() {
            const width = 50 + Math.random() * 40;
            const height = 50;
            const x = laneLeft + Math.random() * (laneWidth - width);
            obstacles.push({
                x: x,
                y: -height,
                width: width,
                height: height,
                type: Math.random() > 0.7 ? 'rock' : 'barrel'
            });
        }

        function update() {
            if (!gameRunning) return;

            // Acceleration & braking
            if (accelPressed) {
                baseSpeed = Math.min(baseSpeed + 0.2, 25);
            }
            if (brakePressed) {
                baseSpeed = Math.max(baseSpeed - 0.3, 0);
            }
            // Natural deceleration when no input
            if (!accelPressed && !brakePressed) {
                baseSpeed *= 0.98;
            }
            speed = baseSpeed;

            // Steering
            let steerSpeed = 6;
            if (leftPressed && truckX > laneLeft + 10) truckX -= steerSpeed;
            if (rightPressed && truckX < laneRight - truckWidth - 10) truckX += steerSpeed;

            // Update obstacles
            for (let i = 0; i < obstacles.length; i++) {
                obstacles[i].y += speed * 0.5;
                // Collision detection (truck hitbox)
                if (obstacles[i].y + obstacles[i].height > canvas.height - 150 &&
                    obstacles[i].y < canvas.height - 100 &&
                    obstacles[i].x < truckX + truckWidth &&
                    obstacles[i].x + obstacles[i].width > truckX) {
                    gameRunning = false;
                    startScreen.style.display = 'flex';
                    startScreen.querySelector('h1').innerHTML = '💥 CRASH!';
                    return;
                }
            }
            // Remove off-screen obstacles
            obstacles = obstacles.filter(obs => obs.y < canvas.height);

            // Spawn new obstacles
            if (speed > 5) {
                obstacleSpawnTimer++;
                let spawnDelay = Math.max(30, 80 - Math.floor(speed));
                if (obstacleSpawnTimer > spawnDelay) {
                    obstacleSpawnTimer = 0;
                    spawnObstacle();
                }
            }

            // Score increases with speed
            score += Math.floor(speed * 0.5);
            updateUI();

            // Animate dashboard
            steeringAngle = (leftPressed ? -0.3 : (rightPressed ? 0.3 : 0)) * 0.8;
            speedometerNeedle = speed / 30;
        }

        function drawDashboard() {
            // Dashboard background
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, canvas.height - 120, canvas.width, 120);
            ctx.fillStyle = '#333';
            ctx.fillRect(10, canvas.height - 110, canvas.width - 20, 100);
            
            // Speedometer (circular)
            const speedX = 100, speedY = canvas.height - 60;
            ctx.beginPath();
            ctx.arc(speedX, speedY, 35, 0, Math.PI * 2);
            ctx.fillStyle = '#111';
            ctx.fill();
            ctx.strokeStyle = '#00ff41';
            ctx.lineWidth = 2;
            ctx.stroke();
            // Needle
            const angle = -Math.PI/2 + (speedometerNeedle * Math.PI);
            const needleX = speedX + Math.cos(angle) * 25;
            const needleY = speedY + Math.sin(angle) * 25;
            ctx.beginPath();
            ctx.moveTo(speedX, speedY);
            ctx.lineTo(needleX, needleY);
            ctx.strokeStyle = '#ff4444';
            ctx.lineWidth = 3;
            ctx.stroke();
            ctx.fillStyle = '#00ff41';
            ctx.font = 'bold 16px monospace';
            ctx.fillText(Math.floor(speed), speedX-12, speedY-10);
            ctx.fillStyle = '#aaa';
            ctx.font = '10px monospace';
            ctx.fillText('km/h', speedX-8, speedY+15);

            // Steering wheel
            const wheelX = canvas.width - 80, wheelY = canvas.height - 60;
            ctx.beginPath();
            ctx.arc(wheelX, wheelY, 30, 0, Math.PI * 2);
            ctx.fillStyle = '#222';
            ctx.fill();
            ctx.strokeStyle = '#aaa';
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.save();
            ctx.translate(wheelX, wheelY);
            ctx.rotate(steeringAngle);
            ctx.beginPath();
            ctx.moveTo(-20, 0);
            ctx.lineTo(20, 0);
            ctx.moveTo(0, -20);
            ctx.lineTo(0, 20);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(0, 0, 12, 0, Math.PI*2);
            ctx.stroke();
            ctx.restore();

            // Info text
            ctx.fillStyle = '#00ff41';
            ctx.font = '12px monospace';
            ctx.fillText('DRIVER: Gesner Deslandes', canvas.width-220, canvas.height-100);
            ctx.fillStyle = '#D21034';
            ctx.fillText('IRON-CLAD CABIN', canvas.width-180, canvas.height-75);
        }

        function drawRoad() {
            // Sky
            ctx.fillStyle = '#0a2f3f';
            ctx.fillRect(0, 0, canvas.width, canvas.height - 120);
            // Road (perspective)
            const roadTopWidth = 200;
            const roadBottomWidth = laneWidth;
            const roadTopY = 100;
            const roadBottomY = canvas.height - 120;
            ctx.beginPath();
            ctx.moveTo((canvas.width-roadTopWidth)/2, roadTopY);
            ctx.lineTo((canvas.width+roadTopWidth)/2, roadTopY);
            ctx.lineTo((canvas.width+roadBottomWidth)/2, roadBottomY);
            ctx.lineTo((canvas.width-roadBottomWidth)/2, roadBottomY);
            ctx.fillStyle = '#2c2c2c';
            ctx.fill();
            ctx.strokeStyle = '#ffff00';
            ctx.beginPath();
            ctx.moveTo(canvas.width/2, roadTopY);
            ctx.lineTo(canvas.width/2, roadBottomY);
            ctx.stroke();
            // Lane markings (dashed)
            for (let i = roadTopY+30; i < roadBottomY; i+=40) {
                ctx.fillStyle = '#ffff00';
                ctx.fillRect(canvas.width/2 - 5, i, 10, 20);
            }
        }

        function drawTruck() {
            const truckY = canvas.height - 150;
            // Cabin
            ctx.fillStyle = '#D21034';
            ctx.fillRect(truckX, truckY, truckWidth, truckHeight);
            // Windows
            ctx.fillStyle = '#87CEEB';
            ctx.fillRect(truckX+10, truckY+10, truckWidth-20, 30);
            ctx.fillStyle = '#00209F';
            ctx.fillRect(truckX+5, truckY+50, truckWidth-10, 15);
            // Wheels
            ctx.fillStyle = '#111';
            ctx.beginPath();
            ctx.arc(truckX+10, truckY+truckHeight-10, 12, 0, Math.PI*2);
            ctx.arc(truckX+truckWidth-10, truckY+truckHeight-10, 12, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = '#888';
            ctx.beginPath();
            ctx.arc(truckX+10, truckY+truckHeight-10, 6, 0, Math.PI*2);
            ctx.arc(truckX+truckWidth-10, truckY+truckHeight-10, 6, 0, Math.PI*2);
            ctx.fill();
        }

        function drawObstacles() {
            for (let obs of obstacles) {
                if (obs.type === 'rock') {
                    ctx.fillStyle = '#8B5A2B';
                    ctx.beginPath();
                    ctx.ellipse(obs.x+obs.width/2, obs.y+obs.height/2, obs.width/2, obs.height/2, 0, 0, Math.PI*2);
                    ctx.fill();
                } else {
                    ctx.fillStyle = '#A0522D';
                    ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                    ctx.fillStyle = '#CD853F';
                    for (let i=0; i<3; i++) {
                        ctx.fillRect(obs.x+5, obs.y+5+i*15, obs.width-10, 5);
                    }
                }
            }
        }

        function gameLoop() {
            if (!gameRunning) {
                // Draw a static scene
                drawRoad();
                drawTruck();
                drawDashboard();
                return;
            }
            update();
            drawRoad();
            drawObstacles();
            drawTruck();
            drawDashboard();
            requestAnimationFrame(gameLoop);
        }

        // Keyboard controls
        window.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') leftPressed = true;
            if (e.key === 'ArrowRight') rightPressed = true;
            if (e.key === 'ArrowUp') accelPressed = true;
            if (e.key === 'ArrowDown') brakePressed = true;
        });
        window.addEventListener('keyup', (e) => {
            if (e.key === 'ArrowLeft') leftPressed = false;
            if (e.key === 'ArrowRight') rightPressed = false;
            if (e.key === 'ArrowUp') accelPressed = false;
            if (e.key === 'ArrowDown') brakePressed = false;
        });

        // Initial draw
        drawRoad();
        drawTruck();
        drawDashboard();
    </script>
</body>
</html>
"""

components.html(game_html, height=700)
