#!/usr/bin/python
import MySQLdb
import csv
import re
import sys

positions = ('1B', '2B', '3B', 'C', 'CF', 'DH', 'LF', 'OF', 'RF', 'SS', 'SP', 'RP', 'P', 'XX')
teams = ('ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
	 'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
	 'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WAS')

cbs_to_playerid = {}
with open(sys.argv[2], 'rb') as infile:
	csv_reader = csv.reader(infile)
	for row in csv_reader:
		cbs_to_playerid[row[0]] = row[1]

csv_reader = csv.DictReader(open(sys.argv[1], 'rb'))

conn = MySQLdb.connect (host = "localhost", user = "tnpldraft", passwd = "tnpldraft", db = "tnpldraft")

cursor = conn.cursor()

positions_re_str = '(?:' + '|'.join(positions) + ')'
teams_re_str = '(?:' + '|'.join(teams) + ')'
extract_name = re.compile(r'(.*) ' + positions_re_str + ' ' + teams_re_str)
for row in csv_reader:
	if row.has_key('AB'):
		if int(float(row['AB'])) == 0: continue
	elif row.has_key('INN'):
		if int(float(row['INN'])) == 0: continue
	else:
		print sys.stderr, "Is this batters or pitchers?"
		sys.exit(1)

	if row['Player'] in cbs_to_playerid: continue
	name_match = extract_name.match(row['Player'])
	if name_match is None:
		print sys.stderr, "Unable to extract name from:", row
		sys.exit(1)
	(lastname, firstname) = name_match.group(1).split(', ')

	cursor.execute('SELECT playerID,nameFirst,nameLast,nameNote,nameGiven,nameNick,birthYear,debut FROM Master WHERE nameFirst = %s AND nameLast = %s AND deathYear IS NULL', (firstname, lastname))
	row_count = cursor.rowcount
	if row_count == 0:
		print sys.stderr, "No master row for: ", row
		print 'No matches found for:', row['Player']
		candidates = [
			" WHERE nameLast = '%s'" % (lastname,),
			" WHERE nameFirst = '%s'" % (firstname,),
		]
		print '\t0)', candidates[0]
		print '\t1)', candidates[1]
		choice = raw_input("Make your selection: ")
		try:
			where = candidates[int(choice)]
		except:
			where = choice
		cursor.execute('SELECT playerID,nameFirst,nameLast,nameNote,nameGiven,nameNick,birthYear,debut FROM Master %s' % (where,))
		candidates = []
		index = 0
		for master_row in cursor.fetchall():
			candidates.append(master_row[0])
			print "\t%d) %s %s (nick: %s given: %s note: %s) birthyear: %s debut: %s" % (
				index, master_row[1], master_row[2], master_row[5], master_row[4], master_row[3], master_row[6], master_row[7])
			index += 1
		choice = raw_input("Make your selection: ")
		try:
			choice = int(choice)
			cbs_to_playerid[row['Player']] = candidates[choice]
		except:
			print "foo"
			pass
	elif row_count == 1:
		master_row = cursor.fetchone()
		cbs_to_playerid[row['Player']] = master_row[0]
	elif row_count > 1:
		candidates = []
		index = 0
		print row['Player']
		for master_row in cursor.fetchall():
			candidates.append(master_row[0])
			print "\t%d) %s %s (nick: %s given: %s note: %s) birthyear: %s debut: %s" % (
				index, master_row[1], master_row[2], master_row[5], master_row[4], master_row[3], master_row[6], master_row[7])
			index += 1
		choice = raw_input("Make your selection: ")
		cbs_to_playerid[row['Player']] = candidates[int(choice)]

cursor.close()

with open(sys.argv[2], 'wb') as outfile:
	csv_writer = csv.writer(outfile)
	for (cbs,playerid) in cbs_to_playerid.iteritems():
		csv_writer.writerow([cbs, playerid])
