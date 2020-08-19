from django import template

register = template.Library()


@register.filter(name='next_message')
def next_message(messages, index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """

    try:
        return messages[int(index)+1]
    except:
        return ""
