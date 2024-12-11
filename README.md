# Задание №3 Индивидуальный вариант №19
## Постановка задачи

Разработать инструмент командной строки для учебного конфигурационного
языка, синтаксис которого приведен далее. Этот инструмент преобразует текст из
входного формата в выходной. Синтаксические ошибки выявляются с выдачей
сообщений.

Входной текст на языке xml принимается из стандартного ввода. Выходной
текст на учебном конфигурационном языке попадает в файл, путь к которому
задан ключом командной строки.

### Однострочные комментарии:

|| Это однострочный комментарий

### Многострочные комментарии:

<!--
Это многострочный
комментарий
-->

### Словари:

dict(
 имя = значение,
 имя = значение,
 имя = значение,
 ...
)

### Имена:

[a-zA-Z][a-zA-Z0-9]*

### Значения:

• Числа.

• Строки.

• Словари.

### Строки:

[[Это строка]]

### Объявление константы на этапе трансляции:

значение -> имя

### Вычисление константного выражения на этапе трансляции (постфиксная форма), пример:

@{имя 1 +}

Результатом вычисления константного выражения является значение.

### Для константных вычислений определены операции и функции:

1. Сложение.

2. Вычитание.

3. Умножение.

4. max().

5. mod().

Все конструкции учебного конфигурационного языка (с учетом их
возможной вложенности) должны быть покрыты тестами.

## Описание функций, используемых для моделирования работы строки

### CommentedTreeBuilder

Расширяет стандартный ET.TreeBuilder, чтобы поддерживать комментарии в XML. Позволяет обрабатывать узлы с комментариями в XML-документе.

### parse_xml(filename)

Парсит XML-файл с использованием CommentedTreeBuilder. Возвращает корневой узел дерева. Если возникает ошибка парсинга, выводит сообщение об ошибке и завершает выполнение программы.

### extract_constants(root)

Извлекает секцию <constants> из корневого XML-узла. Возвращает словарь, где ключи — имена констант, а значения — их значения. Проверяет наличие имени для каждой константы.

### extract_dicts(root)

Извлекает секцию <dicts> из корневого XML-узла. Возвращает словарь, где ключи — имена словарей, а значения — списки пар (ключ, значение). Проверяет наличие имени у словарей и ключей у их элементов.

### evaluate_expression(expr, constants)

Вычисляет значение арифметического выражения, заданного в формате @{...}, используя числовые значения и константы. Поддерживает операции сложения, вычитания, умножения, max, mod. Если возникает ошибка, выводит сообщение об ошибке и завершает выполнение.

### append_comment_node(comment_text, output_lines)

Добавляет многострочные комментарии (начинающиеся с <!-- и заканчивающиеся -->) в список выходных строк.

### traverse_and_collect(node, output_lines)

Рекурсивно обходит XML-дерево. Извлекает текстовые комментарии (начинающиеся с ||) и узлы с комментариями, добавляя их в выходной список.

## Запуск программы

py Transit.py <входной файл>.xml

## Тестики

В один файл все запихнул, вот как оно выглядит

![image](https://github.com/user-attachments/assets/c6e6b86c-6394-447c-bc18-ff2c04b8bedc)

И вот аутпут 

![image](https://github.com/user-attachments/assets/7350557e-6b47-4169-9f28-24878d853d4a)

Юниттест

![image](https://github.com/user-attachments/assets/9dec0855-d5cc-4f30-b1f3-d9487b67922a)

Традиция

![IMG_1463 (1)](https://github.com/user-attachments/assets/6f0a4559-7824-4aab-acea-54d282e56430)









