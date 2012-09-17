# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models
from decimal import Decimal

class HittingValue(object):
    def __init__(self, ab, h, runs, hr, rbi, sb):
        self.ab = ab
        self.h = h
        self.r = runs
        self.hr = hr
        self.rbi = rbi
        self.sb = sb

    _AB_PER_PLAYER = 550
    _PLAYERS_PER_TEAM = 15
    _POINTS_PER_CATEGORY = 100

    _RUNS_GOAL = 1217
    _RBI_GOAL = 1191
    _HR_GOAL = 321
    _SB_GOAL = 226
    _BA_GOAL = Decimal('0.278')

    _RUNS_MUL = Decimal(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _RUNS_GOAL
    _RBI_MUL = Decimal(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _RBI_GOAL
    _HR_MUL = Decimal(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _HR_GOAL
    _SB_MUL = Decimal(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _SB_GOAL
    _HITS_MUL = _POINTS_PER_CATEGORY / (_BA_GOAL * _AB_PER_PLAYER)

    def ba(self):
	if self.ab > 0:
		return Decimal(self.h) / self.ab
	else:
		return 0.0

    def r_val(self):
	return self.r * HittingValue._RUNS_MUL

    def hr_val(self):
	return self.hr * HittingValue._HR_MUL

    def rbi_val(self):
	return self.rbi * HittingValue._RBI_MUL

    def sb_val(self):
	return self.sb * HittingValue._SB_MUL

    def ba_val(self):
	return (HittingValue._POINTS_PER_CATEGORY+
                ((self.h-(self.ab*HittingValue._BA_GOAL))
		 *HittingValue._HITS_MUL))

    def total_val(self):
	return (self.r_val() + self.hr_val() + self.rbi_val() +
                self.sb_val() + self.ba_val())

class PitchingValue(object):
	def __init__(self, w, sv, ipouts, h, er, bb, k):
		self.w = w
		self.sv = sv
		self.ipouts = ipouts
		self.h = h
		self.er = er
		self.bb = bb
		self.k = k

	_IP_PER_PLAYER = 165
	_PLAYERS_PER_TEAM = 10
	_POINTS_PER_CATEGORY = 100

	_WINS_GOAL = 123
	_SAVES_GOAL = 105
	_K_GOAL = 1609
	_ERA_GOAL = Decimal('3.35')
	_WHIP_GOAL = Decimal('1.175')

	_WINS_MUL = Decimal(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _WINS_GOAL
	_SAVES_MUL = Decimal(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _SAVES_GOAL
	_K_MUL = Decimal(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _K_GOAL
	_WH_MUL = _POINTS_PER_CATEGORY / (_WHIP_GOAL * _IP_PER_PLAYER)
	_ER_MUL = _POINTS_PER_CATEGORY / (_ERA_GOAL * (_IP_PER_PLAYER / 9))

	def ip(self):
		return Decimal(self.ipouts) / 3

	def wh(self):
		return self.h + self.bb

	def era(self):
		if self.ipouts > 0:
			return Decimal(self.er) / self.ipouts * 27
		else:
			return Decimal(0)

	def whip(self):
		if self.ipouts > 0:
			return (Decimal(self.h) + Decimal(self.bb)) / self.ipouts * 3
		else:
			return Decimal(0)

	def w_val(self):
		return self.w * PitchingValue._WINS_MUL

	def sv_val(self):
		return self.sv * PitchingValue._SAVES_MUL

	def k_val(self):
		return self.k * PitchingValue._K_MUL

	def whip_val(self):
		return (PitchingValue._POINTS_PER_CATEGORY+
			((((self.ipouts/3)*PitchingValue._WHIP_GOAL)-self.wh())
			 *PitchingValue._WH_MUL))

	def era_val(self):
		return (PitchingValue._POINTS_PER_CATEGORY+
			((((self.ipouts/27)*PitchingValue._ERA_GOAL)-self.er)
			 *PitchingValue._ER_MUL))

	def total_val(self):
		return (self.w_val() + self.sv_val() + self.k_val() +
			self.whip_val() + self.era_val())


class Player(models.Model):
    lahmanid = models.IntegerField(null=True, db_column='lahmanID', blank=True, primary_key=True) 
    playerid = models.CharField(max_length=30, db_column='playerID', unique=True) 
    managerid = models.CharField(max_length=30, db_column='managerID', blank=True) 
    hofid = models.CharField(max_length=30, db_column='hofID', blank=True) 
    birthyear = models.IntegerField(null=True, db_column='birthYear', blank=True) 
    birthmonth = models.IntegerField(null=True, db_column='birthMonth', blank=True) 
    birthday = models.IntegerField(null=True, db_column='birthDay', blank=True) 
    birthcountry = models.CharField(max_length=150, db_column='birthCountry', blank=True) 
    birthstate = models.CharField(max_length=6, db_column='birthState', blank=True) 
    birthcity = models.CharField(max_length=150, db_column='birthCity', blank=True) 
    deathyear = models.IntegerField(null=True, db_column='deathYear', blank=True) 
    deathmonth = models.IntegerField(null=True, db_column='deathMonth', blank=True) 
    deathday = models.IntegerField(null=True, db_column='deathDay', blank=True) 
    deathcountry = models.CharField(max_length=150, db_column='deathCountry', blank=True) 
    deathstate = models.CharField(max_length=6, db_column='deathState', blank=True) 
    deathcity = models.CharField(max_length=150, db_column='deathCity', blank=True) 
    namefirst = models.CharField(max_length=150, db_column='nameFirst', blank=True) 
    namelast = models.CharField(max_length=150, db_column='nameLast', blank=True) 
    namenote = models.CharField(max_length=765, db_column='nameNote', blank=True) 
    namegiven = models.CharField(max_length=765, db_column='nameGiven', blank=True) 
    namenick = models.CharField(max_length=765, db_column='nameNick', blank=True) 
    weight = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    bats = models.CharField(max_length=3, blank=True)
    throws = models.CharField(max_length=3, blank=True)
    debut = models.DateTimeField(null=True, blank=True)
    finalgame = models.DateTimeField(null=True, db_column='finalGame', blank=True) 
    college = models.CharField(max_length=150, blank=True)
    lahman40id = models.CharField(max_length=27, db_column='lahman40ID', blank=True) 
    lahman45id = models.CharField(max_length=27, db_column='lahman45ID', blank=True) 
    retroid = models.CharField(max_length=27, db_column='retroID', blank=True) 
    holtzid = models.CharField(max_length=27, db_column='holtzID', blank=True) 
    bbrefid = models.CharField(max_length=27, db_column='bbrefID', blank=True) 
    class Meta:
        db_table = u'Master'

    def __unicode__(self):
	return "%s %s" % (self.namefirst, self.namelast)

    def is_pitcher(self):
	apps = self.appearances_set.order_by('yearid')[:1][0]
	return float(apps.g_p) / apps.g_all > 0.5


class Appearances(models.Model):
    yearid = models.IntegerField(null=True, db_column='yearID', blank=True) 
    teamid = models.CharField(max_length=9, db_column='teamID', blank=True) 
    lgid = models.CharField(max_length=6, db_column='lgID', blank=True) 
    playerid = models.ForeignKey(Player, db_column='playerID', to_field='playerid') 
    g_all = models.IntegerField(null=True, db_column='G_all', blank=True) 
    g_s = models.IntegerField(null=True, db_column='GS', blank=True) 
    g_batting = models.IntegerField(null=True, db_column='G_batting', blank=True) 
    g_defense = models.IntegerField(null=True, db_column='G_defense', blank=True) 
    g_p = models.IntegerField(null=True, db_column='G_p', blank=True) 
    g_c = models.IntegerField(null=True, db_column='G_c', blank=True) 
    g_1b = models.IntegerField(null=True, db_column='G_1b', blank=True) 
    g_2b = models.IntegerField(null=True, db_column='G_2b', blank=True) 
    g_3b = models.IntegerField(null=True, db_column='G_3b', blank=True) 
    g_ss = models.IntegerField(null=True, db_column='G_ss', blank=True) 
    g_lf = models.IntegerField(null=True, db_column='G_lf', blank=True) 
    g_cf = models.IntegerField(null=True, db_column='G_cf', blank=True) 
    g_rf = models.IntegerField(null=True, db_column='G_rf', blank=True) 
    g_of = models.IntegerField(null=True, db_column='G_of', blank=True) 
    g_dh = models.IntegerField(null=True, db_column='G_dh', blank=True) 
    g_ph = models.IntegerField(null=True, db_column='G_ph', blank=True) 
    g_pr = models.IntegerField(null=True, db_column='G_pr', blank=True) 
    class Meta:
        db_table = u'Appearances'

class Batting(models.Model):
    playerid = models.ForeignKey(Player, db_column='playerID', to_field='playerid') 
    yearid = models.IntegerField(null=True, db_column='yearID', blank=True) 
    stint = models.IntegerField(null=True, blank=True)
    teamid = models.CharField(max_length=9, db_column='teamID', blank=True) 
    lgid = models.CharField(max_length=6, db_column='lgID', blank=True) 
    g = models.IntegerField(null=True, db_column='G', blank=True) 
    g_batting = models.IntegerField(null=True, db_column='G_batting', blank=True) 
    ab = models.IntegerField(null=True, db_column='AB', blank=True) 
    r = models.IntegerField(null=True, db_column='R', blank=True) 
    h = models.IntegerField(null=True, db_column='H', blank=True) 
    
    
    hr = models.IntegerField(null=True, db_column='HR', blank=True) 
    rbi = models.IntegerField(null=True, db_column='RBI', blank=True) 
    sb = models.IntegerField(null=True, db_column='SB', blank=True) 
    cs = models.IntegerField(null=True, db_column='CS', blank=True) 
    bb = models.IntegerField(null=True, db_column='BB', blank=True) 
    so = models.IntegerField(null=True, db_column='SO', blank=True) 
    ibb = models.IntegerField(null=True, db_column='IBB', blank=True) 
    hbp = models.IntegerField(null=True, db_column='HBP', blank=True) 
    sh = models.IntegerField(null=True, db_column='SH', blank=True) 
    sf = models.IntegerField(null=True, db_column='SF', blank=True) 
    gidp = models.IntegerField(null=True, db_column='GIDP', blank=True) 
    g_old = models.IntegerField(null=True, db_column='G_old', blank=True) 
    class Meta:
        db_table = u'Batting'

        

class Pitching(models.Model):
    playerid = models.ForeignKey(Player, db_column='playerID', to_field='playerid') 
    yearid = models.IntegerField(null=True, db_column='yearID', blank=True) 
    stint = models.IntegerField(null=True, blank=True)
    teamid = models.CharField(max_length=9, db_column='teamID', blank=True) 
    lgid = models.CharField(max_length=6, db_column='lgID', blank=True) 
    w = models.IntegerField(null=True, db_column='W', blank=True) 
    l = models.IntegerField(null=True, db_column='L', blank=True) 
    g = models.IntegerField(null=True, db_column='G', blank=True) 
    gs = models.IntegerField(null=True, db_column='GS', blank=True) 
    cg = models.IntegerField(null=True, db_column='CG', blank=True) 
    sho = models.IntegerField(null=True, db_column='SHO', blank=True) 
    sv = models.IntegerField(null=True, db_column='SV', blank=True) 
    ipouts = models.IntegerField(null=True, db_column='IPouts', blank=True) 
    h = models.IntegerField(null=True, db_column='H', blank=True) 
    er = models.IntegerField(null=True, db_column='ER', blank=True) 
    hr = models.IntegerField(null=True, db_column='HR', blank=True) 
    bb = models.IntegerField(null=True, db_column='BB', blank=True) 
    so = models.IntegerField(null=True, db_column='SO', blank=True) 
    baopp = models.FloatField(null=True, db_column='BAOpp', blank=True) 
    era = models.FloatField(null=True, db_column='ERA', blank=True) 
    ibb = models.IntegerField(null=True, db_column='IBB', blank=True) 
    wp = models.IntegerField(null=True, db_column='WP', blank=True) 
    hbp = models.IntegerField(null=True, db_column='HBP', blank=True) 
    bk = models.IntegerField(null=True, db_column='BK', blank=True) 
    bfp = models.IntegerField(null=True, db_column='BFP', blank=True) 
    gf = models.IntegerField(null=True, db_column='GF', blank=True) 
    r = models.IntegerField(null=True, db_column='R', blank=True) 
    sh = models.IntegerField(null=True, db_column='SH', blank=True) 
    sf = models.IntegerField(null=True, db_column='SF', blank=True) 
    gidp = models.IntegerField(null=True, db_column='GIDP', blank=True) 
    class Meta:
        db_table = u'Pitching'


class Teams(models.Model):
    yearid = models.IntegerField(null=True, db_column='yearID', blank=True) 
    lgid = models.CharField(max_length=6, db_column='lgID', blank=True) 
    teamid = models.CharField(max_length=9, db_column='teamID', blank=True) 
    franchid = models.CharField(max_length=9, db_column='franchID', blank=True) 
    divid = models.CharField(max_length=3, db_column='divID', blank=True) 
    rank = models.IntegerField(null=True, db_column='Rank', blank=True) 
    g = models.IntegerField(null=True, db_column='G', blank=True) 
    ghome = models.IntegerField(null=True, db_column='Ghome', blank=True) 
    w = models.IntegerField(null=True, db_column='W', blank=True) 
    l = models.IntegerField(null=True, db_column='L', blank=True) 
    divwin = models.CharField(max_length=3, db_column='DivWin', blank=True) 
    wcwin = models.CharField(max_length=3, db_column='WCWin', blank=True) 
    lgwin = models.CharField(max_length=3, db_column='LgWin', blank=True) 
    wswin = models.CharField(max_length=3, db_column='WSWin', blank=True) 
    r = models.IntegerField(null=True, db_column='R', blank=True) 
    ab = models.IntegerField(null=True, db_column='AB', blank=True) 
    h = models.IntegerField(null=True, db_column='H', blank=True) 
    #2b = models.IntegerField(null=True, db_column='2B', blank=True) # Field name made lowercase.
    #3b = models.IntegerField(null=True, db_column='3B', blank=True) # Field name made lowercase.
    hr = models.IntegerField(null=True, db_column='HR', blank=True) 
    bb = models.IntegerField(null=True, db_column='BB', blank=True) 
    so = models.IntegerField(null=True, db_column='SO', blank=True) 
    sb = models.IntegerField(null=True, db_column='SB', blank=True) 
    cs = models.IntegerField(null=True, db_column='CS', blank=True) 
    hbp = models.IntegerField(null=True, db_column='HBP', blank=True) 
    sf = models.IntegerField(null=True, db_column='SF', blank=True) 
    ra = models.IntegerField(null=True, db_column='RA', blank=True) 
    er = models.IntegerField(null=True, db_column='ER', blank=True) 
    era = models.FloatField(null=True, db_column='ERA', blank=True) 
    cg = models.IntegerField(null=True, db_column='CG', blank=True) 
    sho = models.IntegerField(null=True, db_column='SHO', blank=True) 
    sv = models.IntegerField(null=True, db_column='SV', blank=True) 
    ipouts = models.IntegerField(null=True, db_column='IPouts', blank=True) 
    ha = models.IntegerField(null=True, db_column='HA', blank=True) 
    hra = models.IntegerField(null=True, db_column='HRA', blank=True) 
    bba = models.IntegerField(null=True, db_column='BBA', blank=True) 
    soa = models.IntegerField(null=True, db_column='SOA', blank=True) 
    e = models.IntegerField(null=True, db_column='E', blank=True) 
    dp = models.IntegerField(null=True, db_column='DP', blank=True) 
    fp = models.FloatField(null=True, db_column='FP', blank=True) 
    name = models.CharField(max_length=150, blank=True)
    park = models.CharField(max_length=765, blank=True)
    attendance = models.IntegerField(null=True, blank=True)
    bpf = models.IntegerField(null=True, db_column='BPF', blank=True) 
    ppf = models.IntegerField(null=True, db_column='PPF', blank=True) 
    teamidbr = models.CharField(max_length=9, db_column='teamIDBR', blank=True) 
    teamidlahman45 = models.CharField(max_length=9, db_column='teamIDlahman45', blank=True) 
    teamidretro = models.CharField(max_length=9, db_column='teamIDretro', blank=True) 
    class Meta:
        db_table = u'Teams'


class TNPLTeam(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

class TNPLOwnership(models.Model):
    team = models.ForeignKey(TNPLTeam)
    playerid = models.OneToOneField(Player, db_column='playerID', to_field='playerid') 
    salary = models.DecimalField(max_digits=4, decimal_places=2)

    def __unicode__(self):
        return "%s (%s) $%.2f" % (self.playerid, self.team, self.salary)

class TNPLBattingProj(models.Model):
    playerid = models.OneToOneField(Player, db_column='playerID', to_field='playerid')
    ab = models.IntegerField(null=True, db_column='AB', blank=True)
    r = models.IntegerField(null=True, db_column='R', blank=True)
    h = models.IntegerField(null=True, db_column='H', blank=True)
    hr = models.IntegerField(null=True, db_column='HR', blank=True)
    rbi = models.IntegerField(null=True, db_column='RBI', blank=True)
    sb = models.IntegerField(null=True, db_column='SB', blank=True)

class TNPLPitchingProj(models.Model):
    playerid = models.OneToOneField(Player, db_column='playerID', to_field='playerid')
    w = models.IntegerField(null=True, db_column='W', blank=True) 
    sv = models.IntegerField(null=True, db_column='SV', blank=True) 
    ipouts = models.IntegerField(null=True, db_column='IPouts', blank=True) 
    h = models.IntegerField(null=True, db_column='H', blank=True) 
    er = models.IntegerField(null=True, db_column='ER', blank=True) 
    bb = models.IntegerField(null=True, db_column='BB', blank=True) 
    so = models.IntegerField(null=True, db_column='SO', blank=True) 

