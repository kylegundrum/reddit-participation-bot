import praw
import time

# configuration
SUBREDDIT_NAME = "kg_bot_tests"
REQUIRED_RESPONSE_MINUTES = 180
REMOVED_MESSAGE = ("OP must reply within 3 hours per subreddit rules. "
                   "Since you haven't replied, this post has been removed.\n\n"
                   "If you disagree with this decision, oh well, this is a test.")

# setup

# uses config details from praw.ini file
reddit = praw.Reddit()

me = reddit.user.me()


def check_submission_reply_authors(submission):
    op_author = submission.author

    submission.comments.replace_more(limit=None)
    comments = submission.comments.list()
    
    op_comments = [
        x for x in comments if x.author == op_author
    ]

    me_comments = [
        x for x in comments if x.author == me
    ]

    return len(op_comments) > 0, len(me_comments) > 0


def remove_violation_post(submission):
    submission.mod.remove()
    submission.mod.send_removal_message(REMOVED_MESSAGE)


if __name__ == "__main__":
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    new_submissions = subreddit.new()

    now = time.time()
    required_start = now - REQUIRED_RESPONSE_MINUTES * 60
    required_end = now - (REQUIRED_RESPONSE_MINUTES + 24 * 60) * 60

    # get list of submissions created between REQUIRED_RESPONSE_MINUTES ago and one hour later
    submissions_list = [
        x for x in new_submissions if x.created_utc >= required_end # if x.created_utc <= required_start and x.created_utc >= required_end
    ]

    for submission in submissions_list:
        print(time.asctime(time.gmtime(submission.created_utc)), submission.title)

        if submission.locked:
            print("Skipping evaluation of locked post")
            continue
        
        op_replied, me_replied = check_submission_reply_authors(submission)
        print(op_replied, me_replied)

        if not op_replied and not me_replied:
            print("Removing post due to no OP reply")
            remove_violation_post(submission)
