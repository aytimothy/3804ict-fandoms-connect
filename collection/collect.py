import datetime
import mysql.connector
import praw
from praw.models import MoreComments
import pytz
import time
import sys

mysql_address = "sql181.main-hosting.eu"
mysql_port = 3306
mysql_dbname = ["u606982933_red1", "u606982933_red2", "u606982933_red3"]
mysql_username = ["u606982933_red1", "u606982933_red2", "u606982933_red3"]
mysql_password = "F4nd0m5.C0nnec7"

reddit_appid = "0lKXI8oYAYGUKg"
reddit_secret = "ptTp7vRNPVXQ0WIZwfcuAItUEcI"
reddit_blacklist = ["AutoModerator", "CredoBot", "timezone_bot", "RemindMeBot", "GCX_Bot", "vReddit_Player_Bot"]

userqueue_maxlength = 256
userqueue_processed = 0
userqueue_maxprocessed = 4096

processed_comments = 0
processed_submissions = 0
stored_comments = 0
start_time = time.time()

'''
Basics of what it does:

1. Start with a user (/u/aytimothy)
2. Download all his comments and submissions, store on the server.
3. In all his submissions, create a list of users who have interacted (commented) on it.
4. Do Step 3, but for the submission each comment the user has made.
5. Go back to Step 1, but going through all the users in the list in Step 3.
'''

def output(string):
	logfile = open("collect.log", "a")
	print(string)
	logfile.write(string + "\n")
	logfile.close()

def otheroutput(string, verbose = False):
	otherlogfile = open("read.log", "a")
	if verbose is True:
		print(string)
	otherlogfile.write(string + "\n")
	otherlogfile.close()

def storecompleteduser(username):
	completedfile = open("compelted.txt", "a")
	completedfile.write(username + "\n")
	completedfile.close()

def store_comment(comment):
	global processed_comments, db_conn, db_cursor
	id = comment.id
	otheroutput(id)
	parent = comment.parent_id[3:]
	submission = comment.link_id[3:]
	score = comment.score
	author = comment.author
	if author is None:
		author = "[Deleted]"
	else:
		author = author.name
	timestamp = datetime.datetime.fromtimestamp(comment.created_utc).isoformat()
	body = comment.body

	store_comment_query = "INSERT INTO `Comments` (`ID`, `Parent`, `Submission`, `Score`, `Author`, `Timestamp`, `Body`) VALUES ('" + id + "', '" + parent + "', '" + submission + "', '" + str(score) + "', '" + author + "', '" + str(timestamp) + "', '" + body.replace("\"", "\\\"").replace("'", "\\'") + "')"
	try:
		db_cursor.execute(store_comment_query)
	except:
		db_conn.rollback()
		return False
	db_conn.commit()
	processed_comments += 1
	return True

def store_submission(submission):
	global db_conn, db_cursor
	id = submission.id
	subreddit = submission.subreddit.display_name
	istext = submission.is_self
	istext_num = 0
	if istext is True:
		istext_num = 1
	title = submission.title
	iscrosspost = False
	iscrosspost_num = 0
	if iscrosspost is True:
		iscrosspost_num = 1
	source = ""
	link = submission.url
	body = submission.selftext
	score = submission.score
	author = submission.author
	if author is None:
		author = "[Deleted]"
	else:
		author = author.name
	timestamp = datetime.datetime.fromtimestamp(comment.created_utc).isoformat()

	store_comment_query = "INSERT INTO `Submissions` (`ID`, `Subreddit`, `IsText`, `Title`, `IsCrosspost`, `Source`, `Link`, `Body`, `Score`, `Author`, `Timestamp`) VALUES ('" + id + "', '" + subreddit + "', '" + str(istext_num) + "', '" + title + "', '" + str(iscrosspost_num) + "', '" + source + "', '" + link + "', '" + body + "', '" + str(score) + "', '" + author + "', '" + str(timestamp) + "')"
	try:
		db_cursor.execute(store_comment_query)
	except:
		db_conn.rollback()
		return False
	db_conn.commit()
	return True

def process_submission(submission):
	global processed_submissions, reddit, user_queue, completed_queue
	comment_forest = submission.comments
	comments = [comment for comment in comment_forest]
	while len(comments) > 0:
		comment = comments.pop()
		if isinstance(comment, MoreComments):
			continue
		author = comment.author
		if author is not None:
			author = comment.author.name
			if len(user_queue) < userqueue_maxlength:
				if author not in reddit_blacklist:
					if author not in user_queue and author not in completed_queue:
						user_queue.append(author)
						output("Found new user /u/" + author)
		reply_forest = comment.replies
		for reply in reply_forest:
			comments.append(reply)
		store_comment(comment)

	processed_submissions += 1

reddit = praw.Reddit(client_id = reddit_appid, client_secret = reddit_secret, user_agent = "PRAW 6.3.1")
if reddit is None:
	output("Could not connect to Reddit >:( \nAborting!")
	sys.exit(0)
output("Successfully connected to Reddit.")

user_queue = []
completed_queue = []
submission_queue = []


db_id = 0
db_conn = mysql.connector.connect(host = mysql_address, user = mysql_username[db_id], passwd = mysql_password, database = mysql_dbname[db_id])
if (db_conn is None):
	output("Could not connect to the database >:( \nAborting!")
	sys.exit(0)
db_cursor = db_conn.cursor()
output("Successfully connected to database.")

db_processed_users_query = "SELECT DISTINCT Author FROM `Comments` WHERE Author NOT IN (SELECT DISTINCT Author FROM `Submissions` ORDER BY Timestamp) ORDER BY Timestamp LIMIT " + str(userqueue_maxlength)
# db_processed_users_query = "SELECT DISTINCT Author FROM `Comments` ORDER BY Timestamp"
db_cursor.execute(db_processed_users_query)
db_processed_users = db_cursor.fetchall()
user_queue = [row[0] for row in db_processed_users]
with open("completed.txt") as completedfile:
	completedfile_contents = completedfile.readlines()
completed_queue = [completeduser.strip() for completeduser in completedfile_contents]
user_queue.append("aytimothy")
print("Found " + str(len(user_queue)) + " user(s) waiting for processing, and " + str(len(completed_queue)) + " user(s) who have been mined.")

while len(user_queue) > 0 and userqueue_processed <= userqueue_maxprocessed:
	userqueue_processed += 1
	username = user_queue.pop(0)
	redditor = reddit.redditor(username)
	if (redditor is None):
		output("Error: Could not find /u/" + username)
		continue
	output("Processing /u/" + username + "...")

	redditor_comments = redditor.comments.new()
	redditor_submissions = redditor.submissions.new()

	for comment in redditor_comments:
		submission_id = comment.link_id[3:]
		comment_id = comment.id
		otheroutput(comment_id)
		submission = reddit.submission(id = submission_id)
		submission_queue.append(submission)

	for submission in redditor_submissions:
		submission_id = submission.id
		otheroutput(submission_id)
		submission_queue.append(submission)

	while len(submission_queue) > 0:
		submission = submission_queue.pop()
		if store_submission(submission) is True:
			process_submission(submission)
			output("Processed " + str(processed_submissions) + " submission(s) and " + str(processed_comments) + " comment(s).")

	storecompleteduser(username)