from bs4 import BeautifulSoup
import requests
from selenium_driver import driversetup
import json
from datetime import datetime
import re


def codechef_contestHistory(driver, username):
    if username is None:
        return []

    rating_change_data = []
    url = f"https://www.codechef.com/users/{username}"
    response = requests.get(url, allow_redirects=False)

    # Check if the request was redirected
    if response.status_code != 200:  # 302 status code indicates redirection
        redirected_url = response.headers.get('Location')
        if redirected_url == 'https://www.codechef.com/':
            print(f"No ContestHistory found for {username}.")
            return rating_change_data
    driver.get(f"https://www.codechef.com/users/{username}")
    driver.implicitly_wait(10)

    # Get the HTML content of the page
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all content divs
    content_divs = soup.find_all('div', class_='content')

    # Initialize a dictionary to map contest names to the total number of problems solved
    contest_problems_map = {}

    # Iterate through each content div to extract contest name and number of problems solved
    for content_div in content_divs:
        # Find the contest name
        h5_tag = content_div.find('h5')
        if h5_tag is None:
            continue

        # Find the nested <a> tag within the <h5> tag
        a_tag = h5_tag.find('a')
        if a_tag is None:
            continue

        # Extract the contest name
        contest_name = a_tag.text.strip()

        # Find all problem links within the span
        problem_links = content_div.find_all('a', href=True)

        # Count the number of problems (questions) solved
        num_problems_solved = len(problem_links)

        # Map the contest name to the total number of problems solved
        contest_problems_map[contest_name] = num_problems_solved

    # Extract contest details
    for contest in soup.find_all('script'):
        if 'Drupal.settings' in contest.text:
            data = contest.text.split('Drupal.settings, ')[1]
            start_index = data.find('{')  # Find the starting curly brace
            end_index = data.rfind('}')  # Find the ending curly brace

            # Ensure both start and end indices are found
            if start_index != -1 and end_index != -1:
                json_str = data[start_index:end_index+1]
                try:
                    data_json = json.loads(json_str)
                    prevRating = 1000
                    for c in data_json.get('date_versus_rating', {}).get('all', []):
                        contest_info = {}
                        rating_change = str(int(c.get('rating', 0)) - prevRating)
                        prevRating = int(c.get('rating', 0))
                        contest_name = str(c.get('name'))
                        time = datetime.strptime(
                            c['end_date'], "%Y-%m-%d %H:%M:%S")
                        time = time.strftime("%Y-%m-%dT%H:%M:%S+05:30")
                        global_rank = c.get('rank')
                        if 'Starters' not in contest_name:
                            continue
                        contest_info['platform_user_id'] = username
                        contest_info['rating_change'] = int(rating_change)
                        contest_info['final_rating'] = int(c.get('rating'))
                        contest_info['number_of_problems_solved'] = int(contest_problems_map.get(
                            contest_name, 0))
                        contest_info['time_taken'] = None
                        contest_info['rank'] = int(global_rank)
                        word = re.findall(r'[A-Za-z]+|\d+', contest_name)
                        starters_index = word.index("Starters")
                        contestNo = word[starters_index + 1]
                        # print(contestNo, contest_name)
                        contest_info['contest'] = {'title': contest_name, 'start_time': time,
                                                   'platform': 'codechef', 'url': f"https://www.codechef.com/START{contestNo}", 'duration': '', 'total_questions': 8}
                        rating_change_data.append(contest_info)
                except json.JSONDecodeError as e:
                    print("Error decoding JSON:", e)

    return rating_change_data


# driver setup for codechef
# driver = driversetup()
# usernameV = 'aar9av'  # valid username
# checking history for valid username
# data = codechef_contestHistory(driver, usernameV)
# print(data)
# usernameI = 'coder_s_1761'  # invalid username
# checking history for invalid username
# data = codechef_contestHistory(driver, usernameI)


# printing the data
# for contest in data:
#     print(contest)

# Close the WebDriver
# driver.quit()
