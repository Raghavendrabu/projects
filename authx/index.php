<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AUTHX - Cyber Security Hackathon Portal</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts for futuristic cyberpunk aesthetic -->
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;500;700&family=Orbitron:wght@400;600;800;900&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --red-glow: rgba(239, 68, 68, 0.4);
            --teal-glow: rgba(20, 184, 166, 0.4);
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: #030712;
            overflow-x: hidden;
        }

        .font-mono {
            font-family: 'Share Tech Mono', monospace;
        }

        .font-cyber {
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.1em;
        }

        /* Split background grids */
        .split-bg-left {
            background-size: 50px 50px;
            background-image: 
                linear-gradient(to right, rgba(239, 68, 68, 0.025) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(239, 68, 68, 0.025) 1px, transparent 1px);
            mask-image: radial-gradient(circle at 25% 40%, black, transparent 75%);
            -webkit-mask-image: radial-gradient(circle at 25% 40%, black, transparent 75%);
        }

        .split-bg-right {
            background-size: 50px 50px;
            background-image: 
                linear-gradient(to right, rgba(20, 184, 166, 0.025) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(20, 184, 166, 0.025) 1px, transparent 1px);
            mask-image: radial-gradient(circle at 75% 40%, black, transparent 75%);
            -webkit-mask-image: radial-gradient(circle at 75% 40%, black, transparent 75%);
        }

        /* Ambient scanlines effect */
        .scanlines {
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(
                rgba(18, 16, 16, 0) 50%, 
                rgba(0, 0, 0, 0.25) 50%
            );
            background-size: 100% 4px;
            z-index: 100;
            opacity: 0.4;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(3, 7, 18, 0.5);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(156, 163, 175, 0.3);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(156, 163, 175, 0.5);
        }

        /* Red Card Cyber Glow and Borders */
        .cyber-card-red {
            border: 1px solid rgba(239, 68, 68, 0.25);
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.05);
            background: rgba(7, 10, 18, 0.65);
            backdrop-filter: blur(12px);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .cyber-card-red:hover {
            border-color: rgba(239, 68, 68, 0.6);
            box-shadow: 0 0 35px rgba(239, 68, 68, 0.18), inset 0 0 15px rgba(239, 68, 68, 0.05);
            transform: translateY(-2px);
        }

        /* Teal Card Cyber Glow and Borders */
        .cyber-card-teal {
            border: 1px solid rgba(20, 184, 166, 0.25);
            box-shadow: 0 0 15px rgba(20, 184, 166, 0.05);
            background: rgba(7, 10, 18, 0.65);
            backdrop-filter: blur(12px);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .cyber-card-teal:hover {
            border-color: rgba(20, 184, 166, 0.6);
            box-shadow: 0 0 35px rgba(20, 184, 166, 0.18), inset 0 0 15px rgba(20, 184, 166, 0.05);
            transform: translateY(-2px);
        }

        /* Glowing texts */
        .text-glow-red {
            text-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
        }
        .text-glow-teal {
            text-shadow: 0 0 8px rgba(20, 184, 166, 0.6);
        }
        .text-glow-cyan {
            text-shadow: 0 0 12px rgba(6, 182, 212, 0.8), 0 0 25px rgba(6, 182, 212, 0.4);
        }

        /* Cyberpunk Input fields */
        .cyber-input {
            transition: all 0.3s ease;
            position: relative;
        }
        .cyber-input:focus {
            outline: none;
            box-shadow: 0 0 12px var(--focus-glow);
        }

        /* Button Glow Animations */
        .btn-glow-red {
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
            transition: all 0.3s ease;
        }
        .btn-glow-red:hover:not(:disabled) {
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.6);
            background: rgb(239, 68, 68);
            color: #000;
        }

        .btn-glow-teal {
            box-shadow: 0 0 10px rgba(20, 184, 166, 0.3);
            transition: all 0.3s ease;
        }
        .btn-glow-teal:hover:not(:disabled) {
            box-shadow: 0 0 25px rgba(20, 184, 166, 0.6);
            background: rgb(20, 184, 166);
            color: #000;
        }

        /* Shaking animation on validation failure */
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        .shake-card {
            animation: shake 0.6s ease-in-out;
        }

        /* Terminal input scanning line effect */
        .scanning::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(to bottom, rgba(239, 68, 68, 0), rgba(239, 68, 68, 0.15) 50%, rgba(239, 68, 68, 0) 100%);
            animation: scan-anim 3s linear infinite;
            top: 0;
            left: 0;
            pointer-events: none;
        }

        @keyframes scan-anim {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
        }

        /* Blinking cursor */
        .cursor-blink::after {
            content: '_';
            animation: blink 1s step-start infinite;
        }

        @keyframes blink {
            50% { opacity: 0; }
        }

        /* SVG Dynamic glow classes */
        .svg-glow-red {
            filter: drop-shadow(0px 0px 5px rgba(239, 68, 68, 0.8));
        }
        .svg-glow-teal {
            filter: drop-shadow(0px 0px 5px rgba(20, 184, 166, 0.8));
        }
        .svg-glow-green {
            filter: drop-shadow(0px 0px 6px rgba(16, 185, 129, 0.9));
        }

        @keyframes dash-flow {
            to {
                stroke-dashoffset: -20;
            }
        }
        .flow-line-active {
            stroke-dasharray: 4, 3;
            animation: dash-flow 1.2s linear infinite;
        }

        @keyframes radar-spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .radar-rotate {
            transform-origin: 120px 85px;
            animation: radar-spin 18s linear infinite;
        }

        @keyframes scan-bounce {
            0%, 100% { transform: translateY(-3px); opacity: 0.4; }
            50% { transform: translateY(5px); opacity: 1; }
        }
        .face-scan-line {
            animation: scan-bounce 2s ease-in-out infinite;
        }

        /* Preloader Logo with matching reference image scanlines and neon-glow */
        .authx-preload-logo {
            background: repeating-linear-gradient(
                0deg,
                #00f3ff,
                #00f3ff 2.5px,
                #004e5e 2.5px,
                #004e5e 5px
            );
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 100% 200%;
            animation: shimmer-sweep 8s linear infinite;
        }

        @keyframes shimmer-sweep {
            0% { background-position: 0% 0%; }
            100% { background-position: 0% 100%; }
        }
    </style>
</head>

<body class="relative text-slate-100 min-h-screen flex flex-col justify-between selection:bg-teal-500 selection:text-slate-950">
    
    <!-- FUTURISTIC CYBER SECURITY PRELOADER -->
    <div id="preloader" class="fixed inset-0 bg-[#030712] z-[9999] flex flex-col items-center justify-center select-none transition-all duration-700 opacity-100">
        <!-- Subtle digital grid overlay inside loader -->
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(6,182,212,0.07)_0%,transparent_70%)] pointer-events-none"></div>
        <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: linear-gradient(to right, #06b6d4 1px, transparent 1px), linear-gradient(to bottom, #06b6d4 1px, transparent 1px); background-size: 30px 30px;"></div>
        
        <!-- Preloader HUD Content Wrapper -->
        <div class="relative z-10 flex flex-col items-center max-w-lg w-full px-6 text-center space-y-6">
            <!-- Decorative telemetry bars and labels -->
            <div class="w-full flex justify-between items-center text-[10px] font-mono text-cyan-500/50 uppercase tracking-widest mb-2 select-none">
                <span>[SYSTEM BOOT // SECURE_RSA]</span>
                <span>ID: 0x9A44F</span>
            </div>

            <!-- Stylized Glowing AUTHX logo with horizontal scanline pattern (matching reference!) -->
            <div class="relative py-4 select-none">
                <h1 class="authx-preload-logo font-cyber text-6xl md:text-8xl font-black text-transparent select-none uppercase tracking-widest my-2 filter drop-shadow-[0_0_15px_rgba(6,182,212,0.8)] drop-shadow-[0_0_30px_rgba(6,182,212,0.4)]">
                    AUTHX
                </h1>
                <!-- Symmetrical glow bracket corners -->
                <div class="absolute -top-1 -left-4 w-4 h-4 border-t-2 border-l-2 border-cyan-400"></div>
                <div class="absolute -top-1 -right-4 w-4 h-4 border-t-2 border-r-2 border-cyan-400"></div>
                <div class="absolute -bottom-1 -left-4 w-4 h-4 border-b-2 border-l-2 border-cyan-400"></div>
                <div class="absolute -bottom-1 -right-4 w-4 h-4 border-b-2 border-r-2 border-cyan-400"></div>
            </div>

            <!-- Dynamic Telemetry Log Status text -->
            <div class="h-8 flex items-center justify-center">
                <p id="preload-status" class="font-mono text-xs text-cyan-400/90 tracking-widest uppercase cursor-blink">
                    INITIALIZING ZERO-TRUST BOOT...
                </p>
            </div>

            <!-- Glowing Progress Bar Container -->
            <div class="w-full max-w-sm bg-slate-950 border border-cyan-500/20 rounded p-1.5 shadow-[0_0_15px_rgba(6,182,212,0.05)]">
                <!-- Inner progress glow -->
                <div class="w-full h-2.5 bg-slate-900/50 rounded overflow-hidden relative">
                    <div id="preload-progress-bar" class="h-full w-0 bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-400 shadow-[0_0_10px_rgba(6,182,212,0.8)] transition-all duration-100 ease-out"></div>
                </div>
            </div>

            <!-- Real-time Percentage Indicator -->
            <div class="font-mono text-sm text-cyan-400 tracking-[0.2em] font-bold" id="preload-percentage">
                0%
            </div>

            <!-- Symmetrical base logs -->
            <div class="w-full flex justify-between items-center text-[8px] font-mono text-slate-600 tracking-wider pt-2 select-none border-t border-slate-900/50">
                <span>SECURE BOOT SECTOR: OK</span>
                <span>CORE BOOTED</span>
                <span>V2.0_SECURE</span>
            </div>
        </div>
    </div>
    
    <!-- Separate Glowing Background Grids -->
    <div class="fixed inset-y-0 left-0 w-1/2 split-bg-left pointer-events-none z-0"></div>
    <div class="fixed inset-y-0 right-0 w-1/2 split-bg-right border-l border-slate-900/40 pointer-events-none z-0"></div>

    <!-- Ambient split plexus network canvas background -->
    <canvas id="network-canvas" class="absolute inset-0 w-full h-full pointer-events-none opacity-20 z-0"></canvas>
    
    <!-- Screen overlay elements -->
    <div class="scanlines"></div>

    <!-- MAIN HEADER -->
    <header class="relative z-10 w-full px-8 py-5 border-b border-slate-900/60 bg-slate-950/70 backdrop-blur-md flex flex-col items-center">
        <!-- Sub-Header text -->
        <span class="font-mono text-slate-400 tracking-[0.3em] text-[10px] md:text-xs uppercase mb-1 font-semibold">
            AUTHX CYBERSECURITY PORTAL - REGISTRATION
        </span>
        
        <!-- Big Glowing Central Title -->
        <h1 class="font-cyber text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-400 to-blue-500 text-glow-cyan select-none uppercase tracking-widest my-2">
            AUTHX
        </h1>
        
        <!-- Real-time Status -->
        <div class="flex items-center gap-2 mt-1">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
            <span class="w-2 h-2 rounded-full bg-emerald-500 absolute"></span>
            <span class="font-mono text-[10px] text-slate-500 tracking-wider">
                DECRYPT CHANNELS: <span class="text-teal-400">ACTIVE</span> // ENCRYPTION: SECURE_RSA_4096
            </span>
        </div>
    </header>

    <!-- PORTAL GRID CONTAINER -->
    <main class="relative z-10 flex-1 w-full max-w-7xl mx-auto py-8 px-4 md:px-8 grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch justify-center">

        <!-- LEFT PANEL: MULTI FACTOR AUTHENTICATION REGISTRATION (RED THEME) -->
        <section id="panel-left" class="cyber-card-red rounded-lg p-6 md:p-8 flex flex-col justify-between relative overflow-hidden group">
            <div class="scanning absolute inset-0 opacity-10 pointer-events-none"></div>
            
            <div class="relative z-10">
                <!-- Title Block -->
                <div class="flex flex-col mb-6 border-b border-red-500/10 pb-4">
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-red-950/50 rounded border border-red-500/30 text-red-500 shadow-[0_0_10px_rgba(239,68,68,0.2)]">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="font-cyber text-lg md:text-xl font-bold tracking-wider text-red-500 text-glow-red uppercase">
                                MULTI FACTOR AUTHENTICATION REGISTRATION
                            </h2>
                            <p class="font-mono text-[10px] text-red-400/80 tracking-widest uppercase">
                                REGISTER YOUR OPERATIONAL TEAM SQUAD
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Form Section / Double-column inner flex -->
                <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
                    
                    <!-- Form Fields (Left Side) -->
                    <form id="form-left" class="md:col-span-7 space-y-4" onsubmit="event.preventDefault();">
                        <!-- TEAM NAME FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-red-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[TEAM NAME]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-red-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                    </svg>
                                </div>
                                <input type="text" id="left-team-name" required placeholder="[Team Name Placeholder]"
                                    style="--focus-glow: rgba(239, 68, 68, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-red-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- LEADER NAME FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-red-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[LEADER NAME]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-red-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                </div>
                                <input type="text" id="left-leader-name" required placeholder="[Leader Name Placeholder]"
                                    style="--focus-glow: rgba(239, 68, 68, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-red-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- LEADER EMAIL FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-red-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[LEADER EMAIL]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-red-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <input type="email" id="left-leader-email" required placeholder="[Leader Email Placeholder]"
                                    style="--focus-glow: rgba(239, 68, 68, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-red-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- PHONE NUMBER FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-red-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[PHONE NUMBER]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-red-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                    </svg>
                                </div>
                                <input type="tel" id="left-phone" required placeholder="[Phone Number Placeholder]"
                                    style="--focus-glow: rgba(239, 68, 68, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-red-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- GITHUB / PORTFOLIO HASH FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-red-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[GITHUB/PORTFOLIO HASH]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-red-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                    </svg>
                                </div>
                                <input type="url" id="left-github" required placeholder="https://github.com/profile"
                                    style="--focus-glow: rgba(239, 68, 68, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-red-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- EXPERIENCE LEVEL FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-red-400/90 mb-1 tracking-wider uppercase">
                                [EXPERIENCE LEVEL]:
                            </label>
                            <select id="left-exp" class="w-full bg-slate-950/90 border border-slate-800 text-slate-300 font-mono text-xs py-2 px-3 rounded focus:outline-none focus:border-red-500 focus:text-slate-100">
                                <option value="NOVICE / SCRIPT KIDDIE">[NOVICE / SCRIPT KIDDIE]</option>
                                <option value="INTERMEDIATE / MAIN DEPLOYER">[INTERMEDIATE / MAIN DEPLOYER]</option>
                                <option value="EXPERT / ARCHITECT OPERATIVE">[EXPERT / ARCHITECT OPERATIVE]</option>
                            </select>
                        </div>

                        <!-- DYNAMIC TEAM MEMBERS INPUT -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-red-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[TEAM MEMBERS]:</span>
                                <span class="text-[9px] text-slate-500 font-bold" id="left-members-count">0 ADDED</span>
                            </label>
                            <div class="flex gap-2">
                                <div class="relative flex-1 rounded shadow-sm">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-red-400">
                                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    <input type="text" id="left-member-input" placeholder="Type name & click '+'"
                                        style="--focus-glow: rgba(239, 68, 68, 0.4);"
                                        class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-red-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                                </div>
                                <button type="button" id="btn-left-add-member" class="px-3 bg-red-950/50 hover:bg-red-500/30 text-red-400 border border-red-500/40 rounded font-mono text-xs hover:text-red-200 transition-colors uppercase tracking-wider font-bold">
                                    +
                                </button>
                            </div>
                            <div id="left-members-list" class="flex flex-wrap gap-2 mt-2 pt-1 min-h-[36px] border border-dashed border-red-950/40 rounded p-1.5 bg-red-950/5">
                                <span class="text-[10px] text-slate-600 font-mono italic p-1">No operational squad members registered yet...</span>
                            </div>
                        </div>
                    </form>

                    <!-- Diagrams & Settings (Right Side of Left Card) -->
                    <div class="md:col-span-5 flex flex-col justify-between h-full space-y-4">
                        
                        <!-- MULTI-FACTOR AUTHENTICATION DIAGRAM (SVG BASED GRAPHIC FROM IMAGE 2) -->
                        <div class="p-3.5 bg-slate-950/90 border border-slate-900 rounded-md">
                            <h3 class="font-mono text-[10px] text-red-400 tracking-wider uppercase mb-3 text-center border-b border-red-500/10 pb-1.5 font-bold">
                                MULTI-FACTOR AUTHENTICATION SHIELD FLOW
                            </h3>
                            
                            <div class="flex justify-center py-2 bg-slate-900/30 rounded border border-slate-900">
                                <svg id="mfa-diagram-svg" viewBox="0 0 240 180" class="w-full h-auto max-w-[210px]">
                                    <!-- Glow definitions & gradients -->
                                    <defs>
                                        <filter id="glow-red-mfa" x="-20%" y="-20%" width="140%" height="140%">
                                            <feGaussianBlur stdDeviation="2.5" result="blur"/>
                                            <feMerge>
                                                <feMergeNode in="blur"/>
                                                <feMergeNode in="SourceGraphic"/>
                                            </feMerge>
                                        </filter>
                                        <radialGradient id="shield-grad-red" cx="50%" cy="50%" r="50%">
                                            <stop offset="0%" stop-color="rgba(239, 68, 68, 0.2)" />
                                            <stop offset="100%" stop-color="rgba(3, 7, 18, 0.8)" />
                                        </radialGradient>
                                    </defs>

                                    <!-- Symmetrical background grid overlays -->
                                    <line x1="120" y1="10" x2="120" y2="170" stroke="rgba(239, 68, 68, 0.05)" stroke-width="0.5" stroke-dasharray="2,2"/>
                                    <line x1="10" y1="85" x2="230" y2="85" stroke="rgba(239, 68, 68, 0.05)" stroke-width="0.5" stroke-dasharray="2,2"/>
                                    <circle cx="120" cy="85" r="70" fill="none" stroke="rgba(239, 68, 68, 0.03)" stroke-width="0.5"/>

                                    <!-- Connecting Flow Vector Lines (from nodes to shield) -->
                                    <!-- Vector 1 (Top Left to Shield) -->
                                    <path d="M58 55 Q95 65 102 74" fill="none" stroke="rgba(239, 68, 68, 0.25)" stroke-width="1.5" id="flow-line-1" stroke-dasharray="3,3"/>
                                    <!-- Vector 2 (Top Right to Shield) -->
                                    <path d="M182 55 Q145 65 138 74" fill="none" stroke="rgba(239, 68, 68, 0.25)" stroke-width="1.5" id="flow-line-2" stroke-dasharray="3,3"/>
                                    <!-- Vector 3 (Bottom Center to Shield) -->
                                    <path d="M120 122 L120 102" fill="none" stroke="rgba(239, 68, 68, 0.25)" stroke-width="1.5" id="flow-line-3" stroke-dasharray="3,3"/>

                                    <!-- Floating Tech Badge Hexagons (Zero Trust, Layered Security, etc.) -->
                                    <!-- Top Left Badge: ZERO TRUST -->
                                    <g transform="translate(12, 70)" class="select-none">
                                        <polygon points="12,0 24,7 24,20 12,27 0,20 0,7" fill="rgba(239, 68, 68, 0.02)" stroke="rgba(239, 68, 68, 0.2)" stroke-width="0.75" />
                                        <text x="12" y="11" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" text-anchor="middle" font-weight="bold">ZERO</text>
                                        <text x="12" y="17" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" text-anchor="middle" font-weight="bold">TRUST</text>
                                    </g>
                                    <!-- Bottom Left Badge: DEFENSE IN DEPTH -->
                                    <g transform="translate(12, 107)" class="select-none">
                                        <polygon points="12,0 24,7 24,20 12,27 0,20 0,7" fill="rgba(239, 68, 68, 0.02)" stroke="rgba(239, 68, 68, 0.2)" stroke-width="0.75" />
                                        <text x="12" y="11" font-family="'Share Tech Mono', monospace" font-size="3.5" fill="#64748b" text-anchor="middle" font-weight="bold">DEFENSE</text>
                                        <text x="12" y="17" font-family="'Share Tech Mono', monospace" font-size="3.5" fill="#64748b" text-anchor="middle" font-weight="bold">IN DEPTH</text>
                                    </g>
                                    <!-- Top Right Badge: BEST PRACTICES -->
                                    <g transform="translate(204, 70)" class="select-none">
                                        <polygon points="12,0 24,7 24,20 12,27 0,20 0,7" fill="rgba(239, 68, 68, 0.02)" stroke="rgba(239, 68, 68, 0.2)" stroke-width="0.75" />
                                        <text x="12" y="11" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" text-anchor="middle" font-weight="bold">BEST</text>
                                        <text x="12" y="17" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" text-anchor="middle" font-weight="bold">PRACTICE</text>
                                    </g>
                                    <!-- Bottom Right Badge: LAYERED SECURITY -->
                                    <g transform="translate(204, 107)" class="select-none">
                                        <polygon points="12,0 24,7 24,20 12,27 0,20 0,7" fill="rgba(239, 68, 68, 0.02)" stroke="rgba(239, 68, 68, 0.2)" stroke-width="0.75" />
                                        <text x="12" y="11" font-family="'Share Tech Mono', monospace" font-size="3.5" fill="#64748b" text-anchor="middle" font-weight="bold">LAYERED</text>
                                        <text x="12" y="17" font-family="'Share Tech Mono', monospace" font-size="3.5" fill="#64748b" text-anchor="middle" font-weight="bold">SECURE</text>
                                    </g>

                                    <!-- Node 1: KNOWLEDGE (PASSWORD) - Top Left -->
                                    <g id="node-knowledge" class="transition-all duration-300">
                                        <circle cx="45" cy="45" r="20" fill="#020617" stroke="#dc2626" stroke-width="1.2" id="circle-knowledge" />
                                        <!-- Fingerprint inline icon (detailed vector paths) -->
                                        <g id="icon-knowledge" stroke="#ef4444" stroke-width="1.1" fill="none" stroke-linecap="round" class="transition-all duration-300">
                                            <path d="M41 38 A 5 5 0 0 1 49 38" />
                                            <path d="M39 41 A 7 7 0 0 1 51 41" />
                                            <path d="M37 44 A 9 9 0 0 1 53 44" />
                                            <path d="M36 48 A 11 11 0 0 1 54 48" />
                                            <path d="M38 51 Q45 49 52 51" />
                                            <path d="M42 54 Q45 52 48 54" />
                                            <path d="M44 34 A 2 2 0 0 1 46 34" />
                                        </g>
                                        <text x="45" y="73" text-anchor="middle" font-family="'Share Tech Mono', monospace" font-size="5.5" fill="#94a3b8" font-weight="bold" class="uppercase">1. PASSWORD</text>
                                    </g>

                                    <!-- Node 2: POSSESSION (MOBILE DEVICE) - Top Right -->
                                    <g id="node-possession" class="transition-all duration-300">
                                        <circle cx="195" cy="45" r="20" fill="#020617" stroke="#dc2626" stroke-width="1.2" id="circle-possession" />
                                        <!-- Phone outline/OTP badge vector -->
                                        <g stroke="#ef4444" stroke-width="1.1" fill="none" class="transition-all duration-300">
                                            <!-- Phone Body -->
                                            <rect x="189" y="34" width="12" height="22" rx="1.5" stroke="#ef4444" stroke-width="1.1" id="icon-possession-rect" />
                                            <!-- Checkmark inside mobile screen -->
                                            <path d="M192 44 L194 46 L198 41" stroke="#ef4444" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" id="icon-possession-path" />
                                            <!-- Home button & Camera -->
                                            <circle cx="195" cy="53" r="0.75" fill="#ef4444" stroke="none" />
                                            <circle cx="195" cy="36.5" r="0.5" fill="#ef4444" stroke="none" />
                                            <!-- Floating OTP tag label -->
                                            <rect x="175" y="39" width="11" height="6" rx="1" fill="#ef4444" stroke="none" opacity="0.8" id="otp-rect"/>
                                            <text x="180.5" y="44" font-family="'Share Tech Mono', monospace" font-size="4.5" fill="#030712" text-anchor="middle" font-weight="bold">OTP</text>
                                        </g>
                                        <text x="195" y="73" text-anchor="middle" font-family="'Share Tech Mono', monospace" font-size="5.5" fill="#94a3b8" font-weight="bold" class="uppercase">2. TELECOMM</text>
                                    </g>

                                    <!-- Node 3: INHERENCE (BIOMETRIC) - Bottom Center -->
                                    <g id="node-inherence" class="transition-all duration-300">
                                        <circle cx="120" cy="140" r="20" fill="#020617" stroke="#dc2626" stroke-width="1.2" id="circle-inherence" />
                                        <!-- Biometric face recognition scan matrix -->
                                        <g id="icon-inherence" stroke="#ef4444" stroke-width="1" fill="none" stroke-linecap="round" stroke-linejoin="round" class="transition-all duration-300">
                                            <!-- Crosshair scan corners -->
                                            <path d="M112 131 H115 V134" />
                                            <path d="M128 131 H125 V134" />
                                            <path d="M112 149 H115 V146" />
                                            <path d="M128 149 H125 V146" />
                                            <!-- Face structural outline -->
                                            <path d="M115 141 C115 137, 125 137, 125 141 C125 145, 123 147, 120 148 C117 147, 115 145, 115 141 Z" stroke-width="0.8"/>
                                            <!-- Scan indicators -->
                                            <circle cx="118" cy="140" r="0.5" fill="#ef4444" stroke="none"/>
                                            <circle cx="122" cy="140" r="0.5" fill="#ef4444" stroke="none"/>
                                            <path d="M120 141 L120 143" stroke-width="0.8" />
                                            <path d="M118.5 145 Q120 146.5 121.5 145" stroke-width="0.8"/>
                                            <!-- Bouncing scan telemetry line -->
                                            <line x1="110" y1="140" x2="130" y2="140" stroke="#ef4444" stroke-width="0.8" stroke-dasharray="1,1" class="face-scan-line"/>
                                        </g>
                                        <text x="120" y="168" text-anchor="middle" font-family="'Share Tech Mono', monospace" font-size="5.5" fill="#94a3b8" font-weight="bold" class="uppercase">3. SQUAD MEM</text>
                                    </g>

                                    <!-- Central Shield Group -->
                                    <g id="mfa-central-shield" class="transition-all duration-500">
                                        <!-- concentric background circle radar -->
                                        <circle cx="120" cy="85" r="30" fill="url(#shield-grad-red)" stroke="#dc2626" stroke-width="1.2" stroke-dasharray="3,3" id="mfa-shield-ring" />
                                        
                                        <!-- Main shield path -->
                                        <path d="M120 66 C128 66, 135 62, 135 62 C135 62, 135 88, 120 98 C105 88, 105 62, 105 62 C105 62, 112 66, 120 66 Z" 
                                              fill="rgba(220, 38, 38, 0.08)" stroke="#dc2626" stroke-width="1.5" id="mfa-shield-path" class="transition-all duration-300"/>
                                        
                                        <!-- Lock/check mark icon inside shield -->
                                        <path id="mfa-shield-icon" d="M116 83 L119 86 L125 80" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="transition-all duration-300" />
                                        
                                        <!-- Symmetrical Chevron Arrow (ACCESS GRANTED) pointing to the right -->
                                        <g id="mfa-granted-arrow" class="opacity-0 transition-all duration-500">
                                            <path d="M142 85 L135 79 L135 83 L126 83 L126 87 L135 87 L135 91 Z" fill="#10b981" class="svg-glow-green"/>
                                        </g>
                                        
                                        <!-- Shield status label -->
                                        <text id="mfa-shield-status" x="120" y="111" text-anchor="middle" font-family="'Share Tech Mono', monospace" font-size="7" fill="#ef4444" class="font-bold tracking-wider transition-all duration-300">RESTRICTED</text>
                                    </g>
                                </svg>
                            </div>
                        </div>

                        <!-- TRACK SELECTION -->
                        <div class="relative">
                            <label class="block font-mono text-[10px] text-red-400/90 mb-1 tracking-wider uppercase">
                                TRACK SELECTION
                            </label>
                            <select id="left-track" class="w-full bg-slate-950/90 border border-slate-800 text-slate-300 font-mono text-xs py-2 px-3 rounded focus:outline-none focus:border-red-500 focus:text-slate-100">
                                <option value="SECURE AI DEPLOYMENT">[SECURE AI DEPLOYMENT]</option>
                                <option value="CYBER DEFENSE CHALLENGE">[CYBER DEFENSE CHALLENGE]</option>
                                <option value="HACKATHON OPEN TRACK">[HACKATHON OPEN TRACK]</option>
                            </select>
                        </div>

                        <!-- VISUAL GRAPH -->
                        <div class="p-2.5 bg-slate-950/90 border border-slate-900 rounded-md">
                            <span class="block font-mono text-[9px] text-slate-500 tracking-wider mb-1">VISUAL GRAPH</span>
                            <div class="h-10 w-full relative">
                                <canvas id="sparkline-left" class="w-full h-full"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Status & Actions inside Left Card -->
                <div class="mt-8 flex flex-col sm:flex-row gap-4 justify-between items-center border-t border-red-500/10 pt-5">
                    <!-- Status Lock Panel -->
                    <div class="flex items-center gap-3">
                        <div id="left-lock-box" class="p-2 bg-red-950/30 rounded-full border border-red-500/20 text-red-500 transition-all duration-300">
                            <svg id="left-lock-icon" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </div>
                        <div class="flex gap-1.5" id="left-lock-leds">
                            <span class="w-2.5 h-2.5 rounded-full bg-red-500 transition-all duration-300"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-800 transition-all duration-300"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-800 transition-all duration-300"></span>
                        </div>
                    </div>

                    <!-- Submit Button -->
                    <button id="btn-left-submit" 
                        class="w-full sm:w-auto px-6 py-2.5 bg-red-950/40 hover:bg-red-500 text-red-400 hover:text-slate-950 border border-red-500/50 font-cyber text-xs font-bold uppercase rounded btn-glow-red transition-all">
                        REGISTER & DEPLOY TEAM
                    </button>
                </div>
            </div>
        </section>

        <!-- RIGHT PANEL: THREAD AUTHENTICATION REGISTRATION (TEAL THEME) -->
        <section id="panel-right" class="cyber-card-teal rounded-lg p-6 md:p-8 flex flex-col justify-between relative overflow-hidden group">
            <div class="scanning absolute inset-0 opacity-10 pointer-events-none"></div>
            
            <div class="relative z-10">
                <!-- Title Block -->
                <div class="flex flex-col mb-6 border-b border-teal-500/10 pb-4">
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-teal-950/50 rounded border border-teal-500/30 text-teal-500 shadow-[0_0_10px_rgba(20,184,166,0.2)]">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="font-cyber text-lg md:text-xl font-bold tracking-wider text-teal-500 text-glow-teal uppercase">
                                THREAD AUTHENTICATION REGISTRATION
                            </h2>
                            <p class="font-mono text-[10px] text-teal-400/80 tracking-widest uppercase">
                                REGISTER YOUR OPERATIONAL TEAM SQUAD
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Form Section / Double-column inner flex (TWIN FIELDS!) -->
                <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
                    
                    <!-- Form Fields (Left Side) - SAME FIELDS AS LEFT FORM -->
                    <form id="form-right" class="md:col-span-7 space-y-4" onsubmit="event.preventDefault();">
                        <!-- TEAM NAME FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-teal-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[TEAM NAME]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-teal-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                    </svg>
                                </div>
                                <input type="text" id="right-team-name" required placeholder="[Team Name Placeholder]"
                                    style="--focus-glow: rgba(20, 184, 166, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-teal-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- LEADER NAME FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-teal-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[LEADER NAME]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-teal-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                    </svg>
                                </div>
                                <input type="text" id="right-leader-name" required placeholder="[Leader Name Placeholder]"
                                    style="--focus-glow: rgba(20, 184, 166, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-teal-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- LEADER EMAIL FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-teal-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[LEADER EMAIL]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-teal-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <input type="email" id="right-leader-email" required placeholder="[Leader Email Placeholder]"
                                    style="--focus-glow: rgba(20, 184, 166, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-teal-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- PHONE NUMBER FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-teal-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[PHONE NUMBER]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-teal-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                    </svg>
                                </div>
                                <input type="tel" id="right-phone" required placeholder="[Phone Number Placeholder]"
                                    style="--focus-glow: rgba(20, 184, 166, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-teal-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- GITHUB / PORTFOLIO HASH FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-teal-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[GITHUB/PORTFOLIO HASH]:</span>
                                <span class="text-[9px] text-slate-500 val-status-txt">PENDING</span>
                            </label>
                            <div class="relative rounded shadow-sm">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-teal-400">
                                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                    </svg>
                                </div>
                                <input type="url" id="right-github" required placeholder="https://github.com/profile"
                                    style="--focus-glow: rgba(20, 184, 166, 0.4);"
                                    class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-teal-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                            </div>
                        </div>

                        <!-- EXPERIENCE LEVEL FIELD -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-teal-400/90 mb-1 tracking-wider uppercase">
                                [EXPERIENCE LEVEL]:
                            </label>
                            <select id="right-exp" class="w-full bg-slate-950/90 border border-slate-800 text-slate-300 font-mono text-xs py-2 px-3 rounded focus:outline-none focus:border-teal-500 focus:text-slate-100">
                                <option value="NOVICE / SCRIPT KIDDIE">[NOVICE / SCRIPT KIDDIE]</option>
                                <option value="INTERMEDIATE / MAIN DEPLOYER">[INTERMEDIATE / MAIN DEPLOYER]</option>
                                <option value="EXPERT / ARCHITECT OPERATIVE">[EXPERT / ARCHITECT OPERATIVE]</option>
                            </select>
                        </div>

                        <!-- DYNAMIC TEAM MEMBERS INPUT (FOR MULTI FACTOR CARD) -->
                        <div class="relative">
                            <label class="block font-mono text-xs text-teal-400/90 mb-1 tracking-wider uppercase flex items-center justify-between">
                                <span>[TEAM MEMBERS]:</span>
                                <span class="text-[9px] text-slate-500 font-bold" id="right-members-count">0 ADDED</span>
                            </label>
                            <div class="flex gap-2">
                                <div class="relative flex-1 rounded shadow-sm">
                                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-teal-400">
                                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    <input type="text" id="right-member-input" placeholder="Type name & click '+'"
                                        style="--focus-glow: rgba(20, 184, 166, 0.4);"
                                        class="cyber-input block w-full bg-slate-950/90 border border-slate-800 focus:border-teal-500 text-slate-200 pl-10 pr-3 py-2 rounded font-mono text-xs tracking-wider">
                                </div>
                                <button type="button" id="btn-right-add-member" class="px-3 bg-teal-950/50 hover:bg-teal-500/30 text-teal-400 border border-teal-500/40 rounded font-mono text-xs hover:text-teal-200 transition-colors uppercase tracking-wider font-bold">
                                    +
                                </button>
                            </div>
                            <div id="right-members-list" class="flex flex-wrap gap-2 mt-2 pt-1 min-h-[36px] border border-dashed border-teal-950/40 rounded p-1.5 bg-teal-950/5">
                                <span class="text-[10px] text-slate-600 font-mono italic p-1">No operational squad members registered yet...</span>
                            </div>
                        </div>
                    </form>

                    <!-- Diagrams & Settings (Right Side of Right Card) -->
                    <div class="md:col-span-5 flex flex-col justify-between h-full space-y-4">
                        
                        <!-- THREAD IDENTITY VERIFICATION DIAGRAM (SVG BASED GRAPHIC FROM IMAGE 1) -->
                        <div class="p-3.5 bg-slate-950/90 border border-slate-900 rounded-md">
                            <h3 class="font-mono text-[10px] text-teal-400 tracking-wider uppercase mb-3 text-center border-b border-teal-500/10 pb-1.5 font-bold">
                                THREAD IDENTITY VERIFICATION FLOW
                            </h3>
                            
                            <div class="flex justify-center py-2 bg-slate-900/30 rounded border border-slate-900">
                                <svg id="thread-diagram-svg" viewBox="0 0 240 180" class="w-full h-auto max-w-[210px]">
                                    <!-- Glow definitions & patterns -->
                                    <defs>
                                        <filter id="glow-teal-thread" x="-20%" y="-20%" width="140%" height="140%">
                                            <feGaussianBlur stdDeviation="2" result="blur"/>
                                            <feMerge>
                                                <feMergeNode in="blur"/>
                                                <feMergeNode in="SourceGraphic"/>
                                            </feMerge>
                                        </filter>
                                        <radialGradient id="lock-grad-teal" cx="50%" cy="50%" r="50%">
                                            <stop offset="0%" stop-color="rgba(20, 184, 166, 0.2)" />
                                            <stop offset="100%" stop-color="rgba(3, 7, 18, 0.8)" />
                                        </radialGradient>
                                    </defs>

                                    <!-- Symmetrical background grids & telemetry ticks -->
                                    <line x1="120" y1="10" x2="120" y2="170" stroke="rgba(20, 184, 166, 0.05)" stroke-width="0.5" stroke-dasharray="1,2"/>
                                    <line x1="10" y1="85" x2="230" y2="85" stroke="rgba(20, 184, 166, 0.05)" stroke-width="0.5" stroke-dasharray="1,2"/>
                                    <circle cx="120" cy="85" r="48" fill="none" stroke="rgba(20, 184, 166, 0.04)" stroke-width="0.5" stroke-dasharray="5,5"/>

                                    <!-- Rotating central telemetry lines (Cyber Galaxy Spiral) -->
                                    <g id="galaxy-spiral" class="radar-rotate">
                                        <circle cx="120" cy="85" r="38" fill="none" stroke="rgba(20, 184, 166, 0.15)" stroke-width="0.75" stroke-dasharray="1, 8" />
                                        <circle cx="120" cy="85" r="30" fill="none" stroke="rgba(20, 184, 166, 0.3)" stroke-width="0.75" stroke-dasharray="5, 20" />
                                        <circle cx="120" cy="85" r="24" fill="none" stroke="#14b8a6" stroke-width="1.2" stroke-dasharray="15, 60" class="svg-glow-teal" />
                                        <circle cx="120" cy="85" r="16" fill="none" stroke="#14b8a6" stroke-width="0.75" stroke-dasharray="2, 8" />
                                    </g>

                                    <!-- Central Keyhole & Lock housing structure -->
                                    <g id="central-padlock-housing" transform="translate(108, 90)">
                                        <!-- Lock body -->
                                        <rect x="0" y="10" width="24" height="20" rx="3" fill="url(#lock-grad-teal)" stroke="#14b8a6" stroke-width="1.2" class="svg-glow-teal"/>
                                        <circle cx="12" cy="20" r="3" fill="#020617" stroke="#14b8a6" stroke-width="1.2" id="central-keyhole"/>
                                        <path d="M11 23 L13 23 L14 28 L10 28 Z" fill="#020617" stroke="#14b8a6" stroke-width="1" />
                                    </g>

                                    <!-- Interactive Key Element (slides into place on validation) -->
                                    <g id="dynamic-vector-key" transform="translate(0, -15)" class="transition-all duration-700 opacity-60">
                                        <!-- Futuristic holographic key outline -->
                                        <path d="M120 44 C123 44, 125 41, 125 38 C125 35, 123 32, 120 32 C117 32, 115 35, 115 38 C115 41, 117 44, 120 44 Z M120 44 L120 92 L124 92 L124 96 L120 96 L120 100 L124 100 L124 103 L120 103" 
                                              fill="none" stroke="#14b8a6" stroke-width="1.5" class="svg-glow-teal"/>
                                    </g>

                                    <!-- Big Access Granted Neon Arrow Pointer -->
                                    <g id="access-granted-arrow" class="opacity-30 transition-all duration-500">
                                        <path d="M158 85 L144 77 L144 82 L132 82 L132 88 L144 88 L144 93 Z" fill="#10b981" class="svg-glow-green" />
                                        <text x="145" y="70" text-anchor="middle" font-family="'Orbitron', sans-serif" font-size="5" fill="#10b981" class="font-bold tracking-widest uppercase">ACCESS</text>
                                    </g>

                                    <!-- Left Column Nodes (Operator, Unit, Objectives) -->
                                    <!-- Node 1: [OPERATOR ID] (Top Left) -->
                                    <g id="node-operator" class="transition-all duration-300">
                                        <rect x="12" y="15" width="64" height="42" rx="3" fill="#020617" stroke="rgba(20, 184, 166, 0.4)" stroke-width="1.2" id="rect-operator"/>
                                        <text x="44" y="25" text-anchor="middle" font-family="'Orbitron', sans-serif" font-size="5.5" fill="#94a3b8" font-weight="bold">[OPERATOR]</text>
                                        <!-- Operator Phone diagnostics shape -->
                                        <g stroke="currentColor" stroke-width="0.8" fill="none" opacity="0.6" transform="translate(38, 28)">
                                            <rect x="-4" y="0" width="8" height="13" rx="1"/>
                                            <path d="-2 2 H2 M-2 10 H2"/>
                                            <!-- Tiny checkbox dot -->
                                            <circle cx="2" cy="6" r="1" fill="#14b8a6"/>
                                        </g>
                                    </g>

                                    <!-- Node 2: [UNIT ID] (Middle Left) -->
                                    <g id="node-unit" class="transition-all duration-300">
                                        <rect x="12" y="68" width="64" height="42" rx="3" fill="#020617" stroke="rgba(20, 184, 166, 0.4)" stroke-width="1.2" id="rect-unit"/>
                                        <text x="44" y="78" text-anchor="middle" font-family="'Orbitron', sans-serif" font-size="5.5" fill="#94a3b8" font-weight="bold">[UNIT ID]</text>
                                        <!-- Symmetrical Dual keys vector -->
                                        <g stroke="currentColor" stroke-width="0.8" fill="none" opacity="0.6" transform="translate(30, 81)">
                                            <path d="M0 5 H10 M2 3 V7 M5 3 V7" />
                                            <circle cx="12" cy="5" r="2"/>
                                            <path d="M0 10 H10" stroke-dasharray="1,1"/>
                                        </g>
                                    </g>

                                    <!-- Node 3: [ASSIGNED OBJECTIVES] (Bottom Left) -->
                                    <g id="node-assigned" class="transition-all duration-300">
                                        <rect x="12" y="121" width="64" height="42" rx="3" fill="#020617" stroke="rgba(20, 184, 166, 0.4)" stroke-width="1.2" id="rect-assigned"/>
                                        <text x="44" y="131" text-anchor="middle" font-family="'Orbitron', sans-serif" font-size="4.8" fill="#94a3b8" font-weight="bold">[OBJECTIVES]</text>
                                        <!-- Symmetrical keylock graphics -->
                                        <g stroke="currentColor" stroke-width="0.8" fill="none" opacity="0.6" transform="translate(38, 134)">
                                            <rect x="-4" y="4" width="8" height="6" rx="1"/>
                                            <path d="M-2 4 V2 A 2 2 0 0 1 2 2 V4" />
                                        </g>
                                    </g>

                                    <!-- Right Column Node: [AUTHENTICATION THREAD NODE] -->
                                    <g id="node-thread-node-panel" class="transition-all duration-300">
                                        <rect x="164" y="15" width="64" height="148" rx="4" fill="#020617" stroke="rgba(20, 184, 166, 0.4)" stroke-width="1.2" id="rect-thread-node"/>
                                        <text x="196" y="26" text-anchor="middle" font-family="'Orbitron', sans-serif" font-size="5" fill="#94a3b8" font-weight="bold" tracking-wider>[THREAD NODE]</text>
                                        
                                        <!-- Led Bullet row 1 (Member verification) -->
                                        <circle cx="174" cy="42" r="2.5" fill="#ef4444" class="thread-node-led transition-all duration-300"/>
                                        <text x="180" y="44" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" font-weight="bold">MEMBER IDENT</text>
                                        
                                        <!-- Led Bullet row 2 (Completed profiles status) -->
                                        <circle cx="174" cy="70" r="2.5" fill="#ef4444" class="thread-node-led transition-all duration-300"/>
                                        <text x="180" y="72" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" font-weight="bold">2001 PROFILE</text>

                                        <!-- Led Bullet row 3 (Deployment status) -->
                                        <circle cx="174" cy="98" r="2.5" fill="#ef4444" class="thread-node-led transition-all duration-300"/>
                                        <text x="180" y="100" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" font-weight="bold">DEPLOY SQUAD</text>

                                        <!-- Tech Bars indicators -->
                                        <g fill="rgba(20, 184, 166, 0.15)" stroke="none" transform="translate(172, 120)">
                                            <rect x="0" y="0" width="48" height="3" rx="0.5" />
                                            <rect x="0" y="6" width="36" height="3" rx="0.5" />
                                            <rect x="0" y="12" width="44" height="3" rx="0.5" />
                                            <!-- Mini grid values -->
                                            <text x="24" y="24" font-family="'Share Tech Mono', monospace" font-size="4" fill="#64748b" text-anchor="middle" font-weight="bold" class="select-none">ZERO TRUST</text>
                                        </g>
                                    </g>
                                </svg>
                            </div>
                        </div>

                        <!-- TRACK SELECTION -->
                        <div class="relative">
                            <label class="block font-mono text-[10px] text-teal-400/90 mb-1 tracking-wider uppercase">
                                AUTH METHOD
                            </label>
                            <select id="right-track" class="w-full bg-slate-950/90 border border-slate-800 text-slate-300 font-mono text-xs py-2 px-3 rounded focus:outline-none focus:border-teal-500 focus:text-slate-100">
                                <option value="BIOMETRIC SCAN">[BIOMETRIC SCAN]</option>
                                <option value="SECURITY KEY">[SECURITY KEY]</option>
                                <option value="ONE-TIME PASSWORD">[ONE-TIME PASSWORD]</option>
                            </select>
                        </div>

                        <!-- VISUAL GRAPH -->
                        <div class="p-2.5 bg-slate-950/90 border border-slate-900 rounded-md">
                            <span class="block font-mono text-[9px] text-slate-500 tracking-wider mb-1">REAL-TIME TELEMETRY GRAPH</span>
                            <div class="h-10 w-full relative">
                                <canvas id="sparkline-right" class="w-full h-full"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Status & Actions inside Right Card -->
                <div class="mt-8 flex flex-col sm:flex-row gap-4 justify-between items-center border-t border-teal-500/10 pt-5">
                    <!-- Status Lock Panel -->
                    <div class="flex items-center gap-3">
                        <div id="right-lock-box" class="p-2 bg-teal-950/30 rounded-full border border-teal-500/20 text-teal-500 transition-all duration-300">
                            <svg id="right-lock-icon" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </div>
                        <div class="flex gap-1.5" id="right-lock-leds">
                            <span class="w-2.5 h-2.5 rounded-full bg-teal-500 transition-all duration-300"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-800 transition-all duration-300"></span>
                            <span class="w-2.5 h-2.5 rounded-full bg-slate-800 transition-all duration-300"></span>
                        </div>
                    </div>

                    <!-- Submit Button -->
                    <button id="btn-right-submit" 
                        class="w-full sm:w-auto px-6 py-2.5 bg-teal-950/40 hover:bg-teal-500 text-teal-400 hover:text-slate-950 border border-teal-500/50 font-cyber text-xs font-bold uppercase rounded btn-glow-teal transition-all">
                        REGISTER & DEPLOY TEAM
                    </button>
                </div>
            </div>
        </section>

    </main>

    <!-- FOOTER TERMINAL TELEMETRY -->
    <footer class="relative z-10 w-full text-center py-4 border-t border-slate-900 bg-slate-950/70 backdrop-blur-md">
        <span class="font-mono text-[10px] text-slate-600 tracking-[0.25em] uppercase">
            // AUTHX NODE DEPLOYED // COMPILATION: BUILD_2026.05 // CORE ACCESS SECURED // ALL ENTRANCES RECORDED
        </span>
    </footer>

    <!-- INTERACTIVE CYBER SUBMISSION TERMINAL OVERLAY (Fullscreen Modal) -->
    <div id="terminal-overlay" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-all opacity-0 pointer-events-none duration-500">
        <div class="w-full max-w-2xl bg-black border rounded-lg overflow-hidden flex flex-col h-[500px] shadow-2xl relative" id="terminal-box">
            <!-- Top bar -->
            <div class="bg-slate-900 px-4 py-2 border-b border-slate-800 flex justify-between items-center text-xs font-mono text-slate-400 select-none">
                <div class="flex items-center gap-1.5">
                    <span class="w-3.5 h-3.5 rounded-full bg-red-500/80"></span>
                    <span class="w-3.5 h-3.5 rounded-full bg-yellow-500/80"></span>
                    <span class="w-3.5 h-3.5 rounded-full bg-green-500/80"></span>
                    <span class="ml-2 font-bold tracking-wider">AUTHX SECURE TERMINAL: DEPLOY_SESSION_NODE</span>
                </div>
                <div class="text-[10px] text-slate-500">AES-256 SYMMETRIC DECRYPTION</div>
            </div>
            
            <!-- Terminal Output Area -->
            <div class="flex-1 bg-black p-5 font-mono text-xs md:text-sm text-green-400 overflow-y-auto space-y-2 select-text" id="terminal-logs">
                <div class="text-slate-500 font-bold border-b border-slate-950 pb-2 mb-2">// SECURITY ACCESS PORT INITIALIZED</div>
                <!-- Appending lines will happen via JS -->
            </div>

            <!-- Terminal Decrypting Status bar -->
            <div class="bg-slate-950 px-4 py-2 border-t border-slate-900 flex justify-between items-center text-xs font-mono text-slate-500 select-none">
                <div class="flex items-center gap-2">
                    <span class="w-2.5 h-2.5 bg-green-500 animate-pulse inline-block" id="terminal-status-indicator"></span>
                    <span id="terminal-status-text">DECOMPRESSING SESSION PROTOCOLS...</span>
                </div>
                <div id="terminal-percentage">0%</div>
            </div>

            <!-- Terminal Closing Hologram Area (Hidden until finished) -->
            <div id="success-screen" class="absolute inset-0 bg-black/95 flex flex-col items-center justify-center space-y-6 opacity-0 pointer-events-none transition-opacity duration-500">
                <div class="p-4 bg-teal-950/20 border border-teal-500/30 rounded-full text-teal-400 shadow-[0_0_30px_rgba(20,184,166,0.3)] animate-bounce">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                </div>
                <div class="text-center">
                    <h3 class="font-cyber text-2xl font-black text-teal-400 text-glow-teal tracking-widest uppercase">REGISTRATION SECURED</h3>
                    <p class="font-mono text-xs text-slate-400 mt-2">DECENTRALIZED NODE INJECTED SUCCESSFULLY</p>
                </div>
                <button id="btn-close-terminal" class="px-6 py-2 bg-teal-950/40 hover:bg-teal-500 text-teal-400 hover:text-slate-950 border border-teal-500/50 font-cyber text-xs font-bold uppercase rounded btn-glow-teal transition-all">
                    DISCONNECT TERMINAL
                </button>
            </div>
        </div>
    </div>

    <!-- AUDIO (Fake/Synth audio synthesized using Web Audio API for maximum immersion without asset files!) -->
    <script>
        // Web Audio Context for synthesizer sound effects
        let audioCtx;
        function getAudioContext() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            return audioCtx;
        }

        function playSynthBeep(freq, type, duration, volVal) {
            try {
                const ctx = getAudioContext();
                if (ctx.state === 'suspended') return;

                const osc = ctx.createOscillator();
                const gainNode = ctx.createGain();

                osc.type = type || 'sine';
                osc.frequency.value = freq || 800;

                gainNode.gain.setValueAtTime(volVal || 0.1, ctx.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);

                osc.connect(gainNode);
                gainNode.connect(ctx.destination);

                osc.start();
                osc.stop(ctx.currentTime + duration);
            } catch (e) {
                // Audio context block safeguard
            }
        }

        // Play input typing keyclick synth sound
        function playKeyClick() {
            playSynthBeep(1200 + Math.random() * 400, 'square', 0.05, 0.015);
        }

        // Play validation light up sound
        function playValidationSuccess() {
            playSynthBeep(1000, 'sine', 0.15, 0.05);
            setTimeout(() => playSynthBeep(1500, 'sine', 0.25, 0.05), 80);
        }

        // Play alarm/shake error sound
        function playAlarmError() {
            playSynthBeep(180, 'sawtooth', 0.4, 0.12);
        }
    </script>

    <!-- LIVE TELEMETRY GRAPHS (Sparklines) -->
    <script>
        class TelemetrySparkline {
            constructor(canvasId, strokeColor) {
                this.canvas = document.getElementById(canvasId);
                this.ctx = this.canvas.getContext('2d');
                this.color = strokeColor;
                this.points = [];
                this.maxPoints = 40;

                // Set canvas resolution for crisp lines
                this.resize();
                window.addEventListener('resize', () => this.resize());

                // Initialize points with random walk
                let currentVal = 20;
                for (let i = 0; i < this.maxPoints; i++) {
                    currentVal = Math.max(5, Math.min(35, currentVal + (Math.random() - 0.5) * 8));
                    this.points.push(currentVal);
                }

                this.animate();
            }

            resize() {
                const dpr = window.devicePixelRatio || 1;
                const rect = this.canvas.getBoundingClientRect();
                this.canvas.width = rect.width * dpr;
                this.canvas.height = rect.height * dpr;
                this.ctx.scale(dpr, dpr);
                this.width = rect.width;
                this.height = rect.height;
            }

            animate() {
                // Slide in a new point
                const lastPoint = this.points[this.points.length - 1];
                const newPoint = Math.max(2, Math.min(this.height - 2, lastPoint + (Math.random() - 0.5) * 6));
                this.points.push(newPoint);
                if (this.points.length > this.maxPoints) {
                    this.points.shift();
                }

                // Draw Sparkline
                this.ctx.clearRect(0, 0, this.width, this.height);
                this.ctx.lineWidth = 1.5;
                this.ctx.strokeStyle = this.color;

                // Create glowing shadow
                this.ctx.shadowBlur = 8;
                this.ctx.shadowColor = this.color;

                this.ctx.beginPath();
                const step = this.width / (this.maxPoints - 1);

                this.ctx.moveTo(0, this.points[0]);
                for (let i = 1; i < this.points.length; i++) {
                    this.ctx.lineTo(i * step, this.points[i]);
                }
                this.ctx.stroke();

                // Draw fill gradient below sparkline
                this.ctx.shadowBlur = 0; // disable shadow for fill
                this.ctx.beginPath();
                this.ctx.moveTo(0, this.height);
                this.ctx.lineTo(0, this.points[0]);
                for (let i = 1; i < this.points.length; i++) {
                    this.ctx.lineTo(i * step, this.points[i]);
                }
                this.ctx.lineTo(this.width, this.height);
                this.ctx.closePath();

                const grad = this.ctx.createLinearGradient(0, 0, 0, this.height);
                const strokeColorRgb = this.color.replace('rgb', 'rgba').replace(')', ', 0.15)');
                grad.addColorStop(0, strokeColorRgb);
                grad.addColorStop(1, 'rgba(0,0,0,0)');
                this.ctx.fillStyle = grad;
                this.ctx.fill();

                setTimeout(() => this.animate(), 120);
            }
        }

        // Initialize graphs when page loads
        let leftSpark, rightSpark;
        window.addEventListener('load', () => {
            leftSpark = new TelemetrySparkline('sparkline-left', 'rgb(239, 68, 68)');
            rightSpark = new TelemetrySparkline('sparkline-right', 'rgb(20, 184, 166)');
        });
    </script>

    <!-- AMBIENT Split Canvas Particle Network (Plexus) -->
    <script>
        const canvas = document.getElementById('network-canvas');
        const ctx = canvas.getContext('2d');

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        const particles = [];
        const numParticles = 75;

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.45;
                this.vy = (Math.random() - 0.5) * 0.45;
                this.radius = Math.random() * 2 + 1;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                if (this.x < 0 || this.x > width) this.vx = -this.vx;
                if (this.y < 0 || this.y > height) this.vy = -this.vy;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);

                // Red particles on left side, Teal particles on right side
                if (this.x < width / 2) {
                    ctx.fillStyle = 'rgba(239, 68, 68, 0.4)';
                } else {
                    ctx.fillStyle = 'rgba(20, 184, 166, 0.4)';
                }
                ctx.fill();
            }
        }

        for (let i = 0; i < numParticles; i++) {
            particles.push(new Particle());
        }

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        function animatePlexus() {
            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                p.update();
                p.draw();

                // Draw connection lines inside separate halves
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 125) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        const opacity = (1 - (dist / 125)) * 0.15;

                        // Separate link colors!
                        if (p.x < width / 2) {
                            ctx.strokeStyle = `rgba(239, 68, 68, ${opacity})`;
                        } else {
                            ctx.strokeStyle = `rgba(20, 184, 166, ${opacity})`;
                        }
                        ctx.lineWidth = 0.55;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animatePlexus);
        }

        requestAnimationFrame(animatePlexus);
    </script>

    <!-- INTERACTIVE FORM LOGIC, TEAM MEMBERS & VALIDATIONS -->
    <script>
        // State management for added team members list
        const teamMembers = {
            left: [],
            right: []
        };

        // Form field configurations
        const FORM_FIELDS = {
            left: {
                team: document.getElementById('left-team-name'),
                leaderName: document.getElementById('left-leader-name'),
                email: document.getElementById('left-leader-email'),
                phone: document.getElementById('left-phone'),
                github: document.getElementById('left-github'),
                exp: document.getElementById('left-exp'),
                btn: document.getElementById('btn-left-submit'),
                card: document.getElementById('panel-left'),
                lockBox: document.getElementById('left-lock-box'),
                lockIcon: document.getElementById('left-lock-icon'),
                leds: document.getElementById('left-lock-leds'),
                diagram: {
                    knowledge: document.getElementById('node-knowledge'),
                    circleKnowledge: document.getElementById('circle-knowledge'),
                    iconKnowledge: document.getElementById('icon-knowledge'),
                    possession: document.getElementById('node-possession'),
                    circlePossession: document.getElementById('circle-possession'),
                    iconPossessionRect: document.getElementById('icon-possession-rect'),
                    iconPossessionPath: document.getElementById('icon-possession-path'),
                    inherence: document.getElementById('node-inherence'),
                    circleInherence: document.getElementById('circle-inherence'),
                    iconInherence: document.getElementById('icon-inherence'),
                    shieldPath: document.getElementById('mfa-shield-path'),
                    shieldRing: document.getElementById('mfa-shield-ring'),
                    shieldIcon: document.getElementById('mfa-shield-icon'),
                    shieldStatus: document.getElementById('mfa-shield-status'),
                    flowLine1: document.getElementById('flow-line-1'),
                    flowLine2: document.getElementById('flow-line-2'),
                    flowLine3: document.getElementById('flow-line-3')
                }
            },
            right: {
                team: document.getElementById('right-team-name'),
                leaderName: document.getElementById('right-leader-name'),
                email: document.getElementById('right-leader-email'),
                phone: document.getElementById('right-phone'),
                github: document.getElementById('right-github'),
                exp: document.getElementById('right-exp'),
                btn: document.getElementById('btn-right-submit'),
                card: document.getElementById('panel-right'),
                lockBox: document.getElementById('right-lock-box'),
                lockIcon: document.getElementById('right-lock-icon'),
                leds: document.getElementById('right-lock-leds'),
                diagram: {
                    operator: document.getElementById('node-operator'),
                    rectOperator: document.getElementById('rect-operator'),
                    unit: document.getElementById('node-unit'),
                    rectUnit: document.getElementById('rect-unit'),
                    assigned: document.getElementById('node-assigned'),
                    rectAssigned: document.getElementById('rect-assigned'),
                    arrow: document.getElementById('access-granted-arrow'),
                    key: document.getElementById('dynamic-vector-key')
                }
            }
        };

        // Initialize keyclick sound effects on typing
        document.querySelectorAll('input').forEach(inp => {
            inp.addEventListener('input', () => {
                playKeyClick();
            });
        });

        // Setup Team Member list inputs
        function setupMemberSystem(side) {
            const input = document.getElementById(`${side}-member-input`);
            const addBtn = document.getElementById(`btn-${side}-add-member`);

            function addMember() {
                const name = input.value.trim();
                if (name.length >= 2) {
                    if (!teamMembers[side].includes(name)) {
                        teamMembers[side].push(name);
                        input.value = "";
                        playKeyClick();
                        playValidationSuccess();
                        renderMembers(side);
                    }
                }
            }

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    addMember();
                }
            });

            addBtn.addEventListener('click', (e) => {
                e.preventDefault();
                addMember();
            });

            renderMembers(side);
        }

        function renderMembers(side) {
            const list = document.getElementById(`${side}-members-list`);
            const count = document.getElementById(`${side}-members-count`);
            const activeGlow = side === 'left' ? 'border-red-500/40 bg-red-950/20 text-red-300 shadow-[0_0_8px_rgba(239,68,68,0.15)]' : 'border-teal-500/40 bg-teal-950/20 text-teal-300 shadow-[0_0_8px_rgba(20,184,166,0.15)]';
            const closeHover = side === 'left' ? 'hover:text-red-500' : 'hover:text-teal-400';

            list.innerHTML = "";
            if (teamMembers[side].length === 0) {
                list.innerHTML = `<span class="text-[10px] text-slate-600 font-mono italic p-1">No operational squad members registered yet...</span>`;
                count.textContent = "0 ADDED";
                count.className = "text-[9px] text-slate-500 font-bold";
            } else {
                count.textContent = `${teamMembers[side].length} ADDED`;
                count.className = `text-[9px] font-bold ${side === 'left' ? 'text-red-400' : 'text-teal-400'}`;
                teamMembers[side].forEach((name, index) => {
                    const badge = document.createElement('div');
                    badge.className = `flex items-center gap-1.5 px-2 py-0.5 border rounded text-[10px] font-mono tracking-wider transition-all duration-300 ${activeGlow}`;
                    badge.innerHTML = `
                        <span>${name.toUpperCase()}</span>
                        <button type="button" class="font-bold ml-1 transition-colors ${closeHover}" onclick="removeTeamMember('${side}', ${index})">✕</button>
                    `;
                    list.appendChild(badge);
                });
            }

            // Trigger forms validation on squad change
            validateFormIntegrity(side);
        }

        window.removeTeamMember = function (side, index) {
            teamMembers[side].splice(index, 1);
            playKeyClick();
            renderMembers(side);
        };

        // Real-time Validation handler
        function setupValidation(side) {
            const config = FORM_FIELDS[side];
            const activeColor = side === 'left' ? 'rgb(239, 68, 68)' : 'rgb(20, 184, 166)';

            function validateField(inputElement) {
                const label = inputElement.closest('.relative').querySelector('.val-status-txt');
                let isValid = false;

                if (inputElement.type === 'email') {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    isValid = emailRegex.test(inputElement.value);
                } else if (inputElement.type === 'tel') {
                    isValid = inputElement.value.trim().length >= 8;
                } else if (inputElement.type === 'url') {
                    try {
                        const url = new URL(inputElement.value);
                        isValid = url.protocol === "http:" || url.protocol === "https:";
                    } catch (_) {
                        isValid = inputElement.value.trim().length >= 5;
                    }
                } else {
                    isValid = inputElement.value.trim().length >= 3;
                }

                if (isValid) {
                    label.textContent = "VERIFIED";
                    label.className = `text-[9px] font-bold val-status-txt ${side === 'left' ? 'text-red-400' : 'text-teal-400'}`;
                    inputElement.style.borderColor = activeColor;
                } else {
                    label.textContent = inputElement.value.trim() === "" ? "PENDING" : "INVALID";
                    label.className = "text-[9px] text-slate-500 val-status-txt";
                    inputElement.style.borderColor = "";
                }

                validateFormIntegrity(side);
            }

            // Bind events
            config.team.addEventListener('input', () => validateField(config.team));
            config.leaderName.addEventListener('input', () => validateField(config.leaderName));
            config.email.addEventListener('input', () => validateField(config.email));
            config.phone.addEventListener('input', () => validateField(config.phone));
            config.github.addEventListener('input', () => validateField(config.github));
        }

        function validateFormIntegrity(side) {
            const config = FORM_FIELDS[side];
            const activeBg = side === 'left' ? 'bg-red-500' : 'bg-teal-500';
            const shadowClass = side === 'left' ? 'shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'shadow-[0_0_15px_rgba(20, 184, 166, 0.5)]';

            const isTeamValid = config.team.value.trim().length >= 3;
            const isLeaderValid = config.leaderName.value.trim().length >= 3;
            const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(config.email.value);
            const isPhoneValid = config.phone.value.trim().length >= 8;
            const isGithubValid = config.github.value.trim().length >= 5;

            // Operational squad validation (require at least 1 member added!)
            const isSquadValid = teamMembers[side].length >= 1;

            // DYNAMIC UPDATE OF THE DIAGRAMS BASED ON VALUES!
            if (side === 'left') {
                const dia = config.diagram;
                // Node 1: PASSWORD -> Leader Name valid
                if (isLeaderValid) {
                    dia.circleKnowledge.setAttribute('stroke', '#10b981');
                    dia.circleKnowledge.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
                    dia.iconKnowledge.setAttribute('stroke', '#10b981');
                    dia.circleKnowledge.classList.add('svg-glow-green');
                    dia.flowLine1.setAttribute('stroke', '#10b981');
                    dia.flowLine1.setAttribute('class', 'flow-line-active');
                } else {
                    dia.circleKnowledge.setAttribute('stroke', '#dc2626');
                    dia.circleKnowledge.setAttribute('fill', '#020617');
                    dia.iconKnowledge.setAttribute('stroke', '#ef4444');
                    dia.circleKnowledge.classList.remove('svg-glow-green');
                    dia.flowLine1.setAttribute('stroke', 'rgba(239, 68, 68, 0.25)');
                    dia.flowLine1.removeAttribute('class');
                }

                // Node 2: TELECOMM -> Phone Number valid
                if (isPhoneValid) {
                    dia.circlePossession.setAttribute('stroke', '#10b981');
                    dia.circlePossession.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
                    dia.iconPossessionRect.setAttribute('stroke', '#10b981');
                    dia.iconPossessionPath.setAttribute('stroke', '#10b981');
                    dia.circlePossession.classList.add('svg-glow-green');
                    dia.flowLine2.setAttribute('stroke', '#10b981');
                    dia.flowLine2.setAttribute('class', 'flow-line-active');
                } else {
                    dia.circlePossession.setAttribute('stroke', '#dc2626');
                    dia.circlePossession.setAttribute('fill', '#020617');
                    dia.iconPossessionRect.setAttribute('stroke', '#ef4444');
                    dia.iconPossessionPath.setAttribute('stroke', '#ef4444');
                    dia.circlePossession.classList.remove('svg-glow-green');
                    dia.flowLine2.setAttribute('stroke', 'rgba(239, 68, 68, 0.25)');
                    dia.flowLine2.removeAttribute('class');
                }

                // Node 3: SQUAD MEM -> Squad Valid
                if (isSquadValid) {
                    dia.circleInherence.setAttribute('stroke', '#10b981');
                    dia.circleInherence.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
                    dia.iconInherence.setAttribute('stroke', '#10b981');
                    dia.circleInherence.classList.add('svg-glow-green');
                    dia.flowLine3.setAttribute('stroke', '#10b981');
                    dia.flowLine3.setAttribute('class', 'flow-line-active');
                } else {
                    dia.circleInherence.setAttribute('stroke', '#dc2626');
                    dia.circleInherence.setAttribute('fill', '#020617');
                    dia.iconInherence.setAttribute('stroke', '#ef4444');
                    dia.circleInherence.classList.remove('svg-glow-green');
                    dia.flowLine3.setAttribute('stroke', 'rgba(239, 68, 68, 0.25)');
                    dia.flowLine3.removeAttribute('class');
                }

                // Shield Status
                const allVerified = isTeamValid && isLeaderValid && isEmailValid && isPhoneValid && isGithubValid && isSquadValid;
                const mfaArrow = document.getElementById('mfa-granted-arrow');
                if (allVerified) {
                    dia.shieldPath.setAttribute('stroke', '#10b981');
                    dia.shieldPath.setAttribute('fill', 'rgba(16, 185, 129, 0.12)');
                    dia.shieldRing.setAttribute('stroke', '#10b981');
                    dia.shieldRing.classList.add('svg-glow-green');
                    dia.shieldIcon.setAttribute('stroke', '#10b981');
                    if (mfaArrow) mfaArrow.setAttribute('class', 'opacity-100 transition-all duration-500 svg-glow-green');
                    dia.shieldStatus.textContent = "GRANTED";
                    dia.shieldStatus.setAttribute('fill', '#10b981');
                } else {
                    dia.shieldPath.setAttribute('stroke', '#dc2626');
                    dia.shieldPath.setAttribute('fill', 'rgba(220, 38, 38, 0.08)');
                    dia.shieldRing.setAttribute('stroke', '#dc2626');
                    dia.shieldRing.classList.remove('svg-glow-green');
                    dia.shieldIcon.setAttribute('stroke', '#dc2626');
                    if (mfaArrow) mfaArrow.setAttribute('class', 'opacity-0 transition-all duration-500');
                    dia.shieldStatus.textContent = "RESTRICTED";
                    dia.shieldStatus.setAttribute('fill', '#ef4444');
                }
            } else if (side === 'right') {
                const dia = config.diagram;
                // Operator ID -> Team Name valid
                if (isTeamValid) {
                    dia.rectOperator.setAttribute('stroke', '#10b981');
                    dia.rectOperator.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
                    dia.operator.querySelector('text').setAttribute('fill', '#10b981');
                } else {
                    dia.rectOperator.setAttribute('stroke', 'rgba(20, 184, 166, 0.4)');
                    dia.rectOperator.setAttribute('fill', '#020617');
                    dia.operator.querySelector('text').setAttribute('fill', '#94a3b8');
                }

                // Unit ID -> Email valid
                if (isEmailValid) {
                    dia.rectUnit.setAttribute('stroke', '#10b981');
                    dia.rectUnit.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
                    dia.unit.querySelector('text').setAttribute('fill', '#10b981');
                } else {
                    dia.rectUnit.setAttribute('stroke', 'rgba(20, 184, 166, 0.4)');
                    dia.rectUnit.setAttribute('fill', '#020617');
                    dia.unit.querySelector('text').setAttribute('fill', '#94a3b8');
                }

                // Assigned Objectives -> GitHub valid
                if (isGithubValid) {
                    dia.rectAssigned.setAttribute('stroke', '#10b981');
                    dia.rectAssigned.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
                    dia.assigned.querySelector('text').setAttribute('fill', '#10b981');
                } else {
                    dia.rectAssigned.setAttribute('stroke', 'rgba(20, 184, 166, 0.4)');
                    dia.rectAssigned.setAttribute('fill', '#020617');
                    dia.assigned.querySelector('text').setAttribute('fill', '#94a3b8');
                }

                // Thread Node Status -> Squad Valid
                const threadNode = document.getElementById('rect-thread-node');
                const threadNodeText = document.querySelector('#node-thread-node-panel text');
                const threadLeds = document.querySelectorAll('.thread-node-led');
                if (isSquadValid) {
                    if (threadNode) {
                        threadNode.setAttribute('stroke', '#10b981');
                        threadNode.setAttribute('fill', 'rgba(16, 185, 129, 0.08)');
                    }
                    if (threadNodeText) threadNodeText.setAttribute('fill', '#10b981');
                    threadLeds.forEach(led => {
                        led.setAttribute('fill', '#10b981');
                        led.setAttribute('class', 'thread-node-led svg-glow-green');
                    });
                } else {
                    if (threadNode) {
                        threadNode.setAttribute('stroke', 'rgba(20, 184, 166, 0.4)');
                        threadNode.setAttribute('fill', '#020617');
                    }
                    if (threadNodeText) threadNodeText.setAttribute('fill', '#94a3b8');
                    threadLeds.forEach(led => {
                        led.setAttribute('fill', '#ef4444');
                        led.setAttribute('class', 'thread-node-led');
                    });
                }

                // Key sliding & access granted
                const allVerified = isTeamValid && isLeaderValid && isEmailValid && isPhoneValid && isGithubValid && isSquadValid;
                if (allVerified) {
                    dia.key.setAttribute('transform', 'translate(0, 71)');
                    dia.key.setAttribute('class', 'transition-all duration-700 opacity-100 svg-glow-green');
                    dia.key.querySelector('path').setAttribute('stroke', '#10b981');
                    dia.arrow.setAttribute('class', 'opacity-100 transition-all duration-500 svg-glow-green');
                } else {
                    dia.key.setAttribute('transform', 'translate(0, -15)');
                    dia.key.setAttribute('class', 'transition-all duration-700 opacity-60');
                    dia.key.querySelector('path').setAttribute('stroke', '#14b8a6');
                    dia.arrow.setAttribute('class', 'opacity-30 transition-all duration-500');
                }
            }

            const totalValid = (isTeamValid ? 1 : 0) + (isLeaderValid ? 1 : 0) + (isEmailValid ? 1 : 0) + (isPhoneValid ? 1 : 0) + (isGithubValid ? 1 : 0) + (isSquadValid ? 1 : 0);
            
            // Update the bottom Lock Status LEDs
            const ledElements = config.leds.children;
            if (totalValid === 0) {
                ledElements[0].className = `w-2.5 h-2.5 rounded-full ${activeBg}`;
                ledElements[1].className = `w-2.5 h-2.5 rounded-full bg-slate-800`;
                ledElements[2].className = `w-2.5 h-2.5 rounded-full bg-slate-800`;
            } else if (totalValid < 6) {
                ledElements[0].className = `w-2.5 h-2.5 rounded-full bg-yellow-500`;
                ledElements[1].className = `w-2.5 h-2.5 rounded-full bg-yellow-500`;
                ledElements[2].className = `w-2.5 h-2.5 rounded-full bg-slate-800`;
            } else {
                // Fully valid! Unlock!
                ledElements[0].className = `w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]`;
                ledElements[1].className = `w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]`;
                ledElements[2].className = `w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]`;
            }

            // If fully valid, unlock lock indicator
            if (totalValid === 6) {
                config.lockBox.className = `p-2 bg-emerald-950/40 rounded-full border border-emerald-500/40 text-emerald-400 ${shadowClass}`;
                config.lockIcon.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
                    </svg>
                `;
            } else {
                config.lockBox.className = `p-2 bg-${side}-950/30 rounded-full border border-${side}-500/20 text-${side}-500`;
                config.lockIcon.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                `;
            }
        }

        // Initialize validators & Member arrays
        setupValidation('left');
        setupValidation('right');
        setupMemberSystem('left');
        setupMemberSystem('right');
    </script>

    <!-- FULLSCREEN TERMINAL SUBMISSION LOGIC -->
    <script>
        const overlay = document.getElementById('terminal-overlay');
        const logsContainer = document.getElementById('terminal-logs');
        const percentText = document.getElementById('terminal-percentage');
        const progressIndicator = document.getElementById('terminal-status-indicator');
        const statusText = document.getElementById('terminal-status-text');
        const successScreen = document.getElementById('success-screen');
        const terminalBox = document.getElementById('terminal-box');

        // Submit action trigger
        function triggerRegistration(side) {
            const config = FORM_FIELDS[side];
            
            // Check form validity
            const isTeamValid = config.team.value.trim().length >= 3;
            const isLeaderValid = config.leaderName.value.trim().length >= 3;
            const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(config.email.value);
            const isPhoneValid = config.phone.value.trim().length >= 8;
            const isGithubValid = config.github.value.trim().length >= 5;
            const isSquadValid = teamMembers[side].length >= 1;

            if (!isTeamValid || !isLeaderValid || !isEmailValid || !isPhoneValid || !isGithubValid || !isSquadValid) {
                // SHAKE CARD IF FORM INVALID
                playAlarmError();
                config.card.classList.add('shake-card');
                setTimeout(() => {
                    config.card.classList.remove('shake-card');
                }, 600);
                return;
            }

            // Open Audio Context if first interaction
            getAudioContext();

            // Clear old terminal logs and show terminal modal
            logsContainer.innerHTML = `<div class="text-slate-500 font-bold border-b border-slate-900 pb-2 mb-2">// SECURITY ACCESS PORT INITIALIZED</div>`;
            overlay.className = "fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-all opacity-100 duration-500";
            successScreen.style.opacity = "0";
            successScreen.style.pointerEvents = "none";

            // Set terminal border highlight to match side color
            if (side === 'left') {
                terminalBox.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                terminalBox.style.boxShadow = '0 0 30px rgba(239, 68, 68, 0.15)';
                progressIndicator.className = 'w-2.5 h-2.5 bg-red-500 animate-pulse inline-block';
            } else {
                terminalBox.style.borderColor = 'rgba(20, 184, 166, 0.4)';
                terminalBox.style.boxShadow = '0 0 30px rgba(20, 184, 166, 0.15)';
                progressIndicator.className = 'w-2.5 h-2.5 bg-teal-500 animate-pulse inline-block';
            }

            const membersListStr = teamMembers[side].join(', ').toUpperCase();

            // Prepare AJAX Data Payload
            const formData = new FormData();
            formData.append('reg_type', side === 'left' ? 'mfa' : 'thread');
            formData.append('team_name', config.team.value);
            formData.append('leader_name', config.leaderName.value);
            formData.append('leader_email', config.email.value);
            formData.append('phone_number', config.phone.value);
            formData.append('github_link', config.github.value);
            formData.append('experience_level', config.exp.value);
            formData.append('track_selection', document.getElementById(side + '-track').value);
            formData.append('team_members', JSON.stringify(teamMembers[side]));

            // Simulated terminal sequence lines
            const logQueue = [
                { text: `>> INITIALIZING ENCRYPTED CONNECTION PACKET...`, error: false },
                { text: `>> SECURING HANDSHAKE WITH REMOTE GATEWAY NODE... [OK]`, error: false },
                { text: `>> INJECTING AUTH SYSTEM ENVIRONMENT TELEMETRY...`, error: false },
                { text: `>> VERIFYING IDENTITIES:`, error: false },
                { text: `   - TEAM IDENTIFICATION LABEL: "${config.team.value.toUpperCase()}"`, error: false },
                { text: `   - LEADER OPERATIVE PROFILES: "${config.leaderName.value.toUpperCase()}"`, error: false },
                { text: `   - SECURE DEPLOYMENT EMAIL HASH: "${config.email.value.toUpperCase()}"`, error: false },
                { text: `   - SECURE PORT COMMS TELEMETRY: "${config.phone.value.toUpperCase()}"`, error: false },
                { text: `   - GITHUB/PORTFOLIO SIGNED LINK: "${config.github.value.toUpperCase()}"`, error: false },
                { text: `   - EXPERATIVE DEV LEVEL STATUS: "${config.exp.value}"`, error: false },
                { text: `   - REGISTERED SQUAD MEMBERS: [${membersListStr}]`, error: false }
            ];

            let activeLineIndex = 0;
            let totalSteps = 20;

            function printNextSimulatedLine() {
                if (activeLineIndex < logQueue.length) {
                    const line = logQueue[activeLineIndex];
                    const lineDiv = document.createElement('div');
                    lineDiv.className = line.error ? 'leading-relaxed cursor-blink text-red-500 font-bold' : 'leading-relaxed cursor-blink';
                    lineDiv.textContent = line.text;
                    logsContainer.appendChild(lineDiv);
                    
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                    playKeyClick();

                    activeLineIndex++;
                    const percent = Math.floor((activeLineIndex / totalSteps) * 100);
                    percentText.textContent = `${percent}%`;
                    
                    if (percent < 35) statusText.textContent = "DECOMPRESSING SESSION SECTOR KEY...";
                    else statusText.textContent = "PREPARING LOCAL API NODE HANDSHAKE...";

                    setTimeout(printNextSimulatedLine, 100 + Math.random() * 60);
                } else {
                    // Simulated client logs are done! Now fetch from PHP endpoint
                    statusText.textContent = "TRANSMITTING DATA PACKETS TO DATABASE ENGINE...";
                    
                    fetch('register.php', {
                        method: 'POST',
                        body: formData
                    })
                    .then(res => res.json())
                    .then(data => {
                        // Gather backend database logs from API response
                        const dbLogs = data.db_logs || [];
                        let dbIndex = 0;
                        totalSteps = logQueue.length + dbLogs.length + 1;

                        function printDatabaseLine() {
                            if (dbIndex < dbLogs.length) {
                                const lineText = dbLogs[dbIndex];
                                const lineDiv = document.createElement('div');
                                lineDiv.className = 'leading-relaxed cursor-blink text-cyan-400 font-bold';
                                lineDiv.textContent = lineText;
                                logsContainer.appendChild(lineDiv);
                                
                                logsContainer.scrollTop = logsContainer.scrollHeight;
                                playKeyClick();

                                dbIndex++;
                                const currentStep = logQueue.length + dbIndex;
                                const percent = Math.floor((currentStep / totalSteps) * 100);
                                percentText.textContent = `${percent}%`;

                                if (percent < 75) statusText.textContent = "CONNECTING DATABASE ENGINE...";
                                else statusText.textContent = "COMMITTING DATA TRANSACTION MATRIX...";

                                setTimeout(printDatabaseLine, 120 + Math.random() * 60);
                            } else {
                                // Database logs finished!
                                percentText.textContent = '100%';
                                statusText.textContent = "NODE COMPILATION STRETCH VERIFIED.";
                                
                                if (data.success) {
                                    // Success outcome!
                                    setTimeout(() => {
                                        // Update success message label with row ID
                                        const successTitle = successScreen.querySelector('h3');
                                        const successDesc = successScreen.querySelector('p');
                                        if (successTitle) successTitle.textContent = `REGISTRATION SECURED: ROW #${data.row_id}`;
                                        if (successDesc) successDesc.textContent = `DECENTRALIZED NODE INJECTED TO DB REGISTER SUCCESSFULLY`;
                                        
                                        playValidationSuccess();
                                        successScreen.style.opacity = "1";
                                        successScreen.style.pointerEvents = "auto";
                                    }, 400);
                                } else {
                                    // DB transaction rejected!
                                    handleRegistrationError(data.message || "DATABASE INJECTION PROTOCOL DECLINED.");
                                }
                            }
                        }

                        // Begin printing server database logs!
                        printDatabaseLine();
                    })
                    .catch(err => {
                        handleRegistrationError("CORE CONNECTION FAILURE: REMOTE ENDPOINT UNREACHABLE.");
                    });
                }
            }

            function handleRegistrationError(errMessage) {
                playAlarmError();
                const errDiv = document.createElement('div');
                errDiv.className = 'leading-relaxed cursor-blink text-red-500 font-bold border-t border-red-950 mt-2 pt-2';
                errDiv.textContent = `>> [ERR] INTERACTION HALTED: ${errMessage.toUpperCase()}`;
                logsContainer.appendChild(errDiv);
                
                logsContainer.scrollTop = logsContainer.scrollHeight;
                statusText.textContent = "TRANSACTION SHIELD TIMEOUT // ACCESS DENIED.";
                percentText.textContent = "ERR";
                
                // Add close button dynamically inside logs for errors
                const closeErrBtn = document.createElement('button');
                closeErrBtn.className = "mt-4 px-4 py-1.5 bg-red-950/40 hover:bg-red-500 text-red-400 hover:text-slate-950 border border-red-500/50 font-cyber text-[10px] font-bold uppercase rounded transition-all w-full select-none";
                closeErrBtn.textContent = "DISMISS CONNECTION GATEWAY EXCEPTION";
                closeErrBtn.addEventListener('click', () => {
                    overlay.className = "fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-all opacity-0 pointer-events-none duration-500";
                });
                logsContainer.appendChild(closeErrBtn);
            }

            // Start simulated terminal loop!
            printNextSimulatedLine();
        }

        // Bind clicks to buttons
        FORM_FIELDS.left.btn.addEventListener('click', () => triggerRegistration('left'));
        FORM_FIELDS.right.btn.addEventListener('click', () => triggerRegistration('right'));

        // Bind modal dismiss button
        document.getElementById('btn-close-terminal').addEventListener('click', () => {
            overlay.className = "fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-all opacity-0 pointer-events-none duration-500";
            // Clear inputs inside both forms as a sign of successful submission reset
            FORM_FIELDS.left.team.value = "";
            FORM_FIELDS.left.leaderName.value = "";
            FORM_FIELDS.left.email.value = "";
            FORM_FIELDS.left.phone.value = "";
            FORM_FIELDS.left.github.value = "";
            FORM_FIELDS.right.team.value = "";
            FORM_FIELDS.right.leaderName.value = "";
            FORM_FIELDS.right.email.value = "";
            FORM_FIELDS.right.phone.value = "";
            FORM_FIELDS.right.github.value = "";

            // Reset dynamic member lists
            teamMembers.left = [];
            teamMembers.right = [];
            renderMembers('left');
            renderMembers('right');

            // Re-trigger visual validations to reset state back to defaults
            document.querySelectorAll('.val-status-txt').forEach(lbl => {
                lbl.textContent = "PENDING";
                lbl.className = "text-[9px] text-slate-500 val-status-txt";
            });
            document.querySelectorAll('.cyber-input').forEach(inp => inp.style.borderColor = "");
            
            // Trigger check to turn off lock status LEDs
            const setupLeds = (side) => {
                const config = FORM_FIELDS[side];
                const activeBg = side === 'left' ? 'bg-red-500' : 'bg-teal-500';
                config.leds.children[0].className = `w-2.5 h-2.5 rounded-full ${activeBg}`;
                config.leds.children[1].className = `w-2.5 h-2.5 rounded-full bg-slate-800`;
                config.leds.children[2].className = `w-2.5 h-2.5 rounded-full bg-slate-800`;
                config.lockBox.className = `p-2 bg-${side}-950/30 rounded-full border border-${side}-500/20 text-${side}-500`;
                config.lockIcon.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                `;
            };
            setupLeds('left');
            setupLeds('right');
        });

        // ==========================================
        // FUTURISTIC BOOT PRELOADER LOGIC
        // ==========================================
        window.addEventListener('DOMContentLoaded', () => {
            const preloader = document.getElementById('preloader');
            const progressBar = document.getElementById('preload-progress-bar');
            const percentText = document.getElementById('preload-percentage');
            const statusLabel = document.getElementById('preload-status');

            const statusStages = [
                { limit: 20, text: "INITIALIZING ZERO-TRUST PORT NODES..." },
                { limit: 40, text: "ENGAGING SECURE RSA-4096 NETWORK CHANNELS..." },
                { limit: 60, text: "COMPILING DASHBOARD TELEMETRY GRIDS..." },
                { limit: 80, text: "SYNCING OFFENSIVE & DEFENSIVE OPERATIVES..." },
                { limit: 99, text: "DECRYPTING NODE INTERFACE AND ASSETS..." },
                { limit: 100, text: "ACCESS GRANTED // BOOT STRAP SUCCESSFUL." }
            ];

            let progress = 0;
            const duration = 2400; // total duration of boot in ms
            const intervalTime = 25; // tick interval in ms
            const step = 100 / (duration / intervalTime);

            function playStartupChime() {
                try {
                    // C Major rising high-tech arpeggio (synthesized with Web Audio API)
                    const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50];
                    notes.forEach((freq, idx) => {
                        setTimeout(() => {
                            playSynthBeep(freq, 'sine', 0.55, 0.03);
                        }, idx * 80);
                    });

                    // Sub-bass frequency swell for ultimate power boom feel
                    setTimeout(() => {
                        playSynthBeep(130.81, 'triangle', 0.9, 0.07);
                    }, 120);
                } catch (e) {}
            }

            const timer = setInterval(() => {
                progress += step + (Math.random() - 0.2) * 1.5; // organic random jitter
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(timer);
                    
                    progressBar.style.width = '100%';
                    percentText.textContent = '100%';
                    statusLabel.textContent = statusStages[statusStages.length - 1].text;

                    // Play startup synth chime and unlock overlay!
                    setTimeout(() => {
                        playStartupChime();
                        preloader.classList.add('opacity-0', 'pointer-events-none');
                        setTimeout(() => {
                            preloader.style.display = 'none';
                        }, 700);
                    }, 400);
                } else {
                    const roundedProgress = Math.floor(progress);
                    progressBar.style.width = `${roundedProgress}%`;
                    percentText.textContent = `${roundedProgress}%`;

                    // Update status label text based on current percentage range
                    const stage = statusStages.find(s => roundedProgress <= s.limit) || statusStages[statusStages.length - 1];
                    statusLabel.textContent = stage.text;

                    // Play random micro beep click audio for data sync noise
                    if (Math.random() < 0.15) {
                        playSynthBeep(1800 + Math.random() * 800, 'sine', 0.02, 0.005);
                    }
                }
            }, intervalTime);
        });
    </script>
</body>

</html>