"""
Helpful phone related functions.
"""


def sanitize_phone_number(number):
    """
    Take away the leading '+' for standardization. Just add it back if needed.
    @param number: phone number
    """
    if isinstance(number, int):
        number = str(number)
    elif not isinstance(number, str):
        raise Exception('Invalid phone number: not a str')
    if number[0] == '+':
        number = number[1:]
    if re.match(r'^[0-9]+$', number) is None:
        raise Exception('Invalid phone number: must be 0-9')

    return number
