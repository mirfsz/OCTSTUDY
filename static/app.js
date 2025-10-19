// SPF Study Coach - Client-side JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    
    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    if (currentTheme === 'dark') {
        html.classList.add('dark');
    }
    
    darkModeToggle.addEventListener('click', function() {
        html.classList.toggle('dark');
        const isDark = html.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // Toast notification system
    function showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Hide toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, duration);
    }

    // Global error handling
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
        showToast('An error occurred. Please try again.', 'error');
    });

    // Global fetch error handling
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Fetch error:', e.reason);
        showToast('Network error. Please check your connection.', 'error');
    });

    // Utility functions
    const utils = {
        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Format percentage
        formatPercentage: function(value, decimals = 1) {
            return (value * 100).toFixed(decimals) + '%';
        },

        // Get random element from array
        randomChoice: function(array) {
            return array[Math.floor(Math.random() * array.length)];
        },

        // Shuffle array
        shuffle: function(array) {
            const shuffled = [...array];
            for (let i = shuffled.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
            }
            return shuffled;
        }
    };

    // Make utils available globally
    window.utils = utils;

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape key to close modals/overlays
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (!modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                }
            });
        }

        // Ctrl/Cmd + K for search (if search functionality exists)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });

    // Form validation helpers
    function validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('border-red-500');
                isValid = false;
            } else {
                field.classList.remove('border-red-500');
            }
        });
        
        return isValid;
    }

    // Auto-save functionality for forms
    function setupAutoSave(form, key) {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Load saved data
            const savedData = localStorage.getItem(key);
            if (savedData) {
                try {
                    const data = JSON.parse(savedData);
                    if (data[input.name]) {
                        input.value = data[input.name];
                    }
                } catch (e) {
                    console.warn('Could not load saved data:', e);
                }
            }
            
            // Save on input
            input.addEventListener('input', utils.debounce(function() {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem(key, JSON.stringify(data));
            }, 1000));
        });
    }

    // Progress tracking
    function updateProgress(element, current, total) {
        const percentage = (current / total) * 100;
        const progressBar = element.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = percentage + '%';
        }
        
        const progressText = element.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${current}/${total}`;
        }
    }

    // Animation helpers
    function fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = performance.now();
        
        function animate(time) {
            let elapsed = time - start;
            let progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }

    function fadeOut(element, duration = 300) {
        let start = performance.now();
        
        function animate(time) {
            let elapsed = time - start;
            let progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = 1 - progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
            }
        }
        
        requestAnimationFrame(animate);
    }

    // Make animation helpers available globally
    window.fadeIn = fadeIn;
    window.fadeOut = fadeOut;

    // Service Worker registration (for offline functionality)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('ServiceWorker registration successful');
                })
                .catch(function(err) {
                    console.log('ServiceWorker registration failed');
                });
        });
    }

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
            }, 0);
        });
    }

    // Initialize tooltips (if any)
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const text = this.getAttribute('data-tooltip');
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded shadow-lg';
            tooltipElement.textContent = text;
            tooltipElement.style.top = this.offsetTop - 30 + 'px';
            tooltipElement.style.left = this.offsetLeft + 'px';
            
            this.style.position = 'relative';
            this.appendChild(tooltipElement);
        });
        
        tooltip.addEventListener('mouseleave', function() {
            const tooltipElement = this.querySelector('.absolute');
            if (tooltipElement) {
                tooltipElement.remove();
            }
        });
    });

    console.log('SPF Study Coach initialized successfully');
});
