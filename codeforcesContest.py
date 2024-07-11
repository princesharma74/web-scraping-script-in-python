import requests
from bs4 import BeautifulSoup
from datetime import datetime


def codeforces_contestHistory(username):
    if username is None:
        return []
    rating_change_data = []
    url = f"https://codeforces.com/contests/with/{username}"
    response = requests.get(url, allow_redirects=False)
    if response.status_code != 200:
        print(f"No ContestHistory found for {username}")
        return rating_change_data

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing contest details
        contest_table = soup.find(
            'table', class_='tablesorter user-contests-table')

        # Check if the table exists
        if contest_table:
            # Find all rows in the table
            rows = contest_table.find_all('tr')[1:]  # Skip the header row

            # Iterate over each row and extract contest details
            for row in rows:
                cols = row.find_all('td')
                # Extract contest details
                contest_info = {}
                contest_info['platform_user_id'] = username
                contest_info['rating_change'] = int(cols[5].text.strip())
                contest_info['final_rating'] = int(cols[6].text.strip())
                contest_info['number_of_problems_solved'] = int(
                    cols[4].text.strip())
                contest_info['rank'] = int(cols[3].text.strip())
                time = cols[2].text.strip()
                datet = datetime.strptime(time, "%b/%d/%Y %H:%M")
                formatted_time = datet.strftime("%Y-%m-%dT%H:%M:%S+05:30")
                contest_no = cols[1].find('a').get('href').strip()
                contest_info['contest'] = {'title': cols[1].text.strip(
                ), 'start_time': formatted_time, 'platform': 'codeforces', 'url': f"https://codeforces.com{contest_no}", 'duration': '',
                    'total_questions': 8}
                rating_change_data.append(contest_info)

        else:
            print("Contest table not found on the page.")
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)
    return rating_change_data


# data = codeforces_contestHistory("guptajirock176")
# print(data)
# for contest in data:
# print(contest)

# usernameV="guptajirock176"  # valid username
# contestHistory = codeforces_contestHistory(usernameV)  #checking history for valid username

# usernameInv="shivamBedar"  # invalid username
# contestHistory = codeforces_contestHistory(usernameInv)  #checking history for invalid username

# print("Contest History:")
# for contest in contestHistory:
#     print(contest)
