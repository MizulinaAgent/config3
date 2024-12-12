import sys
import xml.etree.ElementTree as ET


class CommentedTreeBuilder(ET.TreeBuilder):
    def comment(self, data):
        self.start(ET.Comment, {})
        self.data(data)
        self.end(ET.Comment)


def parse_xml(filename):
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    try:
        tree = ET.parse(filename, parser=parser)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        sys.stderr.write(f"Ошибка парсинга XML: {e}\n")
        sys.exit(1)


def extract_constants(root):
    constants = {}
    constants_section = root.find('constants')
    if constants_section is not None:
        for c in constants_section.findall('const'):
            name = c.get('name')
            value = (c.text.strip() if c.text else "")
            if not name:
                sys.stderr.write("Константа без атрибута имени.\n")
                sys.exit(1)
            constants[name] = value
    return constants


def extract_dicts(root, constants):
    dicts = {}
    dicts_section = root.find('dicts')
    if dicts_section is not None:
        for d in dicts_section.findall('dict'):
            name = d.get('name')
            if not name:
                sys.stderr.write("Словарь без атрибута имени.\n")
                sys.exit(1)
            items = []
            for item in d.findall('item'):
                key = item.get('key')
                val = (item.text.strip() if item.text else "")
                if not key:
                    sys.stderr.write("Элемент без ключа.\n")
                    sys.exit(1)
                # Проверяем, является ли значение выражением
                if val.startswith("@{"):
                    val = str(evaluate_expression(val, constants))
                items.append((key, val))
            dicts[name] = items
    return dicts


def evaluate_expression(expr, constants):
    inner = expr[2:-1].strip()
    tokens = inner.split()
    stack = []

    def get_value(token):
        if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
            return int(token)
        if token in constants:
            val = constants[token]
            if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                return int(val)
            else:
                sys.stderr.write(f"Константа '{token}' не является числом.\n")
                sys.exit(1)
        sys.stderr.write(f"Неизвестный токен '{token}' в выражении.\n")
        sys.exit(1)

    def apply_op(op, args):
        if op == '+':
            return args[0] + args[1]
        elif op == '-':
            return args[0] - args[1]
        elif op == '*':
            return args[0] * args[1]
        elif op.startswith('max(') and op.endswith(')'):
            return max(args[0], args[1])
        elif op.startswith('mod(') and op.endswith(')'):
            return args[0] % args[1]
        else:
            sys.stderr.write(f"Неизвестная операция '{op}'.\n")
            sys.exit(1)

    for t in tokens:
        if t in ['+', '-', '*'] or t.startswith('max(') or t.startswith('mod('):
            if len(stack) < 2:
                sys.stderr.write("Недостаточно аргументов в стеке для операции.\n")
                sys.exit(1)
            b = stack.pop()
            a = stack.pop()
            res = apply_op(t, [a, b])
            stack.append(res)
        else:
            val = get_value(t)
            stack.append(val)

    if len(stack) != 1:
        sys.stderr.write("Неверная оценка выражения.\n")
        sys.exit(1)
    return stack[0]


def append_comment_node(comment_text, output_lines):
    output_lines.append("<!--")
    lines = comment_text.splitlines()
    for line in lines:
        output_lines.append(line)
    output_lines.append("-->")


def traverse_and_collect(node, output_lines):
    if node.text and node.text.strip().startswith("||"):
        output_lines.append(node.text.strip())

    for child in node:
        if child.tag is ET.Comment:
            append_comment_node(child.text, output_lines)
            if child.tail and child.tail.strip().startswith("||"):
                output_lines.append(child.tail.strip())
        else:
            traverse_and_collect(child, output_lines)

    if node.tail and node.tail.strip().startswith("||"):
        output_lines.append(node.tail.strip())


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Использование: py Transit.py input.xml\n")
        sys.exit(1)

    input_file = sys.argv[1]
    root = parse_xml(input_file)

    comment_lines = []
    traverse_and_collect(root, comment_lines)

    constants = extract_constants(root)
    dicts = extract_dicts(root, constants)

    output_lines = []
    for line in comment_lines:
        output_lines.append(line)

    for name, value in constants.items():
        output_lines.append(f"{value} -> {name}")

    for dname, items in dicts.items():
        dict_str = ", ".join([f"{k} = {v}" for (k, v) in items])
        output_lines.append(f"dict( {dict_str} ) -> {dname}")

    eval_section = root.find('eval')
    if eval_section is not None:
        for expr_el in eval_section.findall('expression'):
            expr_text = expr_el.text.strip() if expr_el.text else ""
            if expr_text.startswith("@{"):
                res = evaluate_expression(expr_text, constants)
                output_lines.append(str(res))
            else:
                output_lines.append(expr_text)

    with open("output.txt", "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")


if __name__ == "__main__":
    main()
