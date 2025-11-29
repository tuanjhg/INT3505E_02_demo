/**
 * Library API Developer Portal - JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initTabs();
    initCodeTabs();
    initNavScroll();
    initCopyCode();
    initApiExplorer();
});

/**
 * Initialize endpoint tabs (Books, Users, Borrows, Auth)
 */
function initTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            // Remove active from all
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // Add active to clicked
            tab.classList.add('active');
            document.getElementById(target)?.classList.add('active');
        });
    });
}

/**
 * Initialize code example tabs (Python, JavaScript, cURL)
 */
function initCodeTabs() {
    const tabs = document.querySelectorAll('.code-tab');
    const panels = document.querySelectorAll('.code-panel');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.lang;
            
            // Remove active from all
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));
            
            // Add active to clicked
            tab.classList.add('active');
            document.getElementById(`code-${target}`)?.classList.add('active');
        });
    });
}

/**
 * Add shadow to navbar on scroll
 */
function initNavScroll() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

/**
 * Copy code functionality
 */
function initCopyCode() {
    document.querySelectorAll('.code-panel, .hero-code').forEach(block => {
        const pre = block.querySelector('pre');
        if (!pre) return;
        
        // Create copy button
        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.innerHTML = '<i class="fas fa-copy"></i>';
        btn.title = 'Copy to clipboard';
        
        btn.addEventListener('click', async () => {
            const code = pre.textContent;
            try {
                await navigator.clipboard.writeText(code);
                btn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    btn.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
        
        block.style.position = 'relative';
        block.appendChild(btn);
    });
    
    // Add copy button styles
    const style = document.createElement('style');
    style.textContent = `
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            color: #64748b;
            cursor: pointer;
            transition: all 0.3s;
        }
        .copy-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
        }
    `;
    document.head.appendChild(style);
}

/**
 * API Explorer functionality (for explorer page)
 */
function initApiExplorer() {
    const explorerForm = document.getElementById('api-explorer-form');
    if (!explorerForm) return;
    
    explorerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const method = document.getElementById('method').value;
        const endpoint = document.getElementById('endpoint').value;
        const body = document.getElementById('request-body')?.value;
        const token = document.getElementById('auth-token')?.value;
        
        const resultEl = document.getElementById('response-result');
        const statusEl = document.getElementById('response-status');
        
        try {
            resultEl.textContent = 'Loading...';
            statusEl.textContent = '';
            
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            if (token) {
                options.headers['Authorization'] = `Bearer ${token}`;
            }
            
            if (body && ['POST', 'PUT', 'PATCH'].includes(method)) {
                options.body = body;
            }
            
            const startTime = performance.now();
            const response = await fetch(endpoint, options);
            const endTime = performance.now();
            const duration = Math.round(endTime - startTime);
            
            const data = await response.json();
            
            // Show status
            statusEl.innerHTML = `
                <span class="status ${response.ok ? 'success' : 'error'}">
                    ${response.status} ${response.statusText}
                </span>
                <span class="time">${duration}ms</span>
            `;
            
            // Show response
            resultEl.textContent = JSON.stringify(data, null, 2);
            
        } catch (error) {
            statusEl.innerHTML = `<span class="status error">Error</span>`;
            resultEl.textContent = `Error: ${error.message}`;
        }
    });
}

/**
 * Smooth scroll for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/**
 * Animate elements on scroll
 */
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card, .stat-item, .endpoint-item').forEach(el => {
    el.classList.add('animate-ready');
    observer.observe(el);
});

// Add animation styles
const animStyle = document.createElement('style');
animStyle.textContent = `
    .animate-ready {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }
    .animate-in {
        opacity: 1;
        transform: translateY(0);
    }
`;
document.head.appendChild(animStyle);
