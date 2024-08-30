import json
import os
import requests

def get_position_in_diff(file_path, line_number):
    headers = {
        'Authorization': f"Bearer {os.environ['GITHUB_TOKEN']}",
        'Accept': 'application/vnd.github.v3.diff',
    }
    
    url = f"https://api.github.com/repos/{os.environ['REPO']}/pulls/{os.environ['PR_NUMBER']}"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get diff: {response.status_code}")
        return None

    diff = response.text
    current_file = ""
    position = 0
    for line in diff.split('\n'):
        if line.startswith('diff --git'):
            current_file = line.split()[-1][2:]
        elif line.startswith('@@'):
            position = 1
        elif current_file == file_path:
            if position == line_number:
                return position
            position += 1
    return None

# Read the output file
with open('output.json', 'r') as f:
    data = json.load(f)

# Prepare the review comments
comments = []
for file_path, issues in data.items():
    for issue in issues:
        position = get_position_in_diff(file_path, issue['Line'])
        if position is not None:
            comments.append({
                'path': file_path,
                'position': position,
                'body': f"{issue['Severity'].capitalize()}: {issue['Message']}"
            })

# Create the review
headers = {
    'Authorization': f"Bearer {os.environ['GITHUB_TOKEN']}",
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

payload = {
    'commit_id': os.environ['COMMIT_SHA'],
    'body': 'Automated review from Vale',
    'event': 'COMMENT',
    'comments': comments
}

url = f"https://api.github.com/repos/{os.environ['REPO']}/pulls/{os.environ['PR_NUMBER']}/reviews"

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 201:
    print("Review created successfully")
else:
    print(f"Failed to create review: {response.status_code}")
    print(response.text)
    print(f"Request URL: {url}")
    print(f"Request headers: {headers}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")