import sympy as sp
import re

class MathEngine:
    def _solve_equation(self, expression) -> str:
        """Solve equations with one or more variables"""
        try:
            # Split by = sign
            left, right = expression.split('=', 1)
            
            # Parse both sides
            left_expr = sp.sympify(left)
            right_expr = sp.sympify(right)
            
            # Create equation
            eq = sp.Eq(left_expr, right_expr)
            
            # Find variables
            variables = list(eq.free_symbols)
            
            if not variables:
                # No variables, just check if equation is true
                return str(left_expr.equals(right_expr))
            
            # Solve for variables
            solutions = sp.solve(eq, variables)
            
            if isinstance(solutions, dict):
                # Multiple variables
                result_parts = []
                for var, val in solutions.items():
                    result_parts.append(f"{var} = {val}")
                return ", ".join(result_parts)
            elif isinstance(solutions, list):
                if len(variables) == 1:
                    # Single variable, multiple solutions
                    var = variables[0]
                    if len(solutions) == 1:
                        return f"{var} = {solutions[0]}"
                    else:
                        return f"{var} = {solutions}"
                else:
                    return str(solutions)
            else:
                return str(solutions)
                
        except Exception as e:
            return f"Error solving equation: {str(e)}"

    def _handle_special_functions(self, expression) -> str:
        """Handle special mathematical functions"""
        try:
            # Replace common function names with SymPy equivalents
            expr = expression.replace('gcd(', 'sp.gcd(')
            expr = expression.replace('lcm(', 'sp.lcm(')
            expr = expression.replace('factorial(', 'sp.factorial(')
            expr = expression.replace('binomial(', 'sp.binomial(')
            expr = expression.replace('factor(', 'sp.factorint(')
            expr = expression.replace('prime(', 'sp.prime(')
            
            # Evaluate the expression
            result = eval(expr, {"sp": sp, "__builtins__": {}})
            return str(result)
            
        except Exception as e:
            return f"Error with special function: {str(e)}"

    def _handle_modular_arithmetic(self, expression) -> str:
        """Handle modular arithmetic expressions"""
        try:
            # Pattern: number mod modulus
            pattern = r'(\d+|\([^)]+\))\s*mod\s*(\d+)'
            match = re.search(pattern, expression, re.IGNORECASE)
            
            if match:
                base_expr = match.group(1)
                modulus = int(match.group(2))
                
                # Evaluate the base expression first
                if base_expr.startswith('(') and base_expr.endswith(')'):
                    base_expr = base_expr[1:-1]
                
                base_value = sp.sympify(base_expr)
                result = base_value % modulus
                
                return str(result)
            else:
                return "Error: Could not parse modular arithmetic expression"
                
        except Exception as e:
            return f"Error with modular arithmetic: {str(e)}"

    def _evaluate_expression(self, expression) -> str:
        """Evaluate general mathematical expressions"""
        try:
            # Replace common mathematical notation
            expression = expression.replace('^', '**')  # Handle exponentiation
            expression = expression.replace('√', 'sqrt')  # Handle square root symbol
            
            # Parse and evaluate
            result = sp.sympify(expression)
            
            # Try to simplify
            simplified = sp.simplify(result)
            
            # If it's a number, try to get exact form or decimal
            if simplified.is_number:
                if simplified.is_rational:
                    return str(simplified)
                else:
                    # For irrational numbers, show both exact and decimal
                    decimal_val = float(simplified.evalf())
                    return f"{simplified} ≈ {decimal_val}"
            
            return str(simplified)
            
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
        
    def _solve_system_of_equations(self, expression) -> str:
        try:
        # Split equations by semicolon, comma, or newline
            if ';' in expression:
                equations = [eq.strip() for eq in expression.split(';') if eq.strip()]
            elif '\n' in expression:
                equations = [eq.strip() for eq in expression.split('\n') if eq.strip()]
            else:
                # Split by comma, but be careful about commas in function calls
                # First check if we have function calls with commas
                if any(func in expression for func in ['gcd(', 'lcm(', 'binomial(', 'min(', 'max(']):
                    # Don't split by comma if it's likely inside a function
                    equations = [expression.strip()]
                else:
                    equations = [eq.strip() for eq in expression.split(',') if eq.strip() and '=' in eq]
            
            # Parse each equation
            sympy_equations = []
            all_variables = set()
            
            for eq_str in equations:
                if '=' not in eq_str:
                    continue
                    
                left, right = eq_str.split('=', 1)
                left_expr = sp.sympify(left.strip())
                right_expr = sp.sympify(right.strip())
                
                equation = sp.Eq(left_expr, right_expr)
                sympy_equations.append(equation)
                
                # Collect all variables
                all_variables.update(equation.free_symbols)
            
            if not sympy_equations:
                return "Error: No valid equations found"
            
            if not all_variables:
                return "Error: No variables found in system"
            
            # Solve the system
            solutions = sp.solve(sympy_equations, list(all_variables))
            
            if isinstance(solutions, dict):
                # Single solution
                result_parts = []
                for var in sorted(all_variables, key=str):
                    if var in solutions:
                        result_parts.append(f"{var} = {solutions[var]}")
                return ", ".join(result_parts)
            elif isinstance(solutions, list):
                if len(solutions) == 0:
                    return "No solution exists"
                elif len(solutions) == 1 and isinstance(solutions[0], dict):
                    # Single solution in list format
                    solution = solutions[0]
                    result_parts = []
                    for var in sorted(all_variables, key=str):
                        if var in solution:
                            result_parts.append(f"{var} = {solution[var]}")
                    return ", ".join(result_parts)
                else:
                    # Multiple solutions
                    result_parts = []
                    for i, sol in enumerate(solutions):
                        if isinstance(sol, dict):
                            sol_parts = []
                            for var in sorted(all_variables, key=str):
                                if var in sol:
                                    sol_parts.append(f"{var} = {sol[var]}")
                            result_parts.append(f"Solution {i+1}: {', '.join(sol_parts)}")
                        else:
                            result_parts.append(f"Solution {i+1}: {sol}")
                    return "; ".join(result_parts)
            else:
                return str(solutions)
                
        except Exception as e:
            return f"Error solving system: {str(e)}"
