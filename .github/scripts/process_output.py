import json
import os
import requests

# Read the output file
with open('output.json', 'r') as f:
    data = json.load(f)

# Prepare the review comments
comments = []
for file_path, issues in data.items():
    for issue in issues:
        comments.append({
            'path': file_path,
            'position': issue['Line'],
            'body': f"{issue['Severity'].capitalize()}: {issue['Message']}"
        })

# Create the review
headers = {
    'Authorization': f"Bearer {os.environ['GITHUB_TOKEN']}",
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

payload = {
    'commit_id': os.environ['GITHUB_SHA'],
    'body': 'Automated review from Vale',
    'event': 'COMMENT',
    'comments': comments
}

owner, repo = os.environ['GITHUB_REPOSITORY'].split('/')
pr_number = os.environ['PR_NUMBER']

url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 201:
    print("Review created successfully")
else:
    print(f"Failed to create review: {response.status_code}")
    print(response.text)
    print(f"Request URL: {url}")
    print(f"Request headers: {headers}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")