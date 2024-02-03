from django import template
import json
import datetime

register = template.Library()


@register.filter
def json_loads(value):
    return json.loads(value)

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter()
def addDays(days):
   newDate = datetime.date.today() + datetime.timedelta(days=days)
   return newDate