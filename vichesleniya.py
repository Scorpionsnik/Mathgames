import random
import fractions
from typing import List, Dict, Any, Tuple

class EquationGenerator:
    def __init__(self):
        self.variables = ['x', 'y', 'z']
    
    def decode_extended_mode(self, extended_mode: int) -> Dict[str, Any]:
        """Декодирует расширенный режим (64 бита) в конфигурацию"""
        config = {}
        
        # Извлекаем параметры из 64-битного числа
        examples_count = (extended_mode >> 32) & 0xFFFF
        old_extended_mode = extended_mode & 0xFFFFFFFF
        
        # Извлекаем параметры из старого 32-битного формата
        actions_count = (old_extended_mode >> 24) & 0xFF
        min_val = (old_extended_mode >> 16) & 0xFF
        encoded_max = (old_extended_mode >> 8) & 0xFF  # Зашифрованное максимальное число
        mode_number = old_extended_mode & 0xFF  # первые 8 бит - режим
        
        # Декодируем максимальное число
        max_val = self.decode_max_number(encoded_max)
        
        # Декодируем операции из первых 8 бит
        config['use_addition'] = bool(mode_number & 0b00000001)
        config['use_subtraction'] = bool(mode_number & 0b00000010)
        config['use_multiplication'] = bool(mode_number & 0b00000100)
        config['use_division'] = bool(mode_number & 0b00001000)
        config['use_negatives'] = bool(mode_number & 0b00010000)
        config['use_fractions'] = bool(mode_number & 0b00100000)
        config['use_decimals'] = bool(mode_number & 0b01000000)
        config['use_variables'] = bool(mode_number & 0b10000000)
        
        # Формируем список операций
        operations = []
        if config['use_addition']:
            operations.append('+')
        if config['use_subtraction']:
            operations.append('-')
        if config['use_multiplication']:
            operations.append('*')
        if config['use_division']:
            operations.append('/')
        
        config['operations'] = operations
        config['num_variables'] = 1 if config['use_variables'] else 0
        config['actions_count'] = actions_count if actions_count > 0 else 1
        config['number_range'] = (min_val, max_val)  # ИСПРАВЛЕНО: используем декодированные значения
        config['solution_range'] = config['number_range']
        config['examples_count'] = examples_count if examples_count > 0 else 10
        
        # Принцип оценки теперь хранится отдельно в grading_criteria
        config['grading_system'] = 'separate_column'  # Маркер что критерии в отдельной колонке
        
        return config
    
    def decode_max_number(self, encoded):
        """
        Декодирует максимальное число из зашифрованного формата
        Например: 12 -> 100 (1 и 2 нуля), 13 -> 1000 (1 и 3 нуля)
        """
        if encoded < 10:
            return 10  # По умолчанию 10
            
        first_digit = encoded // 10
        zeros_count = encoded % 10
        
        # Восстанавливаем число: первая цифра * 10^zeros_count
        decoded = first_digit * (10 ** zeros_count)
        return decoded
    
    def generate_from_extended_mode(self, extended_mode: int) -> Tuple[str, str, Any]:
        """Генерирует уравнение по расширенному режиму (64 бита)"""
        config = self.decode_extended_mode(extended_mode)
        return self.generate_equation_with_solution(config)
    
    def generate_equation_with_solution(self, config: Dict[str, Any]) -> Tuple[str, str, Any]:
        """
        Генерирует уравнение И его решение
        
        Возвращает: (уравнение, шаги решения, ответ)
        """
        self.config = config
        self._setup_config()
        
        # Определяем тип уравнения на основе доступных операций
        operations = config.get('operations', ['+', '-'])
        use_vars = config.get('use_variables', False)
        actions_count = config.get('actions_count', 1)
        
        if actions_count > 1 and use_vars:
            # Многошаговые выражения с переменными
            return self._generate_multi_step_equation_with_solution()
        elif actions_count > 1:
            # Многошаговые выражения без переменных
            return self._generate_multi_step_expression_with_solution()
        elif not use_vars:
            # Простые примеры без переменных
            return self._generate_simple_expression_with_solution()
        else:
            # Уравнения с переменными
            if len(operations) <= 2 and '*' not in operations and '/' not in operations:
                return self._generate_simple_equation_with_solution()
            else:
                return self._generate_complex_equation_with_solution()
    
    def _generate_multi_step_equation_with_solution(self) -> Tuple[str, str, Any]:
        """Многошаговое уравнение с переменными: 2x + 3 = 11"""
        operations = self.config.get('operations', ['+', '-'])
        use_negatives = self.config.get('use_negatives', False)
        min_val, max_val = self.config.get('number_range', (0, 10))  # ИЗМЕНЕНО: минимальное 0
        actions_count = min(self.config.get('actions_count', 2), 3)  # Ограничиваем сложность
        
        # Генерируем коэффициенты и решение
        x_solution = random.randint(max(1, min_val), max_val)  # ИЗМЕНЕНО: гарантируем минимум 1 для решения
        variable = self.variables[0]
        
        # Если умножение не разрешено, используем только x без коэффициента
        use_multiplication = self.config.get('use_multiplication', False)
        if use_multiplication:
            a = random.randint(1, min(5, max_val))
        else:
            a = 1  # Без умножения используем просто x
        
        b = random.randint(0, min(10, max_val))  # ИЗМЕНЕНО: b может быть 0
        c = a * x_solution + b
        
        # Форматируем уравнение
        if a == 1:
            term1 = variable
        else:
            term1 = f"{a}{variable}"
        
        if b == 0:
            equation = f"{term1} = {c}"
        elif b > 0:
            equation = f"{term1} + {b} = {c}"
        else:
            equation = f"{term1} - {abs(b)} = {c}"
        
        # Шаги решения
        steps = [f"{term1} + {b} = {c}"] if b != 0 else [f"{term1} = {c}"]
        
        if b != 0:
            steps.extend([
                f"{term1} = {c} - {b}",
                f"{term1} = {c - b}",
            ])
        
        if a != 1:
            steps.extend([
                f"{variable} = {c - b} / {a}",
                f"{variable} = {x_solution}"
            ])
        else:
            steps.append(f"{variable} = {x_solution}")
        
        solution_steps = "\n".join(steps)
        
        return equation, solution_steps, x_solution
    
    def _generate_multi_step_expression_with_solution(self) -> Tuple[str, str, Any]:
        """Многошаговое выражение без переменных: 5 + 3 × 2 = 11"""
        operations = self.config.get('operations', ['+', '-'])
        use_negatives = self.config.get('use_negatives', False)
        use_fractions = self.config.get('use_fractions', False)
        use_decimals = self.config.get('use_decimals', False)
        min_val, max_val = self.config.get('number_range', (0, 10))  # ИЗМЕНЕНО: минимальное 0
        actions_count = self.config.get('actions_count', 2)
        
        # Генерируем выражение с несколькими операциями
        expression_parts = []
        current_value = None
        steps = []
        
        for i in range(actions_count + 1):
            num = self._generate_number(use_negatives, use_fractions, use_decimals, min_val, max_val)
            
            if i == 0:
                expression_parts.append(str(num))
                current_value = num
                steps.append(f"Начальное значение: {num}")
            else:
                op = random.choice(operations)
                expression_parts.append(f"{op} {num}")
                
                # Вычисляем результат
                if op == '+':
                    result = self._add_numbers(current_value, num)
                    steps.append(f"{current_value} + {num} = {result}")
                elif op == '-':
                    result = self._subtract_numbers(current_value, num)
                    steps.append(f"{current_value} - {num} = {result}")
                elif op == '*':
                    result = self._multiply_numbers(current_value, num)
                    steps.append(f"{current_value} × {num} = {result}")
                else:  # '/'
                    # Для деления гарантируем корректный результат
                    if isinstance(current_value, int) and isinstance(num, int) and num != 0:
                        if current_value % num == 0:
                            result = current_value // num
                        else:
                            # Если не делится нацело, меняем числа местами
                            result = num
                            num = current_value
                            current_value = result * num
                            expression_parts[-1] = f"{op} {num}"
                            result = current_value
                            steps[-1] = f"Корректировка: {result} × {num} = {current_value}"
                    else:
                        result = self._divide_numbers(current_value, num)
                    steps.append(f"{current_value} ÷ {num} = {result}")
                
                current_value = result
        
        equation = " ".join(expression_parts) + " = ?"
        solution_steps = "\n".join(steps)
        
        return equation, solution_steps, current_value
    
    def _generate_simple_expression_with_solution(self) -> Tuple[str, str, Any]:
        """Простое выражение без переменных: 5 + 3 = 8"""
        operations = self.config.get('operations', ['+', '-'])
        use_negatives = self.config.get('use_negatives', False)
        use_fractions = self.config.get('use_fractions', False)
        use_decimals = self.config.get('use_decimals', False)
        min_val, max_val = self.config.get('number_range', (0, 10))  # ИЗМЕНЕНО: минимальное 0
        
        # Генерируем числа с учетом диапазона
        num1 = self._generate_number(use_negatives, use_fractions, use_decimals, min_val, max_val)
        num2 = self._generate_number(use_negatives, use_fractions, use_decimals, min_val, max_val)
        op = random.choice(operations)
        
        # Вычисляем результат
        if op == '+':
            result = self._add_numbers(num1, num2)
        elif op == '-':
            result = self._subtract_numbers(num1, num2)
        elif op == '*':
            result = self._multiply_numbers(num1, num2)
        else:  # '/'
            # Для деления гарантируем целый результат
            if isinstance(num1, int) and isinstance(num2, int) and num2 != 0:
                if num1 % num2 == 0:
                    result = num1 // num2
                else:
                    # Если не делится нацело, корректируем числа
                    result = num1
                    num1 = result * num2
            else:
                result = self._divide_numbers(num1, num2)
        
        equation = f"{num1} {op} {num2} = ?"
        steps = f"{num1} {op} {num2} = {result}"
        
        return equation, steps, result
    
    def _generate_simple_equation_with_solution(self) -> Tuple[str, str, Any]:
        """Уравнение вида: ax + b = c"""
        min_val, max_val = self.config.get('number_range', (0, 10))  # ИЗМЕНЕНО: минимальное 0
        solution_min, solution_max = self.config.get('solution_range', (1, 10))
        
        # Генерируем коэффициенты с учетом диапазона
        use_multiplication = self.config.get('use_multiplication', False)
        if use_multiplication:
            a = random.randint(1, min(5, max_val))
        else:
            a = 1  # Без умножения используем просто x
        
        b = random.randint(0, min(10, max_val))  # ИЗМЕНЕНО: b может быть 0
        
        # Гарантируем целое решение в заданном диапазоне
        x_solution = random.randint(solution_min, solution_max)
        c = a * x_solution + b
        
        variable = self.variables[0]
        
        # Форматируем уравнение
        if a == 1:
            term1 = variable
        else:
            term1 = f"{a}{variable}"
        
        if b == 0:
            equation = f"{term1} = {c}"
        elif b > 0:
            equation = f"{term1} + {b} = {c}"
        else:
            equation = f"{term1} - {abs(b)} = {c}"
        
        # Шаги решения
        steps = [f"{term1} + {b} = {c}"] if b != 0 else [f"{term1} = {c}"]
        
        if b != 0:
            steps.extend([
                f"{term1} = {c} - {b}",
                f"{term1} = {c - b}",
            ])
        
        if a != 1:
            steps.extend([
                f"{variable} = {c - b} / {a}",
                f"{variable} = {x_solution}"
            ])
        else:
            steps.append(f"{variable} = {x_solution}")
        
        solution_steps = "\n".join(steps)
        
        return equation, solution_steps, x_solution
    
    def _generate_complex_equation_with_solution(self) -> Tuple[str, str, Any]:
        """Сложное уравнение со скобками и разными операциями"""
        min_val, max_val = self.config.get('number_range', (0, 10))  # ИЗМЕНЕНО: минимальное 0
        solution_min, solution_max = self.config.get('solution_range', (1, 10))
        
        x_solution = random.randint(solution_min, solution_max)
        operations = self.config.get('operations', ['+', '-', '*'])
        use_multiplication = self.config.get('use_multiplication', False)
        
        # Выбираем тип уравнения в зависимости от доступных операций
        patterns = []
        
        if use_multiplication and '*' in operations:
            patterns.append({
                # (ax + b) * c = d
                'a': random.randint(2, min(4, max_val)),
                'b': random.randint(0, min(5, max_val)),  # ИЗМЕНЕНО: b может быть 0
                'c': random.randint(2, min(4, max_val)),
                'd': lambda a, b, c, x: (a * x + b) * c,
                'equation': lambda a, b, c, d: f"({a}x + {b}) * {c} = {d}" if b != 0 else f"({a}x) * {c} = {d}",
                'steps': lambda a, b, c, d, x: [
                    f"({a}x + {b}) * {c} = {d}" if b != 0 else f"({a}x) * {c} = {d}",
                    f"{a}x + {b} = {d} / {c}" if b != 0 else f"{a}x = {d} / {c}",
                    f"{a}x + {b} = {d // c}" if b != 0 else f"{a}x = {d // c}",
                    f"{a}x = {d // c} - {b}" if b != 0 else "",
                    f"{a}x = {d // c - b}" if b != 0 else "",
                    f"x = {d // c - b} / {a}" if b != 0 else f"x = {d // c} / {a}",
                    f"x = {x}"
                ]
            })
        
        if use_multiplication and '*' in operations and '+' in operations:
            patterns.append({
                # a(bx + c) + d = e
                'a': random.randint(2, min(3, max_val)),
                'b': random.randint(2, min(3, max_val)),
                'c': random.randint(0, min(4, max_val)),  # ИЗМЕНЕНО: c может быть 0
                'd': random.randint(0, min(6, max_val)),  # ИЗМЕНЕНО: d может быть 0
                'e': lambda a, b, c, d, x: a * (b * x + c) + d,
                'equation': lambda a, b, c, d, e: f"{a}({b}x + {c}) + {d} = {e}" if c != 0 and d != 0 else 
                                                f"{a}({b}x) + {d} = {e}" if c == 0 and d != 0 else
                                                f"{a}({b}x + {c}) = {e}" if c != 0 and d == 0 else
                                                f"{a}({b}x) = {e}",
                'steps': lambda a, b, c, d, e, x: [
                    f"{a}({b}x + {c}) + {d} = {e}" if c != 0 and d != 0 else 
                    f"{a}({b}x) + {d} = {e}" if c == 0 and d != 0 else
                    f"{a}({b}x + {c}) = {e}" if c != 0 and d == 0 else
                    f"{a}({b}x) = {e}",
                    f"{a}({b}x + {c}) = {e} - {d}" if d != 0 else "",
                    f"{a}({b}x + {c}) = {e - d}" if d != 0 else "",
                    f"{b}x + {c} = {e - d} / {a}" if d != 0 else f"{b}x + {c} = {e} / {a}",
                    f"{b}x + {c} = {(e - d) // a}" if d != 0 else f"{b}x + {c} = {e // a}",
                    f"{b}x = {(e - d) // a} - {c}" if c != 0 else "",
                    f"{b}x = {(e - d) // a - c}" if c != 0 else f"{b}x = {(e - d) // a}" if d != 0 else f"{b}x = {e // a}",
                    f"x = {(e - d) // a - c} / {b}" if c != 0 else f"x = {(e - d) // a} / {b}" if d != 0 else f"x = {e // a} / {b}",
                    f"x = {x}"
                ]
            })
        
        if '/' in operations:
            patterns.append({
                # (ax + b) / c = d
                'a': random.randint(2, min(4, max_val)) if use_multiplication else 1,
                'b': random.randint(0, min(5, max_val)),  # ИЗМЕНЕНО: b может быть 0
                'c': random.randint(2, min(3, max_val)),
                'd': lambda a, b, c, x: (a * x + b) // c,
                'equation': lambda a, b, c, d: f"({a}x + {b}) / {c} = {d}" if b != 0 else f"({a}x) / {c} = {d}",
                'steps': lambda a, b, c, d, x: [
                    f"({a}x + {b}) / {c} = {d}" if b != 0 else f"({a}x) / {c} = {d}",
                    f"{a}x + {b} = {d} * {c}" if b != 0 else f"{a}x = {d} * {c}",
                    f"{a}x + {b} = {d * c}" if b != 0 else f"{a}x = {d * c}",
                    f"{a}x = {d * c} - {b}" if b != 0 else "",
                    f"{a}x = {d * c - b}" if b != 0 else "",
                    f"x = {d * c - b} / {a}" if b != 0 else f"x = {d * c} / {a}",
                    f"x = {x}"
                ]
            })
        
        if not patterns:
            # Если нет подходящих сложных шаблонов, используем простой
            return self._generate_simple_equation_with_solution()
        
        pattern = random.choice(patterns)
        
        # Вычисляем параметры
        params = {}
        for key, value in pattern.items():
            if key not in ['equation', 'steps', 'e', 'd']:
                params[key] = value
        
        # Вычисляем правую часть
        if 'e' in pattern:
            params['e'] = pattern['e'](**params, x=x_solution)
        else:
            params['d'] = pattern['d'](**params, x=x_solution)
        
        equation = pattern['equation'](**params)
        steps_list = pattern['steps'](**params, x=x_solution)
        
        # Убираем пустые строки из шагов
        steps_list = [step for step in steps_list if step]
        
        solution_steps = "\n".join(steps_list)
        
        return equation, solution_steps, x_solution
    
    def _generate_number(self, use_negatives: bool, use_fractions: bool, use_decimals: bool, min_val=0, max_val=10) -> Any:
        """Генерирует число в зависимости от настроек"""
        if use_fractions and random.random() < 0.3:
            # Дробь
            numerator = random.randint(1, max_val)
            denominator = random.randint(2, max_val)
            return fractions.Fraction(numerator, denominator)
        
        elif use_decimals and random.random() < 0.2:
            # Десятичная дробь
            return round(random.uniform(max(0, min_val), max_val), 1)  # ИЗМЕНЕНО: гарантируем минимум 0
        
        else:
            # Целое число
            number = random.randint(min_val, max_val)
            if use_negatives and random.random() < 0.3 and number > 0:  # ИЗМЕНЕНО: избегаем отрицательного 0
                number = -number
            return number
    
    def _add_numbers(self, a, b):
        """Сложение чисел разных типов"""
        if isinstance(a, fractions.Fraction) or isinstance(b, fractions.Fraction):
            return fractions.Fraction(a) + fractions.Fraction(b)
        return a + b
    
    def _subtract_numbers(self, a, b):
        """Вычитание чисел разных типов"""
        if isinstance(a, fractions.Fraction) or isinstance(b, fractions.Fraction):
            return fractions.Fraction(a) - fractions.Fraction(b)
        return a - b
    
    def _multiply_numbers(self, a, b):
        """Умножение чисел разных типов"""
        if isinstance(a, fractions.Fraction) or isinstance(b, fractions.Fraction):
            return fractions.Fraction(a) * fractions.Fraction(b)
        return a * b
    
    def _divide_numbers(self, a, b):
        """Деление чисел разных типов"""
        if isinstance(a, fractions.Fraction) or isinstance(b, fractions.Fraction):
            return fractions.Fraction(a) / fractions.Fraction(b)
        return a / b
    
    def _setup_config(self):
        """Настраивает конфигурацию по умолчанию"""
        if 'operations' not in self.config:
            self.config['operations'] = ['+', '-']
        
        if 'number_range' not in self.config:
            self.config['number_range'] = (0, 10)  # ИЗМЕНЕНО: минимальное 0
        
        if 'actions_count' not in self.config:
            self.config['actions_count'] = 1
        
        if 'examples_count' not in self.config:
            self.config['examples_count'] = 10

# Готовые режимы для быстрого использования (старые 8-битные)
MODE_ONLY_ADD = 0b00000001                    # Только сложение
MODE_ADD_SUB = 0b00000011                     # + и -
MODE_ALL_BASIC = 0b00001111                   # + - × /
MODE_WITH_NEGATIVES = 0b00011111              # Все операции + отрицательные
MODE_WITH_FRACTIONS = 0b00101111              # Все операции + дроби
MODE_WITH_DECIMALS = 0b01001111               # Все операции + десятичные
MODE_SIMPLE_EQUATIONS = 0b10000011            # Простые уравнения: x + 5 = 8
MODE_COMPLEX_EQUATIONS = 0b10001111           # Сложные уравнения со всеми операциями
MODE_FULL = 0b11111111                        # Все включено

# Примеры использования
if __name__ == "__main__":
    generator = EquationGenerator()
    
    # Пример создания расширенного режима (64 бита)
    def create_extended_mode_64(examples_count, actions_count, min_val, max_val, mode_number):
        # Шифруем максимальное число
        def encode_max_number(max_number):
            if max_number <= 0:
                return 10
            num_str = str(max_number)
            if num_str[0] == '1' and all(digit == '0' for digit in num_str[1:]):
                first_digit = 1
                zeros_count = len(num_str) - 1
            else:
                first_digit = int(num_str[0])
                zeros_count = len(num_str) - 1
            return first_digit * 10 + zeros_count
        
        encoded_max = encode_max_number(max_val)
        old_extended_mode = (actions_count << 24) | (min_val << 16) | (encoded_max << 8) | mode_number
        extended_mode_64 = (examples_count << 32) | old_extended_mode
        return extended_mode_64
    
    print("=== ПРОСТЫЕ ВЫРАЖЕНИЯ (0-20, 2 действия, 15 примеров, стандартная оценка) ===")
    extended_mode = create_extended_mode_64(15, 2, 0, 20, MODE_ADD_SUB)
    config = generator.decode_extended_mode(extended_mode)
    print(f"Конфигурация: {config}")
    
    for i in range(2):
        equation, steps, answer = generator.generate_from_extended_mode(extended_mode)
        print(f"{i+1}. {equation}")
        print(f"   Ответ: {answer}")
        print(f"   Решение:\n{steps}")
        print()
    
    print("=== УРАВНЕНИЯ (0-50, 1 действие, 20 примеров, кастомная оценка: 18 правильных для 5) ===")
    extended_mode = create_extended_mode_64(20, 1, 0, 50, MODE_SIMPLE_EQUATIONS)
    config = generator.decode_extended_mode(extended_mode)
    print(f"Конфигурация: {config}")
    
    for i in range(2):
        equation, steps, answer = generator.generate_from_extended_mode(extended_mode)
        print(f"{i+1}. {equation}")
        print(f"   Ответ: x = {answer}")
        print(f"   Решение:\n{steps}")
        print()