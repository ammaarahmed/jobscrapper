import os
from dotenv import load_dotenv
from core.data_model import SearchParams, ScrapingMethod
from scrapers.indeed import IndeedScraper
from core.storage import Storage

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize storage
    storage = Storage()
    
    # Example search parameters
    params = SearchParams(
        query="Python Developer",
        location="San Francisco, CA",
        job_type="Full-time",
        is_remote=True,
        date_posted="last_week",
        experience_level="mid_level",
        salary_range="100000-150000",
        limit=50
    )
    
    # Try API method first
    try:
        api_scraper = IndeedScraper(
            scraping_method=ScrapingMethod.API,
            api_key=os.getenv("INDEED_API_KEY")
        )
        
        print("Searching jobs using API...")
        result = api_scraper.search_jobs(params)
        print(f"Found {len(result.jobs)} jobs")
        
        # Save results
        storage.save(result.jobs, format="csv")
        storage.save(result.jobs, format="json")
        
    except Exception as e:
        print(f"API method failed: {str(e)}")
        print("Falling back to browser method...")
        
        # Try browser method
        try:
            browser_scraper = IndeedScraper(
                scraping_method=ScrapingMethod.HEADLESS,
                headless=True
            )
            
            print("Searching jobs using headless browser...")
            result = browser_scraper.search_jobs(params)
            print(f"Found {len(result.jobs)} jobs")
            
            # Save results
            storage.save(result.jobs, format="csv")
            storage.save(result.jobs, format="json")
            
        except Exception as e:
            print(f"Headless browser method failed: {str(e)}")
            print("Falling back to non-headless browser...")
            
            # Try non-headless method
            try:
                non_headless_scraper = IndeedScraper(
                    scraping_method=ScrapingMethod.NON_HEADLESS,
                    headless=False
                )
                
                print("Searching jobs using non-headless browser...")
                result = non_headless_scraper.search_jobs(params)
                print(f"Found {len(result.jobs)} jobs")
                
                # Save results
                storage.save(result.jobs, format="csv")
                storage.save(result.jobs, format="json")
                
            except Exception as e:
                print(f"Non-headless browser method failed: {str(e)}")
                print("All methods failed. Please check your configuration and try again.")

if __name__ == "__main__":
    main() 