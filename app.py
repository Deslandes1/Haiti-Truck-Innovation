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
            padding: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: monospace;
        }
        canvas {
            border: 2px solid #D21034;
            background: #1a2a1a;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            background: rgba(0,0,0,0.7);
            padding: 8px 15px;
            border-radius: 5px;
            z-index: 10;
        }
        #controls {
            position: absolute;
            bottom: 10px;
            left: 10px;
            color: white;
            background: rgba(0,0,0,0.7);
            padding: 8px 15px;
            border-radius: 5px;
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
    </style>
</head>
<body>
    <div id="startScreen">
        <h1 style="color:#D21034;">🇭🇹 EduHumanity</h1>
        <p>IRON-CLAD CABIN LOCK | EXPRESSIVE SIGNS</p>
        <button style="background:#00209F; color:white; padding:10px 30px; border:none; border-radius:5px; font-size:1.2rem; cursor:pointer;">START ENGINE</button>
    </div>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <div id="info">
        <span>DRIVER: Gesner Deslandes</span><br>
        Speed: <span id="speed">0</span> mph &nbsp;|&nbsp;
        Score: <span id="score">0</span>
    </div>
    <div id="controls">
        ← → Steer | ↑ Accelerate
    </div>

    <script>
        // Get canvas and context
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // Game variables
        let gameRunning = false;
        let speed = 0;
        let score = 0;
        let truckX = canvas.width/2;
        const truckWidth = 50;
        const truckHeight = 80;
        const roadWidth = 300;
        const roadLeft = (canvas.width - roadWidth)/2;
        const roadRight = roadLeft + roadWidth;

        // Obstacles
        let obstacles = [];
        let obstacleSpawnCounter = 0;

        // Controls
        let leftPressed = false;
        let rightPressed = false;
        let acceleratePressed = false;

        // Acceleration physics
        let acceleration = 0;

        // Start screen
        const startScreen = document.getElementById('startScreen');
        startScreen.querySelector('button').onclick = () => {
            startScreen.style.display = 'none';
            startGame();
        };

        function startGame() {
            gameRunning = true;
            speed = 5;
            score = 0;
            obstacles = [];
            obstacleSpawnCounter = 0;
            acceleration = 0;
            truckX = canvas.width/2;
            updateUI();
            gameLoop();
        }

        function updateUI() {
            document.getElementById('speed').innerText = Math.floor(speed * 10);
            document.getElementById('score').innerText = score;
        }

        function spawnObstacle() {
            const obstacleWidth = 40 + Math.random() * 30;
            const obstacleHeight = 50;
            const x = roadLeft + Math.random() * (roadWidth - obstacleWidth);
            obstacles.push({
                x: x,
                y: -obstacleHeight,
                width: obstacleWidth,
                height: obstacleHeight
            });
        }

        function update() {
            if (!gameRunning) return;

            // Accelerate / decelerate
            if (acceleratePressed) {
                acceleration += 0.2;
                if (acceleration > 2) acceleration = 2;
            } else {
                acceleration -= 0.1;
                if (acceleration < 0) acceleration = 0;
            }
            speed = 5 + acceleration * 5;
            if (speed > 20) speed = 20;

            // Steering
            if (leftPressed && truckX > roadLeft + 10) truckX -= 8;
            if (rightPressed && truckX < roadRight - truckWidth - 10) truckX += 8;

            // Move obstacles and check collisions
            for (let i = 0; i < obstacles.length; i++) {
                obstacles[i].y += speed;
                // Collision detection
                if (obstacles[i].y + obstacles[i].height > canvas.height/2 - 30 && 
                    obstacles[i].y < canvas.height/2 + 30 &&
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
            obstacleSpawnCounter++;
            if (obstacleSpawnCounter > 30 / (speed/5)) {
                obstacleSpawnCounter = 0;
                spawnObstacle();
            }

            // Score increases with speed
            score += Math.floor(speed * 0.5);
            updateUI();
        }

        function draw() {
            // Clear canvas
            ctx.fillStyle = '#2e7d32';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw road
            ctx.fillStyle = '#2c2c2c';
            ctx.fillRect(roadLeft, 0, roadWidth, canvas.height);
            // Road markings
            ctx.fillStyle = '#ffff00';
            ctx.fillRect(roadLeft + roadWidth/2 - 5, 0, 10, canvas.height);

            // Draw obstacles (rocks / barrels)
            for (let obs of obstacles) {
                ctx.fillStyle = '#8B5A2B';
                ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                ctx.fillStyle = '#654321';
                ctx.fillRect(obs.x+5, obs.y+10, obs.width-10, 5);
            }

            // Draw truck (simple rectangle)
            ctx.fillStyle = '#D21034';
            ctx.fillRect(truckX, canvas.height/2 - truckHeight/2, truckWidth, truckHeight);
            ctx.fillStyle = '#00209F';
            ctx.fillRect(truckX+10, canvas.height/2 - truckHeight/2 + 10, truckWidth-20, 20);
            ctx.fillStyle = '#FFD700';
            ctx.beginPath();
            ctx.arc(truckX + truckWidth/2, canvas.height/2 - truckHeight/2 + 40, 15, 0, Math.PI*2);
            ctx.fill();

            // Display speed and score
            ctx.font = "20px monospace";
            ctx.fillStyle = "white";
            ctx.fillText("SPEED: " + Math.floor(speed*10), 10, 40);
            ctx.fillText("SCORE: " + score, 10, 70);
        }

        function gameLoop() {
            if (gameRunning) {
                update();
                draw();
            } else {
                draw(); // draw final frame
            }
            requestAnimationFrame(gameLoop);
        }

        // Keyboard controls
        window.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') leftPressed = true;
            if (e.key === 'ArrowRight') rightPressed = true;
            if (e.key === 'ArrowUp') acceleratePressed = true;
            if (e.key === ' ' && !gameRunning) {
                startScreen.style.display = 'flex';
            }
        });
        window.addEventListener('keyup', (e) => {
            if (e.key === 'ArrowLeft') leftPressed = false;
            if (e.key === 'ArrowRight') rightPressed = false;
            if (e.key === 'ArrowUp') acceleratePressed = false;
        });

        // Initial draw
        draw();
    </script>
</body>
</html>
"""

components.html(game_html, height=700)
