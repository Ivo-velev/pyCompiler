import sys

class Compiler_error(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(f"Error (line {line}): {message}" if line else f"Error: {message}")

class Undefined_variable_error(Compiler_error): pass
class Stack_underflow_error(Compiler_error): pass
class Syntax_error(Compiler_error): pass

class Ev:
    def ev(self, s):
        self.vars = {}
        lines = [x.strip() for x in s.split("\n") if x.strip() != ""]
        pc = 0
        stack_while = []
        
        while pc < len(lines):
            line = lines[pc]
            
            try:
                parts = line.split(maxsplit=1)
                if not parts:
                    pc += 1
                    continue

                match parts[0]:
                    case 'while':
                        condition = parts[1] if len(parts) > 1 else ""
                        if not condition:
                            raise Syntax_error("Missing while condition", pc+1)
                        
                        # Evaluate condition (e.g., "n 1 >=")
                        cond_result = self.ev_expr(condition, pc+1)
                        
                        if cond_result == 1:
                            stack_while.append(pc)  # Store loop start position
                            pc += 1  # Enter loop body
                        else:
                            # Skip to matching 'end'
                            depth = 1
                            pc += 1
                            while pc < len(lines) and depth > 0:
                                if lines[pc].strip().startswith('while'):
                                    depth += 1
                                elif lines[pc].strip().startswith('end'):
                                    depth -= 1
                                pc += 1
                            if depth != 0:
                                raise Syntax_error("Unclosed 'while' loop", pc+1)
                    
                    case 'end':
                        if not stack_while:
                            raise Syntax_error("Unmatched 'end'", pc+1)
                        pc = stack_while.pop()  # Jump back to 'while'
                        # No pc += 1 here - we want to re-evaluate the condition
                    case _:
                        if '=' in line:
                            name, expr = map(str.strip, line.split('=', 1))
                            if not name or not expr:
                                raise Syntax_error(f"Invalid assignment: '{line}'", pc+1)
                            self.vars[name] = self.ev_expr(expr, pc+1)
                        else:
                            raise Syntax_error(f"Invalid statement: '{line}'", pc+1)
                        pc += 1
            except Compiler_error as e:
                print(e)
                return
        
        print("\nExecution completed. Final variables:")
        for var, val in self.vars.items():
            print(f"{var} = {val}")

    def ev_expr(self, s, line_num=None):
        toks = s.split()
        stack = []
        for tok in toks:
            try:
                if tok.isdigit(): 
                    stack.append(int(tok))
                elif tok in self.vars: 
                    stack.append(self.vars[tok])
                else:
                    if tok not in ["+", "-", "*", ">="]:
                        raise Undefined_variable_error(f"Unknown variable or operator: '{tok}'", line_num)
                    
                    if len(stack) < 2:
                        raise Stack_underflow_error("Not enough operands for operator", line_num)

                    rhs = stack.pop()
                    lhs = stack.pop()
                    if tok == "+": stack.append(lhs + rhs)
                    elif tok == "*": stack.append(lhs * rhs)
                    elif tok == "-": stack.append(lhs - rhs)
                    elif tok == ">=": stack.append(1 if lhs >= rhs else 0)
            except Compiler_error as e:
                raise
            except Exception as e:
                raise Syntax_error(f"Invalid expression: '{s}' (details: {str(e)})", line_num)
        
        if not stack:
            raise Stack_underflow_error("Empty expression", line_num)
        return stack[0]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            Ev().ev(f.read())
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found")
