// Performance utilities for Phase 3 - Lazy Loading & Performance Tuning
// Owned by: Yeldana Kadenova

/**
 * Lazy load images using Intersection Observer
 */
export function lazyLoadImages() {
  if (!('IntersectionObserver' in window)) {
    // Fallback for browsers without IntersectionObserver
    document.querySelectorAll('img[data-src]').forEach(img => {
      img.src = img.dataset.src
      img.classList.add('loaded')
    })
    return
  }

  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target
        img.src = img.dataset.src
        img.classList.add('loaded')
        observer.unobserve(img)
      }
    })
  }, {
    rootMargin: '50px' // Start loading 50px before image enters viewport
  })

  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img)
  })
}

/**
 * Preload critical resources
 */
export function preloadCriticalResources() {
  const criticalResources = [
    '/design-system.css',
    // Add other critical resources here
  ]

  criticalResources.forEach(resource => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.as = 'style'
    link.href = resource
    document.head.appendChild(link)
  })
}

/**
 * Measure and log performance metrics
 */
export function measurePerformance() {
  if ('performance' in window && 'PerformanceObserver' in window) {
    // Measure Largest Contentful Paint (LCP)
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const lastEntry = entries[entries.length - 1]
      console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime)
    })

    try {
      observer.observe({ entryTypes: ['largest-contentful-paint'] })
    } catch (e) {
      // Browser doesn't support LCP
    }

    // Measure First Contentful Paint (FCP)
    const paintObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          console.log('FCP:', entry.startTime)
        }
      }
    })

    try {
      paintObserver.observe({ entryTypes: ['paint'] })
    } catch (e) {
      // Browser doesn't support Paint Timing
    }
  }
}

/**
 * Optimize font loading
 */
export function optimizeFontLoading() {
  // Preload fonts
  const fontLink = document.createElement('link')
  fontLink.rel = 'preconnect'
  fontLink.href = 'https://fonts.googleapis.com'
  document.head.appendChild(fontLink)

  // Use font-display: swap for better perceived performance
  const style = document.createElement('style')
  style.textContent = `
    @font-face {
      font-family: 'Inter';
      font-display: swap;
    }
  `
  document.head.appendChild(style)
}

/**
 * Initialize all performance optimizations
 */
export function initPerformanceOptimizations() {
  // Measure performance
  measurePerformance()

  // Optimize fonts
  optimizeFontLoading()

  // Preload critical resources
  preloadCriticalResources()

  // Lazy load images after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', lazyLoadImages)
  } else {
    lazyLoadImages()
  }
}
