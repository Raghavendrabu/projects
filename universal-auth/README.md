# 🔐 Universal Auth Component

A premium, modern, fully responsive, and highly customizable **Login & Sign Up** component designed to be dropped into any website and connected to any backend in minutes.

---

## 📂 File Directory Structure
All resources are completely modular and self-contained:
```text
universal-auth/
├── index.html   # HTML5 markup for panels, modals, and input fields
├── style.css    # Premium glassmorphic styles, themes, and animations
└── auth.js      # Form controllers, validations, toasts, and API hooks
```

---

## 🎨 Theme Customization (CSS Variables)

To change the theme to match your website, simply edit the custom properties in the `:root` block of `style.css`. You do not need to rewrite complex styling classes!

```css
/* style.css */
:root {
    /* Main Theme Accents */
    --primary-color: #6366f1;         /* Main Accent (e.g. indigo, emerald, crimson) */
    --primary-hover: #4f46e5;         /* Accent color on hover */
    --primary-glow: rgba(99, 102, 241, 0.4);
    
    --secondary-color: #06b6d4;       /* Secondary accent (for gradients) */
    --secondary-glow: rgba(6, 182, 212, 0.3);

    /* Background Panels */
    --bg-gradient-start: #0a0a0f;     /* Dark Mode background gradient start */
    --bg-gradient-end: #12121e;       /* Dark Mode background gradient end */
    --card-bg: rgba(18, 18, 26, 0.65); /* Glassmorphic panel background */
    --border-radius-lg: 20px;          /* Corner roundness */
}
```

---

## 🔌 Connecting to Your Backend

The JavaScript file `auth.js` exposes a global config object `window.AuthAPI`. You can implement your backend calls inside these hooks. 

### 🐍 Option A: Python / Flask Integration
If you are running a Flask app, bind the login/signup events to trigger standard AJAX request calls:

```javascript
// Add this inside auth.js or in a <script> block after importing auth.js
window.AuthAPI = {
    onLogin: async (email, password) => {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            
            if (response.ok) {
                // Redirect user to dashboard or sync state
                window.location.href = '/dashboard';
                return { success: true, message: data.message };
            }
            return { success: false, message: data.error || "Login failed." };
        } catch (err) {
            return { success: false, message: "Server connection failed." };
        }
    },
    
    onRegister: async (username, email, password) => {
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await response.json();
            
            if (response.ok) {
                return { success: true, message: "Registration successful! Redirecting..." };
            }
            return { success: false, message: data.error || "Sign-up failed." };
        } catch (err) {
            return { success: false, message: "Server connection failed." };
        }
    },
    
    onForgotPassword: async (email) => {
        const response = await fetch('/api/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await response.json();
        return { success: response.ok, message: data.message || data.error };
    },

    onSocialLogin: (provider) => {
        // Redirect to Flask OAuth login route
        window.location.href = `/login/${provider}`;
    }
};
```

---

### 🟢 Option B: Node.js / Express Backend
If you have an Express.js server:

```javascript
window.AuthAPI = {
    onLogin: async (email, password) => {
        try {
            const response = await axios.post('/auth/signin', { email, password });
            localStorage.setItem('auth_token', response.data.token);
            window.location.href = '/profile';
            return { success: true, message: "Authenticated!" };
        } catch (err) {
            const errMsg = err.response?.data?.message || "Sign in failed";
            return { success: false, message: errMsg };
        }
    },
    
    onRegister: async (username, email, password) => {
        try {
            await axios.post('/auth/signup', { username, email, password });
            return { success: true, message: "Profile registered!" };
        } catch (err) {
            const errMsg = err.response?.data?.message || "Registration failed";
            return { success: false, message: errMsg };
        }
    }
};
```

---

### ⚡ Option C: Supabase Client Integration
If you are using Supabase for authentication:

```javascript
// Make sure Supabase JS CDN client is imported
window.AuthAPI = {
    onLogin: async (email, password) => {
        const { data, error } = await supabase.auth.signInWithPassword({
            email: email,
            password: password,
        });
        
        if (error) {
            return { success: false, message: error.message };
        }
        window.location.href = '/app';
        return { success: true, message: "Welcome back!" };
    },

    onRegister: async (username, email, password) => {
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
            options: {
                data: { display_name: username }
            }
        });
        
        if (error) {
            return { success: false, message: error.message };
        }
        return { success: true, message: "Registration successful! Please check your email for confirmation." };
    },
    
    onForgotPassword: async (email) => {
        const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: window.location.origin + '/reset-password',
        });
        if (error) return { success: false, message: error.message };
        return { success: true, message: "Reset link sent successfully!" };
    },

    onSocialLogin: async (provider) => {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: provider, // 'google', 'github', etc.
        });
    }
};
```

---

## ⚡ Integration checklist
1. Copy the `universal-auth` folder into your project root directory.
2. Link the stylesheet `style.css` in your project html files.
3. Import the javascript script `auth.js` at the bottom of your body tag.
4. Set up your custom `window.AuthAPI` configs to link to your servers.
