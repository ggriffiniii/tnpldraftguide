CREATE USER 'tnpldraft'@'localhost' IDENTIFIED BY 'tnpldraft';
GRANT ALL PRIVILEGES ON tnpldraft.* TO 'tnpldraft'@'localhost';
use tnpldraft;

DELETE FROM Master where lahmanID = 460;
ALTER TABLE Master MODIFY playerID VARCHAR(10) UNIQUE KEY;
ALTER TABLE Master MODIFY lahmanID INT(11) PRIMARY KEY;
ALTER TABLE Appearances ADD id INTEGER PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE Batting ADD id INTEGER PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE Pitching ADD id INTEGER PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE Teams ADD id INTEGER PRIMARY KEY AUTO_INCREMENT;
CREATE INDEX master_playerid ON Master (playerID);
CREATE INDEX appearances_playerid ON Appearances (playerID);
CREATE INDEX appearances_year on Appearances (yearID);
CREATE INDEX batting_playerid ON Batting (playerID);
CREATE INDEX batting_yearid ON Batting (yearID);
CREATE INDEX pitching_playerid ON Pitching (playerID);
CREATE INDEX pitching_yearid ON Pitching (yearID);
CREATE INDEX battingproj_playerid ON BattingProj(playerID);
CREATE INDEX battingproj_type ON BattingProj(TYPE);
CREATE INDEX pitchingproj_playerid ON PitchingProj(playerID);
CREATE INDEX pitchingproj_type ON PitchingProj(TYPE);

