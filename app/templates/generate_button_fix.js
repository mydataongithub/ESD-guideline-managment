// Generate button
        document.getElementById('generateBtn').addEventListener('click', async function() {
            if (selectedTemplateId) {
                // Show loading state
                const originalText = this.textContent;
                this.textContent = 'Generating...';
                this.disabled = true;
                
                try {
                    let url = `/generate/${technologyName}`;
                    
                    // For now, we'll use the standard generation endpoint
                    // Template selection will be implemented in a future update
                    const response = await fetch(url, { 
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Failed to generate guideline');
                    }
                    
                    const data = await response.json();
                    console.log('Response:', data);
                    
                    if (data.message) {
                        // Check if it's a "no changes" message
                        if (data.message.includes('no changes')) {
                            const confirmView = confirm('Guideline already exists with no changes. Would you like to view it?');
                            if (confirmView) {
                                window.location.href = `/view/${technologyName}/latest`;
                            }
                        } else {
                            alert('Success! ' + data.message);
                            // Redirect to view
                            window.location.href = `/view/${technologyName}/latest`;
                        }
                    } else {
                        throw new Error('No message in response');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error generating guideline: ' + error.message);
                    this.textContent = originalText;
                    this.disabled = false;
                }
            }
        });