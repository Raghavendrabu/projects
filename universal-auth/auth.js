/**
 * ==========================================================================
 * UNIVERSAL AUTH COMPONENT - INTERACTION LOGIC (auth.js)
 * ==========================================================================
 * Contains form toggles, input animations, validations, dynamic toasts,
 * theme management, and the developer integration API configuration hook.
 * ==========================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const authWrapper = document.getElementById("auth-card-wrapper");
    
    // View Switchers
    const desktopToSignup = document.getElementById("desktop-to-signup");
    const desktopToLogin = document.getElementById("desktop-to-login");
    const mobileToSignup = document.getElementById("mobile-to-signup");
    const mobileToLogin = document.getElementById("mobile-to-login");

    // Passwords Visibility
    const loginPwToggle = document.getElementById("login-password-toggle");
    const signupPwToggle = document.getElementById("signup-password-toggle");
    const confirmPwToggle = document.getElementById("signup-confirm-toggle");

    const loginPwInput = document.getElementById("login-password");
    const signupPwInput = document.getElementById("signup-password");
    const confirmPwInput = document.getElementById("signup-confirm-password");

    // Password Strength Meter
    const strengthMeter = document.getElementById("strength-meter-container");
    const strengthBarFill = document.getElementById("strength-bar-fill");
    const strengthText = document.getElementById("strength-text");
    const strengthPct = document.getElementById("strength-percentage");

    // Forms
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const forgotForm = document.getElementById("forgot-form");

    // Modal Details (Forgot Password)
    const forgotTrigger = document.getElementById("trigger-forgot-password");
    const forgotModal = document.getElementById("forgot-password-modal");
    const modalCloseBtn = document.getElementById("modal-close-btn");

    // Theme Toggle Details
    const themeBtn = document.getElementById("theme-toggle-btn");
    const themeIcon = document.getElementById("theme-toggle-icon");

    // Toast Notification Manager
    const toastContainer = document.getElementById("toast-container");

    /* ==========================================================================
       1. DEVELOPER INTEGRATION API HOOKS
       ==========================================================================
       Replace these placeholder hooks with your actual API calls (e.g. fetch/axios).
       Simply return { success: true } or { success: false, message: "Error message" }.
       ========================================================================== */
    window.AuthAPI = {
        /**
         * Triggered when a user submits the Login form.
         * @param {string} email 
         * @param {string} password 
         * @returns {Promise<{success: boolean, message?: string}>}
         */
        onLogin: async (email, password) => {
            console.log("AuthAPI.onLogin called with:", { email, password });
            
            // Mock backend latency
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Replace with your endpoint: e.g. fetch('/api/login', { method: 'POST', ... })
            if (email === "demo@example.com" && password === "Password123!") {
                return { success: true, message: "Login successful!" };
            }
            return { 
                success: false, 
                message: "Invalid credentials. Use demo@example.com and Password123! for demo." 
            };
        },

        /**
         * Triggered when a user submits the Sign Up form.
         * @param {string} username 
         * @param {string} email 
         * @param {string} password 
         * @returns {Promise<{success: boolean, message?: string}>}
         */
        onRegister: async (username, email, password) => {
            console.log("AuthAPI.onRegister called with:", { username, email, password });
            
            // Mock backend latency
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Replace with your endpoint: e.g. fetch('/api/register', { ... })
            return { success: true, message: "Account created successfully! Welcome aboard." };
        },

        /**
         * Triggered when a user requests a password reset code.
         * @param {string} email 
         * @returns {Promise<{success: boolean, message?: string}>}
         */
        onForgotPassword: async (email) => {
            console.log("AuthAPI.onForgotPassword called with:", email);
            
            // Mock backend latency
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            return { success: true, message: "If this email is registered, we have sent a reset link." };
        },

        /**
         * Triggered when a user clicks on a social authentication provider.
         * @param {string} providerName ('google', 'apple', 'github')
         */
        onSocialLogin: (providerName) => {
            console.log(`AuthAPI.onSocialLogin triggered for: ${providerName}`);
            showToast(
                "Social Redirect", 
                `Redirecting to ${providerName.charAt(0).toUpperCase() + providerName.slice(1)} OAuth flow...`, 
                "info"
            );
            // Implement OAuth redirect logic here
            // window.location.href = `/auth/${providerName}`;
        }
    };

    /* ==========================================================================
       2. PANEL SLIDING SWITCH LOGIC
       ========================================================================== */
    const switchToSignup = () => {
        authWrapper.classList.add("sign-up-active");
    };

    const switchToLogin = () => {
        authWrapper.classList.remove("sign-up-active");
    };

    if (desktopToSignup) desktopToSignup.addEventListener("click", switchToSignup);
    if (desktopToLogin) desktopToLogin.addEventListener("click", switchToLogin);
    if (mobileToSignup) mobileToSignup.addEventListener("click", switchToSignup);
    if (mobileToLogin) mobileToLogin.addEventListener("click", switchToLogin);


    /* ==========================================================================
       3. PASSWORD TOGGLE SYSTEM & MASCOT STATE BINDINGS
       ========================================================================== */
    const updateMascotState = (inputEl) => {
        const formPanel = inputEl.closest(".form-panel");
        if (!formPanel) return;
        const mascotContainer = formPanel.querySelector(".mascot-container");

        if (inputEl.type === "password") {
            if (mascotContainer) {
                mascotContainer.classList.add("eyes-covered");
                mascotContainer.classList.remove("eyes-peeking");
            }
            authWrapper.classList.add("password-active");
        } else {
            if (mascotContainer) {
                mascotContainer.classList.remove("eyes-covered");
                mascotContainer.classList.add("eyes-peeking");
            }
            authWrapper.classList.remove("password-active");
        }
    };

    const bindMascotFocus = (inputEl) => {
        if (!inputEl) return;
        const formPanel = inputEl.closest(".form-panel");
        if (!formPanel) return;
        const mascotContainer = formPanel.querySelector(".mascot-container");

        inputEl.addEventListener("focus", () => {
            updateMascotState(inputEl);
        });

        inputEl.addEventListener("blur", () => {
            if (mascotContainer) {
                mascotContainer.classList.remove("eyes-covered");
                mascotContainer.classList.remove("eyes-peeking");
            }
            authWrapper.classList.remove("password-active");
        });
    };

    const setupPasswordToggle = (toggleBtn, inputEl) => {
        if (!toggleBtn || !inputEl) return;
        
        toggleBtn.addEventListener("click", () => {
            const isPassword = inputEl.type === "password";
            inputEl.type = isPassword ? "text" : "password";
            
            // Update icon
            toggleBtn.setAttribute("data-lucide", isPassword ? "eye-off" : "eye");
            lucide.createIcons();

            // Sync mascot state
            updateMascotState(inputEl);
        });
    };

    // Initialize toggles and focus state binders
    setupPasswordToggle(loginPwToggle, loginPwInput);
    setupPasswordToggle(signupPwToggle, signupPwInput);
    setupPasswordToggle(confirmPwToggle, confirmPwInput);

    bindMascotFocus(loginPwInput);
    bindMascotFocus(signupPwInput);
    bindMascotFocus(confirmPwInput);

    // Field focus states triggers for Blobs stretching reactions
    const bindFieldFocusEffects = (inputEl, fieldName) => {
        if (!inputEl) return;
        inputEl.addEventListener("focus", () => {
            authWrapper.classList.add(`focus-${fieldName}`);
        });
        inputEl.addEventListener("blur", () => {
            authWrapper.classList.remove(`focus-${fieldName}`);
        });
    };

    const loginEmailInput = document.getElementById("login-email");
    const signupUsernameInput = document.getElementById("signup-username");
    const signupEmailInput = document.getElementById("signup-email");

    bindFieldFocusEffects(loginEmailInput, "email");
    bindFieldFocusEffects(loginPwInput, "password");
    bindFieldFocusEffects(signupUsernameInput, "username");
    bindFieldFocusEffects(signupEmailInput, "email");
    bindFieldFocusEffects(signupPwInput, "password");
    bindFieldFocusEffects(confirmPwInput, "confirm");

    // Typing states bindings (surprised / curious blobs)
    const textInputs = [
        document.getElementById("login-email"),
        document.getElementById("signup-username"),
        document.getElementById("signup-email"),
        document.getElementById("forgot-email")
    ];

    textInputs.forEach((input) => {
        if (!input) return;
        
        input.addEventListener("input", () => {
            if (input.value.trim().length > 0) {
                authWrapper.classList.add("typing-active");
            } else {
                authWrapper.classList.remove("typing-active");
            }
        });

        input.addEventListener("blur", () => {
            authWrapper.classList.remove("typing-active");
        });

        input.addEventListener("focus", () => {
            if (input.value.trim().length > 0) {
                authWrapper.classList.add("typing-active");
            }
        });
    });

    // Interactive Mascot & Overlay Pupils Cursor Tracking
    document.addEventListener("mousemove", (e) => {
        // 1. Form Mascot (Blobby) Tracking
        const mascotSvgs = document.querySelectorAll(".mascot-svg");
        mascotSvgs.forEach((svg) => {
            const container = svg.closest(".mascot-container");
            if (container && container.classList.contains("eyes-covered")) {
                return;
            }

            const rect = svg.getBoundingClientRect();
            const mascotX = rect.left + rect.width / 2;
            const mascotY = rect.top + rect.height / 2;

            const dx = e.clientX - mascotX;
            const dy = e.clientY - mascotY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            const maxOffset = 3.5;
            const angle = Math.atan2(dy, dx);

            const offsetX = Math.cos(angle) * Math.min(maxOffset, dist / 25);
            const offsetY = Math.sin(angle) * Math.min(maxOffset, dist / 25);

            const leftPupil = svg.querySelector(".left-pupil");
            const rightPupil = svg.querySelector(".right-pupil");

            if (leftPupil && rightPupil) {
                leftPupil.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
                rightPupil.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
            }
        });

        // 2. Sliding Overlay Mascot (The Blobs) Tracking
        const overlayPupils = document.querySelectorAll(".blobs-svg .pupil");
        overlayPupils.forEach((pupil) => {
            // Note: Since CSS overrides pink/purple pupils during password focus,
            // we can safely translate them in JS without breaking closed states.
            const rect = pupil.getBoundingClientRect();
            const pupilX = rect.left + rect.width / 2;
            const pupilY = rect.top + rect.height / 2;

            const dx = e.clientX - pupilX;
            const dy = e.clientY - pupilY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            const maxOffset = 2.5; // smaller range for overlay characters
            const angle = Math.atan2(dy, dx);

            const offsetX = Math.cos(angle) * Math.min(maxOffset, dist / 20);
            const offsetY = Math.sin(angle) * Math.min(maxOffset, dist / 20);

            pupil.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
        });
    });


    /* ==========================================================================
       4. PASSWORD STRENGTH CALCULATION
       ========================================================================== */
    if (signupPwInput) {
        signupPwInput.addEventListener("input", () => {
            const password = signupPwInput.value;
            
            if (password.length === 0) {
                strengthMeter.style.display = "none";
                return;
            }
            
            strengthMeter.style.display = "block";
            let score = 0;

            // Rules
            if (password.length >= 8) score++;
            if (/[A-Z]/.test(password)) score++;
            if (/[0-9]/.test(password)) score++;
            if (/[^A-Za-z0-9]/.test(password)) score++;

            // Visual representations
            let color = "var(--color-error)";
            let label = "Weak";
            let width = "25%";

            switch(score) {
                case 2:
                    color = "var(--color-warning)";
                    label = "Medium";
                    width = "50%";
                    break;
                case 3:
                    color = "var(--primary-color)";
                    label = "Good";
                    width = "75%";
                    break;
                case 4:
                    color = "var(--color-success)";
                    label = "Strong";
                    width = "100%";
                    break;
                default:
                    color = "var(--color-error)";
                    label = "Too Weak";
                    width = "25%";
            }

            strengthBarFill.style.width = width;
            strengthBarFill.style.backgroundColor = color;
            strengthText.textContent = `Strength: ${label}`;
            strengthPct.textContent = `${score * 25}%`;
        });
    }


    /* ==========================================================================
       5. MODAL CONTROL (Forgot Password Overlay)
       ========================================================================== */
    const openModal = (e) => {
        e.preventDefault();
        forgotModal.classList.add("active");
    };

    const closeModal = () => {
        forgotModal.classList.remove("active");
    };

    if (forgotTrigger) forgotTrigger.addEventListener("click", openModal);
    if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);

    // Close on clicking outside the card
    window.addEventListener("click", (e) => {
        if (e.target === forgotModal) {
            closeModal();
        }
    });


    /* ==========================================================================
       6. THEME SWITCHER (Dark & Light theme toggling with storage sync)
       ========================================================================== */
    const currentTheme = localStorage.getItem("auth-theme");
    
    // Apply initial cached theme
    if (currentTheme === "light") {
        document.body.classList.add("light-theme");
        themeIcon.setAttribute("data-lucide", "sun");
    }

    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const isLight = document.body.classList.toggle("light-theme");
            
            // Save settings
            localStorage.setItem("auth-theme", isLight ? "light" : "dark");
            
            // Swap icon
            themeIcon.setAttribute("data-lucide", isLight ? "sun" : "moon");
            lucide.createIcons();
            
            // Trigger mascot squint blink
            authWrapper.classList.add("theme-blink");
            setTimeout(() => {
                authWrapper.classList.remove("theme-blink");
            }, 600);
            
            showToast("Theme Updated", `Switched to ${isLight ? 'Light' : 'Dark'} visual mode.`, "info");
        });
    }


    /* ==========================================================================
       7. DYNAMIC TOAST / NOTIFICATION UTILITY
       ========================================================================== */
    const showToast = (title, message, type = "info") => {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        
        // Trigger panic/shake state for warning and error toasts
        if (type === "warning" || type === "error") {
            authWrapper.classList.add("error-active");
            setTimeout(() => {
                authWrapper.classList.remove("error-active");
            }, 2000);
        }
        
        let iconName = "info";
        if (type === "success") iconName = "check-circle";
        if (type === "warning") iconName = "alert-triangle";
        if (type === "error") iconName = "x-circle";

        toast.innerHTML = `
            <i data-lucide="${iconName}" class="toast-icon"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-desc">${message}</div>
            </div>
            <button class="toast-close" aria-label="Dismiss toast">
                <i data-lucide="x"></i>
            </button>
        `;

        toastContainer.appendChild(toast);
        lucide.createIcons();

        // Dismiss handlers
        const dismissToast = () => {
            toast.style.transform = "translateX(120%)";
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 300);
        };

        toast.querySelector(".toast-close").addEventListener("click", dismissToast);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                dismissToast();
            }
        }, 4000);
    };


    /* ==========================================================================
       8. SUBMIT HANDLERS & VALIDATION
       ========================================================================== */
    
    // Set form button loading state
    const setFormLoading = (form, isLoading, originalText = "Submit") => {
        const btn = form.querySelector('button[type="submit"]');
        if (!btn) return;

        if (isLoading) {
            btn.disabled = true;
            btn.innerHTML = `<span style="display:inline-block; animation: spin 1s linear infinite; margin-right:8px;">◌</span> Processing...`;
        } else {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    };

    // Spin animation CSS rule injected dynamically (keep clean)
    const style = document.createElement('style');
    style.innerHTML = `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`;
    document.head.appendChild(style);

    // Email Helper Validator
    const isValidEmail = (email) => {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(String(email).toLowerCase());
    };

    // LOGIN VALIDATION & DISPATCH
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const emailVal = document.getElementById("login-email").value.trim();
            const pwVal = loginPwInput.value;

            // Form validations
            if (!emailVal || !pwVal) {
                showToast("Required Fields", "Please populate both email and password inputs.", "warning");
                return;
            }

            if (!isValidEmail(emailVal)) {
                showToast("Invalid Email", "Please type a standard email layout (e.g. user@domain.com)", "warning");
                return;
            }

            setFormLoading(loginForm, true, "Sign in");
            
            try {
                // Call developer-configured hook
                const res = await window.AuthAPI.onLogin(emailVal, pwVal);
                
                if (res && res.success) {
                    authWrapper.classList.add("success-active");
                    showToast("Welcome Back!", res.message || "Authorized successfully.", "success");
                    setTimeout(() => {
                        authWrapper.classList.remove("success-active");
                    }, 2500);
                    // Route to destination URL here
                } else {
                    showToast("Authentication Failed", res.message || "Access denied.", "error");
                }
            } catch (err) {
                console.error("Login Hook Error:", err);
                showToast("Connection Error", "Failed to contact authorization node.", "error");
            } finally {
                setFormLoading(loginForm, false, "Sign in");
            }
        });
    }

    // SIGNUP VALIDATION & DISPATCH
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const usernameVal = document.getElementById("signup-username").value.trim();
            const emailVal = document.getElementById("signup-email").value.trim();
            const pwVal = signupPwInput.value;
            const confirmVal = confirmPwInput.value;
            const agreeCheck = document.getElementById("signup-agree");

            // Client Validation Checks
            if (!usernameVal || !emailVal || !pwVal || !confirmVal) {
                showToast("Validation Error", "All form fields are mandatory to create an account.", "warning");
                return;
            }

            if (usernameVal.length < 3) {
                showToast("Validation Error", "Username profile name should exceed 2 letters.", "warning");
                return;
            }

            if (!isValidEmail(emailVal)) {
                showToast("Validation Error", "Please provide a standard active email.", "warning");
                return;
            }

            if (pwVal.length < 8) {
                showToast("Insecure Password", "Passwords should contain at least 8 elements.", "warning");
                return;
            }

            if (pwVal !== confirmVal) {
                showToast("Mismatch Credentials", "Confirm password input does not match original password.", "warning");
                return;
            }

            if (agreeCheck && !agreeCheck.checked) {
                showToast("Consent Required", "You must accept our Terms and conditions to proceed.", "warning");
                return;
            }

            setFormLoading(signupForm, true, "Get Started");

            try {
                // Call developer-configured hook
                const res = await window.AuthAPI.onRegister(usernameVal, emailVal, pwVal);
                
                if (res && res.success) {
                    authWrapper.classList.add("success-active");
                    showToast("Profile Established", res.message || "Sign up completed.", "success");
                    // Transition back to login view after short delay
                    setTimeout(() => {
                        authWrapper.classList.remove("success-active");
                        switchToLogin();
                        document.getElementById("login-email").value = emailVal;
                        // Focus on password
                        loginPwInput.focus();
                    }, 1500);
                } else {
                    showToast("Sign Up Error", res.message || "Failed to register profile.", "error");
                }
            } catch (err) {
                console.error("Register Hook Error:", err);
                showToast("Connection Error", "Registration server link timed out.", "error");
            } finally {
                setFormLoading(signupForm, false, "Get Started");
            }
        });
    }

    // FORGOT PASSWORD VALIDATION & DISPATCH
    if (forgotForm) {
        forgotForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const emailVal = document.getElementById("forgot-email").value.trim();

            if (!emailVal) {
                showToast("Input Required", "Email target field cannot be blank.", "warning");
                return;
            }

            if (!isValidEmail(emailVal)) {
                showToast("Invalid Email", "Please input a valid email.", "warning");
                return;
            }

            setFormLoading(forgotForm, true, "Send recovery link");

            try {
                const res = await window.AuthAPI.onForgotPassword(emailVal);
                
                if (res && res.success) {
                    authWrapper.classList.add("success-active");
                    showToast("Link Dispatched", res.message || "Reset instruction email sent.", "success");
                    setTimeout(() => {
                        authWrapper.classList.remove("success-active");
                        closeModal();
                        document.getElementById("forgot-email").value = "";
                    }, 1500);
                } else {
                    showToast("Reset Blocked", res.message || "Unable to register reset request.", "error");
                }
            } catch (err) {
                console.error("Forgot PW Hook Error:", err);
                showToast("Connection Error", "Service node link unavailable.", "error");
            } finally {
                setFormLoading(forgotForm, false, "Send recovery link");
            }
        });
    }

    // Bind social buttons
    const bindSocialAction = (btnId, providerName) => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener("click", () => {
                if (window.AuthAPI && window.AuthAPI.onSocialLogin) {
                    window.AuthAPI.onSocialLogin(providerName);
                }
            });
        }
    };

    bindSocialAction("social-google-login", "google");
    bindSocialAction("social-apple-login", "apple");
    bindSocialAction("social-github-login", "github");
});
