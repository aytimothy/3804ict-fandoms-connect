import mysql.connector
import praw
from praw.models import MoreComments
import time
import sys

mysql_address = "sql181.main-hosting.eu"
mysql_port = 3306
mysql_dbname = ["u606982933_red1", "u606982933_red2", "u606982933_red3"]
mysql_username = ["u606982933_red1", "u606982933_red2", "u606982933_red3"]
mysql_password = "F4nd0m5.C0nnec7"

reddit_appid = "0lKXI8oYAYGUKg"
reddit_secret = "ptTp7vRNPVXQ0WIZwfcuAItUEcI"

userqueue_maxlength = 2048
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
	

def store_comment(comment):
	global db_cursor, db_conn
	id = comment.id
	parent = comment.parent_id
	if parent == "t3_" + comment.link_id:
		parent = ""
	else:
		parent = parent[3:]
	submission = comment.link_id
	score = comment.score
	author = comment.author.name
	timestamp = comment.created_utc
	body = comment.body
	store_comment_query = "INSERT INTO `Comments` (`ID`, `Parent`, `Submission`, `Score`, `Author`, `Timestamp`, `Body`) VALUES ('" + id + "', '" + parent + "', '" + submission + "', '" + str(score) + "', '" + author + "', '" + str(timestamp) + "', '" + body.replace("\"", "\\\"").replace("'", "\\'") + "')"
	try:
		db_cursor.execute(store_comment_query)
	except:
		db_conn.rollback()
		return False
	db_conn.commit()
	return True
	
def store_submission(submission):
	global db_cursor, db_conn
	id = submission.id
	subreddit = submission.subreddit.name
	istext = submission.is_self
	istext_num = 0
	if istext is True:
		istext_num = 1
	title = submission.name
	iscrosspost = False
	iscrosspost_num = 0
	if iscrosspost is True:
		iscrosspost_num = 1
	source = ""
	link = submission.url
	if istext is True:
		link = ""
	body = submission.selftext
	score = submission.score
	author = "[Unknown]"
	if submission.author is None:
		author = "[Deleted]"
	else:
		author = submission.author.name
	timestamp = submission.created_utc
	
	store_submission_query = "INSERT INTO `Submissions` (`ID`, `Subreddit`, `IsText`, `Title`, `IsCrosspost`, `Source`, `Link`, `Body`, `Score`, `Author`, `Timestamp`) VALUES ('" + id + "', '" + subreddit + "', '" + str(istext_num) + "', '" + title + "', '" + str(iscrosspost_num) + "', '" + source + "', '" + link + "', '" + body + "', '" + str(score) + "', '" + author + "', '" + str(timestamp) + "')"
	try:
		db_cursor.execute(store_submission_query)
	except:
		db_conn.rollback()
		return False
	db_conn.commit()
	return True
	
def process_submission(submission):
	global user_queue, completed_queue, processed_comments
	# //todo: Process overflows
	comment_forest = submission.comments
	comments = [comment for comment in comment_forest]
	while len(comments) > 0:
		comment = comments.pop()
		if isinstance(comment, MoreComments):
			for new_comment in comment.comments:
				comments.append(new_comment)
			continue
		replies_forest = comment.replies
		for reply in replies_forest:
			comments.append(reply)
		if comment.author is None:
			continue
		redditor = comment.author.name
		if redditor in user_queue or redditor in completed_queue:
			continue
		user_queue.append(redditor)
		output("Found new Redditor /u/" + redditor)
		processed_comments += 1

reddit = praw.Reddit(client_id = reddit_appid, client_secret = reddit_secret, user_agent = "PRAW 6.3.1")
if reddit is None:
	output("Could not connect to Reddit >:( \nAborting!")
	sys.exit(0)
output("Successfully connected to Reddit.")

user_queue = []
completed_queue = []
user_queue.append("aytimothy")

db_id = 0
db_conn = mysql.connector.connect(host = mysql_address, user = mysql_username[db_id], passwd = mysql_password, database = mysql_dbname[db_id])
if (db_conn is None):
	output("Could not connect to the database >:( \nAborting!")
	sys.exit(0)
db_cursor = db_conn.cursor()
output("Successfully connected to database.")

output("// todo: Populate completed users.")
output("// todo: Populate in-progress users.")

while len(user_queue) > 0 and userqueue_processed <= userqueue_maxprocessed:
	user = user_queue.pop()
	redditor = reddit.redditor(user)
	completed_queue.append(user)
	output("Processing /u/" + user + "...")
	
	output("Processing /u/" + user + "'s comments...")
	for comment in redditor.comments.new():
		if store_comment(comment) is True:
			stored_comments += 1
		
		comment_submission = reddit.submission(id = comment.link_id[3:])
		if store_submission(comment_submission) is True:
			process_submission(comment_submission)
			processed_submissions += 1
			output("Processed " + str(processed_comments) + " comments and " + str(processed_submissions) + " submissions after " + str(time.time() - start_time) + "...")
	output("Stored " + str(stored_comments) + " comments from " + str(len(completed_queue)) + " user(s) after " + str(time.time() - start_time) + "...")
		
	output("Processing /u/" + user + "'s submissions...")
	for submission in redditor.submissions.new():
		if store_submission(submission) is True:
			process_submission(submission)
			processed_submissions += 1
		output("Processed " + str(processed_comments) + " comments and " + str(processed_submissions) + " submissions after " + str(time.time() - start_time) + "...")
		
	userqueue_processed += 1
	
output("Users not processed yet:")
for username in user_queue:
	output(username)
		
db_conn.close()