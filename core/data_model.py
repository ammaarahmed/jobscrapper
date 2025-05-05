from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Company:
    name: str  # from employer.name
    website: Optional[str]  # from employer.dossier.links.corporateWebsite
    location: Optional[str]  # from employer.dossier.employerDetails.addresses
    contact_email: Optional[str]  # not in API, would need to be scraped
    contact_phone: Optional[str]  # not in API, would need to be scraped

@dataclass
class Job:
    title: str  # from job.title
    company: Company
    location: str  # from job.location.formatted.short
    is_remote: bool  # from job.attributes (check for remote attribute)
    job_type: str  # from job.attributes (check for employment type)
    compensation: Optional[str]  # from job.compensation.estimated.baseSalary.range
    date_posted: datetime  # from job.datePublished
    description: str  # from job.description.html
    application_url: str  # from job.recruit.viewJobUrl
    source_url: str  # from job.recruit.viewJobUrl

@dataclass
class SearchParams:
    what: str  # Job title/keywords
    location: str
    cursor: Optional[str] = None
    filters: Optional[dict] = None

@dataclass
class SearchResult:
    jobs: List[Job]
    next_cursor: Optional[str]

class ScrapingMethod:
    API = "api"
    HEADLESS = "headless"
    NON_HEADLESS = "non_headless"