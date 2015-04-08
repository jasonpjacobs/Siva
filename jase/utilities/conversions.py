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
def float_to_eng(num, width=3, precision=3):
    """Returns a string representation of the input using engineering notation.

    Adapted from http://stackoverflow.com/a/12311220
    """

    import math

    if num == 0:
        return '0'

    if num is None:
        return None

    if num is math.isnan(num):
        return "NaN"

    x = float(num)
    y = abs(x)
    try:
        exponent = int(math.log10(y))
    except:
        raise
    engr_exponent = exponent - exponent%3

    z = y/10**engr_exponent

    format_str = "{:" + str(width) + "." + str(precision) + "f}"

    str_z = format_str.format(z)
    if str_z.endswith("." + "0"*precision):
        str_z = str_z.split('.')[0]

    sign = '-' if x < 0 else ''
    if engr_exponent in exponents_to_units:
        return sign + str_z + exponents_to_units[engr_exponent]
    else:
        #TODO:  Scale to the nearest SI unit
        return sign + str_z + "E" + str(engr_exponent)





