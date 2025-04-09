from django import template


register = template.Library()

@register.filter('get')
def get(d: dict, k: str):
    return d.get(k)
