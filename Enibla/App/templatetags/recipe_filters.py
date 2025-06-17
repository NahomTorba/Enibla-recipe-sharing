from django import template

register = template.Library()

@register.filter
def split_tags(tags_string):
    """Split a comma-separated string into a list of tags"""
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]
