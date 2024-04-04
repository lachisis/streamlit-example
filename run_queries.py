# %%
import requests 
import json
from query import github_pull_requests_query, github_item_query, github_add_option_to_card_mutation
import pandas as pd
import utils_df
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
    
def add_option_to_card(project_Id, item_Id, field_Id, value):
    mutation = github_add_option_to_card_mutation()
    variables = {"projectId": project_Id, "itemId": item_Id, "fieldId": field_Id, "value": value}
    response = requests.post(url, headers=headers, json={"query": mutation, "variables": variables})

    #print(response.json())
    response = response.json()
    print(response)
    print(response.headers)
    #new_card_id = response["data"]["updateProjectV2ItemFieldValue"]["projectV2Item"]["id"]
    #return new_card_id   
        
def get_paginated_prs(repositories=REPOSITORIES):
    
    prs = []
    for repository in repositories: 
        pagination_str = "first: 100"
        print(repository)
        variables = {
            "reponame": repository,
            "org": ORG
        }
        
        has_next_page = True
        while has_next_page:
            print(repository + '-' * 80)
            query = github_pull_requests_query(pagination_str)
            response = requests.post(url, headers=headers, json={"query": query, 
                                                                "variables": variables})
            print(response)
            response = response.json()
            #print(response)
            
            page_info = response['data']["repository"]["pullRequests"]["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            pagination_str = f"first: 100, after: \"{page_info['endCursor']}\""        

            prs.extend(response['data']['repository']['pullRequests']['nodes'])

    return prs


def get_paginated_github_items(variables):
    pagination_str = "first: 100"
    items = []
    fields = []
    has_next_page = True
    while has_next_page:
        print('-' * 80)
        # Make the request and print the response JSON
        query = github_item_query(pagination_str)
        response = requests.post(url, headers=headers, json={"query": query, "variables": variables})

        print(response)
        response = response.json()["data"]
        print(response["organization"]["projectV2"]["id"])
        
        page_info = response["organization"]["projectV2"]["items"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        pagination_str = f"first: 100, after: \"{page_info['endCursor']}\""
        
        items.extend(response["organization"]["projectV2"]["items"]["nodes"])
        fields.extend(response["organization"]["projectV2"]["fields"]["nodes"])
        print(len(items), len(fields))
    return items, fields


def update_dates_on_cards(items):
    # Mutates the items 
    updated_created = 0
    updated_closed = 0
    for i,issue in enumerate(items):
        # this will go over all issues, even if they already have their create date set

        if issue["content"] == {}:
            # It's a PR
            continue

        if issue["fieldValues"]["nodes"] != []:
            has_created_date = False
            has_closed_date = False
            created_date_field = [elem for elem in issue["fieldValues"]["nodes"] if "field" in elem and elem["field"]["id"] == "PVTF_lADOAGRc8M4AKnvAzgOzA2U"]
            assert len(created_date_field) <= 1
            if len(created_date_field) == 1:
                has_created_date = True

            if not has_created_date:
                print("adding created date to card")
                add_option_to_card(project_Id="PVT_kwDOAGRc8M4AKnvA", 
                                item_Id=issue["id"], 
                                field_Id="PVTF_lADOAGRc8M4AKnvAzgOzA2U", 
                                value={"date": issue["content"]["createdAt"]})            
                # avoid having to rerun the query to get the updated dates
                issue["fieldValues"]["nodes"].append({"date": issue["content"]["createdAt"], "field": {"id": "PVTF_lADOAGRc8M4AKnvAzgOzA2U"}})

                updated_created += 1

            closed_date_field = [elem for elem in issue["fieldValues"]["nodes"] if "field" in elem and elem["field"]["id"] == "PVTF_lADOAGRc8M4AKnvAzgOzDks"]
            assert len(closed_date_field) <= 1
            if len(closed_date_field) == 1:
                has_closed_date = True

            if not has_closed_date and "closed" in issue["content"] and issue["content"]["closed"]:
                # Draft Issues don't have closed dates (they never close, they just move to Done)
                print("adding closed date to card")
                add_option_to_card(project_Id="PVT_kwDOAGRc8M4AKnvA", 
                                item_Id=issue["id"], 
                                field_Id="PVTF_lADOAGRc8M4AKnvAzgOzDks", 
                                value={"date": issue["content"]["closedAt"]})        
                # avoid having to rerun the query to get the updated dates
                issue["fieldValues"]["nodes"].append({"date": issue["content"]["closedAt"], "field": {"id": "PVTF_lADOAGRc8M4AKnvAzgOzDks"}})      
                updated_closed +=1 

    print(i,updated_created, updated_closed)
    
def _save_github_data_to_file(github_items, github_fields):
    with open('github_items.json', 'w') as f:
        json.dump(github_items, f)
    with open('github_fields.json', 'w') as f:
        json.dump(github_fields, f)

def generate_ticket_df(DEBUG=True, people_list=PEOPLE_LIST):
    if DEBUG:
        github_items = json.load(open('github_items.json'))
        github_fields = json.load(open('github_fields.json'))
    else:
        github_items, github_fields = get_paginated_github_items(variables=variables) 
        _save_github_data_to_file(github_items, github_fields)
        update_dates_on_cards(github_items)
        _save_github_data_to_file(github_items, github_fields)

    fields_id_to_name_map = utils_df.get_fields_id_to_name_map(github_fields)

    df_issues = [] 
    for i,issue in enumerate(github_items):
        df_issues.append(issue)

    
    df_issues = pd.DataFrame(df_issues)
    df_issues_orig = df_issues.copy()

    df_issues = utils_df.format_tickets_df(df_issues_orig, fields_id_to_name_map, people_list)
    return df_issues



