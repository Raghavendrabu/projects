// theory.js - Educational theory content and student report templates

const THEORY_CONTENT = {
    title: "Theoretical Background & Report Guide",
    introduction: `
        This guide provides a comprehensive summary of the five key structural representations of code, 
        their foundations in Automata Theory, and their applications in modern AI Coding Assistants (like Gemini, Claude, and Copilot). 
        You can use this text as a reference for writing your handwritten report!
    `,
    sections: [
        {
            id: "lexical",
            title: "1. Tokenization / Lexical Analysis",
            content: `
                <p><strong>Definition:</strong> Lexical analysis is the first phase of compilation. It reads the source code characters sequentially and groups them into meaningful sequences called <strong>lexemes</strong>, which are then categorized into <strong>tokens</strong> (e.g., Keywords, Identifiers, Operators, Literals, Punctuation).</p>
                <p><strong>Compiler Role:</strong> Strips out comments and white space, assigning lexical values to identifiers and tracking source positions (line/column) for compiler error messaging.</p>
                <div class="theory-callout">
                    <h4>Automata Theory Connection:</h4>
                    <p>Tokenization is governed by <strong>Regular Expressions (REs)</strong>. The lexer uses REs to describe patterns of tokens (like a digit pattern for numbers or alphabetical pattern for identifiers). These REs are compiled into <strong>Finite Automata</strong> (specifically, Deterministic Finite Automata, or <strong>DFAs</strong>) that process characters with $O(N)$ efficiency, transitioning between states as characters are read.</p>
                </div>
            `
        },
        {
            id: "ast",
            title: "2. Abstract Syntax Tree (AST)",
            content: `
                <p><strong>Definition:</strong> An Abstract Syntax Tree is a hierarchical tree representation of the abstract syntactic structure of source code. Unlike a Parse Tree (concrete syntax tree), it hides grammar details like parentheses, semicolons, and commas, focusing entirely on structural nodes (like loops, operations, declarations, and scope blocks).</p>
                <p><strong>Compiler Role:</strong> The AST represents the semantic nesting of statements. Code verification, type checking, and optimization passes (like constant folding) are conducted directly on the AST.</p>
                <div class="theory-callout">
                    <h4>Automata Theory Connection:</h4>
                    <p>Programming language syntaxes are defined using <strong>Context-Free Grammars (CFGs)</strong>, written in Backus-Naur Form (BNF). To parse this grammar and build the AST, parsers utilize <strong>Pushdown Automata (PDAs)</strong>—machines with a transition state stack that can track nested structures like open/close brackets, parenthesis nesting, and operator hierarchies.</p>
                </div>
            `
        },
        {
            id: "cfg",
            title: "3. Control Flow Graph (CFG)",
            content: `
                <p><strong>Definition:</strong> A Control Flow Graph represents all paths that might be traversed through a program during its execution. Nodes represent statements, expressions, or sequences of instructions called "basic blocks". Directed edges show flow transfer (execution pathways).</p>
                <p><strong>Key Concepts:</strong>
                    <ul>
                        <li><strong>Branching:</strong> Conditionals (like <code>if-else</code>) divide control into two pathways (True/False) that converge later.</li>
                        <li><strong>Loops:</strong> Loop conditions form cycles (back-edges) in the directed graph.</li>
                    </ul>
                </p>
                <p><strong>Compiler Role:</strong> CFG is vital for control flow analysis, dead-code elimination (identifying unreachable nodes), and loop optimizations.</p>
                <div class="theory-callout">
                    <h4>Automata Theory Connection:</h4>
                    <p>CFGs are structured as <strong>Directed Graphs</strong> $G = (V, E)$. The paths through a CFG represent the <strong>regular languages</strong> of execution traces. The structural layout of loop conditions and jumps maps directly to <strong>transition systems</strong> and state transition diagrams studied in state-machine logic.</p>
                </div>
            `
        },
        {
            id: "dfg",
            title: "4. Data Flow Graph (DFG)",
            content: `
                <p><strong>Definition:</strong> A Data Flow Graph represents the data dependencies between operations. It tracks the life cycle of variables, showing how a variable written/defined at one line flows as data into expressions or operations that read/use it.</p>
                <p><strong>Key Concepts:</strong>
                    <ul>
                        <li><strong>Definition (Def):</strong> Where a variable is declared or assigned a value (Write).</li>
                        <li><strong>Use:</strong> Where a variable is read or referenced inside an expression (Read).</li>
                    </ul>
                </p>
                <p><strong>Compiler Role:</strong> DFG enables static analyses like **Reaching Definitions**, **Liveness Analysis** (determining if a variable's register can be recycled), and **Constant Propagation**.</p>
                <div class="theory-callout">
                    <h4>Automata Theory Connection:</h4>
                    <p>Data flow analysis uses **lattices** and **monotone frameworks** (abstract math related to algebraic lattices). Tracing data dependencies across conditional execution blocks is formalized via **Kleene's Fixed Point Theorem**, which determines if a set of reaching definitions converges to a stable state after iterative passes over loop cycles.</p>
                </div>
            `
        },
        {
            id: "cpg",
            title: "5. Code Property Graph (CPG)",
            content: `
                <p><strong>Definition:</strong> A Code Property Graph is a unified graph representation that merges the **AST**, **CFG**, and **DFG** into a single data structure. By storing syntax structure, control pathways, and data flows together, it provides a holistic semantic view of the source code.</p>
                <p><strong>Key Concept:</strong> A CPG contains a single set of nodes (representing variables, statements, types, etc.) linked by three distinct types of edges:
                    <ul>
                        <li><strong>AST Edges:</strong> Define hierarchical syntactic structures.</li>
                        <li><strong>CFG Edges:</strong> Define operational execution order.</li>
                        <li><strong>DFG Edges:</strong> Define data dependencies and value flows.</li>
                    </ul>
                </p>
                <p><strong>Use Cases:</strong> Security auditing, static analysis, vulnerability scanning (e.g., tracing if user-controlled input flows into a dangerous sink function like <code>system()</code> without sanitization).</p>
            `
        },
        {
            id: "ai_assistants",
            title: "6. Connection to AI Coding Assistants",
            content: `
                <p>How do AI tools like Gemini, ChatGPT, Claude, and Copilot understand C code?</p>
                <ul>
                    <li><strong>Token Embeddings:</strong> Code is not treated as a plain sequence of characters. AI models tokenize code (using BPE or WordPiece) and convert tokens into high-dimensional vector embeddings, preserving semantic similarities (e.g., grouping keywords like <code>for</code> and <code>while</code>).</li>
                    <li><strong>Structural Parsing:</strong> When LLMs generate or debug code, their internal attention mechanisms learn to simulate the program's AST and CFG. Transformer models excel at tracking matching brackets and variables across scopes because the attention matrix captures structural distances similar to AST parent-child links.</li>
                    <li><strong>Graph Neural Networks (GNNs):</strong> Advanced developer tools convert source programs into a **Code Property Graph (CPG)** and feed it into a Graph Neural Network (GNN). GNNs process these graph nodes and edges to perform automatic vulnerability detection, code translation, and logic-based bug finding, surpassing raw text-based models.</li>
                    <li><strong>Static Analysis Integration:</strong> Agentic coding tools (like Claude Code or Antigravity) use AST parsing and DFG queries to trace variables, build class diagrams, and navigate large codebases with absolute precision, combining neural generation with compiler correctness.</li>
                </ul>
            `
        }
    ]
};

window.TheoryContent = THEORY_CONTENT;
