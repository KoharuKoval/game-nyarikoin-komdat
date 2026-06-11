const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 1. KONFIGURASI GAME
const GAME_DURATION = 60; // 60 detik
let startTime = Date.now();
let gameOver = false;
let timeLeft = GAME_DURATION;

// Data Pemain 1 (Biru) - Kontrol: WASD
const p1 = {
    x: 150, y: 300,
    size: 40,
    color: '#0066cc',
    score: 0,
    speed: 5,
    name: "Pemain 1"
};

// Data Pemain 2 (Merah) - Kontrol: Panah
const p2 = {
    x: 610, y: 300,
    size: 40,
    color: '#cc0000',
    score: 0,
    speed: 5,
    name: "Pemain 2"
};

// Data Koin (Emas)
const coin = {
    x: Math.floor(Math.random() * 720) + 40,
    y: Math.floor(Math.random() * 520) + 40,
    radius: 10
};

// 2. MENANGKAP INPUT KEYBOARD
const keys = {};
window.addEventListener('keydown', e => { keys[e.key] = true; });
window.addEventListener('keyup', e => { keys[e.key] = false; });

// 3. LOGIKA DETEKSI TABRAKAN (Kotak dengan Lingkaran)
function checkCollision(player, coin) {
    let closestX = Math.max(player.x, Math.min(coin.x, player.x + player.size));
    let closestY = Math.max(player.y, Math.min(coin.y, player.y + player.size));

    let distanceX = coin.x - closestX;
    let distanceY = coin.y - closestY;
    let distanceSquared = (distanceX * distanceX) + (distanceY * distanceY);

    return distanceSquared < (coin.radius * coin.radius);
}

function acakKoin() {
    coin.x = Math.floor(Math.random() * (canvas.width - 80)) + 40;
    coin.y = Math.floor(Math.random() * (canvas.height - 80)) + 40;
}

// 4. UPDATE PERGERAKAN & ATURAN
function update() {
    if (gameOver) return;

    // Hitung Mundur Waktu
    let elapsed = Math.floor((Date.now() - startTime) / 1000);
    timeLeft = GAME_DURATION - elapsed;
    if (timeLeft <= 0) {
        timeLeft = 0;
        gameOver = true;
    }

    // Pergerakan Pemain 1 (WASD)
    if ((keys['w'] || keys['W']) && p1.y > 0) p1.y -= p1.speed;
    if ((keys['s'] || keys['S']) && p1.y < canvas.height - p1.size) p1.y += p1.speed;
    if ((keys['a'] || keys['A']) && p1.x > 0) p1.x -= p1.speed;
    if ((keys['d'] || keys['D']) && p1.x < canvas.width - p1.size) p1.x += p1.speed;

    // Pergerakan Pemain 2 (Tombol Panah)
    if (keys['ArrowUp'] && p2.y > 0) p2.y -= p2.speed;
    if (keys['ArrowDown'] && p2.y < canvas.height - p2.size) p2.y += p2.speed;
    if (keys['ArrowLeft'] && p2.x > 0) p2.x -= p2.speed;
    if (keys['ArrowRight'] && p2.x < canvas.width - p2.size) p2.x += p2.speed;

    // Cek Tabrakan Koin
    if (checkCollision(p1, coin)) {
        p1.score++;
        acakKoin();
    }
    if (checkCollision(p2, coin)) {
        p2.score++;
        acakKoin();
    }
}

// 5. MENGGAMBAR GRAFIS GAME
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Gambar Koin Emas
    if (!gameOver) {
        ctx.beginPath();
        ctx.arc(coin.x, coin.y, coin.radius, 0, 2 * Math.PI);
        ctx.fillStyle = '#FFD700';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#B8860B';
        ctx.stroke();
    }

    // Gambar Pemain 1 (Biru)
    ctx.fillStyle = p1.color;
    ctx.fillRect(p1.x, p1.y, p1.size, p1.size);
    ctx.fillStyle = '#000';
    ctx.font = 'bold 14px Arial';
    ctx.fillText(`P1: ${p1.score}`, p1.x, p1.y - 10);

    // Gambar Pemain 2 (Merah)
    ctx.fillStyle = p2.color;
    ctx.fillRect(p2.x, p2.y, p2.size, p2.size);
    ctx.fillStyle = '#000';
    ctx.font = 'bold 14px Arial';
    ctx.fillText(`P2: ${p2.score}`, p2.x, p2.y - 10);

    // Tampilkan HUD Atas
    ctx.fillStyle = p1.color;
    ctx.font = 'bold 18px Arial';
    ctx.fillText(`Pemain 1 (WASD): ${p1.score}`, 20, 30);

    ctx.fillStyle = p2.color;
    ctx.fillText(`Pemain 2 (Panah): ${p2.score}`, canvas.width - 200, 30);

    ctx.fillStyle = timeLeft <= 10 ? '#cc0000' : '#000';
    ctx.font = 'bold 36px Arial';
    ctx.fillText(`WAKTU: ${timeLeft}s`, canvas.width / 2 - 90, 42);

    // Layar Akhir Game Over
    if (gameOver) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#000';
        ctx.font = 'bold 40px Arial';
        ctx.fillText('PERMAINAN SELESAI!', canvas.width / 2 - 220, canvas.height / 2 - 40);

        let winMsg = "";
        let winColor = "#000";
        
        if (p1.score > p2.score) {
            winMsg = "PEMAIN 1 (BIRU) MENANG!";
            winColor = p1.color;
        } else if (p2.score > p1.score) {
            winMsg = "PEMAIN 2 (MERAH) MENANG!";
            winColor = p2.color;
        } else {
            winMsg = "SERI / SKOR SAMA!";
            winColor = "#555";
        }

        ctx.fillStyle = winColor;
        ctx.fillText(winMsg, canvas.width / 2 - 240, canvas.height / 2 + 20);
        
        ctx.fillStyle = '#000';
        ctx.font = '18px Arial';
        ctx.fillText(`Skor Akhir - P1: ${p1.score} | P2: ${p2.score}`, canvas.width / 2 - 120, canvas.height / 2 + 70);
    }
}

// 6. GAME LOOP
function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// Mulai Game
gameLoop();