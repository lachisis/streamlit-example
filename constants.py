import os 

# Replace with your GitHub personal access token
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

ORG = "servicenow"
PROJECT = "SNR-LABS"
PROJECT_ID = 10
TEAM_SLUG = "sn-research-labs"
ORG_ID = "O_kgDOAGRc8A" #"MDEyOk9yZ2FuaXphdGlvbjY1NzczOTI"
REPOSITORIES = ['research-now-llm', 'web2dataset', 'research-lm-evaluation-harness-wrapper']
PEOPLE_LIST = ['lachisis', 'nitsanluke', 'gebelangsn',
    'christyler3030', 'mmunozm', 'danieltremblay', 'tianyi-chen',
    'erikchwang', 'mebrunet' ]

# Set up the request headers and endpoint URL
# Add schema preview in the Accept header 
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}",
           "Accept": "application/vnd.github.starfox-preview+json"}
url = "https://api.github.com/graphql"

variables = {"project_number": PROJECT_ID, "org": ORG}
pagination_str = "first: 100"
variables2 = {
    "org": ORG, 
    "teamslug": TEAM_SLUG,
    "orgID": ORG_ID
}