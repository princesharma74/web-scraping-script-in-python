import mysql.connector
import json
from dotenv import load_dotenv
from datetime import datetime
from send_email import send
import os
load_dotenv()

smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
sender_email = os.getenv('SENDER_EMAIL')
sender_name = os.getenv('SENDER_NAME')
receiver_email = os.getenv('RECEIVER_EMAIL')
password = os.getenv('PASSWORD')

mydb = mysql.connector.connect(
  host=os.getenv('DATABASE_URL'),
  user=os.getenv('DATABASE_USER'),
  password=os.getenv('DATABASE_PASSWORD'),
  database=os.getenv('DATABASE_NAME')
)

def push_contests(contests):
    mycursor = mydb.cursor()
    query = '''
        INSERT INTO Contest (title, url, platform, start_time, total_questions, updatedAt)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE title=VALUES(title), url=VALUES(url), platform=VALUES(platform), start_time=VALUES(start_time), total_questions=VALUES(total_questions), updatedAt=VALUES(updatedAt)
    '''
    values = [(contest['title'], contest['url'], contest['platform'], contest['start_time'], contest.get('total_questions', 0), datetime.now()) for contest in contests]
    try:
        mycursor.executemany(query, values)
        mydb.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        mydb.rollback()
    mycursor.close()

def get_next_user():
    mycursor = mydb.cursor()
    mycursor.execute('''
        SELECT 
            u.email,
            cf.codeforces_id,
            cc.codechef_id,
            lc.leetcode_id
        FROM 
            User u
        LEFT JOIN 
            Codeforces cf ON u.email = cf.user_email
        LEFT JOIN 
            Codechef cc ON u.email = cc.user_email
        LEFT JOIN 
            Leetcode lc ON u.email = lc.user_email
        WHERE
            cf.codeforces_id IS NOT NULL OR cc.codechef_id IS NOT NULL OR lc.leetcode_id IS NOT NULL
        ORDER BY
            u.lastUpdatedAt
        LIMIT 1;
                     ''')
    user = mycursor.fetchone()
    user_dict = {
        "email": user[0],
        "codeforces_id": user[1],
        "codechef_id": user[2],
        "leetcode_id": user[3]
    }
    return user_dict

def push_user_data(email, user_data):
    mycursor = mydb.cursor()
    query = f'''
        UPDATE User
        SET lastUpdatedAt=%s
        WHERE email=%s 
    '''
    values = (datetime.now(), email)
    mycursor.execute(query, values)
    platforms = ["codeforces", "codechef", "leetcode"]
    for platform in platforms:
        data = user_data.get(platform, {})
        query = f'''
            UPDATE {platform.capitalize()}
            SET global_rank=%s, rating=%s, number_of_contests=%s, number_of_questions=%s
            WHERE user_email=%s
        '''
        values = (data.get('global_rank', None), data.get('rating', None), data.get('number_of_contests', None), data.get('number_of_questions', None), email)
        mycursor.execute(query, values)
    mydb.commit()

def push_user_submission(email, data, chunk_size=30):
    if isinstance(data, list):
        data_chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    else:
        data_chunks = [data]
    
    mycursor = mydb.cursor()
    total_chunks = len(data_chunks)
    
    for i, submissions in enumerate(data_chunks):
        print(f"Processing chunk {i+1}/{total_chunks} of size {len(submissions)}...")
        problem_inserts = []
        submission_inserts = []
        
        for submission in submissions:
            if submission.get('problem_title'):
                problem_inserts.append((
                    submission['problem_title'],
                    submission['platform'],
                    submission['problem_link'],
                    datetime.now()
                ))

            if submission.get('submission_id') and submission.get('problem_title'):
                submission_inserts.append((
                    submission['submission_id'],
                    email,
                    submission['problem_title'],
                    submission['submitted_at'],
                    submission['submission_url'],
                    datetime.now()
                ))

        problem_query = '''
            INSERT INTO Problem (problem_title, platform, problem_link, updatedAt)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE problem_title=VALUES(problem_title), platform=VALUES(platform), problem_link=VALUES(problem_link), updatedAt=VALUES(updatedAt)
        '''
        submission_query = '''
            INSERT INTO Submission (submission_id, user_email, problem_title, submitted_at, submission_url, updatedAt)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE submission_id=VALUES(submission_id), user_email=VALUES(user_email), problem_title=VALUES(problem_title), submitted_at=VALUES(submitted_at), submission_url=VALUES(submission_url), updatedAt=VALUES(updatedAt)
        '''

        try:
            if problem_inserts:
                mycursor.executemany(problem_query, problem_inserts)
            if submission_inserts:
                mycursor.executemany(submission_query, submission_inserts)
            mydb.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            mydb.rollback()

    mycursor.close()

def push_rating_changes(email, data, chunk_size=30):
    if isinstance(data, list):
        data_chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    else:
        data_chunks = [data]
    
    mycursor = mydb.cursor()
    total_chunks = len(data_chunks)
    
    for i, rating_changes in enumerate(data_chunks):
        print(f"Processing chunk {i+1}/{total_chunks} of size {len(rating_changes)}...")
        contest_inserts = []
        rating_change_inserts = []
        
        for rating_change in rating_changes:
            contest = rating_change.get('contest')
            if contest.get('title'):
                contest_inserts.append((
                    contest['title'],
                    contest['url'],
                    contest['platform'],
                    contest['start_time'],
                    contest['total_questions'],
                    datetime.now()
                ))

            if email and contest.get('title'):
                rating_change_inserts.append((
                    contest['title'],
                    email,
                    rating_change['rating_change'],
                    rating_change['rank'],
                    rating_change['number_of_problems_solved'],
                    rating_change['final_rating'],
                    datetime.now()
                ))

        contest_query = '''
            INSERT INTO Contest (title, url, platform, start_time, total_questions, updatedAt)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=VALUES(title), url=VALUES(url), platform=VALUES(platform), start_time=VALUES(start_time), total_questions=VALUES(total_questions), updatedAt=VALUES(updatedAt)
        '''
        rating_change_query = '''
            INSERT INTO RatingChange (contest_title, user_email, rating_change, `rank`, number_of_problems_solved, final_rating, updatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE contest_title=VALUES(contest_title), user_email=VALUES(user_email), rating_change=VALUES(rating_change), `rank`=VALUES(`rank`), number_of_problems_solved=VALUES(number_of_problems_solved), final_rating=VALUES(final_rating), updatedAt=VALUES(updatedAt)
        '''

        try:
            if contest_inserts:
                mycursor.executemany(contest_query, contest_inserts)
            if rating_change_inserts:
                mycursor.executemany(rating_change_query, rating_change_inserts)
            mydb.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            mydb.rollback()

    mycursor.close()


def get_top_performers():
    mycursor = mydb.cursor()
    mycursor.execute('''
        SELECT u.first_name, s.user_email AS email, COUNT(s.user_email) AS numsub
        FROM User u
        JOIN Submission s ON u.email = s.user_email
        WHERE CONVERT_TZ(s.submitted_at, '+00:00', '+05:30') >= DATE_FORMAT(CONVERT_TZ(CURDATE(), '+05:30', '+00:00'), '%Y-%m-%d 00:00:00')
        AND CONVERT_TZ(s.submitted_at, '+00:00', '+05:30') < DATE_FORMAT(CONVERT_TZ(CURDATE() + INTERVAL 1 DAY, '+05:30', '+00:00'), '%Y-%m-%d 00:00:00')
        GROUP BY u.first_name, s.user_email
        ORDER BY numsub DESC
        LIMIT 10;
                     ''')
    performers = mycursor.fetchall()
    performers_list = []
    for performer in performers: 
        performer_dict = {
            "name": performer[0],
            "email": performer[1],
            "submissions_count": performer[2]
        }
        performers_list.append(performer_dict)
    performers_list = [
        {
            "name": "Prince Sharma",
            "email": "princesharma2899@gmail.com",
            "submissions_count": 1
        }
    ]
    return performers_list


def main(): 
    # print(json.dumps(get_last_user(), indent=4))
    user_data =   {
        "codeforces": {
            "rating": 1126,
            "number_of_contests": 15,
            "number_of_questions": 37,
            "email": "princesharma2899@gmail.com"
        },
        "codechef": {
            "rating": 1700,
            "highest_rating": 1700,
            "number_of_contests": 3,
            "global_rank": 9066,
            "country_rank": 7485,
            "number_of_questions": 13,
            "email": "princesharma2899@gmail.com"
        },
        "leetcode": {
            "number_of_questions": 2,
            "email": "princesharma2899@gmail.com"
        }
    }
    # push_user_data(user_data)
    submissions =  [
            {
        "platform": "leetcode",
        "problem_title": "Count Pairs That Form a Complete Day II",
        "problem_link": "https://leetcode.com/problems/count-pairs-that-form-a-complete-day-ii/",
        "submission_id": 1289626712,
        "submission_url": "https://leetcode.com/submissions/detail/1289626712/",
        "submitted_at": "2024-06-16T08:27:42+05:30"
    },
    {
        "platform": "leetcode",
        "problem_title": "Count Pairs That Form a Complete Day I",
        "problem_link": "https://leetcode.com/problems/count-pairs-that-form-a-complete-day-i/",
        "submission_id": 1289573403,
        "submission_url": "https://leetcode.com/submissions/detail/1289573403/",
        "submitted_at": "2024-06-16T08:05:05+05:30"
    }
    ]

    # push_user_submission('princesharma2899@gmail.com', submissions)
    contests = [ 
        {
            "title": "Starters 122 Division 3 (Rated)",
            "start_time": "2024-02-21T22:00:06+05:30",
            "platform": "codechef",
            "url": "https://www.codechef.com/START122",
            "duration": "",
            "total_questions": 8
        }]
    # push_contests(contests)
    rating_change_data = [
        {
            "platform_user_id": "princesharma75",
            "rating_change": 105,
            "final_rating": 1700,
            "number_of_problems_solved": 0,
            "time_taken": None,
            "rank": 353,
            "contest": {
                "title": "Starters 122 Division 3 (Rated)",
                "start_time": "2024-02-21T22:00:06+05:30",
                "platform": "codechef",
                "url": "https://www.codechef.com/START122",
                "duration": "",
                "total_questions": 8
            }
        }
    ]
    push_rating_changes('princesharma2899@gmail.com', rating_change_data)

def test_query():
    performers = get_top_performers()
    rank = 1; 
    for performer in performers:
        send(performer['name'], performer['email'], performer['submissions_count'], rank)

test_query()