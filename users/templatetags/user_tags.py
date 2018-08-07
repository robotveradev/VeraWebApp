from django import template

register = template.Library()


@register.filter
def member_current_action_index(member, vacancy):
    return member.current_action_index(vacancy)
