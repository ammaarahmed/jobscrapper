from scrapers.indeed import IndeedScraper
from core.storage import Storage

def main():
    scraper = IndeedScraper()
    jobs = scraper.search_jobs(query="python developer", location="remote")
    storage = Storage()
    storage.save(jobs)

if __name__ == "__main__":
    main()