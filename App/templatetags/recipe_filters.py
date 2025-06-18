from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@mark_safe
def format_ingredients(ingredients):
    """Format ingredients list for display"""
    if not ingredients:
        return ""
    
    formatted = []
    for ingredient in ingredients:
        formatted.append(f"<li>{ingredient}</li>")
    return f"<ul>{''.join(formatted)}</ul>"

@register.filter
@mark_safe
def format_instructions(instructions):
    """Format instructions list for display"""
    if not instructions:
        return ""
    
    formatted = []
    for i, step in enumerate(instructions, 1):
        formatted.append(f"<li>Step {i}: {step}</li>")
    return f"<ol>{''.join(formatted)}</ol>"

@register.filter
def duration_to_string(duration):
    """Convert duration in minutes to a human-readable string"""
    if not duration:
        return ""
    
    hours = duration // 60
    minutes = duration % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    
    return " ".join(parts)

@register.filter
def split_tags(tags):
    """Split comma-separated tags into a list"""
    if not tags:
        return []
    return [tag.strip() for tag in tags.split(',')]
