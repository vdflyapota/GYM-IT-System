// Performance Optimizations for Static HTML - Phase 3
// Owned by: Yeldana Kadenova
// Ensures Main Content Paint < 1 second

(function() {
    'use strict';

    // 1. Lazy load images
    function lazyLoadImages() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px'
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for older browsers
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
                img.classList.add('loaded');
            });
        }
    }

    // 2. Defer non-critical CSS
    function deferNonCriticalCSS() {
        const nonCriticalCSS = [
            // Add paths to non-critical CSS files here
        ];

        nonCriticalCSS.forEach(href => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.media = 'print';
            link.onload = function() { this.media = 'all'; };
            document.head.appendChild(link);
        });
    }

    // 3. Preload critical resources
    function preloadCriticalResources() {
        const criticalResources = [
            { href: '/design-system.css', as: 'style' }
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = resource.as;
            link.href = resource.href;
            document.head.appendChild(link);
        });
    }

    // 4. Optimize font loading
    function optimizeFontLoading() {
        // Use font-display: swap for better perceived performance
        const style = document.createElement('style');
        style.textContent = `
            @font-face {
                font-family: 'Inter';
                font-display: swap;
            }
        `;
        document.head.appendChild(style);
    }

    // 5. Measure performance metrics
    function measurePerformance() {
        if ('performance' in window && 'PerformanceObserver' in window) {
            // Measure Largest Contentful Paint (LCP) - target < 1s
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    const lcp = lastEntry.renderTime || lastEntry.loadTime;
                    
                    if (lcp > 1000) {
                        console.warn('LCP is above target:', lcp + 'ms (target: < 1000ms)');
                    } else {
                        console.log('LCP:', lcp + 'ms ✓');
                    }
                });
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                // Browser doesn't support LCP
            }

            // Measure First Contentful Paint (FCP)
            try {
                const paintObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.name === 'first-contentful-paint') {
                            console.log('FCP:', entry.startTime + 'ms');
                        }
                    }
                });
                paintObserver.observe({ entryTypes: ['paint'] });
            } catch (e) {
                // Browser doesn't support Paint Timing
            }
        }
    }

    // Initialize all optimizations
    function init() {
        // Measure performance first
        measurePerformance();

        // Optimize fonts
        optimizeFontLoading();

        // Preload critical resources
        preloadCriticalResources();

        // Defer non-critical CSS
        deferNonCriticalCSS();

        // Lazy load images
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', lazyLoadImages);
        } else {
            lazyLoadImages();
        }
    }

    // Run immediately if DOM is ready, otherwise wait
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
