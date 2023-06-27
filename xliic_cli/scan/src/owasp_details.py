from enum import Enum


class ApiConformanceScanOwaspIssues(Enum):
    DEFAULT = 0
    API1 = 1
    API2 = 2
    API3 = 3
    API4 = 4
    API5 = 5
    API6 = 6
    API7 = 7
    API8 = 8
    API9 = 9
    API10 = 10


class OwaspIssueDetail:
    def __init__(self, _id, short_name: str, version: str, long_name: str):
        self.id = _id
        self.short_name = short_name
        self.version = version
        self.long_name = long_name


owaspIssueDetails = [
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.DEFAULT,
        'None',
        '2019',
        'No OWASP issues found'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API1,
        'API1',
        '2019',
        'Broken Object Level Authorization'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API2,
        'API2',
        '2019',
        'Broken User Authentication'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API3,
        'API3',
        '2019',
        'Excessive Data Exposure'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API4,
        'API4',
        '2019',
        'Lack of Resources & Rate Limiting'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API5,
        'API5',
        '2019',
        'Broken Function Level Authorization'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API6,
        'API6',
        '2019',
        'Mass Assignment'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API7,
        'API7',
        '2019',
        'Security Misconfiguration'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API8,
        'API8',
        '2019',
        'Injection'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API9,
        'API9',
        '2019',
        'Improper Assets Management'
    ),
    OwaspIssueDetail(
        ApiConformanceScanOwaspIssues.API10,
        'API10',
        '2019',
        'Insufficient Logging & Monitoring'
    )
]


def get_owasp_issue_detail_by_id(_id: str):
    if _id:
        short_name, version = _id.split(":")
        for detail in owaspIssueDetails:
            if detail.short_name == short_name and detail.version == version:
                return detail
    return owaspIssueDetails[0]
