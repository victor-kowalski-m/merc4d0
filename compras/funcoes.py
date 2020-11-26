def check(number):
    sum = 0
    m = 1

    # Iterates through number string backwards
    for i in reversed(number):
        sum += (int(i) * m) // 10 + (int(i) * m) % 10

        # Changes multiplier value for next iteration
        if m == 1:
            m = 2
        else:
            m = 1

    if sum % 10 != 0:
        return "INVALID"

    elif number[0] == '4' and len(number) in [13,16]:
        return "VISA"

    elif number[:2] in ['34', '37']  and len(number) == 15:
        return "AMEX"

    elif number[:2] in ['51', '52', '53', '54', '55']  and len(number) == 16:
        return "MASTERCARD"

    return "INVALID"