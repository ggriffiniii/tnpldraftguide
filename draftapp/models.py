# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Player(models.Model):
    lahmanid = models.IntegerField(null=True, db_column='lahmanID', blank=True, primary_key=True) # Field name made lowercase.
    playerid = models.CharField(max_length=30, db_column='playerID', unique=True) # Field name made lowercase.
    managerid = models.CharField(max_length=30, db_column='managerID', blank=True) # Field name made lowercase.
    hofid = models.CharField(max_length=30, db_column='hofID', blank=True) # Field name made lowercase.
    birthyear = models.IntegerField(null=True, db_column='birthYear', blank=True) # Field name made lowercase.
    birthmonth = models.IntegerField(null=True, db_column='birthMonth', blank=True) # Field name made lowercase.
    birthday = models.IntegerField(null=True, db_column='birthDay', blank=True) # Field name made lowercase.
    birthcountry = models.CharField(max_length=150, db_column='birthCountry', blank=True) # Field name made lowercase.
    birthstate = models.CharField(max_length=6, db_column='birthState', blank=True) # Field name made lowercase.
    birthcity = models.CharField(max_length=150, db_column='birthCity', blank=True) # Field name made lowercase.
    deathyear = models.IntegerField(null=True, db_column='deathYear', blank=True) # Field name made lowercase.
    deathmonth = models.IntegerField(null=True, db_column='deathMonth', blank=True) # Field name made lowercase.
    deathday = models.IntegerField(null=True, db_column='deathDay', blank=True) # Field name made lowercase.
    deathcountry = models.CharField(max_length=150, db_column='deathCountry', blank=True) # Field name made lowercase.
    deathstate = models.CharField(max_length=6, db_column='deathState', blank=True) # Field name made lowercase.
    deathcity = models.CharField(max_length=150, db_column='deathCity', blank=True) # Field name made lowercase.
    namefirst = models.CharField(max_length=150, db_column='nameFirst', blank=True) # Field name made lowercase.
    namelast = models.CharField(max_length=150, db_column='nameLast', blank=True) # Field name made lowercase.
    namenote = models.CharField(max_length=765, db_column='nameNote', blank=True) # Field name made lowercase.
    namegiven = models.CharField(max_length=765, db_column='nameGiven', blank=True) # Field name made lowercase.
    namenick = models.CharField(max_length=765, db_column='nameNick', blank=True) # Field name made lowercase.
    weight = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    bats = models.CharField(max_length=3, blank=True)
    throws = models.CharField(max_length=3, blank=True)
    debut = models.DateTimeField(null=True, blank=True)
    finalgame = models.DateTimeField(null=True, db_column='finalGame', blank=True) # Field name made lowercase.
    college = models.CharField(max_length=150, blank=True)
    lahman40id = models.CharField(max_length=27, db_column='lahman40ID', blank=True) # Field name made lowercase.
    lahman45id = models.CharField(max_length=27, db_column='lahman45ID', blank=True) # Field name made lowercase.
    retroid = models.CharField(max_length=27, db_column='retroID', blank=True) # Field name made lowercase.
    holtzid = models.CharField(max_length=27, db_column='holtzID', blank=True) # Field name made lowercase.
    bbrefid = models.CharField(max_length=27, db_column='bbrefID', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'Master'

    def __unicode__(self):
	return "%s %s" % (self.namefirst, self.namelast)

    def ownership(self):
	if len(self.tnplownership_set.all()) > 0:
            x = self.tnplownership_set.all()[0]
            return {'team': x.team.name, 'salary': x.salary}
        else:
            return None


    def projected_val(self):
	# For now just use the most recent season the player had
	years = self.batting_set.all().order_by('-yearid')
	if len(years) > 0:
		return years[0].total_val()
	else:
		return 0

class Appearances(models.Model):
    yearid = models.IntegerField(null=True, db_column='yearID', blank=True) # Field name made lowercase.
    teamid = models.CharField(max_length=9, db_column='teamID', blank=True) # Field name made lowercase.
    lgid = models.CharField(max_length=6, db_column='lgID', blank=True) # Field name made lowercase.
    playerid = models.ForeignKey(Player, db_column='playerID', to_field='playerid') # models.CharField(max_length=27, db_column='playerID', blank=True) # Field name made lowercase.
    g_all = models.IntegerField(null=True, db_column='G_all', blank=True) # Field name made lowercase.
    g_s = models.IntegerField(null=True, db_column='GS', blank=True) # Field name made lowercase.
    g_batting = models.IntegerField(null=True, db_column='G_batting', blank=True) # Field name made lowercase.
    g_defense = models.IntegerField(null=True, db_column='G_defense', blank=True) # Field name made lowercase.
    g_p = models.IntegerField(null=True, db_column='G_p', blank=True) # Field name made lowercase.
    g_c = models.IntegerField(null=True, db_column='G_c', blank=True) # Field name made lowercase.
    g_1b = models.IntegerField(null=True, db_column='G_1b', blank=True) # Field name made lowercase.
    g_2b = models.IntegerField(null=True, db_column='G_2b', blank=True) # Field name made lowercase.
    g_3b = models.IntegerField(null=True, db_column='G_3b', blank=True) # Field name made lowercase.
    g_ss = models.IntegerField(null=True, db_column='G_ss', blank=True) # Field name made lowercase.
    g_lf = models.IntegerField(null=True, db_column='G_lf', blank=True) # Field name made lowercase.
    g_cf = models.IntegerField(null=True, db_column='G_cf', blank=True) # Field name made lowercase.
    g_rf = models.IntegerField(null=True, db_column='G_rf', blank=True) # Field name made lowercase.
    g_of = models.IntegerField(null=True, db_column='G_of', blank=True) # Field name made lowercase.
    g_dh = models.IntegerField(null=True, db_column='G_dh', blank=True) # Field name made lowercase.
    g_ph = models.IntegerField(null=True, db_column='G_ph', blank=True) # Field name made lowercase.
    g_pr = models.IntegerField(null=True, db_column='G_pr', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'Appearances'

class Batting(models.Model):
    playerid = models.ForeignKey(Player, db_column='playerID', to_field='playerid') # models.CharField(max_length=27, db_column='playerID', blank=True) # Field name made lowercase.
    yearid = models.IntegerField(null=True, db_column='yearID', blank=True) # Field name made lowercase.
    stint = models.IntegerField(null=True, blank=True)
    teamid = models.CharField(max_length=9, db_column='teamID', blank=True) # Field name made lowercase.
    lgid = models.CharField(max_length=6, db_column='lgID', blank=True) # Field name made lowercase.
    g = models.IntegerField(null=True, db_column='G', blank=True) # Field name made lowercase.
    g_batting = models.IntegerField(null=True, db_column='G_batting', blank=True) # Field name made lowercase.
    ab = models.IntegerField(null=True, db_column='AB', blank=True) # Field name made lowercase.
    r = models.IntegerField(null=True, db_column='R', blank=True) # Field name made lowercase.
    h = models.IntegerField(null=True, db_column='H', blank=True) # Field name made lowercase.
    #2b = models.IntegerField(null=True, db_column='2B', blank=True) # Field name made lowercase.
    #3b = models.IntegerField(null=True, db_column='3B', blank=True) # Field name made lowercase.
    hr = models.IntegerField(null=True, db_column='HR', blank=True) # Field name made lowercase.
    rbi = models.IntegerField(null=True, db_column='RBI', blank=True) # Field name made lowercase.
    sb = models.IntegerField(null=True, db_column='SB', blank=True) # Field name made lowercase.
    cs = models.IntegerField(null=True, db_column='CS', blank=True) # Field name made lowercase.
    bb = models.IntegerField(null=True, db_column='BB', blank=True) # Field name made lowercase.
    so = models.IntegerField(null=True, db_column='SO', blank=True) # Field name made lowercase.
    ibb = models.IntegerField(null=True, db_column='IBB', blank=True) # Field name made lowercase.
    hbp = models.IntegerField(null=True, db_column='HBP', blank=True) # Field name made lowercase.
    sh = models.IntegerField(null=True, db_column='SH', blank=True) # Field name made lowercase.
    sf = models.IntegerField(null=True, db_column='SF', blank=True) # Field name made lowercase.
    gidp = models.IntegerField(null=True, db_column='GIDP', blank=True) # Field name made lowercase.
    g_old = models.IntegerField(null=True, db_column='G_old', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'Batting'

    _AB_PER_PLAYER = 550
    _PLAYERS_PER_TEAM = 15
    _POINTS_PER_CATEGORY = 100

    _RUNS_GOAL = 1217
    _RBI_GOAL = 1191
    _HR_GOAL = 321
    _SB_GOAL = 226
    _BA_GOAL = 0.278

    _RUNS_MUL = float(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _RUNS_GOAL
    _RBI_MUL = float(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _RBI_GOAL
    _HR_MUL = float(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _HR_GOAL
    _SB_MUL = float(_PLAYERS_PER_TEAM * _POINTS_PER_CATEGORY) / _SB_GOAL
    _HITS_MUL = _POINTS_PER_CATEGORY / (_BA_GOAL * _AB_PER_PLAYER)

    def ba(self):
	if self.ab > 0:
		return float(self.h) / self.ab
	else:
		return 0.0

    def r_val(self):
	if self.r is None: return 0
	return self.r * Batting._RUNS_MUL

    def hr_val(self):
	if self.hr is None: return 0
	return self.hr * Batting._HR_MUL

    def rbi_val(self):
	if self.rbi is None: return 0
	return self.rbi * Batting._RBI_MUL

    def sb_val(self):
	if self.sb is None: return 0
	return self.sb * Batting._SB_MUL

    def ba_val(self):
	if self.h is None or self.ab is None: return 0
	return (Batting._POINTS_PER_CATEGORY+
                ((self.h-(self.ab*Batting._BA_GOAL))*Batting._HITS_MUL))

    def total_val(self):
	return (self.r_val() + self.hr_val() + self.rbi_val() +
                self.sb_val() + self.ba_val())
        

class Pitching(models.Model):
    playerid = models.ForeignKey(Player, db_column='playerID', to_field='playerid') # models.CharField(max_length=27, db_column='playerID', blank=True) # Field name made lowercase.
    yearid = models.IntegerField(null=True, db_column='yearID', blank=True) # Field name made lowercase.
    stint = models.IntegerField(null=True, blank=True)
    teamid = models.CharField(max_length=9, db_column='teamID', blank=True) # Field name made lowercase.
    lgid = models.CharField(max_length=6, db_column='lgID', blank=True) # Field name made lowercase.
    w = models.IntegerField(null=True, db_column='W', blank=True) # Field name made lowercase.
    l = models.IntegerField(null=True, db_column='L', blank=True) # Field name made lowercase.
    g = models.IntegerField(null=True, db_column='G', blank=True) # Field name made lowercase.
    gs = models.IntegerField(null=True, db_column='GS', blank=True) # Field name made lowercase.
    cg = models.IntegerField(null=True, db_column='CG', blank=True) # Field name made lowercase.
    sho = models.IntegerField(null=True, db_column='SHO', blank=True) # Field name made lowercase.
    sv = models.IntegerField(null=True, db_column='SV', blank=True) # Field name made lowercase.
    ipouts = models.IntegerField(null=True, db_column='IPouts', blank=True) # Field name made lowercase.
    h = models.IntegerField(null=True, db_column='H', blank=True) # Field name made lowercase.
    er = models.IntegerField(null=True, db_column='ER', blank=True) # Field name made lowercase.
    hr = models.IntegerField(null=True, db_column='HR', blank=True) # Field name made lowercase.
    bb = models.IntegerField(null=True, db_column='BB', blank=True) # Field name made lowercase.
    so = models.IntegerField(null=True, db_column='SO', blank=True) # Field name made lowercase.
    baopp = models.FloatField(null=True, db_column='BAOpp', blank=True) # Field name made lowercase.
    era = models.FloatField(null=True, db_column='ERA', blank=True) # Field name made lowercase.
    ibb = models.IntegerField(null=True, db_column='IBB', blank=True) # Field name made lowercase.
    wp = models.IntegerField(null=True, db_column='WP', blank=True) # Field name made lowercase.
    hbp = models.IntegerField(null=True, db_column='HBP', blank=True) # Field name made lowercase.
    bk = models.IntegerField(null=True, db_column='BK', blank=True) # Field name made lowercase.
    bfp = models.IntegerField(null=True, db_column='BFP', blank=True) # Field name made lowercase.
    gf = models.IntegerField(null=True, db_column='GF', blank=True) # Field name made lowercase.
    r = models.IntegerField(null=True, db_column='R', blank=True) # Field name made lowercase.
    sh = models.IntegerField(null=True, db_column='SH', blank=True) # Field name made lowercase.
    sf = models.IntegerField(null=True, db_column='SF', blank=True) # Field name made lowercase.
    gidp = models.IntegerField(null=True, db_column='GIDP', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'Pitching'

class TNPLTeam(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

class TNPLOwnership(models.Model):
    team = models.ForeignKey(TNPLTeam)
    playerid = models.ForeignKey(Player, db_column='playerID', to_field='playerid') # models.CharField(max_length=27, db_column='playerID', blank=True) # Field name made lowercase.
    salary = models.DecimalField(max_digits=4, decimal_places=2)

    def __unicode__(self):
        return "%s (%s) $%.2f" % (self.playerid, self.team, self.salary)

