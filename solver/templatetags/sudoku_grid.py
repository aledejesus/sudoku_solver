from django import template
register = template.Library()


@register.inclusion_tag('reusables/sudoku_grid.html')
def sudoku_grid(grid_id, key_id=None, numbers=[]):
    return {
        "grid_id": grid_id.replace("{{key}}", key_id) if key_id else grid_id,
        "numbers": numbers}
