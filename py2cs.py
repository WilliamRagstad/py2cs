"""
A transpiler that takes in a python source file, tokenizes it, parses the tokens into an AST, and then walk the AST emitting valid C# (C Sharp) code to an output file.
The source to source compiler should therefore create executable C# code.

Attempt to build a transpiler using OpenAI Codex:
https://beta.openai.com/playground/p/default-english-to-python
"""

import sys
import argparse
import ast

from token import *
from ast import *

# Emit C sharp code to a file from an ast tree, taking the filepath and tree as input.


def emit_csharp(filepath, tree):
    # Open the filepath to write
    # Walk the AST tree and emit C# code to the file descriptor
    with open(filepath, 'w') as f:
        f.write("using System;\n")
        f.write(
            "public class Program {\n\tpublic static void Main(string[] args) {\n")
        f.write(walk_tree(tree))
        f.write("}\n}\n")


def walk_tree(tree):
    # The root node of the AST tree is the module node.
    # The module node contains a list of statements.
    # We will walk the list of statements and emit C# code for each statement.
    csharp = ''
    for statement in tree.body:
        csharp += walk_statement(statement)
    return csharp


def walk_statement(statement: stmt):
    # The statement node can be one of the following:
    # - FunctionDef
    # - ClassDef
    # - Return
    # - Assign
    # - For
    # - While
    # - If
    # - Expression
    if isinstance(statement, FunctionDef):
        return walk_function_def(statement)
    elif isinstance(statement, ClassDef):
        return walk_class_def(statement)
    elif isinstance(statement, Return):
        return walk_return(statement)
    elif isinstance(statement, Assign):
        return walk_assign(statement)
    elif isinstance(statement, For):
        return walk_for(statement)
    elif isinstance(statement, While):
        return walk_while(statement)
    elif isinstance(statement, If):
        return walk_if(statement)
    elif isinstance(statement, Expr):
        return walk_expression(statement.value) + ';\n'
    else:
        raise Exception("Unsupported statement type: " + str(type(statement)))


def walk_function_def(function_def: FunctionDef):
    # The function_def node contains the following fields:
    # - name
    # - args
    # - body
    # - decorator_list
    # - returns

    # Output a function definition of the following form:
    # <return_type> <name>(<type and identifier pairs separated by ,>) {
    #    <body>
    # }
    #
    # Example:
    # int add(int a, int b) {
    #    return a + b;
    # }
    #
    # First calculate the return type of the function_def node returns field using the get_expression_return_type function.
    # Then calculate the argument list of the function_def node args field using the walk_argument_list function.
    # Then calculate the body of the function_def node body field using the walk_statements function.
    # Finally, return the function definition string.
    return_type = get_expression_return_type(function_def.returns)
    name = function_def.name
    argument_list = walk_argument_list(function_def.args)
    body = walk_statements(function_def.body)
    return return_type + ' ' + name + '(' + argument_list + ') {\n' + body + '\n}'


def walk_class_def(class_def):
    # The class_def node contains the following fields:
    # - name
    # - bases
    # - body
    # - decorator_list

    # Output a class definition of the following form:
    # class <name> (: <base class list>) {
    #    <private fields>
    #    <constructor>
    #    <public fields>
    #    <methods>
    # }
    #
    # Example:
    # class Person : Human {
    #    private string name;
    #    private int age;
    #
    #    public Person(string name, int age) {
    #        this.name = name;
    #        this.age = age;
    #    }
    #
    #    public string Lastname;
    #    public string getAge() { return age; }
    # }
    #
    # First calculate the name of the class_def node name field using the get_expression_name function.
    # Then calculate the base class list of the class_def node bases field using the get_expression_base_class_list function.
    # Then calculate the body of the class_def node body field using the walk_class_body function.
    # Finally, return the class definition string.
    name = class_def.name
    base_class_list = walk_base_class_list(class_def.bases)
    body = walk_class_body(class_def.body)
    return 'class ' + name + ' : ' + base_class_list + ' {\n' + body + '\n}'


def walk_base_class_list(base_class_list):
    # The base_class_list node contains the following fields:
    # - bases
    #
    # Example:
    # class Person : Human, LivingBeing {
    #    private string name;
    #    private int age;
    #
    #    public Person(string name, int age) {
    #        this.name = name;
    #        this.age = age;
    #    }
    #
    #    public string Lastname;
    #    public string getAge() { return age; }
    # }
    #
    # First calculate the base class list string of the base_class_list node bases field using the walk_expression_list function.
    # Then return the base class list string.
    return walk_expression_list(base_class_list.bases)


def walk_class_body(class_body):
    # The class_body node contains the following fields:
    # - body
    #
    # Example:
    # class Person : Human, LivingBeing {
    #    private string name;
    #    private int age;
    #
    #    public Person(string name, int age) {
    #        this.name = name;
    #        this.age = age;
    #    }
    #
    #    public string Lastname;
    #    public string getAge() { return age; }
    # }
    #
    # First calculate the body string of the class_body node body field using the walk_statements function.
    # Then return the body string.
    return walk_statements(class_body)


def walk_return(return_statement):
    # The return_statement node contains the following fields:
    # - value
    #
    # Example:
    # return a + b;
    #
    # First calculate the return expression string of the return_statement node value field using the walk_expression function.
    # Then return the return statement string.
    return 'return ' + walk_expression(return_statement.value) + ';'


def walk_assign(assign_statement: Assign):
    # The assign_statement node contains the following fields:
    # - targets
    # - value
    #
    # Example:
    # a = b + c;
    #
    # Only assign to the value to first target in the targets list.
    # First calculate the target string of the first target in the assign_statement node targets field using the walk_expression function.
    # Then calculate the value string of the assign_statement node value field using the walk_expression function.
    # Then return the assignment statement string.
    return get_expression_return_type(assign_statement.value) + ' ' + walk_expression(assign_statement.targets[0]) + ' = ' + walk_expression(assign_statement.value) + ';\n'


def walk_for(for_statement):
    # The for_statement node contains the following fields:
    # - target
    # - iter
    # - body
    # - orelse
    #
    # Example:
    # for (int i = 0; i < 10; i++) {
    #    print(i);
    # }
    #
    # First calculate the target string of the for_statement node target field using the walk_expression function.
    # Then calculate the iter string of the for_statement node iter field using the walk_expression function.
    # Then calculate the body string of the for_statement node body field using the walk_statements function.
    # Finally, return the for statement string.
    return 'for (' + walk_expression(for_statement.target) + ' = ' + walk_expression(for_statement.iter) + ') {\n' + walk_statements(for_statement.body) + '\n}'


def walk_while(while_statement):
    # The while_statement node contains the following fields:
    # - test
    # - body
    # - orelse
    #
    # Example:
    # while (i < 10) {
    #    print(i);
    #    i++;
    # }
    #
    # First calculate the test string of the while_statement node test field using the walk_expression function.
    # Then calculate the body string of the while_statement node body field using the walk_statements function.
    # Finally, return the while statement string.
    return 'while (' + walk_expression(while_statement.test) + ') {\n' + walk_statements(while_statement.body) + '\n}'


def walk_if(if_statement: If):
    # The if_statement node contains the following fields:
    # - test
    # - body
    # - orelse
    #
    # Example:
    # if (i < 10) {
    #    print(i);
    # }
    #
    # First calculate the test string of the if_statement node test field using the walk_expression function.
    # Then calculate the body string of the if_statement node body field using the walk_statements function.
    # Finally, return the if statement string.
    if (len(if_statement.orelse) == 0):
        return 'if (' + walk_expression(if_statement.test) + ') {\n\t' + walk_statements(if_statement.body) + '}\n'
    else:
        return 'if (' + walk_expression(if_statement.test) + ') {\n\t' + walk_statements(if_statement.body) + '}\n' + 'else {\n\t' + walk_statements(if_statement.orelse) + '}\n'


def walk_statements(statements: list[stmt]):
    # Call walk_statement for each statement in the statements.body list.
    # Return the statements string.
    return '\n'.join([walk_statement(statement) for statement in statements])


def walk_expression(expression: expr):
    # The expression node can be one of the following:
    # - BinOp
    # - UnaryOp
    # - Lambda
    # - Array
    # - Call
    # - Num
    # - Str
    # - Identifier
    # - New Class
    # Have a switch statement covering all the cases above.
    # For each case, call the appropriate walk function.
    # The walk function should return the string representation of the expression.
    if isinstance(expression, BinOp):
        return walk_bin_op(expression)
    if isinstance(expression, BoolOp):
        return walk_bin_op(expression)
    elif isinstance(expression, Compare):
        return walk_comp_op(expression)
    elif isinstance(expression, UnaryOp):
        return walk_unary_op(expression)
    elif isinstance(expression, Lambda):
        return walk_lambda(expression)
    elif isinstance(expression, Call):
        return walk_call(expression)
    elif isinstance(expression, Num):
        return walk_num(expression)
    elif isinstance(expression, Str):
        return walk_str(expression)
    elif isinstance(expression, Name):
        return walk_name(expression)
    else:
        raise Exception("Unsupported expression type: " +
                        str(type(expression)))


def get_bin_op_symbol(op: operator):
    if op.__class__.__name__ == 'Add':
        return '+'
    elif op.__class__.__name__ == 'Sub':
        return '-'
    elif op.__class__.__name__ == 'Mult':
        return '*'
    elif op.__class__.__name__ == 'Div':
        return '/'
    elif op.__class__.__name__ == 'Mod':
        return '%'
    elif op.__class__.__name__ == 'Pow':
        return '**'
    elif op.__class__.__name__ == 'LShift':
        return '<<'
    elif op.__class__.__name__ == 'RShift':
        return '>>'
    elif op.__class__.__name__ == 'BitOr':
        return '|'
    elif op.__class__.__name__ == 'BitXor':
        return '^'
    elif op.__class__.__name__ == 'BitAnd':
        return '&'
    elif op.__class__.__name__ == 'FloorDiv':
        return '//'
    elif op.__class__.__name__ == 'Eq':
        return '=='
    elif op.__class__.__name__ == 'NotEq':
        return '!='
    elif op.__class__.__name__ == 'Lt':
        return '<'
    elif op.__class__.__name__ == 'LtE':
        return '<='
    elif op.__class__.__name__ == 'Gt':
        return '>'
    elif op.__class__.__name__ == 'GtE':
        return '>='
    else:
        raise Exception("Unsupported binary operator: " +
                        str(op))


def walk_bin_op(bin_op: BinOp):
    # The bin_op node contains the following fields:
    # - op
    # - left
    # - right
    #
    # Example:
    # a + b;
    #
    # First calculate the left string of the bin_op node left field using the walk_expression function.
    # Then calculate the right string of the bin_op node right field using the walk_expression function.
    # Finally, return the binary operation string.
    return walk_expression(bin_op.left) + ' ' + get_bin_op_symbol(bin_op.op) + ' ' + walk_expression(bin_op.right)


def walk_comp_op(comp_op: Compare):
    # The comp_op node contains the following fields:
    # - ops
    # - left
    # - comparators
    #
    # Example:
    # a < b;
    #
    # First calculate the left string of the comp_op node left field using the walk_expression function.
    # Then calculate the comparators string of the comp_op node comparators field using the walk_expression function.
    # Finally, return the comparision operation string.
    return walk_expression(comp_op.left) + ' ' + ' '.join([get_bin_op_symbol(comp_op.ops[i]) + ' ' + walk_expression(comp_op.comparators[i]) for i in range(len(comp_op.comparators))])


def walk_unary_op(unary_op):
    # The unary_op node contains the following fields:
    # - op
    # - operand
    #
    # Example:
    # -a;
    #
    # First calculate the operand string of the unary_op node operand field using the walk_expression function.
    # Then return the unary operation string.
    return unary_op.op.__class__.__name__ + ' ' + walk_expression(unary_op.operand)


def walk_lambda(lambda_expression):
    # The lambda_expression node contains the following fields:
    # - args
    # - body
    #
    # Example:
    # (a, b) => a + b;
    #
    # First calculate the argument list string of the lambda_expression node args field using the walk_argument_list function.
    # Then calculate the body string of the lambda_expression node body field using the walk_expression function.
    # Finally, return the lambda expression string.
    return '(' + walk_argument_list(lambda_expression.args) + ') => ' + walk_expression(lambda_expression.body)


def lookup_call_builtins(function_name):
    if function_name == 'print':
        return 'Console.WriteLine'
    elif function_name == 'input':
        return 'Console.ReadLine'
    else:
        return function_name


def walk_call(call: Call):
    # The call node contains the following fields:
    # - func
    # - args
    #
    # Example:
    # print(a);
    #
    # First calculate the function string of the call node func field using the walk_expression function.
    # Then calculate the argument list string of the call node args field using the walk_expression_list function.
    # Finally, return the call string.
    return lookup_call_builtins(walk_expression(call.func)) + '(' + walk_expression_list(call.args) + ')'


def walk_num(num):
    # The num node contains the following fields:
    # - n
    #
    # Example:
    # 1;
    #
    # Return the number string.
    return str(num.n)


def walk_str(str):
    # The str node contains the following fields:
    # - s
    #
    # Example:
    # "hello";
    #
    # Return the string string.
    return '"' + str.s + '"'


def walk_name(name):
    # The name node contains the following fields:
    # - id
    #
    # Example:
    # a;
    #
    # Return the identifier string.
    return name.id


def walk_argument_list(argument_list):
    # The argument_list node contains the following fields:
    # - args
    #
    # Example:
    # dynamic a, dynamic b, dynamic c;
    #
    # For each args in argument_list, get their name and add the text "dynamic in front" separated by commas.
    # Then return the argument list string.
    return ', '.join(['dynamic ' + argument.arg for argument in argument_list.args])


def walk_expression_list(expression_list: list[expr]):
    # The expression_list node contains the following fields:
    # - elts
    #
    # Example:
    # [1, 2, 3];
    #
    # For each elts in expression_list, get their name and add the text "dynamic in front" separated by commas.
    # Then return the expression list string.
    return ', '.join([walk_expression(expression) for expression in expression_list])


def get_expression_return_type(expression: expr):
    if isinstance(expression, Num):
        return 'int'
    elif isinstance(expression, Str):
        return 'string'
    elif isinstance(expression, Name):
        return 'dynamic'
    elif isinstance(expression, Call):
        return 'dynamic'
    elif isinstance(expression, BinOp):
        return 'dynamic'
    elif isinstance(expression, Compare):
        return 'bool'
    elif isinstance(expression, UnaryOp):
        return 'dynamic'
    elif isinstance(expression, Lambda):
        return 'dynamic'
    elif isinstance(expression, FunctionDef):
        return 'dynamic'
    elif expression == None:
        return 'dynamic'
    else:
        return get_expression_return_type(expression.value)


def main(argv):
    # Parse the command line arguments
    parser = argparse.ArgumentParser(
        description='Transpiler from Python to C#')
    parser.add_argument('input', help='The input python source file')
    parser.add_argument('output', help='The output C# source file')
    args = parser.parse_args()

    # Open the input source file
    with open(args.input, 'r') as input_file:
        # Read the input source file
        source = input_file.read()
        # Parse the source into an AST
        tree = ast.parse(source)
        # Emit the C# code to the output file
        emit_csharp(args.output, tree)


if __name__ == "__main__":
    main(sys.argv)
