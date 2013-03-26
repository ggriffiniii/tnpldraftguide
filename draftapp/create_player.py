from models import *

def CreatePlayer():
	firstname = raw_input("First name:")
	lastname = raw_input("Last name:")
	positions = set([x.lower() for x in raw_input("Positions:").split(',')])
	if len(positions) == 0:
		raise Error("Need to specify at least one position")

	playerid = lastname[:5].lower() + firstname[:2].lower() + '99'
	newplayer = Player(
		playerid=playerid,
		namefirst=firstname,
		namelast=lastname,
		birthyear=2013,
		birthmonth=1,
		birthday=1)
	newplayer.appearances_set.create(
		yearid=2012,
		g_all=20*len(positions),
		g_p=20 if 'p' in positions else 0,
		g_c=20 if 'c' in positions else 0,
		g_1b=20 if '1b' in positions else 0,
		g_2b=20 if '2b' in positions else 0,
		g_3b=20 if '3b' in positions else 0,
		g_ss=20 if 'ss' in positions else 0,
		g_of=20 if 'of' in positions else 0)
	newplayer.full_clean()
	newplayer.save()

CreatePlayer()
