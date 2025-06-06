// Copy functionality for Cognitrix prompt management system
// Add this JavaScript to your templates/base.html or create a separate static/js/copy.js file

// Copy to clipboard function with visual feedback
async function copyToClipboard(text, buttonElement) {
    try {
        // Use modern clipboard API
        await navigator.clipboard.writeText(text);
        
        // Visual feedback - change button text and style temporarily
        const originalText = buttonElement.innerHTML;
        const originalClass = buttonElement.className;
        
        buttonElement.innerHTML = '<i class="fas fa-check"></i> Copied!';
        buttonElement.className = buttonElement.className.replace('btn-outline-light', 'btn-success');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            buttonElement.innerHTML = originalText;
            buttonElement.className = originalClass;
        }, 2000);
        
    } catch (err) {
        // Fallback for browsers that don't support clipboard API
        fallbackCopyToClipboard(text, buttonElement);
    }
}

// Fallback copy method for older browsers
function fallbackCopyToClipboard(text, buttonElement) {
    // Create temporary textarea element
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    
    try {
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        
        // Visual feedback
        const originalText = buttonElement.innerHTML;
        const originalClass = buttonElement.className;
        
        buttonElement.innerHTML = '<i class="fas fa-check"></i> Copied!';
        buttonElement.className = buttonElement.className.replace('btn-outline-light', 'btn-success');
        
        setTimeout(() => {
            buttonElement.innerHTML = originalText;
            buttonElement.className = originalClass;
        }, 2000);
        
    } catch (err) {
        console.error('Copy failed:', err);
        
        // Show error feedback
        const originalText = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="fas fa-times"></i> Failed';
        buttonElement.className = buttonElement.className.replace('btn-outline-light', 'btn-danger');
        
        setTimeout(() => {
            buttonElement.innerHTML = originalText;
            buttonElement.className = buttonElement.className.replace('btn-danger', 'btn-outline-light');
        }, 2000);
    } finally {
        document.body.removeChild(textArea);
    }
}

// Copy prompt content (handles both simple and templated prompts)
function copyPromptContent(promptContent, variables = {}) {
    // Replace variables in templated prompts
    let processedContent = promptContent;
    
    if (Object.keys(variables).length > 0) {
        // Replace {variable} placeholders with actual values
        for (const [key, value] of Object.entries(variables)) {
            const placeholder = `{${key}}`;
            processedContent = processedContent.replace(new RegExp(placeholder, 'g'), value);
        }
    }
    
    return processedContent;
}

// Event listener for copy buttons
document.addEventListener('DOMContentLoaded', function() {
    // Handle copy buttons on prompt cards
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('copy-btn') || e.target.closest('.copy-btn')) {
            e.preventDefault();
            
            const button = e.target.classList.contains('copy-btn') ? e.target : e.target.closest('.copy-btn');
            const promptContent = button.getAttribute('data-content');
            
            if (promptContent) {
                copyToClipboard(promptContent, button);
                
                // Track usage analytics (optional)
                trackPromptUsage(button.getAttribute('data-prompt-id'));
            }
        }
        
        // Handle copy with variables button
        if (e.target.classList.contains('copy-with-vars-btn') || e.target.closest('.copy-with-vars-btn')) {
            e.preventDefault();
            
            const button = e.target.classList.contains('copy-with-vars-btn') ? e.target : e.target.closest('.copy-with-vars-btn');
            const promptContent = button.getAttribute('data-content');
            const variableInputs = button.closest('.prompt-card').querySelectorAll('.variable-input');
            
            // Collect variable values
            const variables = {};
            variableInputs.forEach(input => {
                const varName = input.getAttribute('data-variable');
                variables[varName] = input.value || `{${varName}}`;
            });
            
            const processedContent = copyPromptContent(promptContent, variables);
            copyToClipboard(processedContent, button);
            
            // Track usage analytics (optional)
            trackPromptUsage(button.getAttribute('data-prompt-id'));
        }
    });
});

// Optional: Track prompt usage for analytics
function trackPromptUsage(promptId) {
    if (!promptId) return;
    
    // Send usage data to backend (implement if needed)
    fetch('/api/track-usage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt_id: promptId,
            action: 'copy',
            timestamp: new Date().toISOString()
        })
    }).catch(err => {
        console.log('Usage tracking failed:', err);
        // Don't show error to user - this is non-critical
    });
}

// Function to add variable input fields dynamically
function addVariableInputs(promptCard, variables) {
    const variablesContainer = promptCard.querySelector('.variables-container');
    if (!variablesContainer || !variables || variables.length === 0) return;
    
    variablesContainer.innerHTML = '';
    
    variables.forEach(variable => {
        const inputGroup = document.createElement('div');
        inputGroup.className = 'mb-2';
        inputGroup.innerHTML = `
            <label class="form-label text-light small">${variable}:</label>
            <input type="text" 
                   class="form-control form-control-sm bg-dark text-light variable-input" 
                   data-variable="${variable}"
                   placeholder="Enter ${variable}">
        `;
        variablesContainer.appendChild(inputGroup);
    });
}

// Keyboard shortcuts for copy functionality
document.addEventListener('keydown', function(e) {
    // Ctrl+C on focused prompt card copies the content
    if (e.ctrlKey && e.key === 'c' && e.target.classList.contains('prompt-card-focused')) {
        e.preventDefault();
        const copyBtn = e.target.querySelector('.copy-btn');
        if (copyBtn) {
            copyBtn.click();
        }
    }
});

// Add focus capability to prompt cards for keyboard navigation
document.addEventListener('DOMContentLoaded', function() {
    const promptCards = document.querySelectorAll('.prompt-card');
    promptCards.forEach(card => {
        card.setAttribute('tabindex', '0');
        
        card.addEventListener('focus', function() {
            this.classList.add('prompt-card-focused');
        });
        
        card.addEventListener('blur', function() {
            this.classList.remove('prompt-card-focused');
        });
    });
});