from pricing import *
from pricing_tests import *


# After a test run you can print spy internals to understand what happened.
# Useful for debugging a failing test interactively.

real_calc = PriceCalculator()
spy_calc  = MagicMock(wraps=real_calc)
engine    = DiscountEngine(spy_calc)
laptop    = Product("LAP-01", 1000.00, "electronics")

# ── Capture the real return value from the call result ────────
# In unittest.mock, the spy returns the real value directly.
# Assign it from the call — no special attribute needed.
result = engine.apply_sale(laptop, 0.10)
print(result["discounted"])  # 900.0  — real formula output
print(result["tax"])         # 100.0  — real formula output

# ── call_count: how many times was this method invoked? ──────
print(spy_calc.discount.call_count)         # 1
print(spy_calc.category_tax.call_count)     # 1

# ── call_args: positional and keyword args of the LAST call ──
args, kwargs = spy_calc.discount.call_args
print(args)     # (Product(sku='LAP-01', base_price=1000.0, ...), 0.1)
print(kwargs)   # {}   (no keyword arguments were used)

# ── call_args_list: full history of every call ────────────────
engine.apply_sale(laptop, 0.20)             # second sale
print(spy_calc.discount.call_args_list)
# [call(laptop, 0.1),   ← first apply_sale
#  call(laptop, 0.2)]   ← second apply_sale

# ── reset_mock(): clear all recorded calls between tests ──────
# (setUp() is usually better, but useful in interactive exploration)
spy_calc.discount.reset_mock()
print(spy_calc.discount.call_count)         # 0 — history cleared

# ── NOTE: spy_return is a pytest-mock feature, not unittest.mock ──
# If you are using pytest-mock (mocker.spy), you can access spy_return.
# In unittest.mock, capture the return value from the call directly (above)