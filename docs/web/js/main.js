// GA-Scrap Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initSmoothScrolling();
    initCodeCopying();
    initSearchFunctionality();
    initThemeToggle();
    initPlayground();
    initTOC();
    initProgressBar();
    
    // Add fade-in animation to elements
    animateOnScroll();
});

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Copy code functionality
function initCodeCopying() {
    // Add copy buttons to code blocks
    document.querySelectorAll('pre code').forEach(block => {
        const button = document.createElement('button');
        button.className = 'btn btn-sm btn-outline-light copy-btn';
        button.innerHTML = '<i class="bi bi-clipboard"></i>';
        button.title = 'Copy code';
        
        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper position-relative';
        block.parentNode.parentNode.insertBefore(wrapper, block.parentNode);
        wrapper.appendChild(block.parentNode);
        wrapper.appendChild(button);
        
        button.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent).then(() => {
                button.innerHTML = '<i class="bi bi-check"></i>';
                button.classList.remove('btn-outline-light');
                button.classList.add('btn-success');
                
                setTimeout(() => {
                    button.innerHTML = '<i class="bi bi-clipboard"></i>';
                    button.classList.remove('btn-success');
                    button.classList.add('btn-outline-light');
                }, 2000);
            });
        });
    });
}

// Search functionality
function initSearchFunctionality() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput) return;
    
    let searchIndex = [];
    
    // Build search index
    function buildSearchIndex() {
        const pages = [
            { title: 'Getting Started', url: 'getting-started.html', content: 'installation setup first scraper' },
            { title: 'Sandbox Mode', url: 'sandbox-mode.html', content: 'error handling development resilient' },
            { title: 'Sync Interface', url: 'sync-interface.html', content: 'synchronous api no async await' },
            { title: 'Playwright API', url: 'playwright-api.html', content: 'complete features a-z access' },
            { title: 'Examples', url: 'examples.html', content: 'real world use cases practical' },
            { title: 'Hot Reload', url: 'hot-reload.html', content: 'development workflow instant feedback' }
        ];
        
        searchIndex = pages;
    }
    
    // Perform search
    function performSearch(query) {
        if (!query.trim()) {
            searchResults.innerHTML = '';
            searchResults.style.display = 'none';
            return;
        }
        
        const results = searchIndex.filter(page => 
            page.title.toLowerCase().includes(query.toLowerCase()) ||
            page.content.toLowerCase().includes(query.toLowerCase())
        );
        
        displaySearchResults(results);
    }
    
    // Display search results
    function displaySearchResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="p-3 text-muted">No results found</div>';
        } else {
            searchResults.innerHTML = results.map(result => `
                <a href="${result.url}" class="list-group-item list-group-item-action">
                    <strong>${result.title}</strong>
                    <div class="text-muted small">${result.content}</div>
                </a>
            `).join('');
        }
        
        searchResults.style.display = 'block';
    }
    
    buildSearchIndex();
    
    searchInput.addEventListener('input', (e) => {
        performSearch(e.target.value);
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}

// Theme toggle functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update icon
        const icon = themeToggle.querySelector('i');
        icon.className = newTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
    });
}

// Playground functionality
function initPlayground() {
    const playground = document.getElementById('playground');
    if (!playground) return;
    
    const editor = document.getElementById('playground-editor');
    const output = document.getElementById('playground-output');
    const runButton = document.getElementById('run-code');
    
    // Initialize with example code
    const exampleCode = `from ga_scrap import SyncGAScrap

with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://quotes.toscrape.com")
    quotes = scraper.get_all_text(".quote .text")
    authors = scraper.get_all_text(".quote .author")
    
    for quote, author in zip(quotes[:3], authors[:3]):
        print(f'"{quote}" - {author}')`;
    
    if (editor) {
        editor.value = exampleCode;
    }
    
    if (runButton) {
        runButton.addEventListener('click', () => {
            runCode(editor.value);
        });
    }
    
    function runCode(code) {
        output.innerHTML = '<div class="text-info">🚀 Running code...</div>';
        
        // Simulate code execution (in real implementation, this would send to backend)
        setTimeout(() => {
            const simulatedOutput = `
🚀 Starting scraper...
✅ Browser started successfully
🌐 Navigating to https://quotes.toscrape.com
📄 Page loaded successfully
🔍 Found 10 quotes on page
📝 Extracting quote data...

"The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking." - Albert Einstein

"It is our choices, Harry, that show what we truly are, far more than our abilities." - J.K. Rowling

"There are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle." - Albert Einstein

✅ Scraping completed successfully!
🔒 Browser closed
`;
            
            output.innerHTML = `<pre>${simulatedOutput}</pre>`;
        }, 2000);
    }
}

// Table of Contents generation
function initTOC() {
    const tocContainer = document.getElementById('toc');
    if (!tocContainer) return;
    
    const headings = document.querySelectorAll('.doc-content h2, .doc-content h3');
    if (headings.length === 0) return;
    
    const tocList = document.createElement('ul');
    tocList.className = 'list-unstyled';
    
    headings.forEach((heading, index) => {
        const id = heading.id || `heading-${index}`;
        heading.id = id;
        
        const listItem = document.createElement('li');
        listItem.className = heading.tagName === 'H3' ? 'ms-3' : '';
        
        const link = document.createElement('a');
        link.href = `#${id}`;
        link.textContent = heading.textContent;
        link.className = 'text-decoration-none';
        
        listItem.appendChild(link);
        tocList.appendChild(listItem);
    });
    
    tocContainer.appendChild(tocList);
}

// Reading progress bar
function initProgressBar() {
    const progressBar = document.getElementById('reading-progress');
    if (!progressBar) return;
    
    window.addEventListener('scroll', () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        
        progressBar.style.width = scrolled + '%';
    });
}

// Animate elements on scroll
function animateOnScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    });
    
    document.querySelectorAll('.feature-card, .learning-path, .doc-content h2').forEach(el => {
        observer.observe(el);
    });
}

// Utility functions
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container') || document.body;
    container.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Export functions for use in other scripts
window.GAScrapDocs = {
    showToast,
    initPlayground,
    initSearchFunctionality
};

// Add CSS for copy buttons
const style = document.createElement('style');
style.textContent = `
.code-wrapper {
    position: relative;
}

.copy-btn {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    z-index: 10;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.code-wrapper:hover .copy-btn {
    opacity: 1;
}

#reading-progress {
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: var(--primary-color);
    z-index: 9999;
    transition: width 0.2s ease;
}

.search-container {
    position: relative;
}

#search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    z-index: 1000;
    max-height: 300px;
    overflow-y: auto;
}

[data-theme="dark"] {
    --bs-body-bg: #1a1a1a;
    --bs-body-color: #e9ecef;
}

[data-theme="dark"] .navbar-dark {
    background-color: #000 !important;
}

[data-theme="dark"] .bg-light {
    background-color: #2d2d2d !important;
}

[data-theme="dark"] .feature-card,
[data-theme="dark"] .learning-path {
    background-color: #2d2d2d;
    color: #e9ecef;
}

[data-theme="dark"] #search-results {
    background-color: #2d2d2d;
    border-color: #495057;
}
`;

document.head.appendChild(style);
