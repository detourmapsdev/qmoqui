__author__ = 'root'
import datetime
from django import template

register = template.Library()

@register.filter(name="timestamp")
def timestamptodate(value):
    return datetime.datetime.fromtimestamp(int(value)).strftime('%m-%d-%Y')

@register.filter(name='dollarizer')
def dollarizer(value):
    dollar = value/100
    return u'$%s%s' % (dollar, ".00")
