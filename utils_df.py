import pandas as pd
import constants 

def get_fields_id_to_name_map(fields_from_github):
    return {
    item['id']: item['name']
    for item in fields_from_github if 'id' in item
    }

def explode_dict_col(df, col):
    tmp = df[col].apply(pd.Series)
    tmp.columns = [f"{col}_{x}" for x in tmp.columns]
    return pd.concat([df, tmp], axis=1).drop(col, axis=1)

def explode_list_col(df, col):
    keys = df[col].explode().explode().unique() #iloc[0][0].keys()
    keys = [key for key in keys if not pd.isnull(key)] # remove nones
    #display(keys)
    for key in keys:
        def _get_key(x,key):
            if type(x) is not list and pd.isnull(x):
                return None
            return [xx[key] for xx in x if key in xx ]
        tmp = df[col].apply(lambda x: _get_key(x, key))
        tmp.name = f"{col}_{key}"
        df = pd.concat([df, tmp], axis=1)
        
    df = df.drop(col, axis=1)
        
    return df

def explode_field_values_list(value_array, fields_id_to_name_map):
    output = {}
    for field_dict in value_array:
        if field_dict == {}:
            continue
        
        if "labels" in field_dict:
            continue
        #print(field_dict)
        field_id = field_dict["field"]["id"]
        if field_id not in fields_id_to_name_map:
            raise ValueError(field_id)
        
        field_name = fields_id_to_name_map[field_id]
        if field_name == "Size (days)":
            value = field_dict["number"]
        elif field_name == "Status":
            value = field_dict["name"]
        elif field_name == "Size (old)":
            value = field_dict["name"]
        elif field_name == "Days remaining":
            value = field_dict["number"]
        elif field_name == "Priority":
            value = field_dict["name"]
        else:
            continue
        output[field_name] = value
    return output


def fix_size(row):
    if not pd.isnull(row["fieldValues_Size (days)"]):
        return row["fieldValues_Size (days)"]
    
    #print(row)
    if not pd.isnull(row["fieldValues_Size (old)"]):
        if "2 weeks" in row["fieldValues_Size (old)"]:
            return 0
        elif "1 week" in row["fieldValues_Size (old)"] or "5 days" in row["fieldValues_Size (old)"]:
            return 5
        elif "3 days" in row["fieldValues_Size (old)"]:
            return 3
        elif "2 days" in row["fieldValues_Size (old)"]:
            return 2
        elif "1 day" in row["fieldValues_Size (old)"]:
            return 1
        elif "0.5" in row["fieldValues_Size (old)"]:
            return 0.5
        else:
            return None
        
    return None



def format_tickets_df(df_issues, fields_id_to_name_map, people_list):
    df_issues = explode_dict_col(df_issues, "content")
    df_issues = explode_dict_col(df_issues, "content_assignees")
    df_issues = explode_dict_col(df_issues, 'fieldValues')
    df_issues = explode_list_col(df_issues, "content_assignees_nodes")

    # convert the date to the nearest friday
    from pandas.tseries.offsets import Week
    df_issues['closedAt_Friday'] = pd.to_datetime(df_issues['content_closedAt']).where(
        pd.to_datetime(df_issues['content_closedAt']) == (( pd.to_datetime(df_issues['content_closedAt']) + Week(weekday=4) ) - Week()), 
        pd.to_datetime(df_issues['content_closedAt']) + Week(weekday=4)).dt.date

    df_issues["fieldValues"] = df_issues["fieldValues_nodes"].apply(lambda x: explode_field_values_list(x, fields_id_to_name_map))
    df_issues = explode_dict_col(df_issues, "fieldValues")

    df_issues["size_all"] = df_issues.apply(fix_size, axis=1)    

    users = df_issues['content_assignees_nodes_login'].explode().unique()

    df_issues_per_user = df_issues.explode('content_assignees_nodes_login')

    df_issues_per_user = df_issues_per_user[df_issues_per_user["content_assignees_nodes_login"].isin(people_list)]
    df_issues_per_user.rename(columns={"content_assignees_nodes_login": "assignee"}, inplace=True)
    f = df_issues_per_user.groupby(['assignee', 'closedAt_Friday'])["size_all"].sum().to_frame()
    f['rollingAvg_size_all'] = f['size_all'].rolling(4).mean()
    
    f = f.reset_index()
    g = pd.melt(f, id_vars=['assignee', 'closedAt_Friday'], value_vars=['rollingAvg_size_all', 'size_all'])
    
    return f,g

def format_prs_df(prs, people_list=constants.PEOPLE_LIST):
    df_prs = pd.DataFrame(prs)

    df_prs = explode_dict_col(df_prs, "author")
    df_prs = explode_dict_col(df_prs, 'reviews')
    from pandas.tseries.offsets import Week
    df_prs['closedAt_Friday'] = pd.to_datetime(df_prs['closedAt']).where(
        pd.to_datetime(df_prs['closedAt']) == (( pd.to_datetime(df_prs['closedAt']) + Week(weekday=4) ) - Week()), 
        pd.to_datetime(df_prs['closedAt']) + Week(weekday=4)).dt.date

    df_prs = df_prs[df_prs["author_login"].isin(people_list)]
    f = df_prs.groupby(['author_login', 'closedAt_Friday'])['closed'].count().to_frame()
    f['rollingAvg_closed'] = f['closed'].rolling(4).mean()
    f = f.reset_index()
    g = pd.melt(f, id_vars=['author_login', 'closedAt_Friday'], value_vars=['rollingAvg_closed', 'closed'])

    df_pr_reviews = df_prs.explode('reviews_nodes')
    df_pr_reviews = explode_dict_col(df_pr_reviews, 'reviews_nodes')
    df_pr_reviews = explode_dict_col(df_pr_reviews, "reviews_nodes_author")
    df_pr_reviews['createdAt_Friday'] = pd.to_datetime(df_pr_reviews['closedAt']).where(
        pd.to_datetime(df_pr_reviews['reviews_nodes_createdAt']) == (( pd.to_datetime(df_pr_reviews['reviews_nodes_createdAt']) + Week(weekday=4) ) - Week()), 
        pd.to_datetime(df_pr_reviews['reviews_nodes_createdAt']) + Week(weekday=4)).dt.date
    
    df_pr_reviews = df_pr_reviews[df_pr_reviews["reviews_nodes_author_login"].isin(people_list)]
    df_pr_reviews.rename(columns={"reviews_nodes_author_login": "author"}, inplace=True)
    h = df_pr_reviews.groupby(['author', 'createdAt_Friday'])["reviews_nodes_createdAt"].count().to_frame()
    h.columns = ['created']
    h['rollingAvg_created'] = h['created'].rolling(4).mean()
    h = h.reset_index()
    j = pd.melt(h, id_vars=['author', 'createdAt_Friday'], value_vars=['rollingAvg_created', 'created'])
    
    return f,g,h,j


def generate_ticket_df(github_items, github_fields, people_list=constants.PEOPLE_LIST):

    fields_id_to_name_map = get_fields_id_to_name_map(github_fields)

    df_issues = [] 
    for i,issue in enumerate(github_items):
        df_issues.append(issue)

    
    df_issues = pd.DataFrame(df_issues)
    df_issues_orig = df_issues.copy()

    df_issues_raw, df_issues_melted = format_tickets_df(df_issues_orig, fields_id_to_name_map, people_list)
    return df_issues_raw, df_issues_melted

def build_table(df, time_col, person_col, value_col):
    max_count = df.drop(columns=[time_col]).groupby([person_col]).count().max()
    a = df.drop(columns=[time_col]).groupby([person_col]).mean().sort_values(value_col)
    b = (df.drop(columns=[time_col]).fillna(0).groupby([person_col]).sum()/max_count).sort_values(value_col)
    
    c = pd.merge(a,b, on=person_col, suffixes=('_contributed', '_all_weeks'))[[f'{value_col}_contributed', f'{value_col}_all_weeks']]    
    return c