// graph-builder.js - Generates nodes and edges for AST, CFG, DFG, and CPG

/**
 * Builds nodes and edges for the AST visualization.
 */
function buildASTGraph(ast) {
    const nodes = [];
    const edges = [];
    const visited = new Set();

    function traverse(node, parentId = null) {
        if (!node) return;

        const nodeId = node.id;
        if (visited.has(nodeId)) return;
        visited.add(nodeId);

        let label = node.type;
        let details = '';

        switch (node.type) {
            case 'Program':
                label = 'Program (Root)';
                break;
            case 'PreprocessorDirective':
                label = `Preprocessor\n${node.value}`;
                break;
            case 'FunctionDeclaration':
                label = `Function\n${node.name}`;
                details = `Returns: ${node.returnType}`;
                break;
            case 'Parameter':
                label = `Param: ${node.name}`;
                details = `Type: ${node.paramType}`;
                break;
            case 'VariableDeclaration':
                label = `Declare: ${node.name}`;
                details = `Type: ${node.varType}`;
                break;
            case 'AssignmentExpression':
                label = `Assign (=)`;
                break;
            case 'BinaryExpression':
                label = `Op (${node.operator})`;
                break;
            case 'UnaryExpression':
                label = `Unary (${node.operator})`;
                break;
            case 'UpdateExpression':
                label = `Update (${node.operator})`;
                break;
            case 'Literal':
                label = `Literal: ${node.raw}`;
                break;
            case 'Identifier':
                label = `Id: ${node.name}`;
                break;
            case 'IfStatement':
                label = 'If Condition';
                break;
            case 'WhileStatement':
                label = 'While Loop';
                break;
            case 'ForStatement':
                label = 'For Loop';
                break;
            case 'ReturnStatement':
                label = 'Return';
                break;
            case 'FunctionCall':
                label = `Call: ${node.name}`;
                break;
            case 'BlockStatement':
                label = 'Block {}';
                break;
            case 'ExpressionStatement':
                label = 'Expr Statement';
                break;
            case 'BreakStatement':
                label = 'Break';
                break;
            case 'ContinueStatement':
                label = 'Continue';
                break;
        }

        nodes.push({
            id: nodeId,
            label: label,
            title: details || node.type,
            group: 'ast',
            shape: 'box',
            margin: 10,
            line: node.line || null,
            font: { face: 'Outfit', color: '#ffffff' },
            color: {
                background: '#4f46e5',
                border: '#818cf8',
                highlight: { background: '#6366f1', border: '#a5b4fc' }
            }
        });

        if (parentId) {
            edges.push({
                from: parentId,
                to: nodeId,
                arrows: 'to',
                color: { color: '#818cf8', highlight: '#c7d2fe' },
                width: 1.5,
                dashes: false,
                label: 'ast_child',
                font: { size: 0 } // Hidden label for debugging
            });
        }

        // Recurse down
        if (node.preprocessors) {
            node.preprocessors.forEach(child => traverse(child, nodeId));
        }
        if (node.body) {
            if (Array.isArray(node.body)) {
                node.body.forEach(child => traverse(child, nodeId));
            } else {
                traverse(node.body, nodeId);
            }
        }
        if (node.params) {
            node.params.forEach(child => traverse(child, nodeId));
        }
        if (node.init) {
            traverse(node.init, nodeId);
        }
        if (node.expression) {
            traverse(node.expression, nodeId);
        }
        if (node.left) {
            traverse(node.left, nodeId);
        }
        if (node.right) {
            traverse(node.right, nodeId);
        }
        if (node.argument) {
            traverse(node.argument, nodeId);
        }
        if (node.arguments) {
            node.arguments.forEach(child => traverse(child, nodeId));
        }
        if (node.test) {
            traverse(node.test, nodeId);
        }
        if (node.consequent) {
            traverse(node.consequent, nodeId);
        }
        if (node.alternate) {
            traverse(node.alternate, nodeId);
        }
        if (node.update) {
            traverse(node.update, nodeId);
        }
    }

    traverse(ast);
    return { nodes, edges };
}

/**
 * Builds nodes and edges for the CFG visualization.
 */
function buildCFGGraph(ast) {
    const nodes = [];
    const edges = [];
    let tempIdCounter = 0;

    function getTempId() {
        return 'cfg_temp_' + (tempIdCounter++);
    }

    // Find all functions in the program
    const functions = ast.body.filter(n => n.type === 'FunctionDeclaration');

    if (functions.length === 0) {
        // Fallback for codes without an explicit function
        // Treat the whole Program body as a main sequence
        buildCFGForSequence('global_main', 'Global Context', ast.body, nodes, edges);
    } else {
        functions.forEach(func => {
            const funcName = func.name;
            const paramLabels = func.params.map(p => `${p.paramType} ${p.name}`).join(', ');
            buildCFGForFunction(func, nodes, edges);
        });
    }

    return { nodes, edges };

    function buildCFGForFunction(func, nodes, edges) {
        const startId = `start_${func.name}`;
        const endId = `end_${func.name}`;

        // Create START and END nodes
        nodes.push({
            id: startId,
            label: `START\n${func.name}(${func.params.map(p => p.name).join(', ')})`,
            shape: 'ellipse',
            group: 'cfg_boundary',
            color: { background: '#10b981', border: '#34d399' },
            font: { face: 'Outfit', color: '#ffffff', bold: true }
        });

        nodes.push({
            id: endId,
            label: `END\n${func.name}`,
            shape: 'ellipse',
            group: 'cfg_boundary',
            color: { background: '#ef4444', border: '#f87171' },
            font: { face: 'Outfit', color: '#ffffff', bold: true }
        });

        // Traverse statements in the function body
        const bodyStatements = func.body.body;
        const entryNodeId = traverseCFGSequence(bodyStatements, endId, endId, null, null, nodes, edges);

        // Connect START to the entry point
        edges.push({
            from: startId,
            to: entryNodeId,
            arrows: 'to',
            color: { color: '#10b981' },
            width: 2
        });
    }

    function buildCFGForSequence(name, label, stmts, nodes, edges) {
        const startId = `start_${name}`;
        const endId = `end_${name}`;

        nodes.push({
            id: startId,
            label: `START\n${label}`,
            shape: 'ellipse',
            group: 'cfg_boundary',
            color: { background: '#10b981', border: '#34d399' },
            font: { face: 'Outfit', color: '#ffffff', bold: true }
        });

        nodes.push({
            id: endId,
            label: `END\n${label}`,
            shape: 'ellipse',
            group: 'cfg_boundary',
            color: { background: '#ef4444', border: '#f87171' },
            font: { face: 'Outfit', color: '#ffffff', bold: true }
        });

        const entryNodeId = traverseCFGSequence(stmts, endId, endId, null, null, nodes, edges);

        edges.push({
            from: startId,
            to: entryNodeId,
            arrows: 'to',
            color: { color: '#10b981' },
            width: 2
        });
    }

    /**
     * Traverses statements, creating CFG edges and nodes.
     * Returns the entry node ID of this sequence.
     */
    function traverseCFGSequence(stmts, nextNodeId, returnNodeId, loopStartId, loopEndId, nodes, edges) {
        if (!stmts || stmts.length === 0) {
            return nextNodeId;
        }

        let currentNext = nextNodeId;
        // Traverse statements in reverse order so we can pass downstream execution targets forward
        for (let i = stmts.length - 1; i >= 0; i--) {
            currentNext = traverseCFGStatement(stmts[i], currentNext, returnNodeId, loopStartId, loopEndId, nodes, edges);
        }

        return currentNext;
    }

    function getStatementString(node) {
        if (!node) return '';
        switch (node.type) {
            case 'VariableDeclaration':
                return `${node.varType} ${node.name}${node.init ? ' = ...' : ''};`;
            case 'ExpressionStatement':
                return getExpressionString(node.expression) + ';';
            case 'AssignmentExpression':
                return `${getExpressionString(node.left)} = ${getExpressionString(node.right)}`;
            case 'ReturnStatement':
                return `return${node.argument ? ' ' + getExpressionString(node.argument) : ''};`;
            case 'IfStatement':
                return `if (${getExpressionString(node.test)})`;
            case 'WhileStatement':
                return `while (${getExpressionString(node.test)})`;
            case 'ForStatement':
                return `for (...)`;
            case 'BreakStatement':
                return 'break;';
            case 'ContinueStatement':
                return 'continue;';
            default:
                return node.type;
        }
    }

    function getExpressionString(node) {
        if (!node) return '';
        switch (node.type) {
            case 'Identifier':
                return node.name;
            case 'Literal':
                return node.raw;
            case 'BinaryExpression':
                return `${getExpressionString(node.left)} ${node.operator} ${getExpressionString(node.right)}`;
            case 'UnaryExpression':
                return node.prefix ? `${node.operator}${getExpressionString(node.argument)}` : `${getExpressionString(node.argument)}${node.operator}`;
            case 'UpdateExpression':
                return node.prefix ? `${node.operator}${getExpressionString(node.argument)}` : `${getExpressionString(node.argument)}${node.operator}`;
            case 'AssignmentExpression':
                return `${getExpressionString(node.left)} = ${getExpressionString(node.right)}`;
            case 'FunctionCall':
                return `${node.name}(${node.arguments.map(getExpressionString).join(', ')})`;
            default:
                return 'expr';
        }
    }

    function traverseCFGStatement(stmt, nextNodeId, returnNodeId, loopStartId, loopEndId, nodes, edges) {
        if (!stmt) return nextNodeId;

        const nodeId = stmt.id;

        // Skip preprocessors in CFG
        if (stmt.type === 'PreprocessorDirective') {
            return nextNodeId;
        }

        switch (stmt.type) {
            case 'BlockStatement':
                return traverseCFGSequence(stmt.body, nextNodeId, returnNodeId, loopStartId, loopEndId, nodes, edges);

            case 'VariableDeclaration':
            case 'ExpressionStatement': {
                nodes.push({
                    id: nodeId,
                    label: getStatementString(stmt),
                    shape: 'box',
                    group: 'cfg_stmt',
                    color: { background: '#064e3b', border: '#059669' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });
                edges.push({
                    from: nodeId,
                    to: nextNodeId,
                    arrows: 'to',
                    color: { color: '#059669' },
                    width: 1.5
                });
                return nodeId;
            }

            case 'ReturnStatement': {
                nodes.push({
                    id: nodeId,
                    label: getStatementString(stmt),
                    shape: 'box',
                    group: 'cfg_stmt',
                    color: { background: '#7f1d1d', border: '#ef4444' }, // Red for return statements
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });
                // Return statement transfers control directly to END of function
                edges.push({
                    from: nodeId,
                    to: returnNodeId,
                    arrows: 'to',
                    color: { color: '#ef4444' },
                    width: 2
                });
                return nodeId;
            }

            case 'BreakStatement': {
                nodes.push({
                    id: nodeId,
                    label: 'break;',
                    shape: 'box',
                    group: 'cfg_stmt',
                    color: { background: '#374151', border: '#9ca3af' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });
                if (loopEndId) {
                    edges.push({
                        from: nodeId,
                        to: loopEndId,
                        arrows: 'to',
                        color: { color: '#9ca3af' },
                        width: 1.5
                    });
                }
                return nodeId;
            }

            case 'ContinueStatement': {
                nodes.push({
                    id: nodeId,
                    label: 'continue;',
                    shape: 'box',
                    group: 'cfg_stmt',
                    color: { background: '#374151', border: '#9ca3af' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });
                if (loopStartId) {
                    edges.push({
                        from: nodeId,
                        to: loopStartId,
                        arrows: 'to',
                        color: { color: '#9ca3af' },
                        width: 1.5
                    });
                }
                return nodeId;
            }

            case 'IfStatement': {
                // Condition Node
                nodes.push({
                    id: nodeId,
                    label: `if (${getExpressionString(stmt.test)})`,
                    shape: 'diamond',
                    group: 'cfg_branch',
                    color: { background: '#1e3a8a', border: '#3b82f6' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });

                // True branch entry point
                const trueEntry = traverseCFGStatement(stmt.consequent, nextNodeId, returnNodeId, loopStartId, loopEndId, nodes, edges);
                edges.push({
                    from: nodeId,
                    to: trueEntry,
                    label: 'T',
                    arrows: 'to',
                    color: { color: '#10b981' },
                    font: { strokeWidth: 0, fill: '#ffffff', face: 'Outfit', size: 12, color: '#10b981' }
                });

                // False branch entry point
                const falseEntry = stmt.alternate 
                    ? traverseCFGStatement(stmt.alternate, nextNodeId, returnNodeId, loopStartId, loopEndId, nodes, edges)
                    : nextNodeId;
                
                edges.push({
                    from: nodeId,
                    to: falseEntry,
                    label: 'F',
                    arrows: 'to',
                    color: { color: '#ef4444' },
                    font: { strokeWidth: 0, fill: '#ffffff', face: 'Outfit', size: 12, color: '#ef4444' }
                });

                return nodeId;
            }

            case 'WhileStatement': {
                // Condition Node
                nodes.push({
                    id: nodeId,
                    label: `while (${getExpressionString(stmt.test)})`,
                    shape: 'diamond',
                    group: 'cfg_branch',
                    color: { background: '#1e3a8a', border: '#3b82f6' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });

                // Loop body entry point (loops back to condition nodeId)
                // Inside body, 'break' jumps to 'nextNodeId', 'continue' jumps to condition 'nodeId'
                const bodyEntry = traverseCFGStatement(stmt.body, nodeId, returnNodeId, nodeId, nextNodeId, nodes, edges);

                // Edge from condition -> body (True)
                edges.push({
                    from: nodeId,
                    to: bodyEntry,
                    label: 'T',
                    arrows: 'to',
                    color: { color: '#10b981' },
                    font: { strokeWidth: 0, fill: '#ffffff', face: 'Outfit', size: 12, color: '#10b981' }
                });

                // Edge from condition -> nextNodeId (False)
                edges.push({
                    from: nodeId,
                    to: nextNodeId,
                    label: 'F',
                    arrows: 'to',
                    color: { color: '#ef4444' },
                    font: { strokeWidth: 0, fill: '#ffffff', face: 'Outfit', size: 12, color: '#ef4444' }
                });

                return nodeId;
            }

            case 'ForStatement': {
                // For a structure: for (init; test; update) body
                // CFG path is: init -> test --[True]--> body -> update -> test
                //                       --[False]--> nextNodeId
                
                const testId = nodeId;
                const updateId = stmt.update ? (stmt.update.id || getTempId()) : testId;

                // 1. Condition diamond
                nodes.push({
                    id: testId,
                    label: stmt.test ? `for: ${getExpressionString(stmt.test)}` : 'for: true',
                    shape: 'diamond',
                    group: 'cfg_branch',
                    color: { background: '#1e3a8a', border: '#3b82f6' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });

                // 2. Update box (if exists)
                if (stmt.update) {
                    nodes.push({
                        id: updateId,
                        label: getExpressionString(stmt.update),
                        shape: 'box',
                        group: 'cfg_stmt',
                        color: { background: '#064e3b', border: '#059669' },
                        font: { face: 'Outfit', color: '#ffffff' },
                        line: stmt.line || null
                    });
                    // Update transitions back to test
                    edges.push({
                        from: updateId,
                        to: testId,
                        arrows: 'to',
                        color: { color: '#059669' },
                        width: 1.5
                    });
                }

                // 3. Body entry
                // Inside body, 'break' jumps to 'nextNodeId', 'continue' jumps to 'updateId'
                const bodyEntry = traverseCFGStatement(stmt.body, updateId, returnNodeId, updateId, nextNodeId, nodes, edges);

                // Edge from test -> body (True)
                edges.push({
                    from: testId,
                    to: bodyEntry,
                    label: 'T',
                    arrows: 'to',
                    color: { color: '#10b981' },
                    font: { strokeWidth: 0, fill: '#ffffff', face: 'Outfit', size: 12, color: '#10b981' }
                });

                // Edge from test -> nextNodeId (False)
                edges.push({
                    from: testId,
                    to: nextNodeId,
                    label: 'F',
                    arrows: 'to',
                    color: { color: '#ef4444' },
                    font: { strokeWidth: 0, fill: '#ffffff', face: 'Outfit', size: 12, color: '#ef4444' }
                });

                // 4. Init statement execution
                if (stmt.init) {
                    const initId = stmt.init.id;
                    nodes.push({
                        id: initId,
                        label: getStatementString(stmt.init) || getExpressionString(stmt.init),
                        shape: 'box',
                        group: 'cfg_stmt',
                        color: { background: '#064e3b', border: '#059669' },
                        font: { face: 'Outfit', color: '#ffffff' },
                        line: stmt.line || null
                    });
                    edges.push({
                        from: initId,
                        to: testId,
                        arrows: 'to',
                        color: { color: '#059669' },
                        width: 1.5
                    });
                    return initId;
                }

                return testId;
            }

            default:
                // Fallback for statements we don't explicitly parse
                nodes.push({
                    id: nodeId,
                    label: stmt.type,
                    shape: 'box',
                    group: 'cfg_stmt',
                    color: { background: '#4b5563', border: '#9ca3af' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: stmt.line || null
                });
                edges.push({
                    from: nodeId,
                    to: nextNodeId,
                    arrows: 'to',
                    color: { color: '#9ca3af' }
                });
                return nodeId;
        }
    }
}

/**
 * Builds nodes and edges for the DFG visualization.
 */
function buildDFGGraph(ast) {
    const nodes = [];
    const edges = [];
    
    // We map variables to the AST node ID where they were last defined
    const writeTracker = new Map();
    let edgeIdCounter = 0;

    function recordWrite(varName, nodeId) {
        writeTracker.set(varName, nodeId);
    }

    function recordRead(varName, readNodeId, readNodeLabel) {
        const lastWriteNodeId = writeTracker.get(varName);
        if (lastWriteNodeId) {
            edges.push({
                id: 'dfg_e_' + (edgeIdCounter++),
                from: lastWriteNodeId,
                to: readNodeId,
                arrows: 'to',
                color: { color: '#f59e0b', highlight: '#fbbf24' },
                width: 2,
                dashes: true,
                label: `use(${varName})`,
                font: { size: 10, color: '#f59e0b', face: 'Outfit', strokeWidth: 0 }
            });
        }
    }

    // Traverses the AST searching for assignments, variable declarations and reads
    function traverse(node) {
        if (!node) return;

        switch (node.type) {
            case 'FunctionDeclaration':
                // Register parameters as initial variable definitions
                if (node.params) {
                    node.params.forEach(param => {
                        nodes.push({
                            id: param.id,
                            label: `Param: ${param.name}`,
                            shape: 'box',
                            color: { background: '#78350f', border: '#d97706' },
                            font: { face: 'Outfit', color: '#ffffff' },
                            line: param.line || null
                        });
                        recordWrite(param.name, param.id);
                    });
                }
                traverse(node.body);
                break;

            case 'VariableDeclaration':
                // Creating a node for variable definition
                nodes.push({
                    id: node.id,
                    label: `Def: ${node.name}`,
                    shape: 'box',
                    color: { background: '#78350f', border: '#d97706' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: node.line || null
                });

                if (node.init) {
                    // Traverse init expression first, so reads in RHS get mapped to prior definitions
                    traverseExpr(node.init, node.id, node.name);
                }
                
                // Set this declaration as the latest definition
                recordWrite(node.name, node.id);
                break;

            case 'AssignmentExpression':
                // LHS should be an Identifier (variable write)
                const varName = node.left.name;
                
                // RHS contains reads
                traverseExpr(node.right, node.id, varName);
                
                // Creating node for the assignment operation
                nodes.push({
                    id: node.id,
                    label: `Write: ${varName}`,
                    shape: 'box',
                    color: { background: '#78350f', border: '#d97706' },
                    font: { face: 'Outfit', color: '#ffffff' },
                    line: node.line || null
                });

                recordWrite(varName, node.id);
                break;

            case 'UpdateExpression':
                // Update is both read and write
                if (node.argument && node.argument.type === 'Identifier') {
                    const name = node.argument.name;
                    // Read the variable
                    recordRead(name, node.id, `update ${name}`);
                    
                    // Create Node for Update
                    nodes.push({
                        id: node.id,
                        label: `Update: ${name}${node.operator}`,
                        shape: 'box',
                        color: { background: '#78350f', border: '#d97706' },
                        font: { face: 'Outfit', color: '#ffffff' },
                        line: node.line || null
                    });
                    
                    // Write back
                    recordWrite(name, node.id);
                }
                break;

            case 'IfStatement':
                traverseExpr(node.test, node.id, 'if_cond');
                traverse(node.consequent);
                traverse(node.alternate);
                break;

            case 'WhileStatement':
                traverseExpr(node.test, node.id, 'while_cond');
                traverse(node.body);
                break;

            case 'ForStatement':
                traverse(node.init);
                if (node.test) traverseExpr(node.test, node.test.id || node.id, 'for_cond');
                traverse(node.body);
                if (node.update) traverse(node.update);
                break;

            case 'ReturnStatement':
                if (node.argument) {
                    traverseExpr(node.argument, node.id, 'return_val');
                    nodes.push({
                        id: node.id,
                        label: `Return`,
                        shape: 'box',
                        color: { background: '#7f1d1d', border: '#ef4444' },
                        font: { face: 'Outfit', color: '#ffffff' },
                        line: node.line || null
                    });
                }
                break;

            case 'ExpressionStatement':
                traverse(node.expression);
                break;

            case 'BlockStatement':
                node.body.forEach(traverse);
                break;

            default:
                // Recurse automatically down properties
                for (let prop in node) {
                    if (node[prop] && typeof node[prop] === 'object') {
                        if (Array.isArray(node[prop])) {
                            node[prop].forEach(child => {
                                if (child && typeof child.type === 'string') traverse(child);
                            });
                        } else if (typeof node[prop].type === 'string') {
                            traverse(node[prop]);
                        }
                    }
                }
        }
    }

    // Traverses expressions checking for Identifier reads
    function traverseExpr(expr, parentNodeId, destVarName) {
        if (!expr) return;

        if (expr.type === 'Identifier') {
            recordRead(expr.name, parentNodeId, destVarName);
        } else if (expr.type === 'BinaryExpression') {
            traverseExpr(expr.left, parentNodeId, destVarName);
            traverseExpr(expr.right, parentNodeId, destVarName);
        } else if (expr.type === 'UnaryExpression' || expr.type === 'UpdateExpression') {
            traverseExpr(expr.argument, parentNodeId, destVarName);
        } else if (expr.type === 'FunctionCall') {
            expr.arguments.forEach(arg => traverseExpr(arg, parentNodeId, destVarName));
        }
    }

    traverse(ast);
    return { nodes, edges };
}

/**
 * Builds the combined Code Property Graph (CPG).
 * Unifies all AST nodes, overlays CFG and DFG edges.
 */
function buildCPGGraph(ast) {
    // 1. Get the AST nodes and edges
    const astGraph = buildASTGraph(ast);
    
    // We clone the nodes and mark them as AST nodes
    const nodes = astGraph.nodes.map(n => ({
        ...n,
        // Make AST nodes visually smaller, semi-transparent by default, so overlays pop out
        color: {
            background: 'rgba(30, 41, 59, 0.6)',
            border: 'rgba(99, 102, 241, 0.4)',
            highlight: { background: '#6366f1', border: '#a5b4fc' }
        },
        font: { face: 'Outfit', color: 'rgba(248, 250, 252, 0.7)', size: 12 }
    }));

    let edgeCounter = 0;

    // Identify standard AST edges
    const edges = astGraph.edges.map(e => ({
        ...e,
        id: `cpg_ast_edge_${edgeCounter++}`,
        type: 'ast',
        label: 'AST Link',
        font: { size: 0 },
        arrows: '',
        color: { color: 'rgba(99, 102, 241, 0.25)', highlight: 'rgba(99, 102, 241, 0.6)' },
        width: 1
    }));

    // 2. Generate CFG transitions and DFG data dependencies
    // CFG transitions connect statement-level nodes.
    // DFG data dependencies connect variable assignment/usage nodes.
    const cfgGraph = buildCFGGraph(ast);
    const dfgGraph = buildDFGGraph(ast);

    // Filter out duplicate CFG boundary nodes (START/END) that don't map to AST, 
    // but keep them in the node set for the CPG layout so the entrance/exits are clear!
    cfgGraph.nodes.forEach(n => {
        if (n.id.startsWith('start_') || n.id.startsWith('end_')) {
            nodes.push({
                ...n,
                // Soften standard colors to fit CPG theme
                font: { face: 'Outfit', color: '#ffffff', size: 12 }
            });
        }
    });

    // 3. Map CFG transitions
    cfgGraph.edges.forEach(e => {
        edges.push({
            id: `cpg_cfg_edge_${edgeCounter++}`,
            from: e.from,
            to: e.to,
            type: 'cfg',
            label: e.label || 'CFG Flow',
            arrows: 'to',
            width: 2.5,
            color: { color: '#10b981', highlight: '#34d399' },
            font: { size: 10, color: '#10b981', face: 'Outfit', strokeWidth: 0 }
        });
    });

    // 4. Map DFG dependencies
    // To match AST nodes, we translate the DFG node links directly onto their corresponding AST identifiers
    dfgGraph.edges.forEach(e => {
        edges.push({
            id: `cpg_dfg_edge_${edgeCounter++}`,
            from: e.from,
            to: e.to,
            type: 'dfg',
            label: e.label || 'DFG Flow',
            arrows: 'to',
            width: 2,
            dashes: true,
            color: { color: '#f59e0b', highlight: '#fbbf24' },
            font: { size: 10, color: '#f59e0b', face: 'Outfit', strokeWidth: 0 }
        });
    });

    return { nodes, edges };
}

// Attach builders to window
window.GraphBuilder = {
    buildASTGraph,
    buildCFGGraph,
    buildDFGGraph,
    buildCPGGraph
};
