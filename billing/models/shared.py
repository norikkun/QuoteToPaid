from decimal import Decimal, ROUND_HALF_UP

ZERO_DECIMAL = Decimal('0.00')
TAX_RATE_DEFAULT = Decimal('10.00')
JPY_AMOUNT_QUANTIZE = Decimal('1')
DEFAULT_AMOUNT_QUANTIZE = Decimal('0.01')


def quantize_amount(amount: Decimal, currency: str = 'JPY') -> Decimal:
    quantizer = JPY_AMOUNT_QUANTIZE if (currency or 'JPY').upper() == 'JPY' else DEFAULT_AMOUNT_QUANTIZE
    return amount.quantize(quantizer, rounding=ROUND_HALF_UP)
