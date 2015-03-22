from decimal import Decimal

si_units = {
    "f" : "e-15",
    "p" : "e-12",
    "n" : "e-9",
    "u" : "e-6",
    "m" : "e-3",
    "K" : "e3",
    "k" : "e3",
    "MEG" : "e6",
    "M" : "e6",
    "G"  : "e9",
    "g" : "e9",
    "T" : "e12",
    "t" : "e12"
}

exponents_to_units = {
    -21: 'z',
    -18: 'a',
    -15: 'f',
    -12: 'p',
    -9: 'n',
    -6: 'u',
    -3: 'm',
     0: '',
    +3: 'K',
    +6: 'MEG',
    +9: 'G',
    +12: 'T',
    +15: 'P'

}
def float_to_eng(num):
    """Returns a string representation of the input using engineering notation.

    Adapted from http://stackoverflow.com/a/12311220
    """

    import math

    if num is 0:
        return '0'
    x = float(num)
    y = abs(x)
    exponent = int(math.log10(y))
    engr_exponent = exponent - exponent%3

    z = y/10**engr_exponent

    # Would it be prettier as an integer?  1e-5 --> 10u
    if z - int(z) == 0:
        z = int(z)

    sign = '-' if x < 0 else ''
    return sign+str(z) + exponents_to_units[engr_exponent]





