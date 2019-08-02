import mysql.connector

mysql_address = "sql181.main-hosting.eu"
mysql_port = 3306
mysql_dbname = ["u606982933_red1", "u606982933_red2", "u606982933_red3"]
mysql_username = ["u606982933_red1", "u606982933_red2", "u606982933_red3"]
mysql_password = "F4nd0m5.C0nnec7"

for username, dbname in zip(mysql_username, mysql_username):
	connection = mysql.connector.connect(host = mysql_address, user = username, passwd = mysql_password, database = dbname)
	if (connection is None):
		print("Could not connect to Database \"" + dbname + "\" on " + mysql_address + "!")
		continue
	print("Connected successfully to Database \"" + dbname + "\" on " + mysql_address + "!")	
	
	cursor = connection.cursor()
	cursor.execute("SHOW TABLES")
	tables = [table_name[0] for table_name in cursor]
	if "Submissions" not in tables:
		print("Could not find a \"Submissions\" table. Creating!")
		submissions_table_create_query = "CREATE TABLE `Submissions` ( `ID` VARCHAR(16) NOT NULL , `Subreddit` VARCHAR(64) NOT NULL , `IsText` BOOLEAN NOT NULL , `Title` VARCHAR(300) NOT NULL , `IsCrosspost` BOOLEAN NOT NULL , `Source` VARCHAR(16) NOT NULL , `Link` TEXT NOT NULL , `Body` TEXT NOT NULL , `Score` INT NOT NULL , `Author` VARCHAR(32) NOT NULL , `Timestamp` TIMESTAMP NOT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;"
		cursor.execute(submissions_table_create_query)
	else:
		print("\"Submissions\" table found. Skipping!")
	if "Comments" not in tables:
		print("Could not find a \"Comments\" table. Creating!")
		comments_table_create_query = "CREATE TABLE `Comments` ( `ID` VARCHAR(16) NOT NULL , `Parent` VARCHAR(16) NOT NULL , `Submission` VARCHAR(16) NOT NULL , `Score` INT NOT NULL , `Author` VARCHAR(32) NOT NULL , `Timestamp` TIMESTAMP NOT NULL , `Body` TEXT NOT NULL , PRIMARY KEY (`ID`)) ENGINE = InnoDB;"
		cursor.execute(comments_table_create_query)
	else:
		print("\"Comments\" table found. Skipping!")
		
	connection.close()
