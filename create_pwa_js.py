import os

frontend_dir = r"C:\Users\tiruv\Desktop\milestone2\frontend"
pwa_js = """// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./service-worker.js')
            .then(registration => {
                console.log('[Service Worker] Registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('[Service Worker] Registration failed:', error);
            });
    });
}

// Handle PWA Installation
let deferredPrompt;
const installBtn = document.getElementById('installBtn');

if (installBtn) {
    installBtn.style.display = 'none'; // Hidden by default
}

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;
    // Update UI notify the user they can install the PWA
    if (installBtn) {
        installBtn.style.display = 'inline-block';
        
        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response to the install prompt: ${outcome}`);
                deferredPrompt = null;
                installBtn.style.display = 'none';
            }
        });
    }
});

window.addEventListener('appinstalled', (evt) => {
    console.log('[PWA] App was installed successfully');
    if (installBtn) installBtn.style.display = 'none';
});
"""

with open(os.path.join(frontend_dir, "pwa.js"), "w") as f:
    f.write(pwa_js)

print("Created pwa.js")
