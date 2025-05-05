"""GraphQL queries for Indeed API"""

JOB_SEARCH = """
query GetJobData(
    $what: String!
    $location: String!
    $cursor: String
    $filters: JobSearchFiltersInput
) {
    jobSearch(
        what: $what
        location: $location
        limit: 100
        cursor: $cursor
        sort: RELEVANCE
        filters: $filters
    ) {
        pageInfo {
            nextCursor
        }
        results {
            job {
                title
                datePublished
                description {
                    html
                }
                location {
                    formatted {
                        short
                    }
                }
                compensation {
                    estimated {
                        baseSalary {
                            range {
                                ... on Range {
                                    min
                                    max
                                }
                            }
                        }
                    }
                }
                attributes {
                    key
                    label
                }
                employer {
                    name
                    dossier {
                        employerDetails {
                            addresses
                        }
                        links {
                            corporateWebsite
                        }
                    }
                }
                recruit {
                    viewJobUrl
                }
            }
        }
    }
}
"""

# API Headers
API_HEADERS = {
    "Host": "apis.indeed.com",
    "content-type": "application/json",
    "indeed-api-key": "161092c2017b5bbab13edb12461a62d5a833871e7cad6d9d475304573de67ac8",
    "accept": "application/json",
    "indeed-locale": "en-US",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 193.1",
    "indeed-app-info": "appv=193.1; appid=com.indeed.jobsearch; osv=16.6.1; os=ios; dtype=phone",
}

# Common attribute keys for job types and remote status
JOB_TYPE_KEYS = ["employment_type", "job_type"]
REMOTE_KEYS = ["remote", "work_from_home"] 