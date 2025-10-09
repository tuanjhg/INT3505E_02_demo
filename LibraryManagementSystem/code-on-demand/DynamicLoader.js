/**
 * CODE-ON-DEMAND CONSTRAINT (Optional)
 * 
 * This is the only OPTIONAL constraint in REST architecture.
 * Servers can temporarily extend client functionality by transferring executable code.
 * 
 * Benefits:
 * - Improved client extensibility
 * - Reduced complexity by moving features to server-side
 * - Easy deployment of features (no client updates needed)
 * 
 * Trade-offs:
 * - Reduces visibility (code executed may not be inspectable)
 * - Security concerns (executing untrusted code)
 * 
 * Common examples:
 * - JavaScript sent from server to browser
 * - Applets, plugins
 * - Server-side rendered components
 */

// ==================== SERVER-SIDE: Code Provider ====================

class CodeOnDemandServer {
    /**
     * Server provides validation logic to client on-demand
     * Client can request and execute this code dynamically
     */
    static getValidationCode() {
        // Server-side validation rules that can be sent to client
        return `
            // ISBN Validation (dynamically loaded from server)
            function validateISBN(isbn) {
                // Remove hyphens and spaces
                const cleaned = isbn.replace(/[-\\s]/g, '');
                
                // Check if it's 13 digits
                if (!/^\\d{13}$/.test(cleaned)) {
                    return {
                        valid: false,
                        message: 'ISBN must be 13 digits'
                    };
                }
                
                // Calculate check digit
                let sum = 0;
                for (let i = 0; i < 12; i++) {
                    const digit = parseInt(cleaned[i]);
                    sum += (i % 2 === 0) ? digit : digit * 3;
                }
                const checkDigit = (10 - (sum % 10)) % 10;
                
                if (checkDigit !== parseInt(cleaned[12])) {
                    return {
                        valid: false,
                        message: 'Invalid ISBN check digit'
                    };
                }
                
                return {
                    valid: true,
                    message: 'Valid ISBN'
                };
            }
            
            // Email Validation (dynamically loaded)
            function validateEmail(email) {
                const pattern = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                return {
                    valid: pattern.test(email),
                    message: pattern.test(email) ? 'Valid email' : 'Invalid email format'
                };
            }
            
            // Borrowing period validation
            function validateBorrowDays(days) {
                if (days < 1 || days > 30) {
                    return {
                        valid: false,
                        message: 'Borrow period must be between 1 and 30 days'
                    };
                }
                return {
                    valid: true,
                    message: 'Valid borrow period'
                };
            }
        `;
    }

    /**
     * Server provides UI enhancement code on-demand
     */
    static getUIEnhancementCode() {
        return `
            // Dynamic book availability indicator
            function enhanceBookDisplay(bookElement, bookData) {
                const indicator = document.createElement('div');
                indicator.className = 'availability-indicator';
                
                if (bookData.available) {
                    indicator.innerHTML = '✓ Available';
                    indicator.style.color = 'green';
                    
                    // Add borrow button
                    const borrowBtn = document.createElement('button');
                    borrowBtn.textContent = 'Borrow Now';
                    borrowBtn.onclick = () => initiateBookBorrow(bookData.id);
                    bookElement.appendChild(borrowBtn);
                } else {
                    indicator.innerHTML = '✗ Currently Borrowed';
                    indicator.style.color = 'red';
                    
                    // Add notification button
                    const notifyBtn = document.createElement('button');
                    notifyBtn.textContent = 'Notify When Available';
                    notifyBtn.onclick = () => subscribeToAvailability(bookData.id);
                    bookElement.appendChild(notifyBtn);
                }
                
                bookElement.appendChild(indicator);
            }
            
            // Auto-complete for book search
            function enableSearchAutocomplete(inputElement) {
                let timeout;
                inputElement.addEventListener('input', function() {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        const query = this.value;
                        if (query.length >= 3) {
                            fetch('/api/books?search=' + query)
                                .then(res => res.json())
                                .then(data => showSuggestions(data.books));
                        }
                    }, 300);
                });
            }
        `;
    }

    /**
     * Server provides analytics code on-demand
     */
    static getAnalyticsCode() {
        return `
            // Track user interactions
            function trackBookView(bookId) {
                fetch('/api/analytics/book-view', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ book_id: bookId, timestamp: Date.now() })
                });
            }
            
            function trackSearch(query, resultCount) {
                fetch('/api/analytics/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        query: query, 
                        results: resultCount,
                        timestamp: Date.now() 
                    })
                });
            }
        `;
    }

    /**
     * API endpoint to serve code on-demand
     */
    static handleCodeRequest(req, res) {
        const codeType = req.params.type;
        
        let code;
        switch (codeType) {
            case 'validation':
                code = this.getValidationCode();
                break;
            case 'ui-enhancement':
                code = this.getUIEnhancementCode();
                break;
            case 'analytics':
                code = this.getAnalyticsCode();
                break;
            default:
                res.status(404).send({ error: 'Code type not found' });
                return;
        }
        
        res.set('Content-Type', 'application/javascript');
        res.send(code);
    }
}

// ==================== CLIENT-SIDE: Code Consumer ====================

class DynamicCodeLoader {
    constructor() {
        this.loadedModules = new Map();
    }

    /**
     * Load and execute code from server dynamically
     */
    async loadCode(codeType) {
        console.log(`[CLIENT] Requesting ${codeType} code from server...`);
        
        // Check if already loaded
        if (this.loadedModules.has(codeType)) {
            console.log(`[CLIENT] Code already loaded: ${codeType}`);
            return this.loadedModules.get(codeType);
        }

        try {
            // Request code from server
            const response = await fetch(`/api/code/${codeType}`);
            const code = await response.text();
            
            console.log(`[CLIENT] Received code from server (${code.length} bytes)`);
            
            // Execute the code
            // In browser: creates functions in global scope
            // In Node.js: eval in local scope
            eval(code);
            
            console.log(`[CLIENT] Code executed successfully`);
            
            this.loadedModules.set(codeType, true);
            return true;
        } catch (error) {
            console.error(`[CLIENT] Error loading code: ${error.message}`);
            return false;
        }
    }

    /**
     * Example: Load validation code and use it
     */
    async enhanceFormValidation(formElement) {
        // Load validation code from server
        await this.loadCode('validation');
        
        // Now we can use the dynamically loaded validation functions
        const isbnInput = formElement.querySelector('#isbn');
        const emailInput = formElement.querySelector('#email');
        const daysInput = formElement.querySelector('#days');
        
        // Add validators (functions loaded from server)
        isbnInput.addEventListener('blur', function() {
            const result = validateISBN(this.value); // Function loaded from server!
            showValidationResult(this, result);
        });
        
        emailInput.addEventListener('blur', function() {
            const result = validateEmail(this.value);
            showValidationResult(this, result);
        });
        
        daysInput.addEventListener('blur', function() {
            const result = validateBorrowDays(parseInt(this.value));
            showValidationResult(this, result);
        });
        
        console.log('[CLIENT] Form validation enhanced with server-provided code');
    }

    /**
     * Example: Load UI enhancement code
     */
    async enhanceBookCatalog(catalogElement) {
        await this.loadCode('ui-enhancement');
        
        // Use server-provided UI enhancement
        const books = catalogElement.querySelectorAll('.book-item');
        books.forEach(bookEl => {
            const bookData = JSON.parse(bookEl.dataset.book);
            enhanceBookDisplay(bookEl, bookData); // Function loaded from server!
        });
        
        // Enable search autocomplete
        const searchInput = document.querySelector('#book-search');
        if (searchInput) {
            enableSearchAutocomplete(searchInput); // Function loaded from server!
        }
        
        console.log('[CLIENT] Book catalog enhanced with server-provided code');
    }

    /**
     * Example: Load analytics code
     */
    async enableAnalytics() {
        await this.loadCode('analytics');
        
        // Use server-provided analytics
        document.querySelectorAll('.book-item').forEach(bookEl => {
            bookEl.addEventListener('click', function() {
                const bookId = this.dataset.bookId;
                trackBookView(bookId); // Function loaded from server!
            });
        });
        
        const searchForm = document.querySelector('#search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                const query = this.querySelector('input').value;
                const results = document.querySelectorAll('.search-result').length;
                trackSearch(query, results); // Function loaded from server!
            });
        }
        
        console.log('[CLIENT] Analytics enabled with server-provided code');
    }
}

// Helper function for validation display
function showValidationResult(inputElement, result) {
    const feedback = inputElement.nextElementSibling || document.createElement('div');
    feedback.className = 'validation-feedback';
    feedback.textContent = result.message;
    feedback.style.color = result.valid ? 'green' : 'red';
    
    if (!inputElement.nextElementSibling) {
        inputElement.parentNode.insertBefore(feedback, inputElement.nextSibling);
    }
}

// ==================== DEMONSTRATION ====================

async function demonstrateCodeOnDemand() {
    console.log('=== Code-On-Demand Constraint Demo ===\n');
    
    const loader = new DynamicCodeLoader();
    
    // Scenario 1: Load validation code on-demand
    console.log('\n--- Scenario 1: Dynamic Form Validation ---');
    await loader.loadCode('validation');
    
    // Test the dynamically loaded validation
    console.log('\nTesting ISBN validation (code from server):');
    // Note: validateISBN function is now available!
    console.log('  9780132350884:', validateISBN('9780132350884'));
    console.log('  1234567890123:', validateISBN('1234567890123'));
    
    // Scenario 2: UI Enhancement code
    console.log('\n--- Scenario 2: Dynamic UI Enhancement ---');
    console.log('Loading UI enhancement code from server...');
    await loader.loadCode('ui-enhancement');
    console.log('UI enhancement code loaded and ready to use');
    
    // Scenario 3: Analytics code
    console.log('\n--- Scenario 3: Dynamic Analytics ---');
    await loader.loadCode('analytics');
    console.log('Analytics code loaded from server');
    
    console.log('\n=== Benefits of Code-On-Demand ===');
    console.log('✓ Client receives up-to-date validation rules from server');
    console.log('✓ New features deployed without client updates');
    console.log('✓ Reduced initial client complexity');
    console.log('✓ Server controls business logic centrally');
    
    console.log('\n=== Trade-offs ===');
    console.log('⚠ Reduced visibility (executed code may not be inspectable)');
    console.log('⚠ Security concerns (must trust server)');
    console.log('⚠ Network dependency (need code before execution)');
}

// Run demonstration in browser or Node.js
if (typeof window === 'undefined') {
    // Node.js environment
    console.log('Code-On-Demand demonstration (simulated)');
    console.log('In a browser, this would dynamically load and execute server code\n');
    
    // Simulate server code
    eval(CodeOnDemandServer.getValidationCode());
    
    console.log('Example: Validating ISBN with server-provided code');
    console.log(validateISBN('9780132350884'));
} else {
    // Browser environment
    demonstrateCodeOnDemand();
}

// ==================== EXPORT ====================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CodeOnDemandServer,
        DynamicCodeLoader
    };
}
