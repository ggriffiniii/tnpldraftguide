# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.db.models import Q
from django.template import Context, loader
from draftapp.models import *
import operator
from django.db import connection
import time

PREV_YEAR = 2011

def players(request, position=None):
	if position is None:
		filter_expr = Q(yearid__gte=PREV_YEAR)
		filter_expr &= Q(playerid__batting__yearid__gte=PREV_YEAR)
		filter_expr &= Q(playerid__batting__ab__gte=20)
	else:
		filter_expr = Q(yearid=PREV_YEAR)
		pos = position.lower()
		if pos == 'c':
			filter_expr &= Q(g_c__gte=20)
		elif pos == '1b':
			filter_expr &= Q(g_1b__gte=20)
		elif pos == '2b':
			filter_expr &= Q(g_2b__gte=20)
		elif pos == '3b':
			filter_expr &= Q(g_3b__gte=20)
		elif pos == 'ss':
			filter_expr &= Q(g_ss__gte=20)
		elif pos == 'of':
			filter_expr &= Q(g_of__gte=20)
			

	results = []
	for x in Appearances.objects.filter(filter_expr):
		try:
			player = x.playerid
			results.append(x.playerid)
		except ObjectDoesNotExist:
			next
	print "done fetching: ", time.time()
	results.sort(key=operator.methodcaller('projected_val'), reverse=True)
	print "done sorting: ", time.time()

	return render_to_response('players.html', {'players': results})


def player(request, player_id):
	player = get_object_or_404(Player, lahmanid=player_id)
	name = "%s %s" % (player.namefirst, player.namelast)
	seasons = [x for x in player.batting_set.all().order_by('yearid')]
	return render_to_response('player.html', {'name': name,
						  'seasons': seasons})
