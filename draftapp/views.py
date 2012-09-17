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
import operator
from django.db import connection
import datetime
import time
from django.utils import simplejson

PREV_YEAR = 2011

class PlayerSummary(object):
	def has_hitting_projection(self):
		return None not in (self.proj_ab, self.proj_h, self.proj_r,
				    self.proj_hr, self.proj_rbi, self.proj_sb)

	def has_pitching_projection(self):
		return None not in (self.proj_w, self.proj_sv, self.proj_ipouts,
				    self.proj_h, self.proj_er, self.proj_bb,
				    self.proj_k)

	def hitting_value(self):
		if self.has_hitting_projection():
			return HittingValue(self.proj_ab, self.proj_h,
					    self.proj_r, self.proj_hr,
					    self.proj_rbi, self.proj_sb)
		else:
			return HittingValue(self.ab, self.h, self.r,
                                            self.hr, self.rbi, self.sb)

	def pitching_value(self):
		if self.has_pitching_projection():
			return PitchingValue(self.proj_w, self.proj_sv,
					     self.proj_ipouts, self.proj_h,
					     self.proj_er, self.proj_bb,
					     self.proj_k)
		else:
			return PitchingValue(self.w, self.sv, self.ipouts,
					     self.h, self.er, self.bb, self.k)

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
					      ('P', 'P'),
					      ('SP', 'SP'),
					      ('RP', 'RP')))


def player_filter(request):
	filter_form = PlayerFilterForm()
	return render_to_response('player_filter.html',
				  {'filter_form': filter_form},
				  context_instance=RequestContext(request))

def player_filter_submit(request):
	if request.method == 'POST':
		form = PlayerFilterForm(request.POST)
		if form.is_valid():
			print form.cleaned_data
			if form.cleaned_data['position'] in ('P', 'SP', 'RP'):
				return json_pitchers(request, form.cleaned_data)

			return json_hitters(request, form.cleaned_data)

	return HttpResponseBadRequest()
		
			

def json_hitters(request, form_data):
	start = time.time()
	where_clause = 'Batting.yearID = %s' % (PREV_YEAR)
	position = form_data['position']
	if position == 'C':
		where_clause += ' AND Appearances.g_c >= 20'
	elif position == '1B':
		where_clause += ' AND Appearances.g_1b >= 20'
	elif position == '2B':
		where_clause += ' AND Appearances.g_2b >= 20'
	elif position == '3B':
		where_clause += ' AND Appearances.g_3b >= 20'
	elif position == 'SS':
		where_clause += ' AND Appearances.g_ss >= 20'
	elif position == 'OF':
		where_clause += ' AND Appearances.g_of >= 20'
	elif position == 'MI':
		where_clause += ' AND (Appearances.g_ss >= 20 OR Appearances.g_2b >= 20)'
	elif position == 'CI':
		where_clause += ' AND (Appearances.g_1b >= 20 OR Appearances.g_3b >= 20)'
			
	results = []
	start_fetch = time.time()
	query = 'SELECT Master.lahmanid, Master.nameFirst, Master.nameLast, draftapp_tnplteam.name, draftapp_tnplteam.id, draftapp_tnplownership.salary, SUM(Batting.AB), SUM(Batting.H), SUM(Batting.R), SUM(Batting.HR), SUM(Batting.RBI), SUM(Batting.SB), draftapp_tnplbattingproj.AB, draftapp_tnplbattingproj.H, draftapp_tnplbattingproj.R, draftapp_tnplbattingproj.HR, draftapp_tnplbattingproj.RBI, draftapp_tnplbattingproj.SB  FROM Master JOIN Batting USING(playerID) JOIN Appearances ON (Batting.playerID = Appearances.playerID AND Batting.yearID = Appearances.yearID) LEFT OUTER JOIN draftapp_tnplownership ON (draftapp_tnplownership.playerID = Master.playerID) LEFT OUTER JOIN draftapp_tnplteam ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id) LEFT OUTER JOIN draftapp_tnplbattingproj ON (draftapp_tnplbattingproj.playerID = Master.playerID) WHERE %s GROUP BY Batting.yearID, Batting.playerID' % (where_clause)
	print query
	cursor = connection.cursor()
	cursor.execute(query)
	for row in cursor:
		player = PlayerSummary()
		player.id = row[0]
		player.name = '%s %s' % (row[1], row[2])
		player.team = row[3]
		player.team_id = row[4]
		player.salary = row[5]
		player.ab = row[6]
		player.h = row[7]
		player.r = row[8]
		player.hr = row[9]
		player.rbi = row[10]
		player.sb = row[11]
		player.proj_ab = row[12]
		player.proj_h = row[13]
		player.proj_r = row[14]
		player.proj_hr = row[15]
		player.proj_rbi = row[16]
		player.proj_sb = row[17]
		results.append(player)
	done_fetch = time.time()
	print "Data Fetch duration: %d ms" % ((done_fetch - start_fetch) * 1000)
	print "%d players" % (len(results))

	def sort_key(player):
		return player.hitting_value().total_val()

	results.sort(key=sort_key, reverse=True)
	done_sort = time.time()
	print "Data Sort duration: %d ms" % ((done_sort - done_fetch) * 1000)
	print "Total time for view: %d ms" % ((done_sort - start) * 1000)

	def player_table_info(player):
		hitting_val = player.hitting_value()
		if player.salary is None:
			salary = None
		else:
			salary = float(player.salary)

		

		if player.team_id is None or player.team is None:
			team_column = {'value': None, 'highlight': True}
			salary_column = {'value': None, 'highlight': True}
		else:
			team_column = {'value': player.team,
				       'link': '/team/%d/' % (player.team_id)}
			salary_column = salary

		def columnize_val(value):
			if value > 100:
				return {'value': float(value),
					'highlight': True}
			else:
				return float(value)
			
		return ({'value': player.name,
			 'link': '/player/%d/' % (player.id)},
			team_column,
			salary_column,
			columnize_val(hitting_val.ba_val()),
			columnize_val(hitting_val.r_val()),
			columnize_val(hitting_val.hr_val()),
			columnize_val(hitting_val.rbi_val()),
			columnize_val(hitting_val.sb_val()))

	headers = (
		{'title': 'Player',
		 'cumulative': False},
		{'title': 'Team',
		 'cumulative': False},
		{'title': 'Salary',
		 'cumulative': False,
		 'tofixed': 2},
		{'title': 'BA',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'Runs',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'HR',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'RBI',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'SB',
		 'cumulative': True,
		 'tofixed': 1})

	table_results = [player_table_info(x) for x in results[:350]]

	return HttpResponse(simplejson.dumps({'headers': headers, 'rows': table_results}), mimetype='application/json')

def json_pitchers(request, form_data):
	start = time.time()
	where_clause = 'Pitching.yearID = %s' % (PREV_YEAR)
	position = form_data['position']
	if position == 'RP':
		where_clause += ' AND (Pitching.IPouts < 300 OR Pitching.SV > 0)'
	elif position == 'SP':
		where_clause += ' AND Pitching.IPouts >= 300'

	results = []
	start_fetch = time.time()
	query = 'SELECT Master.lahmanid, Master.nameFirst, Master.nameLast, draftapp_tnplteam.name, draftapp_tnplteam.id, draftapp_tnplownership.salary, SUM(Pitching.W), SUM(Pitching.SV), SUM(Pitching.IPouts), SUM(Pitching.H), SUM(Pitching.ER), SUM(Pitching.BB), SUM(Pitching.SO), draftapp_tnplpitchingproj.W, draftapp_tnplpitchingproj.SV, draftapp_tnplpitchingproj.IPouts, draftapp_tnplpitchingproj.H, draftapp_tnplpitchingproj.ER, draftapp_tnplpitchingproj.BB, draftapp_tnplpitchingproj.SO FROM Master JOIN Pitching USING(playerID) LEFT OUTER JOIN draftapp_tnplownership ON (draftapp_tnplownership.playerID = Master.playerID) LEFT OUTER JOIN draftapp_tnplteam ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id) LEFT OUTER JOIN draftapp_tnplpitchingproj ON (draftapp_tnplpitchingproj.playerID = Master.playerID) WHERE %s GROUP BY Pitching.yearID, Pitching.playerID' % (where_clause)
	print query
	cursor = connection.cursor()
	cursor.execute(query)
	for row in cursor:
		player = PlayerSummary()
		player.id = row[0]
		player.name = '%s %s' % (row[1], row[2])
		player.team = row[3]
		player.team_id = row[4]
		player.salary = row[5]
		player.w = row[6]
		player.sv = row[7]
		player.ipouts = row[8]
		player.h = row[9]
		player.er = row[10]
		player.bb = row[11]
		player.k = row[12]
		player.proj_w = row[13]
		player.proj_sv = row[14]
		player.proj_ipouts = row[15]
		player.proj_h = row[16]
		player.proj_er = row[17]
		player.proj_bb = row[18]
		player.proj_k = row[19]
		results.append(player)
	done_fetch = time.time()
	print "Data Fetch duration: %d ms" % ((done_fetch - start_fetch) * 1000)
	print "%d players" % (len(results))

	def sort_key(player):
		return player.pitching_value().total_val()

	results.sort(key=sort_key, reverse=True)
	done_sort = time.time()
	print "Data Sort duration: %d ms" % ((done_sort - done_fetch) * 1000)
	print "Total time for view: %d ms" % ((done_sort - start) * 1000)

	def player_table_info(player):
		pitching_val = player.pitching_value()

		if player.team_id is None or player.team is None:
			team_column = {'value': None, 'highlight': True}
			salary_column = {'value': None, 'highlight': True}
		else:
			team_column = {'value': player.team,
				       'link': '/team/%d/' % (player.team_id)}
			salary_column = float(player.salary)

		def columnize_val(value):
			if value > 100:
				return {'value': float(value),
					'highlight': True}
			else:
				return float(value)

		return ( {'value': player.name,
			  'link': '/player/%d/' % (player.id)},
			 team_column,
			 salary_column, 
			 columnize_val(pitching_val.era_val()),
			 columnize_val(pitching_val.whip_val()),
			 columnize_val(pitching_val.w_val()),
			 columnize_val(pitching_val.k_val()),
			 columnize_val(pitching_val.sv_val()))

	headers = (
		{'title': 'Player',
		 'cumulative': False},
		{'title': 'Team',
		 'cumulative': False},
		{'title': 'Salary',
		 'cumulative': False,
		 'tofixed': 2},
		{'title': 'ERA',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'WHIP',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'W',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'K',
		 'cumulative': True,
		 'tofixed': 1},
		{'title': 'S',
		 'cumulative': True,
		 'tofixed': 1})

	table_results = [player_table_info(x) for x in results[:350]]

	return HttpResponse(simplejson.dumps({'headers': headers, 'rows': table_results}), mimetype='application/json')


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

	# Get batting seasons
	query = 'SELECT yearID, teamID, SUM(AB), SUM(H), SUM(R), SUM(HR), SUM(RBI), SUM(SB) from Batting where playerID = %s GROUP BY yearID ORDER BY yearID'
	cursor = connection.cursor()
	cursor.execute(query, [player.playerid])
	seasons = []
	most_recent_teamid = None
	for row in cursor:
		most_recent_teamid = row[1]
		season = SeasonSummary()
		season.year = row[0]
		season.hitting_value = HittingValue(row[2], row[3], row[4], row[5], row[6], row[7])
		seasons.append(season)

	if most_recent_teamid is not None:
		team = Teams.objects.get(teamid=most_recent_teamid, yearid=seasons[-1].year).name
		
	else:
		team = None

	eligibility = set()
	try:
		appearances = player.appearances_set.get(yearid=PREV_YEAR)
		if (appearances.g_c > 20):
			eligibility.add('C')
		if (appearances.g_1b > 20):
			eligibility.add('1B')
			eligibility.add('CI')
		if (appearances.g_2b > 20):
			eligibility.add('2B')
			eligibility.add('MI')
		if (appearances.g_3b > 20):
			eligibility.add('3B')
			eligibility.add('CI')
		if (appearances.g_ss > 20):
			eligibility.add('SS')
			eligibility.add('MI')
		if (appearances.g_of > 20):
			eligibility.add('OF')
	except ObjectDoesNotExist:
		pass
	eligibility.add('U')
	def pos_sort_key(item):
		if item == 'C': return 0
		if item == '1B': return 5
		if item == '2B': return 10
		if item == '3B': return 15
		if item == 'SS': return 20
		if item == 'OF': return 25
		if item == 'CI': return 30
		if item == 'MI': return 35
		if item == 'U': return 40
	eligibility = sorted(eligibility, key=pos_sort_key)

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

	return render_to_response('hitter.html', {'name': name,
			                	  'seasons': seasons,
						  'bats': player.bats,
						  'throws': player.throws,
						  'birthdate': birthdate,
						  'age': age,
						  'team': team,
						  'eligibility': eligibility,
						  'ownership_form': ownership_form}, context_instance=RequestContext(request))

def pitcher(request, player):
	name = "%s %s" % (player.namefirst, player.namelast)

	query = 'SELECT yearID, teamID, SUM(W), SUM(SV), SUM(IPouts), SUM(H), SUM(ER), SUM(BB), SUM(SO) from Pitching where playerID = %s GROUP BY yearID ORDER BY yearID'
	cursor = connection.cursor()
	cursor.execute(query, [player.playerid])
	seasons = []
	most_recent_teamid = None
	for row in cursor:
		most_recent_teamid = row[1]
		season = SeasonSummary()
		season.year = row[0]
		season.pitching_value = PitchingValue(row[2], row[3], row[4], row[5], row[6], row[7], row[8])
		seasons.append(season)

	if most_recent_teamid is not None:
		team = Teams.objects.get(teamid=most_recent_teamid, yearid=seasons[-1].year).name
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

	return render_to_response('pitcher.html', {'name': name,
						   'seasons': seasons,
						   'bats': player.bats,
						   'throws': player.throws,
						   'birthdate': birthdate,
						   'age': age,
						   'team': team,
						   'ownership_form': ownership_form}, context_instance=RequestContext(request))

def player_search(request):
	query = request.GET['q']
	age_filter = Q(birthyear__gt=1962) # only players under 50
	terms = query.split()
	if len(terms) > 0:
		name_filter = Q(namefirst__istartswith=terms[0])
		name_filter |= Q(namelast__istartswith=terms[0])
		for term in terms[1:]:
			filter |= Q(namefirst__istartswith=term)
			filter |= Q(namelast__istartswith=term)

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
	hitters = []
	pitchers = []
	for ownership in team.tnplownership_set.all():
		player = ownership.playerid
		if player.is_pitcher():
			pitchers.append(ownership)
		else:
			hitters.append(ownership)

	hitters_summary = []
	for ownership in hitters:
		player = ownership.playerid
		summary = PlayerSummary()
		summary.id = player.lahmanid
		summary.name = '%s %s' % (player.namefirst, player.namelast)
		summary.salary = ownership.salary
		prev_year = player.batting_set.order_by('-yearid')[:1][0]
		summary.ab = prev_year.ab
		summary.h = prev_year.h
		summary.r = prev_year.r
		summary.hr = prev_year.hr
		summary.rbi = prev_year.rbi
		summary.sb = prev_year.sb
		try:
			proj_year = player.tnplbattingproj
			summary.proj_ab = proj_year.ab
			summary.proj_h = proj_year.h
			summary.proj_r = proj_year.r
			summary.proj_hr = proj_year.hr
			summary.proj_rbi = proj_year.rbi
			summary.proj_sb = proj_year.sb
		except ObjectDoesNotExist:
			summary.proj_ab = None
			summary.proj_h = None
			summary.proj_r = None
			summary.proj_hr = None
			summary.proj_rbi = None
			summary.proj_sb = None
		hitters_summary.append(summary)

	pitchers_summary = []
	for ownership in pitchers:
		player = ownership.playerid
		summary = PlayerSummary()
		summary.id = player.lahmanid
		summary.name = '%s %s' % (player.namefirst, player.namelast)
		summary.salary = ownership.salary
		prev_year = player.pitching_set.order_by('-yearid')[:1][0]
		summary.w = prev_year.w
		summary.sv = prev_year.sv
		summary.ipouts = prev_year.ipouts
		summary.h = prev_year.h
		summary.er = prev_year.er
		summary.bb = prev_year.bb
		summary.k = prev_year.so
		try:
			proj_year = player.tnplpitchingproj
			summary.proj_w = proj_year.w
			summary.proj_sv = proj_year.sv
			summary.proj_ipouts = proj_year.ipouts
			summary.proj_h = proj_year.h
			summary.proj_er = proj_year.er
			summary.proj_bb = proj_year.bb
			summary.proj_k = proj_year.so
		except ObjectDoesNotExist:
			summary.proj_w = None
			summary.proj_sv = None
			summary.proj_ipouts = None
			summary.proj_h = None
			summary.proj_er = None
			summary.proj_bb = None
			summary.proj_k = None
		pitchers_summary.append(summary)

	hitting_totals = {'BA': 0, 'Runs': 0, 'HR': 0, 'RBI': 0, 'SB': 0, 'salary': 0, 'player_count': len(hitters_summary)}
	
	for hitter in hitters_summary:
		hv = hitter.hitting_value()
		hitting_totals['BA'] += hv.ba_val()
		hitting_totals['Runs'] += hv.r_val()
		hitting_totals['HR'] += hv.hr_val()
		hitting_totals['RBI'] += hv.rbi_val()
		hitting_totals['SB'] += hv.sb_val()
		hitting_totals['salary'] += hitter.salary
	hitting_totals['avg_salary'] = hitting_totals['salary'] / hitting_totals['player_count']

	pitching_totals = {'ERA': 0, 'WHIP': 0, 'W': 0, 'K': 0, 'S': 0, 'salary': 0, 'player_count': len(pitchers_summary)}

	for pitcher in pitchers_summary:
		pv = pitcher.pitching_value()
		pitching_totals['ERA'] += pv.era_val()
		pitching_totals['WHIP'] += pv.whip_val()
		pitching_totals['W'] += pv.w_val()
		pitching_totals['K'] += pv.k_val()
		pitching_totals['S'] += pv.sv_val()
		pitching_totals['salary'] += pitcher.salary
	pitching_totals['avg_salary'] = pitching_totals['salary'] / pitching_totals['player_count']

	return render_to_response('team.html', {'name': name,
						  'hitters': hitters_summary,
						  'pitchers': pitchers_summary,
						  'hitting_totals': hitting_totals,
						  'pitching_totals': pitching_totals,
						  }, context_instance=RequestContext(request))

class TeamSummary(object):
	pass

def teams(request):
	teams = []
	for team in TNPLTeam.objects.all():
		summary = TeamSummary()
		summary.pitching_salary = 0
		summary.era_val = 0
		summary.whip_val = 0
		summary.w_val = 0
		summary.k_val = 0
		summary.sv_val = 0
		summary.pitching_val = 0
		summary.hitting_salary = 0
		summary.ba_val = 0
		summary.r_val = 0
		summary.hr_val = 0
		summary.rbi_val = 0
		summary.sb_val = 0
		summary.hitting_val = 0
			
		for ownership in team.tnplownership_set.all():
			player = ownership.playerid
			if player.is_pitcher():
				summary.pitching_salary += ownership.salary
				try:
					proj_year = player.tnplpitchingproj
					pv = PitchingValue(proj_year.w,
							   proj_year.sv,
							   proj_year.ipouts,
							   proj_year.h,
							   proj_year.er,
							   proj_year.bb,
							   proj_year.so)
				except ObjectDoesNotExist:
					prev_year = player.pitching_set.order_by('-yearid')[:1][0]
					pv = PitchingValue(prev_year.w,
							   prev_year.sv,
							   prev_year.ipouts,
							   prev_year.h,
							   prev_year.er,
							   prev_year.bb,
							   prev_year.so)

				summary.era_val += pv.era_val()
				summary.whip_val += pv.whip_val()
				summary.w_val += pv.w_val()
				summary.k_val += pv.k_val()
				summary.sv_val += pv.sv_val()
				summary.pitching_val += pv.total_val()
			else:
				summary.hitting_salary += ownership.salary
				try:
					proj_year = player.tnplbattingproj
					hv = HittingValue(proj_year.ab,
							  proj_year.h,
							  proj_year.r,
							  proj_year.hr,
							  proj_year.rbi,
							  proj_year.sb)
				except ObjectDoesNotExist:
					prev_year = player.batting_set.order_by('-yearid')[:1][0]
					hv = HittingValue(prev_year.ab,
							  prev_year.h,
							  prev_year.r,
							  prev_year.hr,
							  prev_year.rbi,
							  prev_year.sb)
				summary.ba_val += hv.ba_val()
				summary.r_val += hv.r_val()
				summary.hr_val += hv.hr_val()
				summary.rbi_val += hv.rbi_val()
				summary.sb_val += hv.sb_val()
				summary.hitting_val += hv.total_val()

		teams.append({'id': team.id, 'name': team.name, 'summary': summary})

	return render_to_response('teams.html', {'teams': teams}, context_instance=RequestContext(request))
		
		
