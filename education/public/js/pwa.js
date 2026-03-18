// PWA Registration for UEAB SAMS - Frappe 16
(function() {
    'use strict';
    
    // Register service worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('[PWA] ServiceWorker registered:', registration.scope);
                    
                    // Check for updates periodically
                    setInterval(() => registration.update(), 60 * 60 * 1000); // Every hour
                })
                .catch(function(error) {
                    console.log('[PWA] ServiceWorker registration failed:', error);
                });
        });
    }
    
    // Install prompt handling
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', function(e) {
        console.log('[PWA] beforeinstallprompt fired');
        e.preventDefault();
        deferredPrompt = e;
        
        // Show install button after a delay
        setTimeout(showInstallPrompt, 3000);
    });
    
    function showInstallPrompt() {
        if (!deferredPrompt) return;
        if (document.getElementById('pwa-install-prompt')) return;
        
        const prompt = document.createElement('div');
        prompt.id = 'pwa-install-prompt';
        prompt.innerHTML = `
            <div style="position:fixed;bottom:20px;left:20px;right:20px;max-width:400px;margin:0 auto;
                        background:#0b4a6f;color:white;padding:15px 20px;border-radius:12px;
                        box-shadow:0 4px 20px rgba(0,0,0,0.3);z-index:99999;display:flex;
                        align-items:center;gap:15px;font-family:sans-serif;">
                <div style="font-size:32px;">📱</div>
                <div style="flex:1;">
                    <div style="font-weight:600;margin-bottom:4px;">Install UEAB SAMS</div>
                    <div style="font-size:13px;opacity:0.9;">Add to home screen for quick access</div>
                </div>
                <button id="pwa-install-btn" style="background:white;color:#0b4a6f;border:none;
                        padding:10px 20px;border-radius:8px;font-weight:600;cursor:pointer;">
                    Install
                </button>
                <button id="pwa-dismiss-btn" style="background:transparent;color:white;border:none;
                        font-size:20px;cursor:pointer;padding:5px;">✕</button>
            </div>
        `;
        document.body.appendChild(prompt);
        
        document.getElementById('pwa-install-btn').onclick = installPWA;
        document.getElementById('pwa-dismiss-btn').onclick = function() {
            prompt.remove();
        };
        
        // Auto-hide after 15 seconds
        setTimeout(() => prompt.remove(), 15000);
    }
    
    function installPWA() {
        if (!deferredPrompt) return;
        
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function(result) {
            console.log('[PWA] User choice:', result.outcome);
            if (result.outcome === 'accepted') {
                const prompt = document.getElementById('pwa-install-prompt');
                if (prompt) prompt.remove();
            }
            deferredPrompt = null;
        });
    }
    
    // Expose globally
    window.installPWA = installPWA;
    
    // Track installation
    window.addEventListener('appinstalled', function() {
        console.log('[PWA] App installed successfully');
        deferredPrompt = null;
    });
    
    // Detect standalone mode
    if (window.matchMedia('(display-mode: standalone)').matches || 
        window.navigator.standalone === true) {
        console.log('[PWA] Running in standalone mode');
        document.body.classList.add('pwa-standalone');
    }
    
    // Online/Offline indicators
    function updateOnlineStatus() {
        const isOnline = navigator.onLine;
        document.body.classList.toggle('is-offline', !isOnline);
        
        if (!isOnline) {
            // Show offline indicator
            let indicator = document.getElementById('offline-indicator');
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.id = 'offline-indicator';
                indicator.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#f44336;color:white;text-align:center;padding:8px;font-size:14px;z-index:99999;';
                indicator.textContent = '📡 You are offline. Some features may not work.';
                document.body.prepend(indicator);
            }
        } else {
            const indicator = document.getElementById('offline-indicator');
            if (indicator) indicator.remove();
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    console.log('[PWA] Initialized');
})();
