// Interactive bounding line selection and drawing

const overlay = document.getElementById('overlay');
const stream = document.getElementById('stream');
const ctx = overlay.getContext('2d');
const message = document.getElementById('message');
const btn = document.getElementById('setBoundsBtn');

let setting = false;
let points = [];

function adjustCanvas() {
    overlay.width = stream.clientWidth;
    overlay.height = stream.clientHeight;
}

function drawLines() {
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    ctx.strokeStyle = '#ffca28';
    ctx.lineWidth = 2;
    points.forEach((x) => {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, overlay.height);
        ctx.stroke();
    });
}

btn.addEventListener('click', () => {
    setting = true;
    points = [];
    message.textContent = 'Set the bounding lines by clicking on the camera feed';
    drawLines();
});

overlay.addEventListener('click', (e) => {
    if (!setting) return;
    const rect = overlay.getBoundingClientRect();
    const x = e.clientX - rect.left;
    points.push(x);
    drawLines();
    if (points.length === 2) {
        setting = false;
        fetch('/set_bounds', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x1: Math.round(points[0]), x2: Math.round(points[1]) })
        });
        message.textContent = '';
    }
});

window.addEventListener('resize', () => {
    adjustCanvas();
    drawLines();
});

stream.addEventListener('load', () => {
    adjustCanvas();
    drawLines();
});

adjustCanvas();
