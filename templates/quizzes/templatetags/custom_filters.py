from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """사전에서 키에 해당하는 값을 가져오는 필터"""
    if dictionary is None:
        return None
    
    # key가 문자열인 경우 정수로 변환 시도
    if isinstance(key, str) and key.isdigit():
        key = int(key)
        
    return dictionary.get(key)

@register.filter
def index(sequence, position):
    """시퀀스에서 특정 위치의 항목을 가져오는 필터"""
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return None

@register.filter
def percentage(value, total):
    """백분율을 계산하는 필터"""
    try:
        if int(total) > 0:
            return (float(value) / float(total)) * 100
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def to_int(value):
    """문자열을 정수로 변환하는 필터"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0