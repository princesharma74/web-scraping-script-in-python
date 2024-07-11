import requests
from datetime import datetime, timedelta, timezone

def leetcode_contestHistory(username):
    if username is None:
        return []
    query = """
    query userContestRankingHistory($username: String!) {
        userContestRankingHistory(username: $username) {
            attended
            rating
            ranking
            trendDirection
            problemsSolved
            totalProblems
            finishTimeInSeconds
            contest {
                title
                startTime
            }
        }
    }
    """

    url = 'https://leetcode.com/graphql'

    variables = {
        "username": username
    }

    rankingHistory = []

    response = requests.post(
        url, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        data = response.json()

        user_contest_ranking_history = data.get('data', {}).get(
            'userContestRankingHistory', None)

        if user_contest_ranking_history is None:
            print("No contest history found for the user")
            return rankingHistory

        prevRating = 1500
        for history in user_contest_ranking_history:
            if history['attended']:
                contestinfo = {}
                contestinfo['platform_user_id'] = username
                contestinfo['rating_change'] = int(
                    (history['rating'])-prevRating)
                prevRating = int(history.get('rating', None))
                contestinfo['final_rating'] = int(history.get('rating', None))  
                contestinfo['number_of_problems_solved'] = history.get('problemsSolved', None)
                contestinfo['rank'] = history.get('ranking', None)
                contestinfo['contest'] = {
                    'title': history.get('contest', {}).get('title', ''),
                    'start_time': datetime.utcfromtimestamp(history.get('contest', {}).get('startTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'platform': 'leetcode',
                    'url': f"https://leetcode.com/contest/{(history.get('contest', {}).get('title', '')).replace(' ', '-').lower()}",
                    'duration': '',
                    'total_questions': 4
                }
                rankingHistory.append(contestinfo)

    else:
        # Print an error message if the request was unsuccessful
        print("Error fetching data. Status code:", response.status_code)
    return rankingHistory

# Example usage:
# username = 'coder_s_176'  # valid username
# contestHistory = leetcode_contestHistory(username)
# print(contestHistory)
