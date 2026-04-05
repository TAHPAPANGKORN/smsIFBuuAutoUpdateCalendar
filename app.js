/**
 * InforExam Sync - Main Application Logic
 * Professional handcrafted ES6+ JavaScript
 */

const App = {
    state: {
        isDark: false,
        studentId: '',
        exams: [],
        isLoading: false,
    },

    elements: {
        body: document.body,
        input: document.getElementById('std_id'),
        appleBtn: document.getElementById('apple_btn'),
        copyBtn: document.getElementById('copy_btn'),
        preview: document.getElementById('preview'),
        examList: document.getElementById('exam-list'),
        countdown: document.getElementById('countdown'),
        themeToggle: document.getElementById('theme-toggle'),
        guideToggle: document.getElementById('show_how'),
        guideModal: document.getElementById('guide-modal'),
        closeGuide: document.getElementById('close_guide'),
        sunIcon: document.getElementById('sun-icon'),
        moonIcon: document.getElementById('moon-icon'),
    },

    icons: {
        calendar: '<svg width="14" height="14" viewbox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>',
        clock: '<svg width="14" height="14" viewbox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
        mapPin: '<svg width="14" height="14" viewbox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>',
        user: '<svg width="14" height="14" viewbox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
    },

    init() {
        this.loadTheme();
        this.bindEvents();
        console.log('✨ InforExam Sync Application Initialized');
    },

    bindEvents() {
        this.elements.input.addEventListener('input', (e) => this.handleInput(e));
        this.elements.themeToggle.addEventListener('click', () => this.toggleTheme());
        this.elements.appleBtn.addEventListener('click', () => this.subscribeApple());
        this.elements.copyBtn.addEventListener('click', () => this.copyLink());
        this.elements.guideToggle.addEventListener('click', () => this.setGuide(true));
        this.elements.closeGuide.addEventListener('click', () => this.setGuide(false));
        
        window.onclick = (e) => {
            if (e.target === this.elements.guideModal) this.setGuide(false);
        };
    },

    loadTheme() {
        const saved = localStorage.getItem('theme');
        const preferDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.setTheme(saved === 'dark' || (!saved && preferDark));
    },

    setTheme(isDark) {
        this.state.isDark = isDark;
        this.elements.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
        this.elements.sunIcon.style.display = isDark ? 'none' : 'block';
        this.elements.moonIcon.style.display = isDark ? 'block' : 'none';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    },

    toggleTheme() {
        this.setTheme(!this.state.isDark);
    },

    handleInput(e) {
        let val = e.target.value.trim();
        if (val.length > 8) {
            val = val.substring(0, 8);
            e.target.value = val;
        }

        this.state.studentId = val;
        this.updateActionButtons();

        if (val.length === 8) {
            this.fetchExams();
        } else {
            this.setPreviewVisibility(false);
        }
    },

    updateActionButtons() {
        const isValid = this.state.studentId.length === 8;
        this.elements.appleBtn.disabled = !isValid;
        this.elements.copyBtn.disabled = !isValid;
    },

    async fetchExams() {
        this.state.isLoading = true;
        this.showLoadingUI();

        try {
            const res = await fetch(`/api/preview/${this.state.studentId}`);
            if (!res.ok) throw new Error('Fetch failed');
            this.state.exams = await res.json();
            this.renderExams();
        } catch (err) {
            this.showErrorUI();
        } finally {
            this.state.isLoading = false;
        }
    },

    showLoadingUI() {
        this.setPreviewVisibility(true);
        this.elements.countdown.innerText = 'Calculating...';
        this.elements.examList.innerHTML = `
            <div class="exam-card skeleton" style="height: 100px"></div>
            <div class="exam-card skeleton" style="height: 100px"></div>
        `;
    },

    showErrorUI() {
        this.elements.examList.innerHTML = `<div style="text-align:center; padding:2rem; font-weight:600; color:var(--error)">⚠️ No data found for this ID.</div>`;
        this.elements.countdown.innerText = 'Not found';
    },

    setPreviewVisibility(show) {
        this.elements.preview.style.display = show ? 'block' : 'none';
    },

    renderExams() {
        if (!this.state.exams || this.state.exams.length === 0) {
            this.elements.examList.innerHTML = `
                <div style="text-align:center; padding:2rem; color:var(--text-muted)">
                    <p>📅 No upcoming exams found.</p>
                    <p style="font-size:0.85rem; margin-top:0.5rem; opacity:0.8;">
                        You can still subscribe! Your calendar will automatically sync as soon as exams are posted.
                    </p>
                </div>`;
            this.elements.countdown.innerText = 'Empty';
            return;
        }

        this.elements.examList.innerHTML = this.state.exams.map(exam => `
            <div class="exam-card">
                <div class="exam-title">${exam.subject}</div>
                <div class="exam-meta">
                    <div class="meta-item">${this.icons.calendar} <strong>${exam.date}</strong></div>
                    <div class="meta-item">${this.icons.clock} ${exam.time}</div>
                    <div class="meta-item">${this.icons.mapPin} ${exam.room}</div>
                    <div class="meta-item">${this.icons.user} Seat: <strong>${exam.seat || '-'}</strong></div>
                </div>
            </div>
        `).join('');

        this.elements.countdown.innerText = `${this.state.exams.length} Items`;

        // Staggered Entrance Animation
        const cards = this.elements.examList.querySelectorAll('.exam-card');
        cards.forEach((card, i) => {
            setTimeout(() => card.classList.add('show'), i * 80);
        });
    },

    subscribeApple() {
        window.location.href = `webcal://${window.location.host}/std/${this.state.studentId}`;
    },

    async copyLink() {
        const link = `${window.location.origin}/std/${this.state.studentId}`;
        try {
            await navigator.clipboard.writeText(link);
            const originalText = this.elements.copyBtn.innerHTML;
            this.elements.copyBtn.innerHTML = 'Link Copied!';
            setTimeout(() => this.elements.copyBtn.innerHTML = originalText, 2000);
        } catch (err) {
            alert('Calendar Link: ' + link);
        }
    },

    setGuide(show) {
        this.elements.guideModal.style.display = show ? 'flex' : 'none';
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
