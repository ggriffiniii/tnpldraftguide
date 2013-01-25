# Create your views here.
from django.db import connection
from django import forms
from django.forms.fields import ChoiceField, MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from django.template import Context, loader, RequestContext
from draftapp.models import *
import copy
import draftapp.stats
import operator
from django.db import connection
import datetime
import time
from django.utils import simplejson
import math

def get_dataset_choices():
	choices = []
	prev_year = draftapp.stats.PREV_YEAR
	for year in xrange(prev_year, prev_year-6, -1):
		choices.append((str(year), str(year)));

	cursor = connection.cursor()
	choices.append(('avg_2', '2 Year Avg'))
	choices.append(('avg_3', '3 Year Avg'))
	choices.append(('avg_5', '5 Year Avg'))
	cursor.execute('SELECT DISTINCT(TYPE) from BattingProj;')
	for row in cursor:
		type = row[0]
		choices.append(('proj_' + type, type))
	return choices

class PlayerFilterForm(forms.Form):
	position = forms.ChoiceField(choices=(('C', 'C'),
					      ('1B', '1B'),
					      ('2B', '2B'),
					      ('3B', '3B'),
					      ('SS', 'SS'),
					      ('OF', 'OF'),
					      ('CI', 'CI'),
					      ('MI', 'MI'),
					      ('U', 'U'),
					      ('P', 'P')))
	dataset = forms.ChoiceField(choices=get_dataset_choices())


class DataSetForm(forms.Form):
	dataset = forms.ChoiceField(choices=get_dataset_choices())


def player_filter(request):
	if len(request.GET) > 0:
		filter_form = PlayerFilterForm(request.GET)
	else:
		filter_form = PlayerFilterForm({'position': 'U',
						'dataset': 'proj_MARCEL'})
	if filter_form.is_valid():
		js_data = js_players(**filter_form.cleaned_data)

	return render_to_response('player_filter.html',
				  {'filter_form': filter_form,
				   'js_data': js_data},
				  context_instance=RequestContext(request))

def player_filter_submit(request):
	if request.method == 'POST':
		form = PlayerFilterForm(request.POST)
		if form.is_valid() and form.cleaned_data['position'] != 'NO_POS':
			return json_players(request, form.cleaned_data)

	return HttpResponseBadRequest()


def js_players(position, dataset):
	stats = draftapp.stats.PopulationStats()

	# Calculate necessary stats (mean and standard deviation) and sort the
	# hitters and pitchers in descending order of calculated score
	stats.UpdateStats(dataset)

	table_rows = []
	if position == 'P':
		for pitcher in stats.pitchers():
			x = {}
			x['name'] = pitcher.name
			x['player_id'] = pitcher.id
			x['tnpl_team'] = pitcher.tnpl_team
			x['tnpl_team_id'] = pitcher.tnpl_team_id
			x['tnpl_salary'] = pitcher.tnpl_salary
			x['IP'] = pitcher.ipouts / 3.0
			x['ERA'] = pitcher.era()
			x['ERA_dollar'] = pitcher.era_dollar(stats)
			x['WHIP'] = pitcher.whip()
			x['WHIP_dollar'] = pitcher.whip_dollar(stats)
			x['W'] = pitcher.w
			x['W_dollar'] = pitcher.w_dollar(stats)
			x['K'] = pitcher.k
			x['K_dollar'] = pitcher.k_dollar(stats)
			x['S'] = pitcher.s
			x['S_dollar'] = pitcher.s_dollar(stats)
			x['POS'] = 'P'
			x['POS_dollar'] = pitcher.pos_dollar(stats)
			table_rows.append(x)
		dist_data = stats.get_pitching_distributions()
	else:
		for hitter in stats.hitters(position):
			x = {}
			x['name'] = hitter.name
			x['player_id'] = hitter.id
			x['tnpl_team'] = hitter.tnpl_team
			x['tnpl_team_id'] = hitter.tnpl_team_id
			x['tnpl_salary'] = hitter.tnpl_salary
			x['BA'] = hitter.ba()
			x['AB'] = hitter.ab
			x['BA_dollar'] = hitter.h_dollar(stats)
			x['R'] = hitter.r
			x['R_dollar'] = hitter.r_dollar(stats)
			x['HR'] = hitter.hr
			x['HR_dollar'] = hitter.hr_dollar(stats)
			x['RBI'] = hitter.rbi
			x['RBI_dollar'] = hitter.rbi_dollar(stats)
			x['SB'] = hitter.sb
			x['SB_dollar'] = hitter.sb_dollar(stats)
			x['POS'] = hitter.get_position()
			x['POS_dollar'] = hitter.pos_dollar(stats)
			table_rows.append(x)
		dist_data = stats.get_hitting_distributions()
		

	return simplejson.dumps({'distributions': dist_data,
				 'players_table': table_rows})

class PlayerDollarValueForm(forms.Form):
	playerid = forms.IntegerField()
	dataset = forms.CharField()
	is_pitcher = forms.BooleanField(required=False)


def player_dollar_value_submit(request):
	if request.method == 'POST':
		form = PlayerDollarValueForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			dollar_value = js_player_dollar_value(data['playerid'],
							      data['dataset'],
							      data['is_pitcher'])
			return HttpResponse(
				simplejson.dumps(dollar_value),
				mimetype='application/json')
	return HttpResponseBadRequest()

def js_player_dollar_value(player_id, dataset, is_pitcher):
	stats = draftapp.stats.PopulationStats()
	stats.UpdateStats(dataset)
	player = stats.get_player(player_id)
	if player is None:
		raise Exception('No player found')
	elif player.get_position() == 'P':
		return {
			'ERA': player.era_dollar(stats),
			'WHIP': player.whip_dollar(stats),
			'W': player.w_dollar(stats),
			'K': player.k_dollar(stats),
			'S': player.s_dollar(stats),
			'total': player.adjusted_dollar(stats)
		}
	else:
		return {
			'BA': player.h_dollar(stats),
			'R': player.r_dollar(stats),
			'HR': player.hr_dollar(stats),
			'RBI': player.rbi_dollar(stats),
			'SB': player.sb_dollar(stats),
			'total': player.adjusted_dollar(stats)
		}



class OwnershipForm(forms.Form):
	player = forms.ModelChoiceField(queryset=Player.objects.all(), widget=forms.HiddenInput)
	team = forms.ModelChoiceField(queryset=TNPLTeam.objects.all(), empty_label='Free Agent', required=False)
	salary = forms.DecimalField(decimal_places=2)

def ownership_form_submit(request):
	if request.method == 'POST':
		form = OwnershipForm(request.POST)
		if form.is_valid():
			print form.cleaned_data
			player = form.cleaned_data['player']
			if form.cleaned_data['team'] is None:
				try:
					player.tnplownership.delete()
				except ObjectDoesNotExist:
					pass
			else:

				try:
					player.tnplownership.team = form.cleaned_data['team']
					player.tnplownership.salary = form.cleaned_data['salary']
					player.tnplownership.save()
				except ObjectDoesNotExist:
					ownership = TNPLOwnership(playerid=player, team=form.cleaned_data['team'], salary=form.cleaned_data['salary'])
					ownership.save()
			return HttpResponse('', mimetype='application/json')
	return HttpResponseBadRequest()


class SeasonSummary(object):
	pass

def player(request, player_id):
	player = get_object_or_404(Player, lahmanid=player_id)
	if player.is_pitcher():
		return pitcher(request, player)
	else:
		return hitter(request, player)


def hitter(request, player):
	name = "%s %s" % (player.namefirst, player.namelast)

	apps = {
		'C': 0,
		'1B': 0,
		'2B': 0,
		'3B': 0,
		'SS': 0,
		'OF': 0,
	}
	try:
		appearances = player.appearances_set.get(yearid=draftapp.stats.PREV_YEAR)
		apps = {
			'C': appearances.g_c,
			'1B': appearances.g_1b,
			'2B': appearances.g_2b,
			'3B': appearances.g_3b,
			'SS': appearances.g_ss,
			'OF': appearances.g_of,
		}
	except ObjectDoesNotExist:
		pass

	appearances = (
		{ 'pos': 'C', 'eligible': apps['C'] >= 20, 'games': apps['C'] },
		{ 'pos': '1B', 'eligible': apps['1B'] >= 20, 'games': apps['1B'] },
		{ 'pos': '2B', 'eligible': apps['2B'] >= 20, 'games': apps['2B'] },
		{ 'pos': '3B', 'eligible': apps['3B'] >= 20, 'games': apps['3B'] },
		{ 'pos': 'SS', 'eligible': apps['SS'] >= 20, 'games': apps['SS'] },
		{ 'pos': 'OF', 'eligible': apps['OF'] >= 20, 'games': apps['OF'] },
		{ 'pos': 'MI', 'eligible': apps['SS'] >= 20 or apps['2B'] >= 20, 'games': max(apps['SS'], apps['2B']) },
		{ 'pos': 'CI', 'eligible': apps['1B'] >= 20 or apps['3B'] >= 20, 'games': max(apps['1B'], apps['3B']) },
		{ 'pos': 'U', 'eligible': True }
	)

	# Get batting seasons
	query = 'SELECT yearID, teamID, SUM(AB), SUM(H), SUM(R), SUM(HR), SUM(RBI), SUM(SB) from Batting where playerID = %s GROUP BY yearID ORDER BY yearID DESC'
	cursor = connection.cursor()
	cursor.execute(query, (player.playerid,))
	seasons = []
	most_recent_teamid = None
	for row in cursor:
		if most_recent_teamid is None:
			most_recent_teamid = row[1]
		season = {
			'year': row[0],
			'AB': int(row[2]),
			'H': int(row[3]),
			'R': int(row[4]),
			'HR': int(row[5]),
			'RBI': int(row[6]),
			'SB': int(row[7]),
		}
		seasons.append(season)

	if most_recent_teamid is not None:
		print most_recent_teamid
		print seasons[-1]['year']
		team = Teams.objects.get(teamid=most_recent_teamid, yearid=seasons[0]['year']).name
		
	else:
		team = None

	birthdate = datetime.date(player.birthyear, player.birthmonth, player.birthday)
	today = datetime.date.today()
	age = today.year - birthdate.year
	if (today.month < birthdate.month or
		today.month == birthdate.month and today.day < birthdate.day):
		age -= 1

	try:
		ownership_form = OwnershipForm({'player': player.lahmanid, 'team': player.tnplownership.team.id, 'salary': player.tnplownership.salary})
		ownership_form.is_valid()
	except ObjectDoesNotExist:
		ownership_form = OwnershipForm({'player': player.lahmanid})

	projections = []
	for proj in player.battingproj_set.all():
		summary = {
			'type': proj.type,
			'AB': proj.ab,
			'H': proj.h,
			'R': proj.r,
			'HR': proj.hr,
			'RBI': proj.rbi,
			'SB': proj.sb,
		}
		projections.append(summary)
		
			

	return render_to_response('hitter.html', {'name': name,
						  'id': player.lahmanid,
						  'appearances': appearances,
			                	  'seasons': simplejson.dumps(seasons),
						  'projections': simplejson.dumps(projections),
						  'bats': player.bats,
						  'throws': player.throws,
						  'birthdate': birthdate,
						  'age': age,
						  'team': team,
						  'ownership_form': ownership_form}, context_instance=RequestContext(request))

def pitcher(request, player):
	name = "%s %s" % (player.namefirst, player.namelast)

	query = 'SELECT yearID, teamID, SUM(W), SUM(SV), SUM(IPouts), SUM(H), SUM(ER), SUM(BB), SUM(SO) from Pitching where playerID = %s GROUP BY yearID ORDER BY yearID DESC'
	cursor = connection.cursor()
	cursor.execute(query, [player.playerid])
	seasons = []
	most_recent_teamid = None
	for row in cursor:
		if most_recent_teamid is None:
			most_recent_teamid = row[1]
		season = {}
		season['year'] = row[0]
		season['W'] = int(row[2])
		season['S'] = int(row[3])
		season['IP'] = float(row[4]) / 3.0
		season['H'] = int(row[5])
		season['ER'] = int(row[6])
		season['BB'] = int(row[7])
		season['K'] = int(row[8])
		seasons.append(season)
		
	if most_recent_teamid is not None:
		team = Teams.objects.get(teamid=most_recent_teamid, yearid=seasons[-1]['year']).name
	else:
		team = None

	birthdate = datetime.date(player.birthyear, player.birthmonth, player.birthday)
	today = datetime.date.today()
	age = today.year - birthdate.year
	if (today.month < birthdate.month or
		today.month == birthdate.month and today.day < birthdate.day):
		age -= 1
	
	try:
		ownership_form = OwnershipForm({'player': player.lahmanid, 'team': player.tnplownership.team.id, 'salary': player.tnplownership.salary})
		ownership_form.is_valid()
	except ObjectDoesNotExist:
		ownership_form = OwnershipForm({'player': player.lahmanid})

	projections = []
	for proj in player.pitchingproj_set.all():
		summary = {}
		summary['type'] = proj.type
		summary['W'] = proj.w
		summary['S'] = proj.sv
		summary['IP'] = float(proj.ipouts) / 3.0
		summary['H'] = proj.h
		summary['ER'] = proj.er
		summary['BB'] = proj.bb
		summary['K'] = proj.so
		projections.append(summary)

	return render_to_response('pitcher.html', {'name': name,
						   'id': player.lahmanid,
						   'seasons': simplejson.dumps(seasons),
						   'projections': simplejson.dumps(projections),
						   'bats': player.bats,
						   'throws': player.throws,
						   'birthdate': birthdate,
						   'age': age,
						   'team': team,
						   'eligibility': ['P'],
						   'ownership_form': ownership_form}, context_instance=RequestContext(request))

def player_search(request):
	query = request.GET['q']
	age_filter = Q(birthyear__gt=1962) # only players under 50
	terms = query.split()
	if len(terms) > 0:
		name_filter = Q(namefirst__istartswith=terms[0])
		name_filter |= Q(namelast__istartswith=terms[0])
		for term in terms[1:]:
			name_filter |= Q(namefirst__istartswith=term)
			name_filter |= Q(namelast__istartswith=term)

		data = []
		for player in Player.objects.all().filter(age_filter & name_filter):
			playerdata = {'id': player.lahmanid,
				      'name': '%s %s' % (player.namefirst, player.namelast)}
			data.append(playerdata)

		return HttpResponse(simplejson.dumps(data),
			    mimetype='application/json')
	
	return HttpResponseBadRequest()

def team(request, team_id):
        team = get_object_or_404(TNPLTeam, id=team_id)
	name = team.name

	if len(request.GET) > 0:
		dataset_form = DataSetForm(request.GET)
	else:
		dataset_form = DataSetForm({'dataset': 'proj_MARCEL'})

	if not dataset_form.is_valid():
		return HttpResponseBadRequest()

	stats = draftapp.stats.PopulationStats()
	stats.UpdateStats(dataset_form.cleaned_data['dataset'])

	cursor = connection.cursor()
	cursor.execute('''
		SELECT
			Master.lahmanid,
			Master.nameFirst,
			Master.nameLast,
			draftapp_tnplownership.salary
		from draftapp_tnplownership
		JOIN Master USING(playerID)
		WHERE team_id = %s;''',
		(team.id,))

	salary_spent = 0.0
	num_players = 0

	hitters = []
	pitchers = []
	unknown = []
	for row in cursor:
		player_id = row[0]
		salary = float(row[3])
		player_name = '%s %s' % (row[1], row[2])
		num_players += 1
		salary_spent += salary
		player = stats.get_player(player_id)
		if player is None:
			x = {
				'id': player_id,
				'name': player_name,
				'salary': salary,
				'positions': set('U')
			}
			unknown.append(x)
		elif player.get_position() == 'P':
			x = {
				'id': player_id,
				'name': player_name,
				'salary': salary,
				'IP': player.ipouts / 3.0,
				'ER': player.er,
				'ERA': player.era(),
				'ERA_dollar': player.era_dollar(stats),
				'H': player.h,
				'BB': player.bb,
				'WHIP': player.whip(),
				'WHIP_dollar': player.whip_dollar(stats),
				'W': player.w,
				'W_dollar': player.w_dollar(stats),
				'K': player.k,
				'K_dollar': player.k_dollar(stats),
				'S': player.s,
				'S_dollar': player.s_dollar(stats),
				'POS': 'P',
				'POS_dollar': player.pos_dollar(stats),
				'total_dollar': player.adjusted_dollar(stats),
				'positions': set(['P']),
			}
			pitchers.append(x)
		else:
			x = {
				'id': player_id,
				'name': player_name,
				'salary': salary,
				'AB': player.ab,
				'H': player.h,
				'BA': player.ba(),
				'BA_dollar': player.h_dollar(stats),
				'R': player.r,
				'R_dollar': player.r_dollar(stats),
				'HR': player.hr,
				'HR_dollar': player.hr_dollar(stats),
				'RBI': player.rbi,
				'RBI_dollar': player.rbi_dollar(stats),
				'SB': player.sb,
				'SB_dollar': player.sb_dollar(stats),
				'POS': player.get_position(),
				'POS_dollar': player.pos_dollar(stats),
				'total_dollar': player.adjusted_dollar(stats),
				'positions': player.positions,
			}
			hitters.append(x)

	hitter_totals = {}
	for attr in ('salary', 'AB', 'H', 'BA_dollar', 'R', 'R_dollar', 'HR',
		     'HR_dollar', 'RBI', 'RBI_dollar', 'SB', 'SB_dollar',
		     'POS_dollar', 'total_dollar'):
		hitter_totals[attr] = sum([x[attr] for x in hitters])
	hitter_totals['BA'] = float(hitter_totals['H']) / hitter_totals['AB']

	pitcher_totals = {}
	for attr in ('salary', 'IP', 'ER', 'ERA_dollar', 'H', 'BB',
		     'WHIP_dollar', 'W', 'W_dollar', 'K', 'K_dollar', 'S',
		     'S_dollar', 'POS_dollar', 'total_dollar'):
		pitcher_totals[attr] = sum([x[attr] for x in pitchers])
	games_pitched = pitcher_totals['IP'] / 9.0
	pitcher_totals['ERA'] = pitcher_totals['ER'] / games_pitched
	walks_and_hits = pitcher_totals['H'] + pitcher_totals['BB']
	pitcher_totals['WHIP'] = walks_and_hits / pitcher_totals['IP']

	unknown_totals = {
		'salary': sum([x['salary'] for x in unknown])
	}
	

	if num_players >= draftapp.stats.NUM_PLAYERS:
		salary_remaining = 0.0
		positions_remaining = 0
		avg_salary = 0.0
	else:
		salary_remaining = draftapp.stats.SALARY_PER_TEAM - salary_spent
		positions_remaining = draftapp.stats.NUM_PLAYERS - num_players
		avg_salary = salary_remaining / positions_remaining

	# Determine what positions are still draftable
	valid_lineups = dict([(x, []) for x in ('P', 'C', '1B', '2B', '3B', 'SS', 'MI', 'CI', 'OF', 'U')])
	def get_all_lineups(lineup, players):
		if len(players) == 0:
			lineup_copy = lineup.copy()
			for k,v in lineup_copy.iteritems():
				lineup_copy[k] = v[:]
			for pos in [k for (k,v) in lineup_copy.iteritems() if len(v) < draftapp.stats.POS_COUNT[k]]:
				valid_lineups[pos].append(lineup_copy)
			return
		for pos in players[0]['positions']:
			if draftapp.stats.POS_COUNT[pos] - len(lineup[pos]) == 0:
				continue
			lineup[pos].append(players[0])
			get_all_lineups(lineup, players[1:])
			lineup[pos].pop()

	empty_lineup = dict([(x, []) for x in ('P', 'C', '1B', '2B', '3B', 'SS', 'MI', 'CI', 'OF', 'U')])
	get_all_lineups(empty_lineup, pitchers + hitters)
	draftable_positions = set([k for (k,v) in valid_lineups.iteritems() if len(v) > 0])
	print "Draftable positions: ", draftable_positions

	return render_to_response('team.html', {'name': name,
						'team_id': team.id,
						'salary_spent': salary_spent,
						'salary_remaining': salary_remaining,
						'num_players': num_players,
						'positions_remaining': positions_remaining,
						'avg_salary': avg_salary,
						'hitters': hitters,
						'hitter_totals': hitter_totals,
						'hitter_totals_js': simplejson.dumps(hitter_totals),
						'pitchers': pitchers,
						'pitcher_totals': pitcher_totals,
						'pitcher_totals_js': simplejson.dumps(pitcher_totals),
						'unknown': unknown,
						'unknown_totals': unknown_totals,
						'dataset_form': dataset_form,
					       }, context_instance=RequestContext(request))

class TeamSummary(object):
	pass

def teams(request):
	if len(request.GET) > 0:
		dataset_form = DataSetForm(request.GET)
	else:
		dataset_form = DataSetForm({'dataset': 'proj_MARCEL'})

	if not dataset_form.is_valid():
		return HttpResponseBadRequest()

	stats = draftapp.stats.PopulationStats()
	stats.UpdateStats(dataset_form.cleaned_data['dataset'])

	cursor = connection.cursor()
	cursor.execute('''
		SELECT
			draftapp_tnplteam.id,
			draftapp_tnplteam.name,
			Master.lahmanid,
			draftapp_tnplownership.salary
		FROM
			draftapp_tnplownership
		JOIN
			draftapp_tnplteam
		ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id)
		JOIN
			Master
		USING(playerID);
	''')

	teams = {}
	for row in cursor:
		team_id = row[0]
		team_name = row[1]
		player_id = row[2]
		salary = float(row[3])

		if teams.has_key(team_id):
			team = teams[team_id]
		else:
			team = {
				'hitter_totals': {
					'BA_dollar': 0.0,
					'R_dollar': 0.0,
					'HR_dollar': 0.0,
					'RBI_dollar': 0.0,
					'SB_dollar': 0.0,
					'salary': 0.0,
					'num_players': 0,
				},
				'pitcher_totals': {
					'ERA_dollar': 0.0,
					'WHIP_dollar': 0.0,
					'W_dollar': 0.0,
					'K_dollar': 0.0,
					'S_dollar': 0.0,
					'salary': 0.0,
					'num_players': 0,
				},
				'unknown_totals': {
					'salary': 0.0,
					'num_players': 0,
				},
				'name': team_name,
			}
			teams[team_id] = team
		player = stats.get_player(row[2])
		if player is None:
			u_totals = team['unknown_totals']
			u_totals['salary'] += salary
			u_totals['num_players'] += 1
		elif player.get_position() == 'P':
			p_totals = team['pitcher_totals']
			p_totals['ERA_dollar'] += player.era_dollar(stats)
			p_totals['WHIP_dollar'] += player.whip_dollar(stats)
			p_totals['W_dollar'] += player.w_dollar(stats)
			p_totals['K_dollar'] += player.k_dollar(stats)
			p_totals['S_dollar'] += player.s_dollar(stats)
			p_totals['salary'] += salary
			p_totals['num_players'] += 1
		else:
			h_totals = team['hitter_totals']
			h_totals['BA_dollar'] += player.h_dollar(stats)
			h_totals['R_dollar'] += player.r_dollar(stats)
			h_totals['HR_dollar'] += player.hr_dollar(stats)
			h_totals['RBI_dollar'] += player.rbi_dollar(stats)
			h_totals['SB_dollar'] += player.sb_dollar(stats)
			h_totals['salary'] += salary
			h_totals['num_players'] += 1
			

	return render_to_response('teams.html',
				  {'teams': teams,
				   'teams_js': simplejson.dumps(teams),
				   'dataset_form': dataset_form},
				  context_instance=RequestContext(request))
		
		
