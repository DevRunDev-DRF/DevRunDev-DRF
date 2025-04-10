from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """사전에서 키에 해당하는 값을 가져오는 필터"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def multiply(value, arg):
    """값을 인자로 곱하는 필터"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """값을 인자로 나누는 필터"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def percentage(value, total):
    """백분율을 계산하는 필터"""
    try:
        if int(total) > 0:
            return (float(value) / float(total)) * 100
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
