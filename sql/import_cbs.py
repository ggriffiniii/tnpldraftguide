#!/usr/bin/python
import MySQLdb
import csv
import re
import sys

cbs_to_playerid = {}
with open(sys.argv[2], 'rb') as infile:
	csv_reader = csv.reader(infile)
	for row in csv_reader:
		cbs_to_playerid[row[0]] = row[1]

csv_reader = csv.DictReader(open(sys.argv[1], 'rb'))

conn = MySQLdb.connect (host = "localhost", user = "tnpldraft", passwd = "tnpldraft", db = "tnpldraft")

cursor = conn.cursor()

batter_insert = 'INSERT INTO BattingProj (playerID, TYPE, AB, R, H, HR, RBI, SB) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
pitcher_insert = 'INSERT INTO PitchingProj (playerID, TYPE, W, SV, IPouts, H, ER, BB, SO) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
for row in csv_reader:
	if row['Player'] not in cbs_to_playerid:
		print sys.stderr, "Don't know:", row['Player']
		continue
	playerid = cbs_to_playerid[row['Player']]
	if row.has_key('AB'):
		cursor.execute(batter_insert, (playerid, 'CBS', row['AB'], row['R'], row['H'], row['HR'], row['RBI'], row['SB']))
	elif row.has_key('INN'):
		cursor.execute(pitcher_insert, (playerid, 'CBS', row['W'], row['S'], round(float(row['INN'])*3), row['HA'], row['ER'], row['BBI'], row['K']))
	else:
		print sys.stderr, "Is this a batter or pitcher?"
		sys.exit(1)

conn.commit()	
cursor.close()
conn.close()

