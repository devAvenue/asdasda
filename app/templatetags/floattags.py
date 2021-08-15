from django.template.defaultfilters import floatformat
from django.template import Library

register = Library()


def formatted_float(value):
    print(value)
    if value == 0:
        value = floatformat(value)
    elif value > 9:
        value = floatformat(value, 2)
    else:
        value = floatformat(value, 4)
    return str(value).replace(',', '.')


def formatted_percent(value):
    value = floatformat(value, 2)
    return str(value).replace(',', '.')


register.filter('formatted_float', formatted_float)
register.filter('formatted_percent', formatted_percent)
