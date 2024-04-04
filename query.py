def github_pull_requests_query(pagination_str):
    return """query($reponame: String!, $org: String!) {
        repository(name: $reponame, owner: $org) {""" + \
        f"pullRequests ({pagination_str}, states:[MERGED])" + """ {
                pageInfo {
                    endCursor,
                    hasNextPage
                },            
                nodes {
                    author {
                      login  
                    },
                    closed,
                    closedAt,
                    id, 
                    reviews (first:10) {
                        nodes {
                            author {
                                login
                            },
                            id,
                            createdAt,
                        }
                    }
                }
            }
        }
    }
"""

def github_item_query(pagination_str):
    return ("""
    query ($org: String!, $project_number: Int!) { 
        organization(login: $org){
        projectV2(number: $project_number) {
            id,"""
            f"items({pagination_str}) "
            "{"
"""                totalCount,
                pageInfo {
                    endCursor,
                    hasNextPage
                },
                nodes {
                    id,
                    databaseId,
                    content {
                        ... on DraftIssue {
                            id,
                            title,
                            createdAt,
                            updatedAt
                        }
                        ... on Issue {
                            id,
                            title, 
                            assignees(first: 10) {
                              nodes {
                                  ... on User {
                                      id,
                                      login,
                                  }
                              }  
                            },
                            number,
                            createdAt,
                            updatedAt,
                            closedAt,
                            closed,
                            timelineItems(first: 100, itemTypes: [MOVED_COLUMNS_IN_PROJECT_EVENT]) {
                                totalCount,
                                updatedAt,
                                nodes {
                                    ... on MovedColumnsInProjectEvent {
                                        createdAt,
                                        previousProjectColumnName,
                                        projectColumnName
                                    }
                                }
                            }
                        }
                    },
                    fieldValues(first: 100) {
                        nodes {
                            ... on ProjectV2ItemFieldLabelValue {
                                labels (first:10) {
                                    nodes {
                                        id,
                                        name,
                                        description,
                                    }
                                }
                            }
                            ... on ProjectV2ItemFieldDateValue {
                                date,
                                field {
                                    ... on ProjectV2Field {
                                        id
                                    }
                                }
                                id
                            }
                            ... on ProjectV2ItemFieldIterationValue {
                                id,
                                field {
                                    ...on ProjectV2IterationField {
                                        id
                                    }
                                }
                                title
                            }
                            ... on ProjectV2ItemFieldNumberValue {
                                id,
                                field {
                                    ... on ProjectV2Field {
                                        id
                                    }
                                }
                                number
                            }
                            ... on ProjectV2ItemFieldSingleSelectValue {
                                id,
                                field {
                                    ... on ProjectV2SingleSelectField {
                                        id
                                    }
                                }
                                name,
                                optionId,
                                description,
                            }
                        }
                    }
            
                },
            },
            fields(first: 100) {
                    nodes {
                        ... on ProjectV2Field {
                            id,
                            name
                        }
                        ... on ProjectV2IterationField {
                            id,
                            name
                        }
                        ... on ProjectV2SingleSelectField {
                            id,
                            name
                        }
                    }
                }
            }
        }
    }
    """)

def github_add_option_to_card_mutation():
    return """
        mutation ($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
        updateProjectV2ItemFieldValue(input: {projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: $value}) {
                projectV2Item {
                    id,
                }
            }
        }
    """



