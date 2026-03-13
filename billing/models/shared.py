from decimal import Decimal, ROUND_HALF_UP

ZERO_DECIMAL = Decimal('0.00')
TAX_RATE_DEFAULT = Decimal('10.00')


def quantize_amount(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
