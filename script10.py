import requests

response = requests.get("https://api.github.com/users/octocat")

print("Status code:", response.status_code)

data = response.json()
print(data["name"])
print(data["public_repos"])
print(data["created_at"])