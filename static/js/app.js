/* ============================================
   Pachbaale Creations AI Studio — Interactions
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // ── Tab Switching ──────────────────────────────
    const tabs = document.querySelectorAll('.mode-tab');
    const panels = document.querySelectorAll('.engine-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.target;
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });

    // ── File Upload Feedback ───────────────────────
    function setupUpload(inputId, badgeId, labelSingular, labelPlural) {
        const input = document.getElementById(inputId);
        const badge = document.getElementById(badgeId);
        if (!input || !badge) return;

        input.addEventListener('change', () => {
            const count = input.files.length;
            if (count > 0) {
                badge.textContent = `${count} ${count === 1 ? labelSingular : labelPlural} selected ✅`;
                badge.style.display = 'inline-flex';
            } else {
                badge.style.display = 'none';
            }
        });
    }

    setupUpload('videoInput', 'videoBadge', 'video', 'videos');
    setupUpload('photoInput', 'photoBadge', 'photo', 'photos');
    setupUpload('musicInput', 'musicBadge', 'track', 'tracks');

    // ── Drag-and-drop Zones ────────────────────────
    document.querySelectorAll('.upload-zone').forEach(zone => {
        const fileInput = zone.querySelector('input[type="file"]');

        zone.addEventListener('dragover', e => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            if (fileInput && e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    });

    // ── Text-area Character Counter ────────────────
    document.querySelectorAll('.form-textarea').forEach(ta => {
        const counter = ta.parentElement.querySelector('.char-count');
        if (!counter) return;

        const max = ta.maxLength > 0 ? ta.maxLength : 1000;
        const update = () => { counter.textContent = `${ta.value.length} / ${max}`; };
        ta.addEventListener('input', update);
        update();
    });

    // ── Loading Overlay ────────────────────────────
    const overlay = document.getElementById('loadingOverlay');
    document.querySelectorAll('.engine-form').forEach(form => {
        form.addEventListener('submit', () => {
            if (overlay) overlay.classList.add('visible');
        });
    });

    // ── Particle Background ────────────────────────
    const canvas = document.getElementById('particles-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let particles = [];
        const COUNT = 60;
        const COLORS = ['rgba(245,197,24,0.4)', 'rgba(139,92,246,0.3)', 'rgba(6,214,160,0.3)', 'rgba(255,255,255,0.15)'];

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        function createParticle() {
            return {
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: Math.random() * 2 + 0.5,
                dx: (Math.random() - 0.5) * 0.4,
                dy: (Math.random() - 0.5) * 0.4,
                color: COLORS[Math.floor(Math.random() * COLORS.length)],
            };
        }

        for (let i = 0; i < COUNT; i++) particles.push(createParticle());

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.x += p.dx;
                p.y += p.dy;
                if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
            });
            requestAnimationFrame(animate);
        }
        animate();
    }

    // ── Intersection Observer for scroll animations ─
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.engine-card, .result-section').forEach(el => {
        // Set initial state that works even if JS is slow or fails
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
        
        try {
            // Apply animations only if supported and working
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        } catch (err) {
            console.warn("Scroll animation failed to initialize for element:", el, err);
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }
    });
});
