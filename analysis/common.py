import mysql.connector
import pandas as pd

# Database Configuration
mysql_dbaddr = "sql181.main-hosting.eu"
mysql_dbname = "u606982933_red1"
mysql_dbport = 3306
mysql_dbuser = "u606982933_red1"
mysql_dbpass = "F4nd0m5.C0nnec7"

print("ALERT: You should not store passwords in your source files!")

db_conn = mysql.connector.connect(host = mysql_dbaddr, user = mysql_dbuser, passwd = mysql_dbpass, database = mysql_dbname)
if (db_conn is None):
    print("Failed to connect to database.")
if (db_conn is not None):
    db_cursor = db_conn.cursor()

def get_all_data(sift = False):
    global db_conn, db_cursor
    if (db_conn is None):
        print("Not connected to a database. Please connect to a database and store it in 'db_conn'.")
        return None

    comment_query = "SELECT Comments.Author, Submissions.Subreddit FROM Comments INNER JOIN Submissions ON Comments.Submission = Submissions.ID GROUP BY Comments.Author, Submissions.Subreddit;;"
    submission_query = "SELECT Author, Subreddit FROM Submissions GROUP BY Author, Subreddit"

    db_cursor.execute(comment_query)
    comment_result = db_cursor.fetchall()
    db_cursor.execute(submission_query)
    submission_result = db_cursor.fetchall()

    output = []
    if sift is True:
        for result in comment_result:
            if result not in output:
                output.append(result)
        for result in submission_result:
            if result not in output:
                output.append(result)
    if sift is False:       # Fast this way. Otherwise we're doing set operations always.
        for result in comment_result:
            output.append(result)
        for result in submission_result:
            output.append(result)
    df = pd.DataFrame(output, columns = ["User", "Subreddit"])
    return df

def get_local_data():
    # get_all_data() but stored locally as a CSV, because database queries are slow and internet is useless.
    filepath = "data.csv"
    df = pd.read_csv(filepath)
    return  df
