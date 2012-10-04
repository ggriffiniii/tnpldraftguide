from django import template

register = template.Library()

def dollars(value):
	if value < 0.0:
		prefix = '-$'
	else:
		prefix = '$'

	return "%s%.2f" % (prefix, abs(value))

register.filter('dollars', dollars)
