import unittest
from unittest.mock import *
from pricing import *

class TestDiscountEngine(unittest.TestCase):

    def setUp(self):
        real_calc      = PriceCalculator()
        self.spy_calc  = MagicMock(wraps=real_calc)  # spy



        self.engine    = DiscountEngine(self.spy_calc)

        self.laptop = Product("LAP-01", 1000.00, "electronics")
        self.shirt  = Product("SHT-99", 50.00, "clothing")

    def test_apply_sale_returns_correct_totals(self):
        # Real PriceCalculator runs — results are trustworthy
        result = self.engine.apply_sale(self.laptop, 0.10)  # 10% off

        self.assertEqual(result["discounted"], 900.00)  # 1000 * 0.9
        self.assertEqual(result["tax"],        100.00)  # 1000 * 10%
        self.assertEqual(result["total"],      1000.00) # 900 + 100

    def test_discount_called_with_correct_product_and_pct(self):
        real_calc = PriceCalculator()
        self.spy_calc = patch.object(real_calc, "discount", wraps=real_calc.discount)

        engine = DiscountEngine(real_calc)
        shirt = Product("SHT-99", 50.00, "clothing")

        with patch.object(real_calc, "discount", wraps=real_calc.discount) as spy_discount:
            engine.apply_sale(shirt, 0.25)

        # Assertions remain the same
        spy_discount.assert_called_once_with(shirt, 0.25)

    def test_category_tax_called_with_correct_product(self):
       
        self.engine.apply_sale(self.laptop, 0.05)

        self.spy_calc.category_tax.assert_called_once_with(self.laptop)

    def test_both_calculator_methods_called_once_per_sale(self):
        # Guard against accidental double-calls
        self.engine.apply_sale(self.shirt, 0.10)

        self.assertEqual(self.spy_calc.discount.call_count,     1)
        self.assertEqual(self.spy_calc.category_tax.call_count, 1)

    def test_real_return_value_flows_into_result_dict(self):
        # In unittest.mock, the spy returns the real value directly.
        # Capture the result of apply_sale() — it contains the real computed values.
        # This confirms both: the formula is correct AND DiscountEngine
        # stored the value in the dict without any transformation.
        result = self.engine.apply_sale(self.laptop, 0.20)

        # Real formula: 1000 * (1 - 0.20) = 800.00
        self.assertEqual(result["discounted"], 800.00)  # 1000 * 0.8
        self.assertEqual(result["tax"],        100.00)  # 1000 * 10%
    
    def test_sale_count(self):
        burger = Product(sku="BUR-01", base_price=55.99, category="food")
        pizza = Product(sku="PIZ-03", base_price=9.99, category="food")
        spagetti = Product(sku="SPA-673", base_price=29.99, category="food")

        self.engine.apply_sale(burger, 0.25)
        self.engine.apply_sale(pizza, 0.55)
        self.engine.apply_sale(spagetti, 0.88)

        self.assertEqual(self.spy_calc.discount.call_count, 3)
        self.assertEqual(self.spy_calc.discount.call_args_list, [
            call(burger, 0.25),
            call(pizza, 0.55),
            call(spagetti, 0.88),
        ])




class TestDiscountEngineWithMock(unittest.TestCase):
    """
    Using a mock instead of a spy. Notice:
    - We must configure every return_value manually
    - The real calculator logic is NEVER tested here
    - If PriceCalculator.discount had a bug, this test wouldn't catch it
    """
    def setUp(self):
        self.mock_calc = MagicMock()
        self.mock_calc.discount.return_value     = 800.00  # hardcoded
        self.mock_calc.category_tax.return_value = 100.00  # hardcoded
        self.engine = DiscountEngine(self.mock_calc)

    def test_total_uses_values_from_calculator(self):
        product = Product("X", 0.0, "electronics")  # base_price irrelevant
        result  = self.engine.apply_sale(product, 0.20)

        # Tests InvoiceService wiring — not calculator correctness
        self.assertEqual(result["total"], 900.00)  # 800 + 100
        self.mock_calc.discount.assert_called_once()