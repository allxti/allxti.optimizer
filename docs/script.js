// ============================================
// GitHub Release Download Handler
// ============================================

const GITHUB_REPO = 'allxti/allxti.optimizer';
let latestReleaseData = null;
let downloadUrl = null;

// Fetch latest release info on page load
async function fetchLatestRelease() {
    try {
        const response = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/releases/latest`);

        if (response.status === 404) {
            // No releases yet - show fallback
            updateDownloadUI(null, 'No hay releases aún');
            return;
        }

        if (!response.ok) {
            throw new Error('API error');
        }

        latestReleaseData = await response.json();

        // Find the installer asset (look for .exe, .msi, or .zip)
        const assets = latestReleaseData.assets || [];
        let installerAsset = null;

        // Priority: .exe > .msi > .zip
        installerAsset = assets.find(a => a.name.endsWith('.exe'));
        if (!installerAsset) installerAsset = assets.find(a => a.name.endsWith('.msi'));
        if (!installerAsset) installerAsset = assets.find(a => a.name.endsWith('.zip'));

        if (installerAsset) {
            downloadUrl = installerAsset.browser_download_url;
            const sizeMB = (installerAsset.size / (1024 * 1024)).toFixed(1);
            updateDownloadUI(latestReleaseData.tag_name, `Instalador para Windows • ${sizeMB}MB`);
        } else if (latestReleaseData.zipball_url) {
            // Fallback to source code zip
            downloadUrl = latestReleaseData.zipball_url;
            updateDownloadUI(latestReleaseData.tag_name, 'Código fuente (ZIP)');
        } else {
            // Link to release page as last resort
            downloadUrl = latestReleaseData.html_url;
            updateDownloadUI(latestReleaseData.tag_name, 'Ver en GitHub Releases');
        }

    } catch (error) {
        console.warn('Could not fetch release info:', error);
        // Fallback to release page
        downloadUrl = `https://github.com/${GITHUB_REPO}/releases/latest`;
        updateDownloadUI('v0.1', 'Instalador para Windows');
    }
}

function updateDownloadUI(version, sizeText) {
    const versionEl = document.getElementById('latest-version');
    const sizeEl = document.getElementById('download-size');

    if (versionEl && version) {
        versionEl.textContent = version;
    }
    if (sizeEl) {
        sizeEl.textContent = sizeText;
    }
}

function downloadLatestRelease() {
    if (downloadUrl) {
        // Direct download
        window.location.href = downloadUrl;
    } else {
        // Fallback to releases page
        window.open(`https://github.com/${GITHUB_REPO}/releases/latest`, '_blank');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', fetchLatestRelease);

// ============================================
// Smooth scroll for navigation links
// ============================================
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

// ============================================
// Navbar background on scroll
// ============================================
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(10, 10, 15, 0.95)';
    } else {
        navbar.style.background = 'rgba(10, 10, 15, 0.8)';
    }
});

// ============================================
// Animate elements on scroll
// ============================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe feature cards, donate cards, etc.
document.querySelectorAll('.feature-card, .donate-card, .download-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Add animation class
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

// Stagger animations for grid items
document.querySelectorAll('.features-grid, .donate-grid').forEach(grid => {
    const children = grid.children;
    Array.from(children).forEach((child, index) => {
        child.style.transitionDelay = `${index * 0.1}s`;
    });
});

// ============================================
// Preview tiles live animation
// ============================================
const tiles = document.querySelectorAll('.tile-value');
setInterval(() => {
    tiles.forEach(tile => {
        const currentValue = tile.textContent;
        if (currentValue.includes('%')) {
            const num = parseInt(currentValue);
            const variation = Math.floor(Math.random() * 5) - 2;
            const newNum = Math.max(10, Math.min(90, num + variation));
            tile.textContent = newNum + '%';
        } else if (currentValue.includes('°C')) {
            const num = parseInt(currentValue);
            const variation = Math.floor(Math.random() * 3) - 1;
            const newNum = Math.max(45, Math.min(80, num + variation));
            tile.textContent = newNum + '°C';
        } else if (currentValue.includes('W')) {
            const num = parseInt(currentValue);
            const variation = Math.floor(Math.random() * 10) - 5;
            const newNum = Math.max(50, Math.min(150, num + variation));
            tile.textContent = newNum + 'W';
        } else if (!isNaN(parseInt(currentValue))) {
            const num = parseInt(currentValue);
            const variation = Math.floor(Math.random() * 10) - 5;
            const newNum = Math.max(60, Math.min(240, num + variation));
            tile.textContent = newNum;
        }
    });
}, 2000);

// ============================================
// Console easter egg
// ============================================
console.log('%c🚀 Allxti Optimizer', 'font-size: 24px; font-weight: bold; color: #6366f1;');
console.log('%cGracias por usar Allxti Optimizer!', 'font-size: 14px; color: #22d3ee;');
console.log('%c¿Interesado en el código? https://github.com/allxti/allxti.optimizer', 'font-size: 12px; color: #94a3b8;');
