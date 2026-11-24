/**
 * chat.js - Frontend client with Version Switching Dropdown, Quick Test Chips, Web Speech API & Debug Drawer
 */

document.addEventListener("DOMContentLoaded", () => {
    const chatWindow = document.getElementById("chatWindow");
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const resetBtn = document.getElementById("resetBtn");
    const micBtn = document.getElementById("micBtn");
    const debugToggle = document.getElementById("debugToggle");
    const versionSelect = document.getElementById("versionSelect");
    const versionBadge = document.getElementById("versionBadge");
    const versionDesc = document.getElementById("versionDesc");
    const chipList = document.getElementById("chipList");

    // Version definitions with description and realistic quick-test questions
    const versionConfig = {
        v1: {
            badge: "V1: RULE-BASED MONOLITH",
            desc: "<strong>V1 Deterministic Rule Matcher:</strong> Hardcoded regex with no NLU or state. Notice how slight phrasing variations or abbreviations fail.",
            chips: [
                { label: "When is Rahul Patil's birthday?", type: "pass" },
                { label: "birthday of Rahul (Fails in V1)", type: "fail", text: "birthday of Rahul" },
                { label: "nephew birthdays in sept (Fails)", type: "fail", text: "nephew birthdays in sept" },
                { label: "birthdays this week (Fails)", type: "fail", text: "birthdays this week" },
                { label: "What are the upcoming birthdays?", type: "pass" },
                { label: "How many birthdays are there next month?", type: "pass" }
            ]
        },
        v2: {
            badge: "V2: NLU + SERVICE",
            desc: "<strong>V2 Modular NLU & Service:</strong> Extracts {intent, entities} and executes queries, but is <em>stateless</em> (cannot carry over context).",
            chips: [
                { label: "Count nephew birthdays in September", type: "pass" },
                { label: "Where does Rahul Patil stay?", type: "pass" },
                { label: "Show birthdays next month", type: "pass" },
                { label: "Step 1: Any nephew birthdays in September?", type: "pass" },
                { label: "Step 2: What about October? (Loses context in V2)", type: "fail", text: "What about October?" }
            ]
        },
        v3: {
            badge: "V3: DIALOGUE STATE & CLARIFICATION",
            desc: "<strong>V3 Dialogue State & Clarification:</strong> Carries over omitted slots across turns and asks for disambiguation when multiple people match.",
            chips: [
                { label: "Step 1: Any nephew birthdays in September?", type: "pass" },
                { label: "Step 2: What about October? (Carries 'nephew')", type: "pass", text: "What about October?" },
                { label: "Ambiguity Test: When is my nephew's birthday?", type: "pass", text: "When is my nephew's birthday?" },
                { label: "Resolve Ambiguity: Nikhil", type: "pass", text: "Nikhil" }
            ]
        },
        v4: {
            badge: "V4: GROUNDED LLM NLU",
            desc: "<strong>V4 Grounded LLM Layer:</strong> Uses LLM as NLU with strict JSON schema validation and offline rules fallback. Facts are strictly retrieved from Excel.",
            chips: [
                { label: "When is Rahul Patil's birthday?", type: "pass" },
                { label: "Hallucination Test: When is Einstein's birthday?", type: "pass", text: "When is Einstein's birthday?" },
                { label: "Who is my nephew?", type: "pass" },
                { label: "Garbage test: asdfgh", type: "pass", text: "asdfgh" }
            ]
        },
        v5: {
            badge: "V5: MULTIMODAL VOICE",
            desc: "<strong>V5 Full Multimodal Voice:</strong> Hands-free Speech-to-Text (Mic) and Text-to-Speech (TTS) backed by the grounded V4 architecture.",
            chips: [
                { label: "Click Mic & speak: 'Is there any birthday tomorrow?'", type: "pass", text: "Is there any birthday tomorrow?" },
                { label: "What are the upcoming birthdays?", type: "pass" },
                { label: "Where does Rahul Patil stay?", type: "pass" },
                { label: "When is Einstein's birthday?", type: "pass" }
            ]
        }
    };

    function updateVersionUI(ver) {
        const config = versionConfig[ver] || versionConfig.v5;
        versionBadge.textContent = config.badge;
        versionDesc.innerHTML = config.desc;

        // Render chips
        chipList.innerHTML = "";
        config.chips.forEach(chip => {
            const span = document.createElement("span");
            span.className = `chip ${chip.type === 'fail' ? 'fail' : ''}`;
            span.textContent = chip.label;
            span.title = `Run: "${chip.text || chip.label}"`;
            span.addEventListener("click", () => {
                const queryText = chip.text || chip.label;
                userInput.value = queryText;
                submitMessage(queryText);
            });
            chipList.appendChild(span);
        });
    }

    // Version dropdown listener
    versionSelect.addEventListener("change", (e) => {
        const ver = e.target.value;
        updateVersionUI(ver);
        appendMessage("bot", `[System] Switched to ${versionConfig[ver].badge}. Try the quick test buttons above.`);
    });

    // Initialize UI with default version (v5)
    updateVersionUI(versionSelect.value);

    // Speech Recognition setup (Web Speech API)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isRecording = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-IN"; // Configured for Indian English accents

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add("recording");
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            submitMessage(transcript);
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };
    } else {
        micBtn.style.display = "none";
        console.warn("Web Speech API recognition not supported in this browser.");
    }

    function startRecording() {
        if (recognition && !isRecording) {
            try {
                recognition.start();
            } catch (err) {
                console.error("Failed to start speech recognition:", err);
            }
        }
    }

    function stopRecording() {
        isRecording = false;
        micBtn.classList.remove("recording");
    }

    micBtn.addEventListener("click", () => {
        if (isRecording) {
            recognition.stop();
        } else {
            startRecording();
        }
    });

    // Text-to-Speech (speechSynthesis)
    function speakText(text) {
        // If in V5, speak response aloud
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
            const cleanText = text.replace(/[\n\r]+/g, ". ").replace(/[*_#]/g, "");
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.lang = "en-IN";
            window.speechSynthesis.speak(utterance);
        }
    }

    // Debug toggle
    debugToggle.addEventListener("change", (e) => {
        if (e.target.checked) {
            document.body.classList.add("show-debug");
        } else {
            document.body.classList.remove("show-debug");
        }
    });

    // Append Message to UI
    function appendMessage(sender, text, debugInfo = null) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}-message`;

        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        contentDiv.textContent = text;
        msgDiv.appendChild(contentDiv);

        if (debugInfo && Object.keys(debugInfo).length > 0) {
            const debugDiv = document.createElement("div");
            debugDiv.className = "debug-card";
            debugDiv.textContent = JSON.stringify(debugInfo, null, 2);
            msgDiv.appendChild(debugDiv);
        }

        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Submit message handler
    async function submitMessage(messageText) {
        const text = messageText.trim();
        if (!text) return;

        const currentVersion = versionSelect.value;
        appendMessage("user", text);
        userInput.value = "";

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, version: currentVersion })
            });

            const data = await res.json();
            appendMessage("bot", data.reply, data.debug);
            
            // In V5, vocalize reply via Web Speech TTS
            if (currentVersion === "v5") {
                speakText(data.reply);
            }
        } catch (err) {
            console.error("Chat error:", err);
            appendMessage("bot", "Network error connecting to backend service.");
        }
    }

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        submitMessage(userInput.value);
    });

    // Reset conversation session
    resetBtn.addEventListener("click", async () => {
        try {
            const res = await fetch("/reset", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });
            const data = await res.json();
            appendMessage("bot", data.reply);
            if (versionSelect.value === "v5") {
                speakText(data.reply);
            }
        } catch (err) {
            console.error("Reset error:", err);
        }
    });
});
