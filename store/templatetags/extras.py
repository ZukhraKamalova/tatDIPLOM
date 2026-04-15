from django import template

register = template.Library()

@register.filter
def get_item(queryset, name):
    return queryset.filter(name=name).first()
