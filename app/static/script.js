// app/static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const techSelector = document.getElementById('technologySelector');
    const generateBtn = document.getElementById('generateBtn');
    const viewLatestBtn = document.getElementById('viewLatestBtn');
    const viewHistoryBtn = document.getElementById('viewHistoryBtn');
    const generationStatus = document.getElementById('generationStatus');
    const systemStatus = document.getElementById('systemStatus');

    // Initialize the application
    init();

    async function init() {
        await loadTechnologies();
        await loadSystemStatus();
    }

    // Fetch and populate technologies
    async function loadTechnologies() {
        try {
            showStatus('Loading technologies...', 'info');
            const response = await fetch('/technologies');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const technologies = await response.json();
            
            techSelector.innerHTML = '<option value="">-- Select a Technology --</option>';
            
            if (technologies.length === 0) {
                techSelector.innerHTML += '<option value="">No technologies found</option>';
                showStatus('No technologies found. Please add configuration files.', 'warning');
                return;
            }
            
            technologies.forEach(tech => {
                const option = document.createElement('option');
                option.value = tech;
                option.textContent = formatTechnologyName(tech);
                techSelector.appendChild(option);
            });
            
            showStatus('Technologies loaded successfully.', 'success');
            
        } catch (error) {
            console.error('Error fetching technologies:', error);
            techSelector.innerHTML = '<option value="">Error loading technologies</option>';
            showStatus(`Error loading technologies: ${error.message}`, 'error');
        }
    }

    // Load system status
    async function loadSystemStatus() {
        try {
            const response = await fetch('/status');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const status = await response.json();
            displaySystemStatus(status);
            
        } catch (error) {
            console.error('Error fetching system status:', error);
            systemStatus.innerHTML = `<div class="status-error">Error loading system status: ${error.message}</div>`;
        }
    }

    // Display system status
    function displaySystemStatus(status) {
        let statusHtml = '';
        
        if (status.system === 'operational') {
            statusHtml += '<div class="status-ok">System: Operational</div>';
            statusHtml += `<div class="status-info">Available Technologies: ${status.available_technologies.length}</div>`;
            
            if (status.repository) {
                statusHtml += '<div class="status-section">';
                statusHtml += '<strong>Repository Status:</strong><br>';
                
                if (status.repository.git_available === false) {
                    statusHtml += '<div class="status-warning">Git: Not Available</div>';
                    statusHtml += '<div class="status-info">Version control features disabled</div>';
                    statusHtml += '<div class="status-info">Install Git to enable versioning</div>';
                } else {
                    statusHtml += `Branch: ${status.repository.active_branch || 'Unknown'}<br>`;
                    statusHtml += `Latest Commit: ${status.repository.latest_commit?.sha || 'None'}<br>`;
                    statusHtml += `Uncommitted Changes: ${status.repository.is_dirty ? 'Yes' : 'No'}`;
                }
                statusHtml += '</div>';
            }
        } else {
            statusHtml += `<div class="status-error">System Error: ${status.error}</div>`;
        }
        
        systemStatus.innerHTML = statusHtml;
    }

    // Generate guidelines
    generateBtn.addEventListener('click', async () => {
        const selectedTech = techSelector.value;
        
        if (!selectedTech) {
            showStatus('Please select a technology first.', 'warning');
            return;
        }
        
        try {
            showStatus(`Generating guidelines for ${formatTechnologyName(selectedTech)}...`, 'info');
            generateBtn.disabled = true;
            generateBtn.textContent = 'Generating...';
            
            const response = await fetch(`/generate/${selectedTech}`, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Generation failed');
            }
            
            const data = await response.json();
            
            let statusMessage = `✅ ${data.message}\n`;
            statusMessage += `📁 File: ${data.file_path}\n\n`;
            statusMessage += `📄 Content Preview:\n${data.content}`;
            
            showStatus(statusMessage, 'success');
            
            // Refresh system status
            await loadSystemStatus();
            
        } catch (error) {
            console.error('Error generating guidelines:', error);
            showStatus(`❌ Error: ${error.message}`, 'error');
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate/Update Selected';
        }
    });

    // View latest guidelines
    viewLatestBtn.addEventListener('click', () => {
        const selectedTech = techSelector.value;
        
        if (!selectedTech) {
            showStatus('Please select a technology to view.', 'warning');
            return;
        }
        
        window.open(`/view/${selectedTech}/latest`, '_blank');
    });

    // View guidelines history
    viewHistoryBtn.addEventListener('click', () => {
        const selectedTech = techSelector.value;
        
        if (!selectedTech) {
            showStatus('Please select a technology to view history.', 'warning');
            return;
        }
        
        window.open(`/view/${selectedTech}/history`, '_blank');
    });

    // Utility functions
    function formatTechnologyName(tech) {
        return tech.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function showStatus(message, type = 'info') {
        generationStatus.textContent = message;
        generationStatus.className = `status-${type}`;
        
        // Auto-clear success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                if (generationStatus.textContent === message) {
                    generationStatus.textContent = 'Ready to generate guidelines...';
                    generationStatus.className = '';
                }
            }, 5000);
        }
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'g':
                    e.preventDefault();
                    generateBtn.click();
                    break;
                case 'l':
                    e.preventDefault();
                    viewLatestBtn.click();
                    break;
                case 'h':
                    e.preventDefault();
                    viewHistoryBtn.click();
                    break;
            }
        }
    });

    // Add tooltip for keyboard shortcuts
    generateBtn.title = 'Generate guidelines (Ctrl+G)';
    viewLatestBtn.title = 'View latest guidelines (Ctrl+L)';
    viewHistoryBtn.title = 'View history (Ctrl+H)';
});
