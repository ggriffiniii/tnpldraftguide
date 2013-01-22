#!/usr/bin/python
import MySQLdb
import csv
import datetime

class Type(object):
	def fromString(self, str_value):
		if len(str_value) == 0:
			return None
		return self.toValue(str_value)

class Int(Type):
	def spec(self):
		return 'int(10)'

	def toValue(self, str_value):
		return int(str_value)

class Varchar(Type):
	def spec(self):
		return 'varchar(100)'

	def toValue(self, str_value):
		return str_value

class Double(Type):
	def spec(self):
		return 'double(10,4)'

	def toValue(self, str_value):
		return float(str_value)

class Datetime(Type):
	def spec(self):
		return 'datetime'

	def toValue(self, str_value):
		return str(datetime.datetime.strptime(str_value, '%m/%d/%Y'))

class Table(object):
	def __init__(self):
		self.cols = self.define_cols()

	def filename(self):
		return self.table() + '.csv'

	def dropTable(self, conn):
		cursor = conn.cursor()
		cursor.execute('DROP TABLE IF EXISTS ' + self.table());
		conn.commit()
		cursor.close()

	def createTable(self, conn):
		def colspec(col):
			return '%s %s DEFAULT NULL' % (col['name'], col['type'].spec())
		colspecs = [colspec(x) for x in self.cols]
		statement = 'CREATE TABLE ' + self.table() + ' ( ' + ', '.join(colspecs) + ' )'
		print statement
		cursor = conn.cursor()
		cursor.execute(statement)
		conn.commit()
		cursor.close()

	def importData(self, conn):
		colnames = ','.join([x['name'] for x in self.cols])
		placeholders = ','.join(['%s' for x in self.cols])
		statement = 'INSERT INTO `' + self.table() + '` (' + colnames + ') VALUES (' + placeholders + ')'
		csv_reader = csv.reader(open(self.filename(), 'rb'))
		csv_reader.next() # skip the header row
		cursor = conn.cursor()
		for row in csv_reader:
			data = []
			for i in xrange(len(self.cols)):
				data.append(self.cols[i]['type'].fromString(row[i]))
			data = tuple(data)
			cursor.execute(statement, data)
		conn.commit()
		cursor.close()

	def importTable(self, conn):
		self.dropTable(conn)
		self.createTable(conn)
		self.importData(conn)

class Master(Table):
	def table(self):
		return 'Master'

	def define_cols(self):
		return [
			{ 'name': 'lahmanID', 'type': Int() },
			{ 'name': 'playerID', 'type': Varchar() },
			{ 'name': 'managerID', 'type': Varchar() },
			{ 'name': 'hofID', 'type': Varchar() },
			{ 'name': 'birthYear', 'type': Int() },
			{ 'name': 'birthMonth', 'type': Int() },
			{ 'name': 'birthDay', 'type': Int() },
			{ 'name': 'birthCountry', 'type': Varchar() },
			{ 'name': 'birthState', 'type': Varchar() },
			{ 'name': 'birthCity', 'type': Varchar() },
			{ 'name': 'deathYear', 'type': Int() },
			{ 'name': 'deathMonth', 'type': Int() },
			{ 'name': 'deathDay', 'type': Int() },
			{ 'name': 'deathCountry', 'type': Varchar() },
			{ 'name': 'deathState', 'type': Varchar() },
			{ 'name': 'deathCity', 'type': Varchar() },
			{ 'name': 'nameFirst', 'type': Varchar() },
			{ 'name': 'nameLast', 'type': Varchar() },
			{ 'name': 'nameNote', 'type': Varchar() },
			{ 'name': 'nameGiven', 'type': Varchar() },
			{ 'name': 'nameNick', 'type': Varchar() },
			{ 'name': 'weight', 'type': Int() },
			{ 'name': 'height', 'type': Double() },
			{ 'name': 'bats', 'type': Varchar() },
			{ 'name': 'throws', 'type': Varchar() },
			{ 'name': 'debut', 'type': Datetime() },
			{ 'name': 'finalGame', 'type': Datetime() },
			{ 'name': 'college', 'type': Varchar() },
			{ 'name': 'lahman40ID', 'type': Varchar() },
			{ 'name': 'lahman45ID', 'type': Varchar() },
			{ 'name': 'retroID', 'type': Varchar() },
			{ 'name': 'holtzID', 'type': Varchar() },
			{ 'name': 'bbrefID', 'type': Varchar() },
		]

class Appearances(Table):
	def table(self):
		return 'Appearances'

	def define_cols(self):
		return [
			{ 'name': 'yearID', 'type': Int() },
			{ 'name': 'teamID', 'type': Varchar() },
			{ 'name': 'lgID', 'type': Varchar() },
			{ 'name': 'playerID', 'type': Varchar() },
			{ 'name': 'G_all', 'type': Int() },
			{ 'name': 'GS', 'type': Int() },
			{ 'name': 'G_batting', 'type': Int() },
			{ 'name': 'G_defense', 'type': Int() },
			{ 'name': 'G_p', 'type': Int() },
			{ 'name': 'G_c', 'type': Int() },
			{ 'name': 'G_1b', 'type': Int() },
			{ 'name': 'G_2b', 'type': Int() },
			{ 'name': 'G_3b', 'type': Int() },
			{ 'name': 'G_ss', 'type': Int() },
			{ 'name': 'G_lf', 'type': Int() },
			{ 'name': 'G_cf', 'type': Int() },
			{ 'name': 'G_rf', 'type': Int() },
			{ 'name': 'G_of', 'type': Int() },
			{ 'name': 'G_dh', 'type': Int() },
			{ 'name': 'G_ph', 'type': Int() },
			{ 'name': 'G_pr', 'type': Int() },
		]

class Batting(Table):
	def table(self):
		return 'Batting'

	def define_cols(self):
		return [
			{ 'name': 'playerID', 'type': Varchar() },
			{ 'name': 'yearID', 'type': Int() },
			{ 'name': 'stint', 'type': Int() },
			{ 'name': 'teamID', 'type': Varchar() },
			{ 'name': 'lgID', 'type': Varchar() },
			{ 'name': 'G', 'type': Int() },
			{ 'name': 'G_batting', 'type': Int() },
			{ 'name': 'AB', 'type': Int() },
			{ 'name': 'R', 'type': Int() },
			{ 'name': 'H', 'type': Int() },
			{ 'name': '2B', 'type': Int() },
			{ 'name': '3B', 'type': Int() },
			{ 'name': 'HR', 'type': Int() },
			{ 'name': 'RBI', 'type': Int() },
			{ 'name': 'SB', 'type': Int() },
			{ 'name': 'CS', 'type': Int() },
			{ 'name': 'BB', 'type': Int() },
			{ 'name': 'SO', 'type': Int() },
			{ 'name': 'IBB', 'type': Int() },
			{ 'name': 'HBP', 'type': Int() },
			{ 'name': 'SH', 'type': Int() },
			{ 'name': 'SF', 'type': Int() },
			{ 'name': 'GIDP', 'type': Int() },
			{ 'name': 'G_old', 'type': Int() },
		]

class Pitching(Table):
	def table(self):
		return 'Pitching'

	def define_cols(self):
		return [
			{ 'name': 'playerID', 'type': Varchar() },
			{ 'name': 'yearID', 'type': Int() },
			{ 'name': 'stint', 'type': Int() },
			{ 'name': 'teamID', 'type': Varchar() },
			{ 'name': 'lgID', 'type': Varchar() },
			{ 'name': 'W', 'type': Int() },
			{ 'name': 'L', 'type': Int() },
			{ 'name': 'G', 'type': Int() },
			{ 'name': 'GS', 'type': Int() },
			{ 'name': 'CG', 'type': Int() },
			{ 'name': 'SHO', 'type': Int() },
			{ 'name': 'SV', 'type': Int() },
			{ 'name': 'IPouts', 'type': Int() },
			{ 'name': 'H', 'type': Int() },
			{ 'name': 'ER', 'type': Int() },
			{ 'name': 'HR', 'type': Int() },
			{ 'name': 'BB', 'type': Int() },
			{ 'name': 'SO', 'type': Int() },
			{ 'name': 'BAOpp', 'type': Double() },
			{ 'name': 'ERA', 'type': Double() },
			{ 'name': 'IBB', 'type': Int() },
			{ 'name': 'WP', 'type': Int() },
			{ 'name': 'HBP', 'type': Int() },
			{ 'name': 'BK', 'type': Int() },
			{ 'name': 'BFP', 'type': Int() },
			{ 'name': 'GF', 'type': Int() },
			{ 'name': 'R', 'type': Int() },
			{ 'name': 'SH', 'type': Int() },
			{ 'name': 'SF', 'type': Int() },
			{ 'name': 'GIDP', 'type': Int() },
		]

class Teams(Table):
	def table(self):
		return 'Teams'

	def define_cols(self):
		return [
			{ 'name': 'yearID', 'type': Int() },
			{ 'name': 'lgID', 'type': Varchar() },
			{ 'name': 'teamID', 'type': Varchar() },
			{ 'name': 'franchID', 'type': Varchar() },
			{ 'name': 'divID', 'type': Varchar() },
			{ 'name': 'Rank', 'type': Int() },
			{ 'name': 'G', 'type': Int() },
			{ 'name': 'Ghome', 'type': Int() },
			{ 'name': 'W', 'type': Int() },
			{ 'name': 'L', 'type': Int() },
			{ 'name': 'DivWin', 'type': Varchar() },
			{ 'name': 'WCWin', 'type': Varchar() },
			{ 'name': 'LgWin', 'type': Varchar() },
			{ 'name': 'WSWin', 'type': Varchar() },
			{ 'name': 'R', 'type': Int() },
			{ 'name': 'AB', 'type': Int() },
			{ 'name': 'H', 'type': Int() },
			{ 'name': '2B', 'type': Double() },
			{ 'name': '3B', 'type': Double() },
			{ 'name': 'HR', 'type': Int() },
			{ 'name': 'BB', 'type': Int() },
			{ 'name': 'SO', 'type': Int() },
			{ 'name': 'SB', 'type': Int() },
			{ 'name': 'CS', 'type': Int() },
			{ 'name': 'HBP', 'type': Int() },
			{ 'name': 'SF', 'type': Int() },
			{ 'name': 'RA', 'type': Int() },
			{ 'name': 'ER', 'type': Int() },
			{ 'name': 'ERA', 'type': Double() },
			{ 'name': 'CG', 'type': Int() },
			{ 'name': 'SHO', 'type': Int() },
			{ 'name': 'SV', 'type': Int() },
			{ 'name': 'IPouts', 'type': Int() },
			{ 'name': 'HA', 'type': Int() },
			{ 'name': 'HRA', 'type': Int() },
			{ 'name': 'BBA', 'type': Int() },
			{ 'name': 'SOA', 'type': Int() },
			{ 'name': 'E', 'type': Int() },
			{ 'name': 'DP', 'type': Int() },
			{ 'name': 'FP', 'type': Double() },
			{ 'name': 'name', 'type': Varchar() },
			{ 'name': 'park', 'type': Varchar() },
			{ 'name': 'attendance', 'type': Int() },
			{ 'name': 'BPF', 'type': Int() },
			{ 'name': 'PPF', 'type': Int() },
			{ 'name': 'teamIDBR', 'type': Varchar() },
			{ 'name': 'teamIDlahman45', 'type': Varchar() },
			{ 'name': 'teamIDretro', 'type': Varchar() },
		]

class TeamsFranchises(Table):
	def table(self):
		return 'TeamsFranchises'

	def define_cols(self):
		return [
			{ 'name': 'franchID', 'type': Varchar() },
			{ 'name': 'franchName', 'type': Varchar() },
			{ 'name': 'active', 'type': Varchar() },
			{ 'name': 'NAassoc', 'type': Varchar() },
		]

if __name__ == '__main__':
	conn = MySQLdb.connect (host = "localhost", user = "tnpldraft", passwd = "tnpldraft", db = "tnpldraft")
	Master().importTable(conn)
	Appearances().importTable(conn)
	Batting().importTable(conn)
	Pitching().importTable(conn)
	Teams().importTable(conn)
	TeamsFranchises().importTable(conn)
	conn.close()

