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
            'line': issue['Line'],
            'body': f"{issue['Severity'].capitalize()}: {issue['Message']}"
        })

# Create the review
headers = {
    'Authorization': f"token {os.environ['GITHUB_TOKEN']}",
    'Accept': 'application/vnd.github.v3+json'
}

payload = {
    'commit_id': os.environ['GITHUB_SHA'],
    'event': 'COMMENT',
    'comments': comments
}

response = requests.post(
    f"https://api.github.com/repos/{os.environ['REPO']}/pulls/{os.environ['PR_NUMBER']}/reviews",
    headers=headers,
    json=payload
)

if response.status_code == 200:
    print("Review created successfully")
else:
    print(f"Failed to create review: {response.status_code}")
    print(response.text)