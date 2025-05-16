import sys
class Compiler_error(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(f"Error (line {line}): {message}" if line else f"Error: {message}")
class Ev:
    def ev(self, s):
        self.vars = {}
        lines = [x for x in s.split("\n") if x.strip() != ""]
        pc = 0
        while pc < len(lines):
            line = lines[pc]
            match line.split(maxsplit=1)[0]:
                case 'while':
                    if self.ev_expr(line.split(maxsplit=1)[1]) == 1: pc += 1
                    else:
                        while lines[pc].split(maxsplit=1)[0] != 'end': pc += 1
                        pc += 1
                case 'end':
                    while lines[pc].split(maxsplit=1)[0] != 'while': pc -= 1
                case _:
                    (name, _, expr) = line.split(maxsplit=2)
                    self.vars[name] = self.ev_expr(expr)
                    pc += 1
        print(self.vars)
    def ev_expr(self, s):
        toks = s.split()
        stack = []
        for tok in toks:
            if tok.isdigit(): stack.append(int(tok))
            elif tok in self.vars: stack.append(self.vars[tok])
            else:
                rhs = stack.pop()
                lhs = stack.pop()
                if tok == "+": stack.append(lhs+rhs)
                elif tok == "*": stack.append(lhs*rhs)
                elif tok == "-": stack.append(lhs-rhs)
                elif tok == ">=":
                    if lhs >= rhs: stack.append(1)
                    else: stack.append(0)
        return stack[0]

Ev().ev(open(sys.argv[1]).read())
