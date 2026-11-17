import pytest
from enterprise_ai.tools.builtin import calculator

@pytest.mark.parametrize(("expression","expected"),[
    ("2 + 3 * 4","14"),("(10 - 2) / 4","2.0"),("2 ** 3","8")
])
def test_calculator(expression,expected):
    assert calculator.invoke({"expression":expression})==expected

@pytest.mark.parametrize("expression",[
    "__import__('os').system('id')","open('/etc/passwd').read()","2 ** 99"
])
def test_calculator_rejects_code_and_unbounded_power(expression):
    assert calculator.invoke({"expression":expression}).startswith("Calculation rejected:")
