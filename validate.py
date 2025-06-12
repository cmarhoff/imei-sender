import re

def is_valid_imei(imei):
    if not re.match(r"^\d{15}$", imei):
        return False
    return luhn_check(imei)

def luhn_check(imei):
    sum = 0
    for i, digit in enumerate(reversed(imei)):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        sum += n
    return sum % 10 == 0
