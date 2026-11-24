// parser.js - Lexer and Recursive Descent Parser for a representative C subset

const TOKEN_TYPES = {
    PREPROCESSOR: 'PREPROCESSOR',
    KEYWORD: 'KEYWORD',
    IDENTIFIER: 'IDENTIFIER',
    NUMBER: 'NUMBER',
    STRING: 'STRING',
    OPERATOR: 'OPERATOR',
    PUNCTUATION: 'PUNCTUATION',
    COMMENT: 'COMMENT',
    UNKNOWN: 'UNKNOWN'
};

const KEYWORDS = new Set([
    'int', 'float', 'double', 'char', 'void',
    'if', 'else', 'while', 'for', 'return',
    'break', 'continue', 'struct'
]);

/**
 * Tokenizes C source code into a list of tokens.
 */
function tokenize(source) {
    const tokens = [];
    let line = 1;
    let col = 1;
    let cursor = 0;
    const length = source.length;

    // Helper to check characters
    function peekChar(offset = 0) {
        if (cursor + offset >= length) return null;
        return source[cursor + offset];
    }

    function consumeChar() {
        const char = source[cursor];
        cursor++;
        if (char === '\n') {
            line++;
            col = 1;
        } else {
            col++;
        }
        return char;
    }

    let tokenId = 0;

    while (cursor < length) {
        const char = peekChar();

        // 1. Whitespace
        if (/\s/.test(char)) {
            consumeChar();
            continue;
        }

        const startLine = line;
        const startCol = col;
        const startCursor = cursor;

        // 2. Comments
        // Line Comment: //
        if (char === '/' && peekChar(1) === '/') {
            let val = '';
            while (cursor < length && peekChar() !== '\n') {
                val += consumeChar();
            }
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.COMMENT,
                value: val,
                line: startLine,
                column: startCol
            });
            continue;
        }

        // Block Comment: /* ... */
        if (char === '/' && peekChar(1) === '*') {
            let val = consumeChar() + consumeChar(); // consume /*
            while (cursor < length && !(peekChar() === '*' && peekChar(1) === '/')) {
                val += consumeChar();
            }
            if (cursor < length) {
                val += consumeChar() + consumeChar(); // consume */
            }
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.COMMENT,
                value: val,
                line: startLine,
                column: startCol
            });
            continue;
        }

        // 3. Preprocessor directive (e.g. #include <stdio.h>)
        if (char === '#') {
            let val = '';
            while (cursor < length && peekChar() !== '\n') {
                val += consumeChar();
            }
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.PREPROCESSOR,
                value: val.trim(),
                line: startLine,
                column: startCol
            });
            continue;
        }

        // 4. String Literals
        if (char === '"') {
            let val = consumeChar(); // opening quote
            while (cursor < length && peekChar() !== '"') {
                if (peekChar() === '\\') {
                    val += consumeChar(); // escape char
                }
                val += consumeChar();
            }
            if (cursor < length) {
                val += consumeChar(); // closing quote
            }
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.STRING,
                value: val,
                line: startLine,
                column: startCol
            });
            continue;
        }

        // 5. Operators & Double Character Operators
        const doubleOp = char + peekChar(1);
        const doubleOps = ['++', '--', '<=', '>=', '==', '!=', '&&', '||', '+=', '-=', '*=', '/='];
        if (doubleOps.includes(doubleOp)) {
            consumeChar();
            consumeChar();
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.OPERATOR,
                value: doubleOp,
                line: startLine,
                column: startCol
            });
            continue;
        }

        const singleOps = ['+', '-', '*', '/', '%', '=', '<', '>', '&', '|', '!'];
        if (singleOps.includes(char)) {
            consumeChar();
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.OPERATOR,
                value: char,
                line: startLine,
                column: startCol
            });
            continue;
        }

        // 6. Punctuations
        const punctuations = [';', ',', '(', ')', '{', '}', '[', ']'];
        if (punctuations.includes(char)) {
            consumeChar();
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.PUNCTUATION,
                value: char,
                line: startLine,
                column: startCol
            });
            continue;
        }

        // 7. Numbers (integer and floats)
        if (/\d/.test(char)) {
            let val = '';
            let dotSeen = false;
            while (cursor < length) {
                const next = peekChar();
                if (/\d/.test(next)) {
                    val += consumeChar();
                } else if (next === '.' && !dotSeen) {
                    dotSeen = true;
                    val += consumeChar();
                } else {
                    break;
                }
            }
            tokens.push({
                id: 't' + (tokenId++),
                type: TOKEN_TYPES.NUMBER,
                value: val,
                line: startLine,
                column: startCol
            });
            continue;
        }

        // 8. Identifiers and Keywords
        if (/[a-zA-Z_]/.test(char)) {
            let val = '';
            while (cursor < length && /[a-zA-Z0-9_]/.test(peekChar())) {
                val += consumeChar();
            }

            const type = KEYWORDS.has(val) ? TOKEN_TYPES.KEYWORD : TOKEN_TYPES.IDENTIFIER;
            tokens.push({
                id: 't' + (tokenId++),
                type: type,
                value: val,
                line: startLine,
                column: startCol
            });
            continue;
        }

        // 9. Unknown character (fallback)
        const unknownChar = consumeChar();
        tokens.push({
            id: 't' + (tokenId++),
            type: TOKEN_TYPES.UNKNOWN,
            value: unknownChar,
            line: startLine,
            column: startCol
        });
    }

    return tokens;
}

/**
 * Parses a list of C tokens into a simplified Abstract Syntax Tree (AST).
 */
class Parser {
    constructor(tokens) {
        // Filter out comments and keep preprocessors at top level
        this.allTokens = tokens;
        this.tokens = tokens.filter(t => t.type !== TOKEN_TYPES.COMMENT);
        this.index = 0;
        this.astNodeId = 0;
    }

    nextId() {
        return 'ast_' + (this.astNodeId++);
    }

    peek(offset = 0) {
        if (this.index + offset >= this.tokens.length) return null;
        return this.tokens[this.index + offset];
    }

    consume(expectedType, expectedValue = null) {
        const token = this.peek();
        if (!token) {
            throw new Error(`Unexpected EOF. Expected token of type ${expectedType}`);
        }
        if (token.type !== expectedType || (expectedValue !== null && token.value !== expectedValue)) {
            throw new Error(`Parse error at line ${token.line}, col ${token.column}: Expected '${expectedValue || expectedType}' but got '${token.value}'`);
        }
        this.index++;
        return token;
    }

    isEOF() {
        return this.index >= this.tokens.length;
    }

    match(type, value = null) {
        const token = this.peek();
        if (!token) return false;
        if (token.type !== type) return false;
        if (value !== null && token.value !== value) return false;
        return true;
    }

    matchKeyword(val) {
        return this.match(TOKEN_TYPES.KEYWORD, val);
    }

    parse() {
        const body = [];
        const preprocessors = [];

        while (!this.isEOF()) {
            if (this.match(TOKEN_TYPES.PREPROCESSOR)) {
                const tok = this.consume(TOKEN_TYPES.PREPROCESSOR);
                const prepNode = {
                    id: this.nextId(),
                    type: 'PreprocessorDirective',
                    value: tok.value,
                    line: tok.line,
                    tokenIds: [tok.id]
                };
                body.push(prepNode);
                preprocessors.push(prepNode);
            } else {
                try {
                    const node = this.parseDeclarationOrFunction();
                    if (node) {
                        body.push(node);
                    }
                } catch (e) {
                    console.error("Parsing failed at token index", this.index, this.peek(), e);
                    // Skip token to prevent infinite loop on syntax errors
                    this.index++;
                }
            }
        }

        return {
            id: this.nextId(),
            type: 'Program',
            body: body,
            preprocessors: preprocessors
        };
    }

    // Parses a function definition or global variable declaration
    parseDeclarationOrFunction() {
        const tokenType = this.peek();
        if (!tokenType) return null;

        // For simple C, declarations start with variable/return types (like int, void, float, etc.)
        let baseType = 'int';
        if (tokenType.type === TOKEN_TYPES.KEYWORD && ['int', 'float', 'double', 'char', 'void'].includes(tokenType.value)) {
            baseType = this.consume(TOKEN_TYPES.KEYWORD).value;
        } else {
            // If it doesn't match a known type, try parsing as expression statement directly (e.g. orphan expressions)
            return this.parseStatement();
        }

        const nameTok = this.consume(TOKEN_TYPES.IDENTIFIER);
        const name = nameTok.value;

        // Function Declaration
        if (this.match(TOKEN_TYPES.PUNCTUATION, '(')) {
            this.consume(TOKEN_TYPES.PUNCTUATION, '(');
            const params = [];
            while (!this.match(TOKEN_TYPES.PUNCTUATION, ')')) {
                const pTypeTok = this.consume(TOKEN_TYPES.KEYWORD);
                const pNameTok = this.consume(TOKEN_TYPES.IDENTIFIER);
                params.push({
                    id: this.nextId(),
                    type: 'Parameter',
                    paramType: pTypeTok.value,
                    name: pNameTok.value,
                    line: pTypeTok.line,
                    tokenIds: [pTypeTok.id, pNameTok.id]
                });
                if (this.match(TOKEN_TYPES.PUNCTUATION, ',')) {
                    this.consume(TOKEN_TYPES.PUNCTUATION, ',');
                }
            }
            this.consume(TOKEN_TYPES.PUNCTUATION, ')');

            // Parse body (must be a block statement)
            const body = this.parseBlockStatement();

            return {
                id: this.nextId(),
                type: 'FunctionDeclaration',
                returnType: baseType,
                name: name,
                params: params,
                body: body,
                line: nameTok.line,
                tokenIds: [nameTok.id]
            };
        }

        // Variable declaration
        let initValue = null;
        const tokenIds = [nameTok.id];
        if (this.match(TOKEN_TYPES.OPERATOR, '=')) {
            const eq = this.consume(TOKEN_TYPES.OPERATOR, '=');
            tokenIds.push(eq.id);
            initValue = this.parseExpression();
        }
        
        const semi = this.consume(TOKEN_TYPES.PUNCTUATION, ';');
        tokenIds.push(semi.id);

        return {
            id: this.nextId(),
            type: 'VariableDeclaration',
            varType: baseType,
            name: name,
            init: initValue,
            line: nameTok.line,
            tokenIds: tokenIds
        };
    }

    parseBlockStatement() {
        const start = this.consume(TOKEN_TYPES.PUNCTUATION, '{');
        const body = [];
        while (!this.match(TOKEN_TYPES.PUNCTUATION, '}')) {
            if (this.isEOF()) break;
            const stmt = this.parseStatement();
            if (stmt) body.push(stmt);
        }
        const end = this.consume(TOKEN_TYPES.PUNCTUATION, '}');

        return {
            id: this.nextId(),
            type: 'BlockStatement',
            body: body,
            line: start.line,
            tokenIds: [start.id, end.id]
        };
    }

    parseStatement() {
        if (this.match(TOKEN_TYPES.PUNCTUATION, '{')) {
            return this.parseBlockStatement();
        }

        if (this.match(TOKEN_TYPES.KEYWORD)) {
            const keyword = this.peek().value;
            switch (keyword) {
                case 'if':
                    return this.parseIfStatement();
                case 'while':
                    return this.parseWhileStatement();
                case 'for':
                    return this.parseForStatement();
                case 'return':
                    return this.parseReturnStatement();
                case 'break': {
                    const tok = this.consume(TOKEN_TYPES.KEYWORD);
                    const semi = this.consume(TOKEN_TYPES.PUNCTUATION, ';');
                    return { id: this.nextId(), type: 'BreakStatement', line: tok.line, tokenIds: [tok.id, semi.id] };
                }
                case 'continue': {
                    const tok = this.consume(TOKEN_TYPES.KEYWORD);
                    const semi = this.consume(TOKEN_TYPES.PUNCTUATION, ';');
                    return { id: this.nextId(), type: 'ContinueStatement', line: tok.line, tokenIds: [tok.id, semi.id] };
                }
                case 'int':
                case 'float':
                case 'double':
                case 'char':
                case 'void':
                    return this.parseDeclarationOrFunction(); // Variable decl inside block
            }
        }

        // Expression statement or assignment
        const expr = this.parseExpression();
        const semi = this.consume(TOKEN_TYPES.PUNCTUATION, ';');
        return {
            id: this.nextId(),
            type: 'ExpressionStatement',
            expression: expr,
            line: expr.line,
            tokenIds: [...(expr.tokenIds || []), semi.id]
        };
    }

    parseIfStatement() {
        const ifTok = this.consume(TOKEN_TYPES.KEYWORD, 'if');
        this.consume(TOKEN_TYPES.PUNCTUATION, '(');
        const test = this.parseExpression();
        this.consume(TOKEN_TYPES.PUNCTUATION, ')');
        
        const consequent = this.parseStatement();
        let alternate = null;

        if (this.match(TOKEN_TYPES.KEYWORD, 'else')) {
            this.consume(TOKEN_TYPES.KEYWORD, 'else');
            alternate = this.parseStatement();
        }

        return {
            id: this.nextId(),
            type: 'IfStatement',
            test: test,
            consequent: consequent,
            alternate: alternate,
            line: ifTok.line,
            tokenIds: [ifTok.id]
        };
    }

    parseWhileStatement() {
        const whileTok = this.consume(TOKEN_TYPES.KEYWORD, 'while');
        this.consume(TOKEN_TYPES.PUNCTUATION, '(');
        const test = this.parseExpression();
        this.consume(TOKEN_TYPES.PUNCTUATION, ')');
        const body = this.parseStatement();

        return {
            id: this.nextId(),
            type: 'WhileStatement',
            test: test,
            body: body,
            line: whileTok.line,
            tokenIds: [whileTok.id]
        };
    }

    parseForStatement() {
        const forTok = this.consume(TOKEN_TYPES.KEYWORD, 'for');
        this.consume(TOKEN_TYPES.PUNCTUATION, '(');

        let init = null;
        if (!this.match(TOKEN_TYPES.PUNCTUATION, ';')) {
            // Could be variable declaration or expression
            const next = this.peek();
            if (next.type === TOKEN_TYPES.KEYWORD && ['int', 'float', 'double'].includes(next.value)) {
                // Parse variable declaration, which consumes its own semicolon
                const varType = this.consume(TOKEN_TYPES.KEYWORD).value;
                const nameTok = this.consume(TOKEN_TYPES.IDENTIFIER);
                let initVal = null;
                if (this.match(TOKEN_TYPES.OPERATOR, '=')) {
                    this.consume(TOKEN_TYPES.OPERATOR, '=');
                    initVal = this.parseExpression();
                }
                init = {
                    id: this.nextId(),
                    type: 'VariableDeclaration',
                    varType,
                    name: nameTok.value,
                    init: initVal,
                    line: nameTok.line,
                    tokenIds: [nameTok.id]
                };
                // For-loop declarations in C don't always end in semicolon inside 'for(...)', 
                // but the grammar has ';' separation. We expect the next token to be ';' and consume it.
                this.consume(TOKEN_TYPES.PUNCTUATION, ';');
            } else {
                init = this.parseExpression();
                this.consume(TOKEN_TYPES.PUNCTUATION, ';');
            }
        } else {
            this.consume(TOKEN_TYPES.PUNCTUATION, ';');
        }

        let test = null;
        if (!this.match(TOKEN_TYPES.PUNCTUATION, ';')) {
            test = this.parseExpression();
        }
        this.consume(TOKEN_TYPES.PUNCTUATION, ';');

        let update = null;
        if (!this.match(TOKEN_TYPES.PUNCTUATION, ')')) {
            update = this.parseExpression();
        }
        this.consume(TOKEN_TYPES.PUNCTUATION, ')');

        const body = this.parseStatement();

        return {
            id: this.nextId(),
            type: 'ForStatement',
            init: init,
            test: test,
            update: update,
            body: body,
            line: forTok.line,
            tokenIds: [forTok.id]
        };
    }

    parseReturnStatement() {
        const retTok = this.consume(TOKEN_TYPES.KEYWORD, 'return');
        let argument = null;
        if (!this.match(TOKEN_TYPES.PUNCTUATION, ';')) {
            argument = this.parseExpression();
        }
        const semi = this.consume(TOKEN_TYPES.PUNCTUATION, ';');

        return {
            id: this.nextId(),
            type: 'ReturnStatement',
            argument: argument,
            line: retTok.line,
            tokenIds: [retTok.id, semi.id]
        };
    }

    parseExpression() {
        return this.parseAssignment();
    }

    parseAssignment() {
        const node = this.parseLogicalOr();

        if (this.match(TOKEN_TYPES.OPERATOR, '=')) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR, '=');
            const right = this.parseAssignment();
            
            // Check if left-hand side is assignable (usually Identifier in simple C)
            if (node.type !== 'Identifier') {
                console.warn("Left hand side of assignment is not an Identifier, but parsing anyway.");
            }

            return {
                id: this.nextId(),
                type: 'AssignmentExpression',
                operator: '=',
                left: node,
                right: right,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }

        return node;
    }

    parseLogicalOr() {
        let node = this.parseLogicalAnd();
        while (this.match(TOKEN_TYPES.OPERATOR, '||')) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            const right = this.parseLogicalAnd();
            node = {
                id: this.nextId(),
                type: 'BinaryExpression',
                operator: opTok.value,
                left: node,
                right: right,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }
        return node;
    }

    parseLogicalAnd() {
        let node = this.parseEquality();
        while (this.match(TOKEN_TYPES.OPERATOR, '&&')) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            const right = this.parseEquality();
            node = {
                id: this.nextId(),
                type: 'BinaryExpression',
                operator: opTok.value,
                left: node,
                right: right,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }
        return node;
    }

    parseEquality() {
        let node = this.parseRelational();
        while (this.match(TOKEN_TYPES.OPERATOR, '==') || this.match(TOKEN_TYPES.OPERATOR, '!=')) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            const right = this.parseRelational();
            node = {
                id: this.nextId(),
                type: 'BinaryExpression',
                operator: opTok.value,
                left: node,
                right: right,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }
        return node;
    }

    parseRelational() {
        let node = this.parseAdditive();
        const relationalOps = ['<', '>', '<=', '>='];
        while (this.match(TOKEN_TYPES.OPERATOR) && relationalOps.includes(this.peek().value)) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            const right = this.parseAdditive();
            node = {
                id: this.nextId(),
                type: 'BinaryExpression',
                operator: opTok.value,
                left: node,
                right: right,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }
        return node;
    }

    parseAdditive() {
        let node = this.parseMultiplicative();
        while (this.match(TOKEN_TYPES.OPERATOR, '+') || this.match(TOKEN_TYPES.OPERATOR, '-')) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            const right = this.parseMultiplicative();
            node = {
                id: this.nextId(),
                type: 'BinaryExpression',
                operator: opTok.value,
                left: node,
                right: right,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }
        return node;
    }

    parseMultiplicative() {
        let node = this.parseUnary();
        while (this.match(TOKEN_TYPES.OPERATOR, '*') || this.match(TOKEN_TYPES.OPERATOR, '/') || this.match(TOKEN_TYPES.OPERATOR, '%')) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            const right = this.parseUnary();
            node = {
                id: this.nextId(),
                type: 'BinaryExpression',
                operator: opTok.value,
                left: node,
                right: right,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }
        return node;
    }

    parseUnary() {
        if (this.match(TOKEN_TYPES.OPERATOR) && ['-', '!', '++', '--'].includes(this.peek().value)) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            const argument = this.parseUnary();
            return {
                id: this.nextId(),
                type: 'UnaryExpression',
                operator: opTok.value,
                prefix: true,
                argument: argument,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }

        return this.parsePostfix();
    }

    parsePostfix() {
        let node = this.parsePrimary();

        // Handle postfix update expressions: i++ or i--
        if (this.match(TOKEN_TYPES.OPERATOR, '++') || this.match(TOKEN_TYPES.OPERATOR, '--')) {
            const opTok = this.consume(TOKEN_TYPES.OPERATOR);
            node = {
                id: this.nextId(),
                type: 'UpdateExpression',
                operator: opTok.value,
                prefix: false,
                argument: node,
                line: opTok.line,
                tokenIds: [opTok.id]
            };
        }

        return node;
    }

    parsePrimary() {
        const token = this.peek();
        if (!token) throw new Error("Unexpected end of expression");

        if (token.type === TOKEN_TYPES.NUMBER) {
            this.consume(TOKEN_TYPES.NUMBER);
            return {
                id: this.nextId(),
                type: 'Literal',
                value: Number(token.value),
                raw: token.value,
                line: token.line,
                tokenIds: [token.id]
            };
        }

        if (token.type === TOKEN_TYPES.STRING) {
            this.consume(TOKEN_TYPES.STRING);
            return {
                id: this.nextId(),
                type: 'Literal',
                value: token.value.replace(/"/g, ''),
                raw: token.value,
                line: token.line,
                tokenIds: [token.id]
            };
        }

        if (token.type === TOKEN_TYPES.IDENTIFIER) {
            this.consume(TOKEN_TYPES.IDENTIFIER);

            // Check for Function Call: name(args)
            if (this.match(TOKEN_TYPES.PUNCTUATION, '(')) {
                this.consume(TOKEN_TYPES.PUNCTUATION, '(');
                const args = [];
                while (!this.match(TOKEN_TYPES.PUNCTUATION, ')')) {
                    args.push(this.parseExpression());
                    if (this.match(TOKEN_TYPES.PUNCTUATION, ',')) {
                        this.consume(TOKEN_TYPES.PUNCTUATION, ',');
                    }
                }
                const closeParen = this.consume(TOKEN_TYPES.PUNCTUATION, ')');
                return {
                    id: this.nextId(),
                    type: 'FunctionCall',
                    name: token.value,
                    arguments: args,
                    line: token.line,
                    tokenIds: [token.id, closeParen.id]
                };
            }

            return {
                id: this.nextId(),
                type: 'Identifier',
                name: token.value,
                line: token.line,
                tokenIds: [token.id]
            };
        }

        if (this.match(TOKEN_TYPES.PUNCTUATION, '(')) {
            const lp = this.consume(TOKEN_TYPES.PUNCTUATION, '(');
            const expr = this.parseExpression();
            const rp = this.consume(TOKEN_TYPES.PUNCTUATION, ')');
            
            // Return expression with brackets tracked
            expr.tokenIds = [lp.id, ...(expr.tokenIds || []), rp.id];
            return expr;
        }

        throw new Error(`Unexpected token in expression: '${token.value}' at line ${token.line}, col ${token.column}`);
    }
}

// Export tokenizer and parser classes to window context so other scripts can access it
window.CParser = {
    tokenize,
    parseCode: function(source) {
        const tokens = tokenize(source);
        const parser = new Parser(tokens);
        const ast = parser.parse();
        return { tokens: parser.allTokens, ast };
    }
};
