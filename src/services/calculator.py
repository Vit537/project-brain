"""
Calculator Service
Performs mathematical calculations - local, no internet
"""
import re
from colorama import Fore, Style, init

init(autoreset=True)


class Calculator:
    """Handles mathematical calculations"""
    
    @staticmethod
    def calculate(expression):
        """
        Safely evaluate a mathematical expression
        
        Args:
            expression (str): Math expression like "2 + 2" or "10 * 5"
            
        Returns:
            tuple: (success: bool, result: str)
        """
        try:
            # Remove spaces
            expr = expression.replace(" ", "")
            
            # Whitelist: only allow numbers, operators, parentheses, decimal points
            if not re.match(r'^[0-9+\-*/.()]+$', expr):
                return False, "Invalid expression"
            
            # Prevent dangerous patterns
            if '..' in expr or expr.count('(') != expr.count(')'):
                return False, "Invalid expression"
            
            # Evaluate safely
            result = eval(expr)
            
            # Format result
            if isinstance(result, float):
                if result == int(result):
                    return True, str(int(result))
                else:
                    return True, f"{result:.2f}"
            return True, str(result)
            
        except ZeroDivisionError:
            return False, "Cannot divide by zero"
        except Exception as e:
            return False, "Invalid calculation"
    
    @staticmethod
    def format_result(expression, result, language='en'):
        """Format calculation result for speech"""
        if language == 'es':
            return f"{expression} es igual a {result}"
        else:
            return f"{expression} equals {result}"
