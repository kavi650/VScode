// E-Bank Main JavaScript Functions

// QR Scanner functionality
function openQRScanner() {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'qr-modal';
    modal.innerHTML = `
        <div class="qr-modal-content">
            <div class="qr-modal-header">
                <h3><i class="fas fa-qrcode"></i> Scan & Pay</h3>
                <button class="qr-modal-close" onclick="closeQRScanner()">&times;</button>
            </div>
            <div class="qr-modal-body">
                <div class="qr-scanner-section">
                    <div class="camera-container">
                        <div class="camera-placeholder">
                            <i class="fas fa-camera" style="font-size: 4rem; color: #ccc;"></i>
                            <p>Camera will appear here</p>
                            <small>Point your camera at a QR code to scan</small>
                        </div>
                    </div>
                </div>
                
                <div class="qr-manual-section">
                    <h4>Or enter payment details manually:</h4>
                    <form class="qr-payment-form" onsubmit="processQRPayment(event)">
                        <div class="form-group">
                            <label>Recipient Account Number</label>
                            <input type="text" name="recipient" class="form-control" pattern="[0-9]{8}" required>
                        </div>
                        <div class="form-group">
                            <label>Amount (₹)</label>
                            <input type="number" name="amount" class="form-control" min="0.01" step="0.01" required>
                        </div>
                        <div class="form-group">
                            <label>Enter PIN</label>
                            <input type="password" name="pin" class="form-control" pattern="[0-9]{4}" maxlength="4" required>
                        </div>
                        <button type="submit" class="btn" style="width: 100%;">
                            <i class="fas fa-paper-plane"></i> Send Payment
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add modal styles
    const modalStyles = document.createElement('style');
    modalStyles.textContent = `
        .qr-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: fadeIn 0.3s ease-in;
        }
        
        .qr-modal-content {
            background: white;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
            max-height: 90%;
            overflow-y: auto;
        }
        
        .qr-modal-header {
            background: linear-gradient(135deg, var(--primary-dark), var(--primary-light));
            color: white;
            padding: 1.5rem;
            border-radius: 15px 15px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .qr-modal-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 50%;
            transition: background 0.3s ease;
        }
        
        .qr-modal-close:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .qr-modal-body {
            padding: 2rem;
        }
        
        .camera-container {
            margin: 2rem 0;
        }
        
        .camera-placeholder {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 3rem 2rem;
            text-align: center;
            color: #666;
        }
        
        .qr-manual-section {
            border-top: 1px solid #eee;
            margin-top: 2rem;
            padding-top: 2rem;
        }
    `;
    document.head.appendChild(modalStyles);
}

function closeQRScanner() {
    const modal = document.querySelector('.qr-modal');
    if (modal) {
        modal.remove();
    }
}

async function processQRPayment(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const paymentData = {
        recipient: formData.get('recipient'),
        amount: parseFloat(formData.get('amount')),
        pin: formData.get('pin')
    };
    
    try {
        // Show loading
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        submitBtn.disabled = true;
        
        // Simulate payment processing (replace with actual API call)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // For demo purposes, show success message
        showNotification('Payment sent successfully!', 'success');
        closeQRScanner();
        
        // Refresh page to update balance
        setTimeout(() => {
            window.location.reload();
        }, 1500);
        
    } catch (error) {
        showNotification('Payment failed. Please try again.', 'error');
        
        // Reset button
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Payment';
        submitBtn.disabled = false;
    }
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 'info-circle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Add notification styles if not already added
    if (!document.querySelector('#notification-styles')) {
        const notificationStyles = document.createElement('style');
        notificationStyles.id = 'notification-styles';
        notificationStyles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                color: var(--text-dark);
                padding: 1rem 1.5rem;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                z-index: 1001;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                animation: slideInRight 0.3s ease-out;
                max-width: 300px;
                border-left: 4px solid var(--primary-light);
            }
            
            .notification-success {
                border-left-color: var(--success);
            }
            
            .notification-error {
                border-left-color: var(--danger);
            }
            
            .notification button {
                background: none;
                border: none;
                font-size: 1.2rem;
                cursor: pointer;
                margin-left: auto;
                opacity: 0.6;
                transition: opacity 0.3s ease;
            }
            
            .notification button:hover {
                opacity: 1;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(notificationStyles);
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Form validation helpers
function validatePhoneNumber(input) {
    input.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
        if (this.value.length > 10) {
            this.value = this.value.slice(0, 10);
        }
    });
}

function validatePIN(input) {
    input.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
        if (this.value.length > 4) {
            this.value = this.value.slice(0, 4);
        }
    });
}

function validateAadhar(input) {
    input.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
        if (this.value.length > 12) {
            this.value = this.value.slice(0, 12);
        }
    });
}

// Tab functionality
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active classes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active classes
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// Loading overlay
function showLoadingOverlay(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    
    const overlayStyles = document.createElement('style');
    overlayStyles.textContent = `
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .loading-content {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .loading-content p {
            margin-top: 1rem;
            color: var(--text-dark);
        }
    `;
    
    if (!document.querySelector('#loading-overlay-styles')) {
        overlayStyles.id = 'loading-overlay-styles';
        document.head.appendChild(overlayStyles);
    }
    
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Dark Mode functionality
function initializeDarkMode() {
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    
    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Show notification
            showNotification(`${newTheme === 'dark' ? '🌙' : '☀️'} Switched to ${newTheme} mode`, 'success');
        });
    }
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dark mode
    initializeDarkMode();
    
    // Initialize tabs if present
    if (document.querySelector('.tab-btn')) {
        initializeTabs();
    }
    
    // Add validation to common form fields
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(validatePhoneNumber);
    
    const pinInputs = document.querySelectorAll('input[pattern="[0-9]{4}"]');
    pinInputs.forEach(validatePIN);
    
    const aadharInputs = document.querySelectorAll('input[pattern="[0-9]{12}"]');
    aadharInputs.forEach(validateAadhar);
    
    // Close modal when clicking outside
    document.addEventListener('click', function(event) {
        const modal = document.querySelector('.qr-modal');
        if (modal && event.target === modal) {
            closeQRScanner();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeQRScanner();
        }
    });
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Animation helpers
function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const difference = end - start;
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const value = start + (difference * progress);
        
        element.textContent = formatCurrency(value);
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}
