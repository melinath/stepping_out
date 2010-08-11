from django import template

register = template.Library()

@register.filter
def get_description(link, category):
    return link.linkmetainfo_set.get(category__id=category.id).description

@register.filter
def has_description(link, category):
    try:
        if link.linkmetainfo_set.get(category__id=category.id).description:
            return True
    except:
        pass
    return False