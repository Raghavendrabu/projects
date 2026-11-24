# 🎓 Project Presentation Guide: How It Works (Simple Version)

Use this guide to understand exactly how your code works and how to explain it to your professor ("Sir") in a simple, impressive way.

---

## 1. The Big Picture (How it runs)
When Sir asks: **"How does this app run?"**
> **Your Answer:** 
> *"Sir, this is a **100% client-side web application** built with Vanilla JavaScript, HTML5, and CSS3. It does not require any backend server, compiler installation, or database. Everything—from parsing the C code to drawing the graphs—runs instantly in the browser using a custom parsing engine and the Vis.js library."*

---

## 2. The Code Architecture (What each file does)
If Sir asks: **"Show me your files. What did you write in each script?"**

Here is the simple explanation of your files:

### 📁 1. `index.html` & `style.css` (The UI/Layout)
* **What it does:** Creates the interactive workspace layout. 
* **Key feature:** A glassmorphic dark-mode interface with a split-screen. The left has the C code editor and options, and the right has tabs for Token tables and Graph canvases.

### ⚙️ 2. `parser.js` (The Compiler Brain)
* **What it does:** Reads the raw C text and understands its structure. It does this in two steps:
  1. **Lexical Analysis (Tokenizing):** Uses regular expressions (regex) to break the C code into basic units called "tokens" (like keywords, variables, numbers, operators).
  2. **Syntax Analysis (Parsing):** Uses a **Recursive Descent Parser** (a classic compiler parsing method) to check if the tokens follow C grammar rules and group them into a nested JavaScript tree structure (the AST).

### 📐 3. `graph-builder.js` (The Graph Generator)
* **What it does:** Takes the abstract tree from `parser.js` and builds nodes and arrows.
* **Key feature:** It contains the logic to convert:
  * Nested nodes into an **AST tree structure**.
  * Sequential instructions and branching (loops/if-statements) into **CFG blocks**.
  * Variable usage (where they are created vs. where they are read) into **DFG data streams**.
  * Merges them all together for the **CPG graph**.

### 🕸️ 4. `visualizer.js` (The Visual Coordinator)
* **What it does:** Links the code editor, the parser, and the graph drawing.
* **Key feature:** Whenever you click the "Analyze & Visualize" button or switch tabs, it clears the canvas, runs the parser, gets the nodes/edges, and uses **Vis.js** (a graph drawing library) with simulated physics to display them.

### 📚 5. `theory.js` (The Knowledge Base)
* **What it does:** Stores the descriptions, connection to Automata Theory, and AI Assistant notes that appear at the bottom of the screens to make the app educational.

---

## 3. The 5 Visualization Tabs Explained Simply

Explain each tab in one simple sentence:

| Tab | What It Shows | Simple Analogy |
| :--- | :--- | :--- |
| **1. Lexical Tokens** | A table of categorized code elements (e.g. `int` is a keyword, `x` is an identifier). | Like separating an English sentence into words and labeling them as nouns, verbs, and adjectives. |
| **2. AST (Syntax Tree)** | The parent-child grammatical hierarchy of the code. | Like a family tree showing how parts of a sentence belong to one another, ignoring commas and semicolons. |
| **3. CFG (Control Flow)** | The pathways of execution (branches, loops, jumps). | Like a roadmap or GPS navigation showing the route, detours (if-else), and destination. |
| **4. DFG (Data Flow)** | How values move from where variables are set to where they are used. | Like water pipes tracking how water flows from the water station (variable creation) to household taps (variable usage). |
| **5. CPG (Property Graph)** | A combined view merging AST structure, CFG roads, and DFG water pipes. | Like overlaying a map of water pipes and roads onto a city's structural blueprint. |

---

## 4. The 3-Minute Presentation Script (Say this to Sir)

Follow these steps when you demo:

### ⏱️ Minute 1: The Intro & Lexical
* **Action:** Open the app, select **Simple Assignment & Math**, click **Analyze & Visualize**.
* **What to say:** 
  > *"Good morning Sir. My project is a C Program Structural Visualizer. The main goal is to visually demonstrate how compilers dissect code. 
  > 
  > Right now, we are in the Lexical Analysis stage. The raw C code has been broken down into color-coded tokens. If I click on any row in the table, it highlights the corresponding line in the editor, proving the connection between characters and syntax units."*

### ⏱️ Minute 2: AST & CFG
* **Action:** Click the **AST** tab, drag a node. Then switch to **If-Else Branching**, click **Analyze & Visualize**, and click the **CFG** tab.
* **What to say:** 
  > *"Next, the parser builds the Abstract Syntax Tree (AST) showing grammatical hierarchy. 
  > 
  > When I switch to the Control Flow Graph (CFG) for the if-else code, we see the execution branches. The blue diamond node represents the conditional test `x > 10`. It forks into True and False branches and merges back at the return node. This maps execution flow."*

### ⏱️ Minute 3: DFG, CPG, and Security
* **Action:** Switch to **Factorial Function**, click **Analyze & Visualize**, go to **CPG**, and toggle the checkboxes.
* **What to say:** 
  > *"The Data Flow Graph (DFG) tracks how variables flow. Finally, the Code Property Graph (CPG) integrates AST, CFG (solid green arrows), and DFG (dashed orange lines). 
  > 
  > I can toggle these layers. This unified CPG is the industry standard for modern security analyzers because it allows us to track if an unsafe user input reaches a sensitive function without sanitization. 
  > 
  > This is my project, Sir. I am ready for any questions you might have."*
