// Cache for styled buttons to avoid re-styling
const styledButtonsCache = new WeakSet();

// Function to style yao line buttons by directly applying inline styles
function styleYaoButtons() {
    // Use more specific selector - only buttons with yao-line-button class or containing hexagram symbols
    const yaoButtons = document.querySelectorAll('button.yao-line-button, button:has-text("▅▅")');
    // Fallback: query all buttons but check early
    const allButtons = yaoButtons.length > 0 ? yaoButtons : document.querySelectorAll('button');
    let styledCount = 0;
    
    allButtons.forEach(button => {
        // Early exit: skip if already styled and in cache
        if (styledButtonsCache.has(button)) {
            return;
        }
        
        // Get button text from various possible locations
        let buttonText = '';
        // Try different ways to get the button text
        if (button.textContent) {
            buttonText = button.textContent.trim();
        } else if (button.innerText) {
            buttonText = button.innerText.trim();
        } else if (button.value) {
            buttonText = button.value.trim();
        }
        
        // Early exit: only process buttons that contain hexagram symbols
        if (!buttonText.includes('▅▅')) {
            return;
        }
        
        // Also check the button's label or any child elements
        const label = button.querySelector('label');
        if (label && label.textContent) {
            buttonText = label.textContent.trim();
        }
        
        // Check for text in nested spans or divs - Gradio might wrap text
        const textElement = button.querySelector('span, div');
        if (textElement && textElement.textContent) {
            const nestedText = textElement.textContent.trim();
            if (nestedText.includes('▅▅')) {
                buttonText = nestedText;
            }
        }
        
        // Double-check after getting all text sources
        if (!buttonText.includes('▅▅')) {
            return;
        }
        
        styledCount++;
        
        // Add the yao-line-button class if not present
        if (!button.classList.contains('yao-line-button')) {
            button.classList.add('yao-line-button');
        }
        
        // Determine if it's yang or yin and if it's changing
        const isYang = buttonText.includes('▅▅▅▅▅▅');
        const isYin = buttonText.includes('▅▅  ▅▅');
        const isChanging = buttonText.includes('○') || buttonText.includes('×');
        
        // Apply inline styles directly - this is more reliable than classes
        // Use !important to override any Gradio defaults
        // Set width, height, and alignment
        button.style.setProperty('max-width', '350px', 'important');
        button.style.setProperty('width', '100%', 'important');
        button.style.setProperty('margin-left', 'auto', 'important');
        button.style.setProperty('min-height', '80px', 'important');
        button.style.setProperty('padding', '20px 20px', 'important');
        
        if (isYang) {
            if (isChanging) {
                button.style.setProperty('background-color', '#e96a6a', 'important');
                button.style.setProperty('border', '1.5px solid #d32f2f', 'important');
                button.style.setProperty('color', '#ffffff', 'important');
                button.style.setProperty('box-shadow', '0 2px 6px rgba(211, 47, 47, 0.5)', 'important');
                button.style.setProperty('font-weight', '600', 'important');
            } else {
                button.style.setProperty('background-color', '#ef4444', 'important');
                button.style.setProperty('border', '1.5px solid #b71c1c', 'important');
                button.style.setProperty('color', '#ffffff', 'important');
                button.style.setProperty('box-shadow', '0 1px 3px rgba(183, 28, 28, 0.4)', 'important');
                button.style.setProperty('font-weight', '400', 'important');
            }
        } else if (isYin) {
            if (isChanging) {
                button.style.setProperty('background-color', '#64db68', 'important');
                button.style.setProperty('border', '1.5px solid #2e7d32', 'important');
                button.style.setProperty('color', '#ffffff', 'important');
                button.style.setProperty('box-shadow', '0 2px 6px rgba(46, 125, 50, 0.5)', 'important');
                button.style.setProperty('font-weight', '600', 'important');
            } else {
                button.style.setProperty('background-color', '#75cc0d', 'important');
                button.style.setProperty('border', '1.5px solid #1b5e20', 'important');
                button.style.setProperty('color', '#ffffff', 'important');
                button.style.setProperty('box-shadow', '0 1px 3px rgba(27, 94, 32, 0.4)', 'important');
                button.style.setProperty('font-weight', '400', 'important');
            }
        }
        
        // Also ensure all child elements (spans, divs) inherit the white color
        const children = button.querySelectorAll('*');
        children.forEach(child => {
            child.style.setProperty('color', '#ffffff', 'important');
        });
        
        // Also update classes for CSS fallback
        button.classList.remove('yang-button', 'yin-button', 'changing');
        if (isYang) {
            button.classList.add('yang-button');
        } else if (isYin) {
            button.classList.add('yin-button');
        }
        if (isChanging) {
            button.classList.add('changing');
        }
        
        // Mark as styled in cache
        styledButtonsCache.add(button);
    });
    
    // Debug: log how many buttons were styled (only in development)
    if (styledCount > 0 && window.location.hostname === 'localhost') {
        console.log(`Styled ${styledCount} yao buttons`);
    }
}

// Enhanced function that also checks Gradio's internal structure
function styleYaoButtonsEnhanced() {
    styleYaoButtons();
    // Also check for Gradio's button structure - use more specific selector
    const gradioButtons = document.querySelectorAll('button[class*="button"], button[data-testid*="button"]');
    let foundNew = false;
    gradioButtons.forEach(btn => {
        if (styledButtonsCache.has(btn)) {
            return; // Skip already styled buttons
        }
        if (btn.textContent && (btn.textContent.includes('▅▅▅▅▅▅') || btn.textContent.includes('▅▅  ▅▅'))) {
            if (!btn.classList.contains('yao-line-button')) {
                btn.classList.add('yao-line-button');
            }
            foundNew = true;
        }
    });
    // Only re-run if we found new buttons
    if (foundNew) {
        styleYaoButtons();
    }
}

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        styleYaoButtonsEnhanced();
        // Run fewer times to catch all buttons
        setTimeout(styleYaoButtonsEnhanced, 500);
        setTimeout(styleYaoButtonsEnhanced, 1000);
    });
} else {
    styleYaoButtonsEnhanced();
    setTimeout(styleYaoButtonsEnhanced, 500);
}

// Also run after Gradio updates (using MutationObserver with debounce)
let styleTimeout;
const observer = new MutationObserver(function(mutations) {
    clearTimeout(styleTimeout);
    // Increased debounce from 50ms to 200ms
    styleTimeout = setTimeout(styleYaoButtonsEnhanced, 200);
});

// Start observing when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'value', 'textContent']
        });
        // Reduced frequency from 100ms/200ms to 500ms/1000ms
        setInterval(forceStyleButtons, 500);
        setInterval(styleYaoButtonsEnhanced, 1000);
    });
} else {
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'value', 'textContent']
    });
    // Reduced frequency from 100ms/200ms to 500ms/1000ms
    setInterval(forceStyleButtons, 500);
    setInterval(styleYaoButtonsEnhanced, 1000);
}

// More aggressive styling that runs immediately and repeatedly
function forceStyleButtons() {
    // Use the main styling function which now applies inline styles
    styleYaoButtons();
    styleYaoButtonsEnhanced();
}

// Listen for button clicks to immediately update styling
document.addEventListener('click', function(e) {
    const button = e.target.closest('button');
    if (button && (button.textContent.includes('▅▅') || button.classList.contains('yao-line-button'))) {
        // Clear cache for this button to force re-styling
        styledButtonsCache.delete(button);
        // Reduced from 5 setTimeout calls to 2
        forceStyleButtons();
        setTimeout(forceStyleButtons, 100);
    }
}, true);

// Also listen for input events which Gradio might use
document.addEventListener('input', function(e) {
    if (e.target && e.target.tagName === 'BUTTON') {
        styledButtonsCache.delete(e.target);
        setTimeout(forceStyleButtons, 100);
    }
}, true);

// Hook into Gradio's update mechanism
if (window.gradio_config) {
    const checkAndStyle = function() {
        setTimeout(forceStyleButtons, 200);
    };
    if (window.addEventListener) {
        window.addEventListener('gradio:update', checkAndStyle);
    }
}

// Cache for ganzhi buttons to avoid re-setting up
const ganzhiButtonsCache = new WeakSet();

// Add click effects for ganzhi buttons (天干 and 地支)
function addGanzhiButtonEffects() {
    const ganzhiButtons = document.querySelectorAll('.ganzhi-button');
    ganzhiButtons.forEach(button => {
        // Skip if already set up
        if (ganzhiButtonsCache.has(button)) {
            return;
        }
        
        // Add click effect directly without cloning (more efficient)
        button.addEventListener('click', function() {
            // Add clicked class for visual feedback
            this.classList.add('clicked');
            
            // Remove clicked class after animation
            setTimeout(() => {
                this.classList.remove('clicked');
            }, 300);
            
            // Temporarily highlight the button
            const originalBg = this.style.backgroundColor;
            const originalColor = this.style.color;
            this.style.backgroundColor = '#000000';
            this.style.color = '#ffffff';
            
            // Reset after a short delay
            setTimeout(() => {
                this.style.backgroundColor = originalBg || '';
                this.style.color = originalColor || '';
            }, 200);
        });
        
        // Mark as set up
        ganzhiButtonsCache.add(button);
    });
}

// Run ganzhi button effects setup
function setupGanzhiButtons() {
    addGanzhiButtonEffects();
}

// Run on page load - reduced from 3 calls to 2
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setupGanzhiButtons();
        setTimeout(setupGanzhiButtons, 500);
    });
} else {
    setupGanzhiButtons();
    setTimeout(setupGanzhiButtons, 500);
}

// Also run after Gradio updates - with debounce
let ganzhiTimeout;
const ganzhiObserver = new MutationObserver(function(mutations) {
    clearTimeout(ganzhiTimeout);
    ganzhiTimeout = setTimeout(setupGanzhiButtons, 200);
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        ganzhiObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
} else {
        ganzhiObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Screen width detection for responsive formatting
function updateScreenWidth() {
    const width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    // Store in a data attribute on body for easy access
    document.body.setAttribute('data-screen-width', width);
    // Also try to update via Gradio if available
    if (window.gradio_config && window.updateScreenWidthState) {
        window.updateScreenWidthState(width);
    }
}

// Update on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateScreenWidth);
} else {
    updateScreenWidth();
}

// Update on resize (with debounce)
let resizeTimeout;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(updateScreenWidth, 100);
});

// Also update when Gradio is ready
if (window.gradio_config) {
    setTimeout(updateScreenWidth, 500);
    setTimeout(updateScreenWidth, 1000);
}

// Sync HTML5 date/time inputs with Gradio number inputs
function setupMobileDateInputs() {
    const dateInput = document.getElementById('mobile-date-input');
    const timeInput = document.getElementById('mobile-time-input');
    
    if (!dateInput || !timeInput) {
        return;
    }
    
    // Find the corresponding Gradio number inputs
    // Look for inputs in the desktop-date-inputs row
    const findNumberInputs = () => {
        const desktopRow = document.querySelector('.desktop-date-inputs');
        if (!desktopRow) {
            return {};
        }
        
        const numberInputs = {};
        const inputs = desktopRow.querySelectorAll('input[type="number"]');
        
        // Try to find inputs by their position or by looking for nearby labels
        inputs.forEach((input, index) => {
            // Try multiple methods to find the label
            let label = null;
            
            // Method 1: Look for label in the same container
            const container = input.closest('.form, .block, [class*="container"]');
            if (container) {
                label = container.querySelector('label');
            }
            
            // Method 2: Look for label before the input
            if (!label) {
                let prev = input.previousElementSibling;
                while (prev && !label) {
                    if (prev.tagName === 'LABEL') {
                        label = prev;
                    }
                    prev = prev.previousElementSibling;
                }
            }
            
            // Method 3: Look for label after the input
            if (!label) {
                let next = input.nextElementSibling;
                while (next && next.tagName !== 'INPUT' && !label) {
                    if (next.tagName === 'LABEL') {
                        label = next;
                    }
                    next = next.nextElementSibling;
                }
            }
            
            // Method 4: Look for label by searching parent
            if (!label) {
                const parent = input.parentElement;
                if (parent) {
                    label = parent.querySelector('label');
                }
            }
            
            if (label) {
                const labelText = label.textContent.trim();
                if (labelText === '年' || labelText.includes('年')) {
                    numberInputs.year = input;
                } else if (labelText === '月' || labelText.includes('月')) {
                    numberInputs.month = input;
                } else if (labelText === '日' || labelText.includes('日')) {
                    numberInputs.day = input;
                } else if (labelText === '時' || labelText.includes('時')) {
                    numberInputs.hour = input;
                }
            } else {
                // Fallback: assign by index (year, month, day, hour)
                if (index === 0) numberInputs.year = input;
                else if (index === 1) numberInputs.month = input;
                else if (index === 2) numberInputs.day = input;
                else if (index === 3) numberInputs.hour = input;
            }
        });
        
        return numberInputs;
    };
    
    const syncToNumbers = () => {
        const numberInputs = findNumberInputs();
        
        if (dateInput.value && Object.keys(numberInputs).length >= 3) {
            const dateParts = dateInput.value.split('-');
            if (dateParts.length === 3) {
                if (numberInputs.year) {
                    numberInputs.year.value = dateParts[0];
                    // Trigger Gradio's change event
                    numberInputs.year.dispatchEvent(new Event('input', { bubbles: true }));
                    numberInputs.year.dispatchEvent(new Event('change', { bubbles: true }));
                    // Also try focus/blur to trigger updates
                    numberInputs.year.focus();
                    numberInputs.year.blur();
                }
                if (numberInputs.month) {
                    numberInputs.month.value = dateParts[1];
                    numberInputs.month.dispatchEvent(new Event('input', { bubbles: true }));
                    numberInputs.month.dispatchEvent(new Event('change', { bubbles: true }));
                    numberInputs.month.focus();
                    numberInputs.month.blur();
                }
                if (numberInputs.day) {
                    numberInputs.day.value = dateParts[2];
                    numberInputs.day.dispatchEvent(new Event('input', { bubbles: true }));
                    numberInputs.day.dispatchEvent(new Event('change', { bubbles: true }));
                    numberInputs.day.focus();
                    numberInputs.day.blur();
                }
            }
        }
        
        if (timeInput.value && numberInputs.hour) {
            const timeParts = timeInput.value.split(':');
            if (timeParts.length >= 1) {
                numberInputs.hour.value = timeParts[0];
                numberInputs.hour.dispatchEvent(new Event('input', { bubbles: true }));
                numberInputs.hour.dispatchEvent(new Event('change', { bubbles: true }));
                numberInputs.hour.focus();
                numberInputs.hour.blur();
            }
        }
    };
    
    // Sync when HTML5 inputs change
    dateInput.addEventListener('change', syncToNumbers);
    timeInput.addEventListener('change', syncToNumbers);
    dateInput.addEventListener('input', syncToNumbers);
    timeInput.addEventListener('input', syncToNumbers);
}

// Run setup on page load and after Gradio updates
function initMobileDateInputs() {
    setupMobileDateInputs();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initMobileDateInputs();
        setTimeout(initMobileDateInputs, 500);
        setTimeout(initMobileDateInputs, 1000);
    });
} else {
    initMobileDateInputs();
    setTimeout(initMobileDateInputs, 500);
    setTimeout(initMobileDateInputs, 1000);
}

// Also run after Gradio updates
let mobileDateTimeout;
const mobileDateObserver = new MutationObserver(function(mutations) {
    clearTimeout(mobileDateTimeout);
    mobileDateTimeout = setTimeout(initMobileDateInputs, 200);
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        mobileDateObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
} else {
    mobileDateObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
}