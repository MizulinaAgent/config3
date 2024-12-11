import io
import sys
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch, mock_open

# Импортируем тестируемые функции из исходного кода
from Transit import (
    parse_xml,
    extract_constants,
    extract_dicts,
    evaluate_expression,
    traverse_and_collect,
    CommentedTreeBuilder
)

class TestTransit(unittest.TestCase):
    def setUp(self):
        # Пример простого XML для тестов
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <constants>
        <const name="CONST_ONE">10</const>
        <const name="CONST_TWO">20</const>
    </constants>
    <dicts>
        <dict name="test_dict">
            <item key="key1">val1</item>
            <item key="key2">val2</item>
        </dict>
    </dicts>
    <eval>
        <expression>@{ CONST_ONE CONST_TWO + }</expression>
        <expression>@{ CONST_TWO 5 * }</expression>
        <expression>Just a text</expression>
    </eval>
    <!-- Комментарий -->
</root>
        """

        # Файл с неправильным XML для проверки ошибки парсинга
        self.invalid_xml = """<root>
            <constants>
                <const name="C1">10</const>
            </constants>
            <!-- отсутствующий закрывающий тег
        """

        # XML с некорректными данными для вычисления выражения
        self.invalid_expr_xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <constants>
        <const name="A">abc</const>
    </constants>
    <eval>
        <expression>@{ A 10 + }</expression>
    </eval>
</root>
        """

    def test_parse_xml_valid(self):
        # Проверяем, что парсер возвращает корневой элемент при корректном XML
        with patch('builtins.open', mock_open(read_data=self.sample_xml)):
            root = parse_xml('fakefile.xml')
            self.assertEqual(root.tag, 'root')

    def test_parse_xml_invalid(self):
        # Проверяем, что при неверном XML парсер завершит работу с ошибкой
        with patch('builtins.open', mock_open(read_data=self.invalid_xml)), \
             patch('sys.stderr', new_callable=io.StringIO) as fake_stderr, \
             self.assertRaises(SystemExit):
            parse_xml('fakefile.xml')
        self.assertIn("Ошибка парсинга XML", fake_stderr.getvalue())

    def test_extract_constants(self):
        # Проверяем корректность извлечения констант
        root = ET.fromstring(self.sample_xml)
        constants = extract_constants(root)
        self.assertIn("CONST_ONE", constants)
        self.assertEqual(constants["CONST_ONE"], "10")
        self.assertIn("CONST_TWO", constants)
        self.assertEqual(constants["CONST_TWO"], "20")

    def test_extract_dicts(self):
        # Проверяем корректность извлечения словарей
        root = ET.fromstring(self.sample_xml)
        dicts = extract_dicts(root)
        self.assertIn("test_dict", dicts)
        self.assertEqual(dicts["test_dict"], [("key1", "val1"), ("key2", "val2")])

    def test_evaluate_expression(self):
        # Проверяем вычисление выражений с константами
        constants = {"CONST_ONE": "10", "CONST_TWO": "20"}
        res = evaluate_expression("@{ CONST_ONE CONST_TWO + }", constants)
        self.assertEqual(res, 30)
        res = evaluate_expression("@{ CONST_TWO 5 * }", constants)
        self.assertEqual(res, 100)

    def test_evaluate_expression_error_unknown_token(self):
        # Проверяем обработку неизвестного токена
        constants = {"A": "1"}
        with patch('sys.stderr', new_callable=io.StringIO) as fake_stderr, \
             self.assertRaises(SystemExit):
            evaluate_expression("@{ B 10 + }", constants)
        self.assertIn("Неизвестный токен 'B'", fake_stderr.getvalue())

    def test_evaluate_expression_error_non_numeric_const(self):
        # Проверяем обработку константы, которая не является числом
        root = ET.fromstring(self.invalid_expr_xml)
        constants = extract_constants(root)
        with patch('sys.stderr', new_callable=io.StringIO) as fake_stderr, \
             self.assertRaises(SystemExit):
            evaluate_expression("@{ A 10 + }", constants)
        self.assertIn("Константа 'A' не является числом", fake_stderr.getvalue())

    def test_traverse_and_collect(self):
        # Проверяем сбор комментариев и текстов
        # Добавим текстовые узлы с префиксом "||", чтобы проверить логику
        test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    ||Текст в корне
    <child>||Текст в элементе</child>
    <!-- Комментарий -->
    ||Хвостовой текст
</root>"""
        root = ET.fromstring(test_xml, parser=ET.XMLParser(target=CommentedTreeBuilder()))
        output_lines = []
        traverse_and_collect(root, output_lines)
        self.assertIn("||Текст в корне", output_lines)
        self.assertIn("||Текст в элементе", output_lines)
        self.assertIn("<!--", output_lines)  # начало комментария
        self.assertIn(" Комментарий ", output_lines)
        self.assertIn("-->", output_lines)
        self.assertIn("||Хвостовой текст", output_lines)


if __name__ == "__main__":
    unittest.main()
