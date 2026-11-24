// visualizer.js - Controls UI events, orchestrates parser inputs, and builds Vis.js networks

// Preloaded C code examples
const EXAMPLES = {
    math: `#include <stdio.h>\n\nint main() {\n    int a = 5;\n    int b = 10;\n    int sum = a + b;\n    return sum;\n}`,
    branch: `int main() {\n    int x = 15;\n    int y;\n    if (x > 10) {\n        y = 100;\n    } else {\n        y = 200;\n    }\n    return y;\n}`,
    while: `int main() {\n    int count = 0;\n    int total = 0;\n    while (count < 5) {\n        total = total + count;\n        count = count + 1;\n    }\n    return total;\n}`,
    for: `int main() {\n    int base = 2;\n    int result = 1;\n    for (int i = 0; i < 4; i++) {\n        result = result * base;\n    }\n    return result;\n}`,
    factorial: `int factorial(int n) {\n    if (n <= 1) {\n        return 1;\n    }\n    return n * factorial(n - 1);\n}\n\nint main() {\n    int num = 5;\n    int fact = factorial(num);\n    return fact;\n}`
};

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const exampleSelect = document.getElementById('example-select');
    const editorTextarea = document.getElementById('editor-textarea');
    const lineNumbers = document.getElementById('line-numbers');
    const btnRun = document.getElementById('btn-run');
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    const emptyState = document.getElementById('empty-state');
    const searchInput = document.getElementById('search-input');
    
    // Floating Widgets
    const detailsWidget = document.getElementById('details-widget');
    const detailsTitle = document.getElementById('details-title');
    const detailsContent = document.getElementById('details-content');
    const detailsClose = document.getElementById('details-close');
    
    // CPG Overlay Switches
    const switchAst = document.getElementById('switch-ast');
    const switchCfg = document.getElementById('switch-cfg');
    const switchDfg = document.getElementById('switch-dfg');

    // Global application state
    let currentData = null; // Holds latest parsed { tokens, ast }
    let activeTabId = 'tab-lexical';
    let visNetworks = {}; // Store Vis.js Network instances
    let activeTokenSearch = '';

    // Initialize Monaco-like editor text scroll synchronizer
    function updateLineNumbers() {
        const text = editorTextarea.value;
        const lines = text.split('\n');
        const count = lines.length;
        let numHtml = '';
        for (let i = 1; i <= count; i++) {
            numHtml += `${i}<br>`;
        }
        lineNumbers.innerHTML = numHtml;
    }

    editorTextarea.addEventListener('input', updateLineNumbers);
    editorTextarea.addEventListener('scroll', () => {
        lineNumbers.scrollTop = editorTextarea.scrollTop;
    });

    // Populate theory panel
    populateTheoryPanel();

    // Select preloaded example
    exampleSelect.addEventListener('change', () => {
        const val = exampleSelect.value;
        if (EXAMPLES[val]) {
            editorTextarea.value = EXAMPLES[val];
            updateLineNumbers();
            // Trigger visualizer
            runAnalysis();
        }
    });

    // Setup initial code
    editorTextarea.value = EXAMPLES.math;
    updateLineNumbers();

    // Button Click Analyzer
    btnRun.addEventListener('click', runAnalysis);

    // Tab Navigation switching
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            navTabs.forEach(t => t.classList.remove('active'));
            
            // Explicitly set inline display style to none for all contents, then flex for target
            document.querySelectorAll('.tab-content').forEach(el => {
                el.classList.remove('active');
                el.style.display = 'none';
            });
            
            tab.classList.add('active');
            const targetEl = document.getElementById(target);
            targetEl.classList.add('active');
            targetEl.style.display = 'flex';
            
            activeTabId = target;

            // Trigger redraw or fit if it's a network graph tab
            if (currentData) {
                renderActiveTabGraph();
                
                // Force Vis.js resize/fit calculations right after display toggles
                const network = visNetworks[activeTabId];
                if (network) {
                    setTimeout(() => {
                        network.setSize('100%', '100%');
                        network.redraw();
                        network.fit();
                    }, 50); // Small 50ms delay to allow browser layout reflow
                }
            }
        });
    });

    // Close floating details widget
    detailsClose.addEventListener('click', () => {
        detailsWidget.style.display = 'none';
    });

    // CPG Toggle Switch change events
    [switchAst, switchCfg, switchDfg].forEach(sw => {
        sw.addEventListener('change', () => {
            if (activeTabId === 'tab-cpg' && visNetworks['tab-cpg']) {
                applyCPGFilters();
            }
        });
    });

    // Token Table Search Filter
    searchInput.addEventListener('input', () => {
        activeTokenSearch = searchInput.value.toLowerCase();
        renderTokenTable();
    });

    // Initial load
    runAnalysis();

    /**
     * Ingests the C code, parses it, and populates data structures.
     */
    function runAnalysis(event) {
        if (event && typeof event.preventDefault === 'function') {
            event.preventDefault();
        }
        const code = editorTextarea.value;
        try {
            // Run lexical scanner and parser
            currentData = window.CParser.parseCode(code);
            
            // Hide empty state
            emptyState.style.display = 'none';
            detailsWidget.style.display = 'none';

            // Reset vis networks to force fresh rebuilds
            visNetworks = {};

            // Render whatever tab is currently selected
            renderActiveTabGraph();
            
        } catch (err) {
            console.error(err);
            alert(`Analysis Warning: ${err.message}\nShowing partial parse structures.`);
            // Still display what we can
            try {
                const tokens = window.CParser.tokenize(code);
                currentData = { tokens, ast: { id: 'err', type: 'Program', body: [] } };
                emptyState.style.display = 'none';
                visNetworks = {};
                renderActiveTabGraph();
            } catch (e) {
                // Completely invalid
                emptyState.style.display = 'flex';
            }
        }
    }

    /**
     * Renders or redraws the visualization on the active tab
     */
    function renderActiveTabGraph() {
        if (!currentData) return;

        // Lexical Token Table
        if (activeTabId === 'tab-lexical') {
            renderTokenTable();
            return;
        }

        // Theory Tab doesn't need graph rendering
        if (activeTabId === 'tab-theory') {
            return;
        }

        // Check if Vis.js network is already initialized for this tab
        if (visNetworks[activeTabId]) {
            visNetworks[activeTabId].fit(); // Auto-fit zoom
            return;
        }

        // Build graphs based on current AST
        let nodesData = [];
        let edgesData = [];
        let containerId = '';
        let options = getCommonVisOptions();

        switch (activeTabId) {
            case 'tab-ast':
                const astG = window.GraphBuilder.buildASTGraph(currentData.ast);
                nodesData = astG.nodes;
                edgesData = astG.edges;
                containerId = 'ast-canvas';
                
                // AST uses a strict Hierarchical layout
                options.layout = {
                    hierarchical: {
                        direction: 'UD',
                        sortMethod: 'directed',
                        nodeSpacing: 160,
                        levelSeparation: 90,
                        parentCentralization: true
                    }
                };
                options.physics = {
                    hierarchicalRepulsion: {
                        nodeSpacing: 180
                    }
                };
                options.edges = {
                    smooth: {
                        type: 'cubicBezier',
                        forceDirection: 'vertical',
                        roundness: 0.4
                    }
                };
                break;

            case 'tab-cfg':
                const cfgG = window.GraphBuilder.buildCFGGraph(currentData.ast);
                nodesData = cfgG.nodes;
                edgesData = cfgG.edges;
                containerId = 'cfg-canvas';
                
                // CFG layout - dynamic spring forces
                options.physics = {
                    barnesHut: {
                        gravitationalConstant: -2000,
                        centralGravity: 0.3,
                        springLength: 120,
                        springConstant: 0.04,
                        damping: 0.09,
                        avoidOverlap: 0.5
                    }
                };
                break;

            case 'tab-dfg':
                const dfgG = window.GraphBuilder.buildDFGGraph(currentData.ast);
                nodesData = dfgG.nodes;
                edgesData = dfgG.edges;
                containerId = 'dfg-canvas';
                
                // DFG layout - physics spacing
                options.physics = {
                    barnesHut: {
                        gravitationalConstant: -1800,
                        springLength: 100,
                        springConstant: 0.05
                    }
                };
                break;

            case 'tab-cpg':
                const cpgG = window.GraphBuilder.buildCPGGraph(currentData.ast);
                nodesData = cpgG.nodes;
                edgesData = cpgG.edges;
                containerId = 'cpg-canvas';
                
                // CPG uses physics to float the nodes in space nicely
                options.physics = {
                    barnesHut: {
                        gravitationalConstant: -2800,
                        centralGravity: 0.2,
                        springLength: 140,
                        springConstant: 0.03,
                        damping: 0.08,
                        avoidOverlap: 0.8
                    }
                };
                break;
        }

        if (containerId) {
            const container = document.getElementById(containerId);
            container.innerHTML = ''; // Clear container

            // Wrap data in Vis.js DataSets so we can dynamically modify them (useful for CPG toggles)
            const visNodes = new vis.DataSet(nodesData);
            const visEdges = new vis.DataSet(edgesData);
            
            const networkData = { nodes: visNodes, edges: visEdges };
            
            // Create Network instance
            const network = new vis.Network(container, networkData, options);
            visNetworks[activeTabId] = network;

            // Store original edge sets on network object for CPG filters
            network.originalEdges = edgesData;
            network.visEdges = visEdges;

            // Hook up events
            network.on('click', (params) => {
                if (params.nodes.length > 0) {
                    const selectedNodeId = params.nodes[0];
                    const selectedNode = visNodes.get(selectedNodeId);
                    showNodeDetails(selectedNode);
                } else {
                    detailsWidget.style.display = 'none';
                }
            });

            // If CPG, apply initial filter checkboxes
            if (activeTabId === 'tab-cpg') {
                applyCPGFilters();
            }
        }
    }

    /**
     * Filters CPG edges dynamically based on checkbox toggles
     */
    function applyCPGFilters() {
        const network = visNetworks['tab-cpg'];
        if (!network || !network.originalEdges) return;

        const showAst = switchAst.checked;
        const showCfg = switchCfg.checked;
        const showDfg = switchDfg.checked;

        const filteredEdges = network.originalEdges.filter(edge => {
            if (edge.type === 'ast') return showAst;
            if (edge.type === 'cfg') return showCfg;
            if (edge.type === 'dfg') return showDfg;
            return true;
        });

        // Clear existing, load filtered
        network.visEdges.clear();
        network.visEdges.add(filteredEdges);
    }

    /**
     * Renders the interactive Token list table
     */
    function renderTokenTable() {
        const tbody = document.getElementById('tokens-body');
        tbody.innerHTML = '';

        if (!currentData || !currentData.tokens) return;

        const filtered = currentData.tokens.filter(token => {
            if (token.type === TOKEN_TYPES.COMMENT) return false; // Hide comments in table unless requested
            if (activeTokenSearch) {
                return token.value.toLowerCase().includes(activeTokenSearch) || 
                       token.type.toLowerCase().includes(activeTokenSearch);
            }
            return true;
        });

        filtered.forEach((tok, index) => {
            const tr = document.createElement('tr');
            tr.dataset.line = tok.line;
            
            // Generate HTML structure
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td><span class="badge badge-${tok.type.toLowerCase()}">${tok.type}</span></td>
                <td style="color:#a5b4fc">${escapeHtml(tok.value)}</td>
                <td style="color:#64748b">Line ${tok.line}, Col ${tok.column}</td>
            `;

            // Row click: highlight line in Editor
            tr.addEventListener('click', () => {
                document.querySelectorAll('table.tokens-table tbody tr').forEach(r => r.classList.remove('active-token'));
                tr.classList.add('active-token');
                highlightEditorLine(tok.line);
            });

            tbody.appendChild(tr);
        });
    }

    /**
     * Highlights the selected line in the C editor
     */
    function highlightEditorLine(lineNum) {
        if (!lineNum) return;
        const lines = editorTextarea.value.split('\n');
        
        // Compute cursor selection range
        let charStart = 0;
        for (let i = 0; i < lineNum - 1; i++) {
            charStart += lines[i].length + 1; // +1 for newline character
        }
        const charEnd = charStart + lines[lineNum - 1].length;

        // Focus and select the line text
        editorTextarea.focus();
        editorTextarea.setSelectionRange(charStart, charEnd);

        // Scroll editor to match position
        const lineHeight = 21.6; // Line height in pixels (1.5 * 14.4px font size)
        editorTextarea.scrollTop = (lineNum - 3) * lineHeight;
        lineNumbers.scrollTop = editorTextarea.scrollTop;
    }

    /**
     * Displays floating details card for the clicked node
     */
    function showNodeDetails(node) {
        if (!node) return;

        detailsTitle.innerHTML = node.label.replace('\n', '<br>');
        
        let detailsHtml = `
            <p style="margin-bottom: 0.5rem;"><strong>ID:</strong> <code>${node.id}</code></p>
            <p style="margin-bottom: 0.5rem;"><strong>Representation:</strong> ${node.title || node.group || 'Node'}</p>
        `;

        if (node.line) {
            detailsHtml += `<p style="margin-bottom: 0.85rem;"><strong>Line Reference:</strong> Line ${node.line}</p>`;
            detailsHtml += `<button type="button" id="btn-highlight-node" class="btn-run" style="padding: 0.35rem 0.75rem; font-size: 0.75rem; border-radius: 4px; box-shadow: none;">Highlight Source Line</button>`;
        }

        detailsContent.innerHTML = detailsHtml;
        detailsWidget.style.display = 'block';

        // Add handler to highlight button
        const hlBtn = document.getElementById('btn-highlight-node');
        if (hlBtn) {
            hlBtn.addEventListener('click', () => {
                highlightEditorLine(node.line);
            });
        }
    }

    /**
     * Fills up the Theory & Explanations tab content
     */
    function populateTheoryPanel() {
        const theoryContainer = document.getElementById('theory-content-area');
        if (!theoryContainer || !window.TheoryContent) return;

        let html = `
            <h2>${window.TheoryContent.title}</h2>
            <p class="intro">${window.TheoryContent.introduction}</p>
        `;

        window.TheoryContent.sections.forEach(sec => {
            html += `
                <div class="theory-section" id="sec-${sec.id}">
                    <h3>${sec.title}</h3>
                    <div>${sec.content}</div>
                </div>
            `;
        });

        theoryContainer.innerHTML = html;
    }

    // Common styling configuration for Vis.js
    function getCommonVisOptions() {
        return {
            nodes: {
                shadow: {
                    enabled: true,
                    color: 'rgba(0,0,0,0.4)',
                    size: 8,
                    x: 0,
                    y: 4
                },
                borderWidth: 1.5,
                shape: 'box',
                font: {
                    face: 'Outfit',
                    size: 13,
                    color: '#f8fafc'
                }
            },
            edges: {
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.95
                    }
                },
                smooth: {
                    enabled: true,
                    type: 'continuous',
                    roundness: 0.5
                },
                shadow: {
                    enabled: false
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 150,
                zoomView: true,
                dragView: true
            }
        };
    }

    // Helper to escape HTML characters
    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
