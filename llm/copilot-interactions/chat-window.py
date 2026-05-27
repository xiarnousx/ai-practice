import urllib.request
import urllib.parse
import json

def get_github_user(username):
    with urllib.request.urlopen(f'https://api.github.com/users/{username}') as response:
        data = response.read()
        return json.loads(data.decode('utf-8'))

def post_data(url, payload):
    data = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as response:
        result = response.read()
        return result.decode('utf-8')