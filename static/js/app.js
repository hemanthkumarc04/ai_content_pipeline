/* ============================================================
   AI VIDEO GENERATOR — Interactive JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    // ─── Elements ───
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    const form = document.getElementById('video-form');
    const textarea = document.getElementById('script-input');
    const charCounter = document.getElementById('char-counter');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeBtn = document.getElementById('remove-file');
    const generateBtn = document.getElementById('generate-btn');
    const formContent = document.getElementById('form-content');
    const progressOverlay = document.getElementById('progress-overlay');
    const progressFill = document.querySelector('.ring-fill');
    const progressPct = document.getElementById('progress-pct');
    const steps = document.querySelectorAll('.progress-step');

    const MAX_CHARS = 1000;

    // ─── Particle System ───
    let particles = [];

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            this.opacity = Math.random() * 0.5 + 0.1;
            this.hue = Math.random() > 0.5 ? 270 : 190; // violet or cyan
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
            if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${this.hue}, 80%, 70%, ${this.opacity})`;
            ctx.fill();
        }
    }

    function initParticles() {
        resizeCanvas();
        particles = [];
        const count = Math.min(80, Math.floor((canvas.width * canvas.height) / 15000));
        for (let i = 0; i < count; i++) {
            particles.push(new Particle());
        }
    }

    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(139, 92, 246, ${0.06 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        drawConnections();
        requestAnimationFrame(animateParticles);
    }

    window.addEventListener('resize', initParticles);
    initParticles();
    animateParticles();

    // ─── Character Counter ───
    if (textarea && charCounter) {
        textarea.addEventListener('input', () => {
            const count = textarea.value.length;
            charCounter.textContent = `${count} / ${MAX_CHARS}`;
            charCounter.classList.remove('warning', 'danger');
            if (count > MAX_CHARS * 0.9) charCounter.classList.add('danger');
            else if (count > MAX_CHARS * 0.7) charCounter.classList.add('warning');
        });
    }

    // ─── Drag and Drop ───
    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        ['dragenter', 'dragover'].forEach(evt => {
            dropZone.addEventListener(evt, e => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(evt => {
            dropZone.addEventListener(evt, e => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
            });
        });

        dropZone.addEventListener('drop', e => {
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                showFileInfo(files[0].name);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                showFileInfo(fileInput.files[0].name);
            }
        });

        if (removeBtn) {
            removeBtn.addEventListener('click', e => {
                e.stopPropagation();
                fileInput.value = '';
                fileInfo.classList.remove('visible');
            });
        }
    }

    function showFileInfo(name) {
        if (fileName) fileName.textContent = name;
        if (fileInfo) fileInfo.classList.add('visible');
    }

    // ─── Form Submission with Progress ───
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Validate
            if (!textarea.value.trim()) {
                shakeElement(textarea);
                return;
            }
            if (!fileInput.files.length) {
                shakeElement(dropZone);
                return;
            }

            // Show progress
            formContent.style.display = 'none';
            progressOverlay.classList.add('active');
            generateBtn.disabled = true;

            // Animate progress steps
            const stepTimings = [
                { step: 0, pct: 15, delay: 300 },
                { step: 1, pct: 50, delay: 3000 },
                { step: 2, pct: 85, delay: 6000 },
            ];

            stepTimings.forEach(({ step, pct, delay }) => {
                setTimeout(() => {
                    activateStep(step, pct);
                }, delay);
            });

            // Actually submit the form via AJAX
            const formData = new FormData(form);

            fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
                .then(res => res.json())
                .then(data => {
                    // Complete progress
                    activateStep(2, 100);
                    steps.forEach(s => s.classList.add('completed'));

                    setTimeout(() => {
                        progressOverlay.classList.remove('active');
                        formContent.style.display = '';

                        if (data.success) {
                            showResult(data.video_url);
                        } else {
                            showMessage(data.error || 'Something went wrong.', 'error');
                        }
                        generateBtn.disabled = false;
                    }, 1200);
                })
                .catch(() => {
                    progressOverlay.classList.remove('active');
                    formContent.style.display = '';
                    showMessage('Network error. Please try again.', 'error');
                    generateBtn.disabled = false;
                });
        });
    }

    function activateStep(index, pct) {
        steps.forEach((s, i) => {
            s.classList.remove('active');
            if (i < index) s.classList.add('completed');
        });
        if (steps[index]) {
            steps[index].classList.add('active');
            steps[index].classList.remove('completed');
        }

        const offset = 226 - (226 * pct) / 100;
        if (progressFill) progressFill.style.strokeDashoffset = offset;
        if (progressPct) progressPct.textContent = `${pct}%`;
    }

    function showResult(videoUrl) {
        const resultSection = document.getElementById('result-section');
        const resultVideo = document.getElementById('result-video');
        const downloadBtn = document.getElementById('download-btn');

        if (resultVideo) resultVideo.src = videoUrl;
        if (downloadBtn) downloadBtn.href = videoUrl;
        if (resultSection) resultSection.classList.add('visible');
    }

    function showMessage(text, type) {
        const banner = document.getElementById('message-banner');
        const msgText = document.getElementById('message-text');
        if (banner && msgText) {
            msgText.textContent = text;
            banner.className = 'message-banner visible ' + type;
            setTimeout(() => banner.classList.remove('visible'), 5000);
        }
    }

    function shakeElement(el) {
        el.style.animation = 'none';
        el.offsetHeight; // trigger reflow
        el.style.animation = 'shake 0.4s ease';
        setTimeout(() => el.style.animation = '', 400);
    }

    // ─── New Video Button ───
    const newVideoBtn = document.getElementById('new-video-btn');
    if (newVideoBtn) {
        newVideoBtn.addEventListener('click', () => {
            const resultSection = document.getElementById('result-section');
            if (resultSection) resultSection.classList.remove('visible');
            textarea.value = '';
            fileInput.value = '';
            fileInfo.classList.remove('visible');
            charCounter.textContent = `0 / ${MAX_CHARS}`;
            // Reset progress
            steps.forEach(s => { s.classList.remove('active', 'completed'); });
            if (progressFill) progressFill.style.strokeDashoffset = 226;
            if (progressPct) progressPct.textContent = '0%';
        });
    }
});

// Shake keyframes (injected)
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25%      { transform: translateX(-6px); }
    50%      { transform: translateX(6px); }
    75%      { transform: translateX(-4px); }
  }
`;
document.head.appendChild(shakeStyle);
