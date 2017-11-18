from django import template
register = template.Library()


@register.filter
def return_item(arr, i):
    try:
        if arr[int(i)] == 0:
            return " "
        else:
            return arr[int(i)]
    except ValueError:
        return None
