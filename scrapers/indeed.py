from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from scrapers.base import BaseScraper
from core.data_model import Job, SearchParams, SearchResult, Company
from core.queries import JOB_SEARCH, API_HEADERS, JOB_TYPE_KEYS, REMOTE_KEYS

class IndeedScraper(BaseScraper):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://www.indeed.com"
        self.search_url = f"{self.base_url}/jobs"
        self.api_url = "https://apis.indeed.com/graphql"

    def search_jobs(self, params: SearchParams) -> SearchResult:
        """Search for jobs using the configured scraping method"""
        if self.scraping_method == "api":
            return self._search_jobs_api(params)
        else:
            return self._search_jobs_browser(params)

    def _search_jobs_api(self, params: SearchParams) -> SearchResult:
        """Search jobs using Indeed's GraphQL API"""
        try:
            # Prepare GraphQL variables
            variables = {
                "what": params.what,
                "location": params.location,
                "cursor": params.cursor,
                "filters": params.filters
            }

            # Make GraphQL request
            response = self._make_request(
                self.api_url,
                method="POST",
                headers=API_HEADERS,
                json={
                    "query": JOB_SEARCH,
                    "variables": variables
                }
            )
            
            data = response.json()
            return self._parse_api_response(data)
            
        except Exception as e:
            self.logger.error(f"API search failed: {str(e)}")
            raise

    def _parse_api_response(self, data: Dict[str, Any]) -> SearchResult:
        """Parse GraphQL API response into SearchResult"""
        jobs = []
        job_search = data.get("data", {}).get("jobSearch", {})
        
        for result in job_search.get("results", []):
            try:
                job_data = result.get("job", {})
                
                # Parse employer/company data
                employer_data = job_data.get("employer", {})
                dossier = employer_data.get("dossier", {})
                employer_details = dossier.get("employerDetails", {})
                links = dossier.get("links", {})
                
                company = Company(
                    name=employer_data.get("name", ""),
                    website=links.get("corporateWebsite"),
                    location=employer_details.get("addresses", [None])[0],
                    contact_email=None,  # Not available in API
                    contact_phone=None   # Not available in API
                )
                
                # Parse job attributes
                attributes = job_data.get("attributes", [])
                is_remote = self._check_remote_status(attributes)
                job_type = self._determine_job_type(attributes)
                
                # Parse compensation
                compensation = self._parse_compensation(job_data.get("compensation", {}))
                
                # Create job object
                job = Job(
                    title=job_data.get("title", ""),
                    company=company,
                    location=job_data.get("location", {}).get("formatted", {}).get("short", ""),
                    is_remote=is_remote,
                    job_type=job_type,
                    compensation=compensation,
                    date_posted=datetime.fromisoformat(job_data.get("datePublished", "")),
                    description=job_data.get("description", {}).get("html", ""),
                    application_url=job_data.get("recruit", {}).get("viewJobUrl", ""),
                    source_url=job_data.get("recruit", {}).get("viewJobUrl", "")
                )
                
                jobs.append(job)
                
            except Exception as e:
                self.logger.error(f"Error parsing job data: {str(e)}")
                continue
        
        return SearchResult(
            jobs=jobs,
            next_cursor=job_search.get("pageInfo", {}).get("nextCursor")
        )

    def _check_remote_status(self, attributes: List[Dict[str, str]]) -> bool:
        """Check if job is remote based on attributes"""
        for attr in attributes:
            if attr.get("key", "").lower() in REMOTE_KEYS:
                return True
        return False

    def _determine_job_type(self, attributes: List[Dict[str, str]]) -> str:
        """Determine job type from attributes"""
        for attr in attributes:
            if attr.get("key", "").lower() in JOB_TYPE_KEYS:
                return attr.get("label", "Unknown")
        return "Unknown"

    def _parse_compensation(self, compensation_data: Dict[str, Any]) -> Optional[str]:
        """Parse compensation data into a readable string"""
        try:
            estimated = compensation_data.get("estimated", {})
            base_salary = estimated.get("baseSalary", {})
            salary_range = base_salary.get("range", {})
            
            min_salary = salary_range.get("min")
            max_salary = salary_range.get("max")
            
            if min_salary and max_salary:
                return f"${min_salary:,.2f} - ${max_salary:,.2f}"
            elif min_salary:
                return f"From ${min_salary:,.2f}"
            elif max_salary:
                return f"Up to ${max_salary:,.2f}"
            
            return None
            
        except Exception:
            return None

    def _search_jobs_browser(self, params: SearchParams) -> SearchResult:
        """Search jobs using browser automation"""
        try:
            # Construct search URL
            search_url = self._build_search_url(params)
            self.driver.get(search_url)
            
            # Wait for job cards to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
            )
            
            # Get all job cards
            job_cards = self.driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
            jobs = []
            
            for card in job_cards[:100]:  # Limit to 100 results
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.error(f"Failed to parse job card: {str(e)}")
                    continue
            
            return SearchResult(
                jobs=jobs,
                next_cursor=None  # Browser scraping doesn't support pagination
            )
            
        except TimeoutException:
            self.logger.error("Timeout waiting for job cards to load")
            raise
        except Exception as e:
            self.logger.error(f"Browser search failed: {str(e)}")
            raise

    def _parse_job_card(self, card) -> Optional[Job]:
        """Parse a job card element into a Job object"""
        try:
            # Extract basic information
            title = card.find_element(By.CLASS_NAME, "jobTitle").text
            company_name = card.find_element(By.CLASS_NAME, "companyName").text
            
            # Get company details
            company = Company(
                name=company_name,
                website=None,  # Would need to visit company page
                location=None,  # Would need to visit company page
                contact_email=None,
                contact_phone=None
            )
            
            # Get location
            location = card.find_element(By.CLASS_NAME, "companyLocation").text
            
            # Get job type and remote status
            metadata = card.find_element(By.CLASS_NAME, "metadata").text.lower()
            is_remote = "remote" in metadata
            job_type = self._extract_job_type_from_metadata(metadata)
            
            # Get salary if available
            compensation = None
            try:
                salary_elem = card.find_element(By.CLASS_NAME, "salary-snippet")
                compensation = salary_elem.text
            except NoSuchElementException:
                pass
            
            # Get job link
            link_elem = card.find_element(By.CLASS_NAME, "jcs-JobTitle")
            job_url = link_elem.get_attribute("href")
            
            return Job(
                title=title,
                company=company,
                location=location,
                is_remote=is_remote,
                job_type=job_type,
                compensation=compensation,
                date_posted=datetime.now(),  # Would need to parse from job page
                description="",  # Would need to visit job page
                application_url=job_url,
                source_url=job_url
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing job card: {str(e)}")
            return None

    def _extract_job_type_from_metadata(self, metadata: str) -> str:
        """Extract job type from metadata text"""
        if "full-time" in metadata:
            return "Full-time"
        elif "part-time" in metadata:
            return "Part-time"
        elif "contract" in metadata:
            return "Contract"
        elif "temporary" in metadata:
            return "Temporary"
        elif "internship" in metadata:
            return "Internship"
        return "Unknown"

    def _build_search_url(self, params: SearchParams) -> str:
        """Build Indeed search URL with parameters"""
        url_parts = [self.search_url]
        
        # Add query parameters
        url_parts.append(f"q={params.what}")
        url_parts.append(f"l={params.location}")
        
        if params.filters:
            if params.filters.get("job_type"):
                url_parts.append(f"jt={params.filters['job_type']}")
            if params.filters.get("is_remote"):
                url_parts.append("sc=0kf%3Aattr(FSFW)%3B")
            
        return "&".join(url_parts)
