CREATE USER 'tnpldraft'@'localhost' IDENTIFIED BY 'tnpldraft';
GRANT ALL PRIVILEGES ON tnpldraft.* TO 'tnpldraft'@'localhost';
use tnpldraft;
ALTER TABLE Master MODIFY playerID VARCHAR(10) UNIQUE KEY;
ALTER TABLE Master MODIFY lahmanID INT(11) PRIMARY KEY;
ALTER TABLE Appearances ADD id INTEGER PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE Batting ADD id INTEGER PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE Pitching ADD id INTEGER PRIMARY KEY AUTO_INCREMENT;
CREATE INDEX master_playerid ON Master (playerID);
CREATE INDEX appearances_playerid ON Appearances (playerID);
CREATE INDEX batting_playerid ON Batting (playerID);
CREATE INDEX pitching_playerid ON Pitching (playerID);
