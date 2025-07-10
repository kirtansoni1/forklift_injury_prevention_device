// Interactive bounding line selection and drawing

const overlay = document.getElementById('overlay');
const stream = document.getElementById('stream');
const ctx = overlay.getContext('2d');
const message = document.getElementById('message');
const btn = document.getElementById('setBoundsBtn');
const phoneLabel = document.getElementById('phoneLabel');
const operatorLabel = document.getElementById('operatorLabel');
const countLabel = document.getElementById('countLabel');
const noticeBox = document.getElementById('notice');

let setting = false;
let points = [];

function adjustCanvas() {
    overlay.width = stream.clientWidth;
    overlay.height = stream.clientHeight;
}

function drawLines() {
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--primary-color');
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
    fetch('/reset_bounds', { method: 'POST' });
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
        const x1Norm = points[0] / overlay.width;
        const x2Norm = points[1] / overlay.width;
        fetch('/set_bounds', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x1: x1Norm, x2: x2Norm })
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

function pollStatus() {
    fetch('/status')
        .then(r => r.json())
        .then(data => {
            phoneLabel.textContent = 'Phone Detected: ' + (data.phone ? 'Yes' : 'No');
            operatorLabel.textContent = 'Operator: ' + data.operator;
            countLabel.textContent = 'Number of Operator: ' + data.count;

            if (data.phone || data.operator === 'Outside safe zone') {
                stream.classList.add('alert');
            } else {
                stream.classList.remove('alert');
            }

            if (data.notice && data.notice.message) {
                noticeBox.textContent = data.notice.message;
                noticeBox.className = 'notice ' + data.notice.level;
                noticeBox.style.display = 'block';
            } else {
                noticeBox.style.display = 'none';
            }
        })
        .catch(() => { })
        .finally(() => {
            setTimeout(pollStatus, 1000);
        });
}

adjustCanvas();
pollStatus();