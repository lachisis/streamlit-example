# %%
import requests 
import json
from query import github_pull_requests_query, github_item_query, github_add_option_to_card_mutation
import utils
import constants

    
def add_option_to_card(project_Id, item_Id, field_Id, value):
    mutation = github_add_option_to_card_mutation()
    variables = {"projectId": project_Id, "itemId": item_Id, "fieldId": field_Id, "value": value}
    response = requests.post(constants.url, headers=constants.headers, json={"query": mutation, "variables": variables})

    response = response.json()
    print(response)
    #new_card_id = response["data"]["updateProjectV2ItemFieldValue"]["projectV2Item"]["id"]
    #return new_card_id   
        
def get_paginated_prs(repositories=constants.REPOSITORIES):
    
    prs = []
    for repository in repositories: 
        pagination_str = "first: 100"
        print(repository)
        variables = {
            "reponame": repository,
            "org": constants.ORG
        }
        
        has_next_page = True
        while has_next_page:
            print(repository + '-' * 80)
            query = github_pull_requests_query(pagination_str)
            response = requests.post(constants.url, headers=constants.headers, json={"query": query, 
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
        response = requests.post(constants.url, headers=constants.headers, json={"query": query, "variables": variables})

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
    

def regenerate_ticket_data(date):
    github_items, github_fields = get_paginated_github_items(variables=constants.variables) 
    utils.save_github_data_to_file(date, github_items, github_fields)
    update_dates_on_cards(github_items)
    utils.save_github_data_to_file(date, github_items, github_fields)

    return github_items, github_fields
    

def regenerate_prs_data(date):
    github_prs = get_paginated_prs()
    utils.save_github_prs_data_to_file(date, github_prs)

    return github_prs




