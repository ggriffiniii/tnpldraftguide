import copy
import math
import operator
from django.db import connection

PREV_YEAR = 2012
NUM_TEAMS = 13

NUM_C = 2
NUM_1B = 1
NUM_2B = 1
NUM_3B = 1
NUM_SS = 1
NUM_OF = 5
NUM_CI = 1
NUM_MI = 1
NUM_U = 2
NUM_P = 10

NUM_HITTERS = (NUM_C + NUM_1B + NUM_2B + NUM_3B + NUM_SS +
	       NUM_OF + NUM_CI + NUM_MI + NUM_U)
NUM_PLAYERS = NUM_HITTERS + NUM_P
SALARY_PER_TEAM = 130
MIN_BID = 0.5

class Player(object):
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.tnpl_team = None
		self.tnpl_team_id = None
		self.tnpl_salary = None
		self.positions = set()

	def get_position(self):
		if 'P' in self.positions:
			return 'P'
                elif 'C' in self.positions:
                        return 'C'
                elif 'SS' in self.positions:
                        return 'SS'
                elif '2B' in self.positions:
                        return '2B'
                elif '3B' in self.positions:
                        return '3B'
                elif 'OF' in self.positions:
                        return 'OF'
                elif '1B' in self.positions:
                        return '1B'
                else:
                        return 'U'

	def zscore(self, stats):
		pass

	def dollar(self, stats):
		pass

	# zscore with positional adjustments
	def adjusted_zscore(self, stats):
		return self.zscore(stats) + self.pos_zscore(stats)

	def adjusted_dollar(self, stats):
		return self.dollar(stats) + self.pos_dollar(stats)

	def pos_zscore(self, stats):
		return stats.get_replacement_value(self.get_position()) * -1

	def pos_dollar(self, stats):
		return stats.zscore_to_dollar(self.pos_zscore(stats)) + MIN_BID


class Hitter(Player):
	def __init__(self, id, name):
		super(Hitter, self).__init__(id, name)
		self.ab = 0
		self.h = 0
		self.r = 0
		self.hr = 0
		self.rbi = 0
		self.sb = 0
		self.positions = set(['U'])

	def ba(self):
		if self.ab > 0:
			return float(self.h) / self.ab
		else:
			return 0.0

	def zscore(self, stats):
		return (self.h_zscore(stats) + self.r_zscore(stats) +
			self.hr_zscore(stats) + self.rbi_zscore(stats) +
			self.sb_zscore(stats))

	def dollar(self, stats):
		return (self.h_dollar(stats) + self.r_dollar(stats) +
			self.hr_dollar(stats) + self.rbi_dollar(stats) +
			self.sb_dollar(stats))

	def h_zscore(self, stats):
		xh = self.h - (self.ab * stats.ba_mean)
		if stats.h_sd > 0.0:
			return xh / stats.h_sd
		else:
			return xh

	def h_dollar(self, stats):
		return stats.zscore_to_dollar(self.h_zscore(stats))

	def r_zscore(self, stats):
		xr = self.r - stats.r_mean
		if stats.r_sd > 0.0:
			return xr / stats.r_sd
		else:
			return xr

	def r_dollar(self, stats):
		return stats.zscore_to_dollar(self.r_zscore(stats))

	def hr_zscore(self, stats):
		xhr = self.hr - stats.hr_mean
		if stats.hr_sd > 0.0:
			return xhr / stats.hr_sd
		else:
			return xhr

	def hr_dollar(self, stats):
		return stats.zscore_to_dollar(self.hr_zscore(stats))

	def rbi_zscore(self, stats):
		xrbi = self.rbi - stats.rbi_mean
		if stats.rbi_sd > 0.0:
			return xrbi / stats.rbi_sd
		else:
			return xrbi

	def rbi_dollar(self, stats):
		return stats.zscore_to_dollar(self.rbi_zscore(stats))

	def sb_zscore(self, stats):
		xsb = self.sb - stats.sb_mean
		if stats.sb_sd > 0.0:
			return xsb / stats.sb_sd
		else:
			return xsb

	def sb_dollar(self, stats):
		return stats.zscore_to_dollar(self.sb_zscore(stats))


class Pitcher(Player):
	def __init__(self, id, name):
		super(Pitcher, self).__init__(id, name)
		self.positions = set(['P'])

	def ip(self):
		return self.ipouts / 3.0

	def era(self):
		if self.ipouts > 0:
			gp = self.ipouts / 27.0
			return self.er / gp
		else:
			return 0.0

	def whip(self):
		if self.ipouts > 0:
			ip = self.ipouts / 3.0
			return (self.h + self.bb) / ip
		else:
			return 0.0

	def zscore(self, stats):
		return (self.era_zscore(stats) + self.whip_zscore(stats) +
			self.w_zscore(stats) + self.k_zscore(stats) +
			self.s_zscore(stats))

	def dollar(self, stats):
		return (self.era_dollar(stats) + self.whip_dollar(stats) +
			self.w_dollar(stats) + self.k_dollar(stats) +
			self.s_dollar(stats))

	def era_zscore(self, stats):
		games_pitched = self.ipouts / 27.0
		xer = games_pitched * stats.era_mean - self.er
		if stats.er_sd > 0.0:
			return xer / stats.er_sd
		else:
			return xer

	def era_dollar(self, stats):
		return stats.zscore_to_dollar(self.era_zscore(stats))

	def whip_zscore(self, stats):
		wh = self.h + self.bb
		ip = self.ipouts / 3.0
		xwh = ip * stats.whip_mean - wh
		if stats.wh_sd > 0.0:
			return xwh / stats.wh_sd
		else:
			return xwh

	def whip_dollar(self, stats):
		return stats.zscore_to_dollar(self.whip_zscore(stats))

	def w_zscore(self, stats):
		xw = self.w - stats.w_mean
		if stats.w_sd > 0.0:
			return xw / stats.w_sd
		else:
			return xw

	def w_dollar(self, stats):
		return stats.zscore_to_dollar(self.w_zscore(stats))

	def k_zscore(self, stats):
		xk = self.k - stats.k_mean
		if stats.k_sd > 0.0:
			return xk / stats.k_sd
		else:
			return xk

	def k_dollar(self, stats):
		return stats.zscore_to_dollar(self.k_zscore(stats))

	def s_zscore(self, stats):
		xs = self.s - stats.s_mean
		if stats.s_sd > 0.0:
			return xs / stats.s_sd
		else:
			return xs

	def s_dollar(self, stats):
		return stats.zscore_to_dollar(self.s_zscore(stats))


class HittingQuery(object):
        year_query = '''
        SELECT
                Master.lahmanid,
                Master.nameFirst,
                Master.nameLast,
                draftapp_tnplteam.name,
                draftapp_tnplteam.id,
                draftapp_tnplownership.salary,
                BattingTotals.AB,
                BattingTotals.H,
                BattingTotals.R,
                BattingTotals.HR,
                BattingTotals.RBI,
                BattingTotals.SB,
                AppearancesTotals.g_c,
                AppearancesTotals.g_1b,
                AppearancesTotals.g_2b,
                AppearancesTotals.g_3b,
                AppearancesTotals.g_ss,
                AppearancesTotals.g_of
        FROM Master
        JOIN (
                SELECT
                        playerID,
                        SUM(AB) as AB,
                        SUM(H) as H,
                        SUM(R) as R,
                        SUM(HR) as HR,
                        SUM(RBI) as RBI,
                        SUM(SB) as SB
                FROM Batting
                WHERE yearID = %s
                GROUP BY playerID) AS BattingTotals
        USING(playerID) LEFT OUTER JOIN (
                SELECT
                        playerID,
                        SUM(g_c) AS g_c,
                        SUM(g_1b) AS g_1b,
                        SUM(g_2b) AS g_2b,
                        SUM(g_3b) AS g_3b,
                        SUM(g_ss) AS g_ss,
                        SUM(g_of) AS g_of
                FROM Appearances
                WHERE yearID = %s
                GROUP BY playerID) AS AppearancesTotals
        USING (playerID) LEFT OUTER JOIN
        draftapp_tnplownership
        USING (playerID) LEFT OUTER JOIN
        draftapp_tnplteam
        ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id)'''

        projection_query = '''
        SELECT
                Master.lahmanid,
                Master.nameFirst,
                Master.nameLast,
                draftapp_tnplteam.name,
                draftapp_tnplteam.id,
                draftapp_tnplownership.salary,
                BattingProj.AB,
                BattingProj.H,
                BattingProj.R,
                BattingProj.HR,
                BattingProj.RBI,
                BattingProj.SB,
                AppearancesTotals.g_c,
                AppearancesTotals.g_1b,
                AppearancesTotals.g_2b,
                AppearancesTotals.g_3b,
                AppearancesTotals.g_ss,
                AppearancesTotals.g_of
        FROM Master
        JOIN BattingProj
        USING(playerID) LEFT OUTER JOIN (
                SELECT
                        playerID,
                        SUM(g_c) AS g_c,
                        SUM(g_1b) AS g_1b,
                        SUM(g_2b) AS g_2b,
                        SUM(g_3b) AS g_3b,
                        SUM(g_ss) AS g_ss,
                        SUM(g_of) AS g_of
                FROM Appearances
                WHERE yearID = %s
                GROUP BY playerID) AS AppearancesTotals
        USING (playerID) LEFT OUTER JOIN
        draftapp_tnplownership
        USING (playerID) LEFT OUTER JOIN
        draftapp_tnplteam
        ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id)
        WHERE BattingProj.TYPE = %s;'''

        avg_query = '''
        SELECT
                Master.lahmanid,
                Master.nameFirst,
                Master.nameLast,
                draftapp_tnplteam.name,
                draftapp_tnplteam.id,
                draftapp_tnplownership.salary,
                BattingAverages.AB,
                BattingAverages.H,
                BattingAverages.R,
                BattingAverages.HR,
                BattingAverages.RBI,
                BattingAverages.SB,
                AppearancesTotals.g_c,
                AppearancesTotals.g_1b,
                AppearancesTotals.g_2b,
                AppearancesTotals.g_3b,
                AppearancesTotals.g_ss,
                AppearancesTotals.g_of
        FROM Master
        JOIN (
		SELECT
			playerID,
			AVG(BattingTotals.AB) as AB,
			AVG(BattingTotals.H) as H,
			AVG(BattingTotals.R) as R,
			AVG(BattingTotals.HR) as HR,
			AVG(BattingTotals.RBI) as RBI,
			AVG(BattingTotals.SB) as SB
		FROM (
			SELECT
				playerID,
				yearID,
				SUM(AB) as AB,
				SUM(H) as H,
				SUM(R) as R,
				SUM(HR) as HR,
				SUM(RBI) as RBI,
				SUM(SB) as SB
			FROM Batting
			GROUP BY playerID,yearID) AS BattingTotals
		WHERE BattingTotals.yearID > %s AND
		      BattingTotals.yearID <= %s
		GROUP BY playerID) AS BattingAverages
        USING(playerID) LEFT OUTER JOIN (
                SELECT
                        playerID,
                        SUM(g_c) AS g_c,
                        SUM(g_1b) AS g_1b,
                        SUM(g_2b) AS g_2b,
                        SUM(g_3b) AS g_3b,
                        SUM(g_ss) AS g_ss,
                        SUM(g_of) AS g_of
                FROM Appearances
                WHERE yearID = %s
                GROUP BY playerID) AS AppearancesTotals
        USING (playerID) LEFT OUTER JOIN
        draftapp_tnplownership
        USING (playerID) LEFT OUTER JOIN
        draftapp_tnplteam
        ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id)'''

        def get_cursor(self, dataset):
                cursor = connection.cursor()
                if dataset.startswith('proj_'):
                        proj_type = dataset[5:]
                        cursor.execute(HittingQuery.projection_query, (PREV_YEAR, proj_type))
                elif dataset.startswith('avg_'):
			n_years = int(dataset[4:])
			cursor.execute(HittingQuery.avg_query,
				       (PREV_YEAR - n_years,
					PREV_YEAR,
					PREV_YEAR))
                else:
                        year = int(dataset)
                        #cursor.execute(HittingQuery.year_query, (year, PREV_YEAR))
                        cursor.execute(HittingQuery.year_query, (year, year))
                return cursor


class PitchingQuery(object):
        year_query = '''
        SELECT
                Master.lahmanid,
                Master.nameFirst,
                Master.nameLast,
                draftapp_tnplteam.name,
                draftapp_tnplteam.id,
                draftapp_tnplownership.salary,
                PitchingTotals.W,
                PitchingTotals.SV,
                PitchingTotals.IPouts,
                PitchingTotals.H,
                PitchingTotals.ER,
                PitchingTotals.BB,
                PitchingTotals.SO
        FROM Master
        JOIN (
                SELECT
                        playerID,
                        SUM(W) AS W,
                        SUM(SV) AS SV,
                        SUM(IPouts) AS IPouts,
                        SUM(H) AS H,
                        SUM(ER) AS ER,
                        SUM(BB) AS BB,
                        SUM(SO) AS SO
                FROM Pitching
                WHERE yearID = %s
                GROUP BY playerID) AS PitchingTotals
        USING(playerID) LEFT OUTER JOIN draftapp_tnplownership
        USING (playerID)
        LEFT OUTER JOIN draftapp_tnplteam
        ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id)'''

        projection_query = '''
        SELECT
                Master.lahmanid,
                Master.nameFirst,
                Master.nameLast,
                draftapp_tnplteam.name,
                draftapp_tnplteam.id,
                draftapp_tnplownership.salary,
                PitchingProj.W,
                PitchingProj.SV,
                PitchingProj.IPouts,
                PitchingProj.H,
                PitchingProj.ER,
                PitchingProj.BB,
                PitchingProj.SO
        FROM Master
        JOIN PitchingProj
        USING(playerID) LEFT OUTER JOIN draftapp_tnplownership
        USING (playerID) LEFT OUTER JOIN draftapp_tnplteam
        ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id)
        WHERE PitchingProj.TYPE = %s'''

	avg_query = '''
        SELECT
                Master.lahmanid,
                Master.nameFirst,
                Master.nameLast,
                draftapp_tnplteam.name,
                draftapp_tnplteam.id,
                draftapp_tnplownership.salary,
                PitchingAverages.W,
                PitchingAverages.SV,
                PitchingAverages.IPouts,
                PitchingAverages.H,
                PitchingAverages.ER,
                PitchingAverages.BB,
                PitchingAverages.SO
        FROM Master
        JOIN (
		SELECT
			playerID,
			AVG(PitchingTotals.W) AS W,
			AVG(PitchingTotals.SV) AS SV,
			AVG(PitchingTotals.IPouts) AS IPouts,
			AVG(PitchingTotals.H) AS H,
			AVG(PitchingTotals.ER) AS ER,
			AVG(PitchingTotals.BB) AS BB,
			AVG(PitchingTotals.SO) AS SO
		FROM (
			SELECT
				playerID,
				yearID,
				SUM(W) AS W,
				SUM(SV) AS SV,
				SUM(IPouts) AS IPouts,
				SUM(H) AS H,
				SUM(ER) AS ER,
				SUM(BB) AS BB,
				SUM(SO) AS SO
			FROM Pitching
			GROUP BY playerID,yearID) AS PitchingTotals
		WHERE PitchingTotals.yearID > %s AND
		      PitchingTotals.yearID <= %s
		GROUP BY playerID) as PitchingAverages
        USING(playerID) LEFT OUTER JOIN draftapp_tnplownership
        USING (playerID)
        LEFT OUTER JOIN draftapp_tnplteam
        ON (draftapp_tnplownership.team_id = draftapp_tnplteam.id)'''

        def get_cursor(self, dataset):
                cursor = connection.cursor()
                if dataset.startswith('proj_'):
                        proj_type = dataset[5:]
                        cursor.execute(PitchingQuery.projection_query, (proj_type,))
                elif dataset.startswith('avg_'):
			n_years = int(dataset[4:])
			cursor.execute(PitchingQuery.avg_query,
				       (PREV_YEAR - n_years, PREV_YEAR))
                else:
                        year = int(dataset)
                        cursor.execute(PitchingQuery.year_query, (year,))
                return cursor


class PopulationStats(object):
	def UpdateStats(self, dataset):
		self.dataset = dataset
		self._fetch_hitters()
		self._fetch_pitchers()
		# First hitters
		for i in xrange(20):
			prev_list = self._hitters[:]
			self.calculate_hitter_mean()
			self.calculate_hitter_stddev()
			self._hitters.sort(
				key=operator.methodcaller('zscore', self),
				reverse=True)
			diff = [x for x, y
				in zip(prev_list, self._hitters)
				if x.id != y.id]
			if len(diff) == 0:
				print "Successfully found ideal hitter pool in %d iterations" % (i+1)
				break
		else:
			print "Couldn't find ideal hitter pool in %d iterations" % (i+1)

		# Now do pitchers
		for i in xrange(20):
			prev_list = self._pitchers[:]
			self.calculate_pitcher_mean()
			self.calculate_pitcher_stddev()
			self._pitchers.sort(
				key=operator.methodcaller('zscore', self),
				reverse=True)
			diff = [x for x, y
				in zip(prev_list, self._pitchers)
				if x.id != y.id]
			if len(diff) == 0:
				print "Successfully found ideal pitcher pool in %d iterations" % (i+1)
				break
		else:
			print "Couldn't find ideal pitcher pool in %d iterations" % (i+1)

		self.calculate_replacement_values()
		self._hitters.sort(
			key=operator.methodcaller('adjusted_zscore', self),
			reverse=True)
		self._pitchers.sort(
			key=operator.methodcaller('adjusted_zscore', self),
			reverse=True)
		self.calculate_sum_of_draft()
		self._initialize_free_agent_data()
		self.use_normal_dollar_values()

		print " ##### Hitting Stats #####"
                print "BA Mean: %.3f" % (self.ba_mean)
                print "BA STDDev: %.3f" % (self.h_sd)
                print "R Mean: %.3f" % (self.r_mean)
                print "R STDDev: %.3f" % (self.r_sd)
                print "HR Mean: %.3f" % (self.hr_mean)
                print "HR STDDev: %.3f" % (self.hr_sd)
                print "RBI Mean: %.3f" % (self.rbi_mean)
                print "RBI STDDev: %.3f" % (self.rbi_sd)
                print "SB Mean: %.3f" % (self.sb_mean)
                print "SB STDDev: %.3f" % (self.sb_sd)
		print " ##### Pitching Stats #####"
		print "ERA Mean: %.3f" % (self.era_mean)
		print "ERA STDDev: %.3f" % (self.er_sd)
		print "WHIP Mean: %.3f" % (self.whip_mean)
		print "WHIP STDDev: %.3f" % (self.wh_sd)
		print "W Mean: %.3f" % (self.w_mean)
		print "W STDDev: %.3f" % (self.w_sd)
		print "K Mean: %.3f" % (self.k_mean)
		print "K STDDev: %.3f" % (self.k_sd)
		print "S Mean: %.3f" % (self.s_mean)
		print "S STDDev: %.3f" % (self.s_sd)

	def _fetch_hitters(self):
		self._hitters = []
		self._unordered_hitters = {}
		query = HittingQuery()
		cursor = query.get_cursor(self.dataset)
		for row in cursor:
			id = row[0]
			hitter = Hitter(id, '%s %s' % (row[1], row[2]))
			hitter.tnpl_team = row[3]
			hitter.tnpl_team_id = row[4]
			if row[5] is None:
				hitter.tnpl_salary = None
			else:
				hitter.tnpl_salary = float(row[5])
			if row[6] is None:
				hitter.ab = 0
				hitter.h = 0
				hitter.r = 0
				hitter.hr = 0
				hitter.rbi = 0
				hitter.sb = 0
			else:
				hitter.ab = int(row[6])
				hitter.h = int(row[7])
				hitter.r = int(row[8])
				hitter.hr = int(row[9])
				hitter.rbi = int(row[10])
				hitter.sb = int(row[11])
			g_c = row[12]
			g_1b = row[13]
			g_2b = row[14]
			g_3b = row[15]
			g_ss = row[16]
			g_of = row[17]
			if g_c is not None and g_c >= 20:
				hitter.positions.add('C')
			if g_1b is not None and g_1b >= 20:
				hitter.positions.update(['1B', 'CI'])
			if g_2b is not None and g_2b >= 20:
				hitter.positions.update(['2B', 'MI'])
			if g_3b is not None and g_3b >= 20:
				hitter.positions.update(['3B', 'CI'])
			if g_ss is not None and g_ss >= 20:
				hitter.positions.update(['SS', 'MI'])
			if g_of is not None and g_of >= 20:
				hitter.positions.add('OF')
			self._hitters.append(hitter)
			self._unordered_hitters[id] = hitter

	def _fetch_pitchers(self):
		self._pitchers = []
		self._unordered_pitchers = {}
		query = PitchingQuery()
		cursor = query.get_cursor(self.dataset)
		for row in cursor:
			id = row[0]
			pitcher = Pitcher(id, '%s %s' % (row[1], row[2]))
			pitcher.tnpl_team = row[3]
			pitcher.tnpl_team_id = row[4]
			if row[5] is None:
				pitcher.tnpl_salary = None
			else:
				pitcher.tnpl_salary = float(row[5])
			pitcher.w = int(row[6])
			pitcher.s = int(row[7])
			pitcher.ipouts = int(row[8])
			pitcher.h = int(row[9])
			pitcher.er = int(row[10])
			pitcher.bb = int(row[11])
			pitcher.k = int(row[12])
			self._pitchers.append(pitcher)
			self._unordered_pitchers[id] = pitcher

	def calculate_hitter_mean(self):
		entries = 0

		ab_sum = 0
		h_sum = 0
		r_sum = 0
		hr_sum = 0
		rbi_sum = 0
		sb_sum = 0

		for hitter in self._hitters:
			if not self._count_hitter_for_stats(hitter): continue
			entries += 1
			ab_sum += hitter.ab
			h_sum += hitter.h
			r_sum += hitter.r
			hr_sum += hitter.hr
			rbi_sum += hitter.rbi
			sb_sum += hitter.sb
			if entries == NUM_HITTERS * NUM_TEAMS:
				break

		if ab_sum > 0:
			self.ba_mean = float(h_sum) / ab_sum
		else:
			self.ba_mean = 0.0
		self.r_mean = float(r_sum) / entries
		self.hr_mean = float(hr_sum) / entries
		self.rbi_mean = float(rbi_sum) / entries
		self.sb_mean = float(sb_sum) / entries

	def calculate_pitcher_mean(self):
		entries = 0

		ipouts_sum = 0
		er_sum = 0
		bb_sum = 0
		h_sum = 0
		w_sum = 0
		k_sum = 0
		s_sum = 0
		for pitcher in self._pitchers:
			if not self._count_pitcher_for_stats(pitcher): continue
			entries += 1
			ipouts_sum += pitcher.ipouts
			er_sum += pitcher.er
			bb_sum += pitcher.bb
			h_sum += pitcher.h
			w_sum += pitcher.w
			k_sum += pitcher.k
			s_sum += pitcher.s
			if entries == NUM_P * NUM_TEAMS:
				break

		self.era_mean = er_sum / (ipouts_sum / 27.0)
		self.whip_mean = (bb_sum + h_sum) / (ipouts_sum / 3.0)
		self.w_mean = float(w_sum) / entries
		self.k_mean = float(k_sum) / entries
		self.s_mean = float(s_sum) / entries

	def calculate_hitter_stddev(self):
		entries = 0

		h_var_sum = 0
		r_var_sum = 0
		hr_var_sum = 0
		rbi_var_sum = 0
		sb_var_sum = 0

		for hitter in self._hitters:
			if not self._count_hitter_for_stats(hitter): continue
			entries += 1
			xh = hitter.h - (hitter.ab * self.ba_mean)
			h_var_sum += math.pow(xh, 2)
			r_var_sum += math.pow(hitter.r - self.r_mean, 2)
			hr_var_sum += math.pow(hitter.hr - self.hr_mean, 2)
			rbi_var_sum += math.pow(hitter.rbi - self.rbi_mean, 2)
			sb_var_sum += math.pow(hitter.sb - self.sb_mean, 2)
			if entries == NUM_HITTERS * NUM_TEAMS:
				break
				

		self.h_sd = math.sqrt(h_var_sum / entries)
		self.r_sd = math.sqrt(r_var_sum / entries)
		self.hr_sd = math.sqrt(hr_var_sum / entries)
		self.rbi_sd = math.sqrt(rbi_var_sum / entries)
		self.sb_sd = math.sqrt(sb_var_sum / entries)
		
	def calculate_pitcher_stddev(self):
		entries = 0

		er_var_sum = 0
		wh_var_sum = 0
		w_var_sum = 0
		k_var_sum = 0
		s_var_sum = 0

		for pitcher in self._pitchers:
			if not self._count_pitcher_for_stats(pitcher): continue
			entries += 1
			xer = pitcher.ipouts / 27.0 * self.era_mean - pitcher.er
			er_var_sum += math.pow(xer, 2)
			wh = pitcher.bb + pitcher.h
			xwh = pitcher.ipouts / 3.0 * self.whip_mean - wh
			wh_var_sum += math.pow(xwh, 2)
			w_var_sum += math.pow(pitcher.w - self.w_mean, 2)
			k_var_sum += math.pow(pitcher.k - self.k_mean, 2)
			s_var_sum += math.pow(pitcher.s - self.s_mean, 2)
			if entries == NUM_P * NUM_TEAMS:
				break

		self.er_sd = math.sqrt(er_var_sum / entries)
		self.wh_sd = math.sqrt(wh_var_sum / entries)
		self.w_sd = math.sqrt(w_var_sum / entries)
		self.k_sd = math.sqrt(k_var_sum / entries)
		self.s_sd = math.sqrt(s_var_sum / entries)

	def _count_hitter_for_stats(self, hitter):
		return hitter.ab > 0

	def _count_pitcher_for_stats(self, pitcher):
		return pitcher.ipouts > 300 or pitcher.s >= 15

	def _update_position_value(self, pos, zscore):
		if self.pos_remaining[pos] > 0:
			self.rv[pos] = zscore
			self.pos_remaining[pos] -= 1
		elif pos in ('1B', '3B'):
			self._update_flex_position_value(pos, 'CI', zscore)
		elif pos in ('SS', '2B'):
			self._update_flex_position_value(pos, 'MI', zscore)
		elif self.pos_remaining['U'] > 0:
			self.rv[pos] = zscore
			self.pos_remaining['U'] -= 1
			self._decrement_flex_position(zscore)

	def _update_flex_position_value(self, orig_pos, flex_pos, zscore):
		if self.pos_remaining[flex_pos] > 0:
			self.rv[orig_pos] = zscore
			self.pos_remaining[flex_pos] -= 1
			self._decrement_flex_position(zscore)
		elif self.pos_remaining['U'] > 0:
			self.rv[orig_pos] = zscore
			self.pos_remaining['U'] -= 1
			self._decrement_flex_position(zscore)

	def _decrement_flex_position(self, zscore):
		self.available_flex_positions -= 1
		if self.available_flex_positions == 0:
			self.rv['U'] = zscore

	def calculate_replacement_values(self):
		self.rv = {}
		self.pos_remaining = {
			'C': NUM_C * NUM_TEAMS,
			'1B': NUM_1B * NUM_TEAMS,
			'2B': NUM_2B * NUM_TEAMS,
			'3B': NUM_3B * NUM_TEAMS,
			'SS': NUM_SS * NUM_TEAMS,
			'OF': NUM_OF * NUM_TEAMS,
			'CI': NUM_CI * NUM_TEAMS,
			'MI': NUM_MI * NUM_TEAMS,
			'U': NUM_U * NUM_TEAMS,
			'P': NUM_P * NUM_TEAMS,
		}
		self.available_flex_positions = (self.pos_remaining['CI'] +
						 self.pos_remaining['MI'] +
						 self.pos_remaining['U'])
                for hitter in self._hitters:
                        pos = hitter.get_position()
			zs = hitter.zscore(self)
			self._update_position_value(pos, zs)

		for pitcher in self._pitchers:
			zs = pitcher.zscore(self)
			self._update_position_value('P', zs)

                for k, v in self.rv.iteritems():
                        print "Replacement %s: %.3f" % (k, v * -1)

	def calculate_sum_of_draft(self):
		self.normal_zscore_sum = 0.0
		self.free_agent_zscore_sum = 0.0
		for hitter in self._hitters:
			x = hitter.adjusted_zscore(self)
			if x > 0.0:
				self.normal_zscore_sum += x
				if hitter.tnpl_team is None:
					self.free_agent_zscore_sum += x
			else:
				break

		for pitcher in self._pitchers:
			x = pitcher.adjusted_zscore(self)
			if x > 0.0:
				self.normal_zscore_sum += x
				if pitcher.tnpl_team is None:
					self.free_agent_zscore_sum += x
			else:
				break

	def get_hitting_distributions(self):
		def add_or_increment(dict, key):
			if dict.has_key(key):
				dict[key] += 1
			else:
				dict[key] = 1

		dists = {'H': {}, 'R': {}, 'HR': {}, 'RBI': {}, 'SB': {}}
		free_dists = {'H': {}, 'R': {}, 'HR': {}, 'RBI': {}, 'SB': {}}
		for hitter in self._hitters:
			if hitter.adjusted_zscore(self) < 0.0: break
			if hitter.tnpl_team is None:
				dist = free_dists
			else:
				dist = dists
			xh = int(round(hitter.h - (hitter.ab * self.ba_mean)))
			add_or_increment(dist['H'], xh)
			add_or_increment(dist['R'], hitter.r / 2)
			add_or_increment(dist['HR'], hitter.hr)
			add_or_increment(dist['RBI'], hitter.rbi / 2)
			add_or_increment(dist['SB'], hitter.sb / 2)

		dist_data = []
		for category in ('H', 'R', 'HR', 'RBI', 'SB'):
			c = {'title': category}
			multiplier = 1
			if category == 'H':
				c['mean'] = 0
			elif category == 'R':
				c['mean'] = int(round(self.r_mean))
				multiplier = 2
			elif category == 'HR':
				c['mean'] = int(round(self.hr_mean))
			elif category == 'RBI':
				c['mean'] = int(round(self.rbi_mean))
				multiplier = 2
			elif category == 'SB':
				c['mean'] = int(round(self.sb_mean))
				multiplier = 2
			
			cmin = min(dists[category].keys() +
				   free_dists[category].keys())
			cmax = max(dists[category].keys() +
				   free_dists[category].keys())
			values = []
			free_values = []
			for i in range(cmin, cmax+1):
				if dists[category].has_key(i):
					values.append([i * multiplier, dists[category][i]])
				else:
					values.append([i * multiplier, 0])
				if free_dists[category].has_key(i):
					free_values.append([i * multiplier, free_dists[category][i]])
				else:
					free_values.append([i * multiplier, 0])
			c['data'] = values
			c['free_data'] = free_values
			dist_data.append(c)
		return dist_data

	def get_pitching_distributions(self):
		def add_or_increment(dict, key):
			if dict.has_key(key):
				dict[key] += 1
			else:
				dict[key] = 1

		dists = {'ER': {}, 'WH': {}, 'W': {}, 'K': {}, 'S': {}}
		free_dists = {'ER': {}, 'WH': {}, 'W': {}, 'K': {}, 'S': {}}
		for pitcher in self._pitchers:
			if pitcher.adjusted_zscore(self) < 0.0: break
			if pitcher.tnpl_team is None:
				dist = free_dists
			else:
				dist = dists
			gp = pitcher.ipouts / 27.0
			xer = int(round(gp * self.era_mean - pitcher.er))
			add_or_increment(dist['ER'], xer)
			ip = pitcher.ipouts / 3.0
			xwh = int(round(ip * self.whip_mean - pitcher.h - pitcher.bb))
			add_or_increment(dist['WH'], xwh)
			add_or_increment(dist['W'], pitcher.w)
			add_or_increment(dist['K'], pitcher.k / 5)
			if pitcher.s > 0:
				add_or_increment(dist['S'], pitcher.s)

		dist_data = []
		for category in ('ER', 'WH', 'W', 'K', 'S'):
			c = {'title': category}
			multiplier = 1
			if category == 'ER':
				c['mean'] = 0
			elif category == 'WH':
				c['mean'] = 0
			elif category == 'W':
				c['mean'] = int(round(self.w_mean))
			elif category == 'K':
				c['mean'] = int(round(self.k_mean))
				multiplier = 5
			elif category == 'S':
				c['mean'] = int(round(self.s_mean))
			
			cmin = min(dists[category].keys() + free_dists[category].keys())
			cmax = max(dists[category].keys() + free_dists[category].keys())
			values = []
			free_values = []
			for i in range(cmin, cmax+1):
				if dists[category].has_key(i):
					values.append([i * multiplier, dists[category][i]])
				else:
					values.append([i * multiplier, 0])
				if free_dists[category].has_key(i):
					free_values.append([i * multiplier, free_dists[category][i]])
				else:
					free_values.append([i * multiplier, 0])
			c['data'] = values
			c['free_data'] = free_values
			dist_data.append(c)
		return dist_data

	def _initialize_free_agent_data(self):
		self.free_agent_salary_remaining = 0.0
		self.free_agent_positions_remaining = 0
                cursor = connection.cursor()
		cursor.execute('''
			SELECT
				COUNT(playerID),
				SUM(salary)
			FROM draftapp_tnplownership
			GROUP BY team_id''')
		for row in cursor:
			num_players = int(row[0])
			salary = float(row[1])
			if num_players < NUM_PLAYERS:
				self.free_agent_salary_remaining += (
					SALARY_PER_TEAM - salary)
				self.free_agent_positions_remaining += (
					NUM_PLAYERS - num_players)

	def use_normal_dollar_values(self):
		self.positions_remaining = NUM_PLAYERS * NUM_TEAMS
		self.salary_remaining = SALARY_PER_TEAM * NUM_TEAMS
		self.zscore_sum = self.normal_zscore_sum
		print " ##### Using normal dollar values #####"
                print "Sum of Draft: %.3f" % (self.zscore_sum)
                print "Total Salary: %.3f" % (self.salary_remaining)

	def use_free_agent_dollar_values(self):
		self.positions_remaining = self.free_agent_positions_remaining
		self.salary_remaining = self.free_agent_salary_remaining
		self.zscore_zum = self.free_agent_zscore_sum
		print " ##### Using free agent dollar values #####"
                print "Sum of Draft: %.3f" % (self.zscore_sum)
                print "Total Salary: %.3f" % (self.salary_remaining)

	def get_replacement_value(self, position):
		return self.rv.get(position, 0.0)

	def zscore_to_dollar(self, zscore):
		min_salary = self.positions_remaining * MIN_BID
		marginal_salary = self.salary_remaining - min_salary
		if self.zscore_sum == 0:
			return 0.0
		zscore_ratio = zscore / self.zscore_sum
		return zscore_ratio * marginal_salary

	def get_hitter(self, playerid):
		return self._unordered_hitters.get(playerid, None)

	def get_pitcher(self, playerid):
		return self._unordered_pitchers.get(playerid, None)

	def get_player(self, playerid):
		hitter = self.get_hitter(playerid)
		pitcher = self.get_pitcher(playerid)
		if hitter is None:
			return pitcher
		elif pitcher is None:
			return hitter
		else:
			h_val = hitter.adjusted_dollar(self)
			p_val = pitcher.adjusted_dollar(self)
			if p_val > h_val:
				return pitcher
			else:
				return hitter
		

	def hitters(self, pos=None):
		if pos is None:
			return self._hitters
		else:
			return [x for x in self._hitters if pos in x.positions]

	def pitchers(self):
		return self._pitchers

