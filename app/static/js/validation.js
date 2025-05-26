/* app/static/js/validation.js */
/**
 * Validation functionality for ESD & Latch-up Guidelines application
 * Handles notifications and validation-related UI interactions
 */

// Notification system
class NotificationSystem {
    constructor() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.style.position = 'fixed';
        this.container.style.top = '20px';
        this.container.style.right = '20px';
        this.container.style.zIndex = '1000';
        document.body.appendChild(this.container);
    }

    /**
     * Show a notification message
     * @param {string} message - The message to display
     * @param {string} type - Type of notification (success, error, warning, info)
     * @param {number} duration - Duration in milliseconds
     */
    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            ${message}
            <button class="notification-close">&times;</button>
        `;

        // Add notification to container
        this.container.appendChild(notification);

        // Add close button functionality
        const closeButton = notification.querySelector('.notification-close');
        closeButton.addEventListener('click', () => {
            this.close(notification);
        });

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);

        // Auto close after duration
        if (duration > 0) {
            setTimeout(() => {
                this.close(notification);
            }, duration);
        }

        return notification;
    }

    /**
     * Close a notification
     * @param {HTMLElement} notification - The notification to close
     */
    close(notification) {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-10px)';

        setTimeout(() => {
            notification.remove();
        }, 300);
    }

    /**
     * Show a success message
     * @param {string} message - The message to display
     * @param {number} duration - Duration in milliseconds
     */
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    /**
     * Show an error message
     * @param {string} message - The message to display
     * @param {number} duration - Duration in milliseconds
     */
    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    /**
     * Show a warning message
     * @param {string} message - The message to display
     * @param {number} duration - Duration in milliseconds
     */
    warning(message, duration = 5000) {
        return this.show(message, 'warning', duration);
    }

    /**
     * Show an info message
     * @param {string} message - The message to display
     * @param {number} duration - Duration in milliseconds
     */
    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }
}

// Initialize the notification system
const notifications = new NotificationSystem();

// Function to approve validation with notification
function approveValidation(id) {
    const username = prompt("Enter your name for validation attribution:", "");
    const notes = prompt("Enter any comments or notes:", "");
    
    if (username !== null) {
        fetch(`/validation/review/${id}/approve?validator=${encodeURIComponent(username)}&validator_notes=${encodeURIComponent(notes || '')}`, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Approval failed');
            }
            return response.json();
        })
        .then(data => {
            notifications.success(`Rule approved successfully and added to guidelines!`);
            setTimeout(() => {
                window.location.href = '/validation/ui/list';
            }, 2000);
        })
        .catch(error => {
            notifications.error(`Error: ${error.message}`);
        });
    }
}

// Function to reject validation with notification
function rejectValidation(id) {
    const username = prompt("Enter your name for validation attribution:", "");
    const notes = prompt("Please provide a reason for rejection:", "");
    
    if (username !== null) {
        if (!notes) {
            notifications.warning("Please provide a reason for rejection.");
            return;
        }
        
        fetch(`/validation/review/${id}/reject?validator=${encodeURIComponent(username)}&validator_notes=${encodeURIComponent(notes)}`, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Rejection failed');
            }
            return response.json();
        })
        .then(data => {
            notifications.info(`Rule rejected. Team will be notified.`);
            setTimeout(() => {
                window.location.href = '/validation/ui/list';
            }, 2000);
        })
        .catch(error => {
            notifications.error(`Error: ${error.message}`);
        });
    }
}

// Function to mark validation for review with notification
function needsReview(id) {
    const username = prompt("Enter your name for validation attribution:", "");
    const notes = prompt("Enter details about what needs to be reviewed:", "");
    
    if (username !== null) {
        fetch(`/validation/review/${id}/needs-review?validator=${encodeURIComponent(username)}&validator_notes=${encodeURIComponent(notes || '')}`, {
            method: 'POST'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Status update failed');
            }
            return response.json();
        })
        .then(data => {
            notifications.info(`Rule marked for expert review. ESD experts will be notified.`);
            setTimeout(() => {
                window.location.href = '/validation/ui/list';
            }, 2000);
        })
        .catch(error => {
            notifications.error(`Error: ${error.message}`);
        });
    }
}

// Export functions globally
window.approveValidation = approveValidation;
window.rejectValidation = rejectValidation;
window.needsReview = needsReview;
window.notifications = notifications;
