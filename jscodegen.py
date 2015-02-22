from enum import Enum, IntEnum


class Syntax(Enum):
    BlockStatement = "BlockStatement"
    Program = "Program"
    ExpressionStatement = "ExpressionStatement"

STATEMENTS = {Syntax.BlockStatement, Syntax.Program}


class Precedence(IntEnum):
    Sequence = 0
    Yield = 1
    Await = 1
    Assignment = 1
    Conditional = 2
    ArrowFunction = 2
    LogicalOR = 3
    LogicalAND = 4
    BitwiseOR = 5
    BitwiseXOR = 6
    BitwiseAND = 7
    Equality = 8
    Relational = 9
    BitwiseSHIFT = 10
    Additive = 11
    Multiplicative = 12
    Unary = 13
    Postfix = 14
    Call = 15
    New = 16
    TaggedTemplate = 17
    Member = 18
    Primary = 19


BinaryPrecedence = {
    '||': Precedence.LogicalOR,
    '&&': Precedence.LogicalAND,
    '|': Precedence.BitwiseOR,
    '^': Precedence.BitwiseXOR,
    '&': Precedence.BitwiseAND,
    '==': Precedence.Equality,
    '!=': Precedence.Equality,
    '===': Precedence.Equality,
    '!==': Precedence.Equality,
    'is': Precedence.Equality,
    'isnt': Precedence.Equality,
    '<': Precedence.Relational,
    '>': Precedence.Relational,
    '<=': Precedence.Relational,
    '>=': Precedence.Relational,
    'in': Precedence.Relational,
    'instanceof': Precedence.Relational,
    '<<': Precedence.BitwiseSHIFT,
    '>>': Precedence.BitwiseSHIFT,
    '>>>': Precedence.BitwiseSHIFT,
    '+': Precedence.Additive,
    '-': Precedence.Additive,
    '*': Precedence.Multiplicative,
    '%': Precedence.Multiplicative,
    '/': Precedence.Multiplicative
}


class CodeGenerator:

    def __init__(self, options):
        pass


    def program(self, stmt):
        result = []
        for b in stmt['body']:
            result += self.generate_statement(b)
        return "".join(result)

    def expressionstatement(self, stmt):
        result = [self.generate_expression(stmt['expression'], Precedence.Sequence)]
        return " ".join(result)

    def binaryexpression(self, expr, precedence):
        operator = expr['operator']
        current_precedence = BinaryPrecedence[operator]
        result = [
            self.generate_expression(expr['left'], current_precedence),
            operator,
            self.generate_expression(expr['right'], current_precedence)
        ]
        return self.parenthesize(" ".join(result), current_precedence, precedence)

    def unaryexpression(self, expr, precedence):
        operator = expr['operator']
        result = operator + (" " if len(operator) > 2 else "") + self.generate_expression(expr['argument'], Precedence.Unary)
        return self.parenthesize(result, Precedence.Unary, precedence)

    def updateexpression(self, expr, precedence):
        operator = expr['operator']
        if expr["prefix"]:
            return self.parenthesize(operator + self.generate_expression(expr['argument'], Precedence.Unary), Precedence.Unary, precedence)
        else:
            return self.parenthesize(self.generate_expression(expr['argument'], Precedence.Postfix) + operator, Precedence.Postfix, precedence)

    def memberexpression(self, expr, precedence):
        result = [self.generate_expression(expr['object'], Precedence.Call) ]
        if expr['computed']:
            result += ["[", self.generate_expression(expr['property'], Precedence.Sequence), "]"]
        else:
            result += [".", self.generate_expression(expr['property'], Precedence.Sequence)]

        return self.parenthesize("".join(result), Precedence.Member, precedence);

    def callexpression(self, expr, precedence):
        result = [self.generate_expression(expr['callee'], Precedence.Call), '(' ]
        args = []
        for arg in expr['arguments']:
            args.append(self.generate_expression(arg, Precedence.Assignment))

        result.append(", ".join(args))
        result.append(')')
        return "".join(result)

    def identifier(self, expr, precedence):
        return self.generate_identifier(expr)

    def literal(self, expr, precedence):
        value = expr['value']
        # print(value)
        return str(value)

    def variabledeclaration(self, stmt):
        kind = stmt["kind"]
        declarations = []
        for declaration in stmt['declarations']:
            declarations.append(self.generate_statement(declaration))
        return kind + " " + ", ".join(declarations) + ";"

    def variabledeclarator(self, stmt):
        result = self.generate_expression(stmt['id'], Precedence.Assignment)
        if stmt['init']:
            result += " = " + self.generate_expression(stmt['init'], Precedence.Assignment)
        return result

    def functionexpression(self, expr, precedence):
        result = ['function']
        if expr['id']:
            result.append(self.generate_identifier(expr['id']))

        result.append(self.generate_function_body(expr))
        result.append(self.generate_statement(expr["body"]))
        return "".join(result)

    def blockstatement(self, stmt):
        result = " {\n"
        return result + "}"

    def parenthesize(self, text, current, should):
        if current < should:
            return '(' + text + ')'
        return text


    def is_statement(self, node):
        return Syntax(node["type"]) in STATEMENTS


    def generate_function_params(self, node):
        params = []
        for param in node['params']:
            params.append(self.generate_identifier(param))
        return '(' + ", ".join(params) + ')'

    def generate_function_body(self, node):
        result = self.generate_function_params(node)
        return result

    def generate_expression(self, expr, precedence):
        node_type = expr["type"]
        attr = getattr(self, node_type.lower())
        # print(attr, precedence)
        return attr(expr, precedence)

    def generate_statement(self, stmt):
        node_type = stmt["type"]
        attr = getattr(self, node_type.lower())
        # print(attr)
        return attr(stmt)

    def generate_identifier(self, node):
        return node["name"]

    def generate(self, node):
        if self.is_statement(node):
            return self.generate_statement(node)
        else:
            print("Unknown", node["type"])
        pass


def generate(node, options=None):
    g = CodeGenerator(options)
    return g.generate(node)
