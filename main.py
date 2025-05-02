import csv
from jobspy import scrape_jobs
from swiftshadow import QuickProxy
from swiftshadow.classes import Proxy


swift = Proxy(protocol='https',autoRotate=True)
swift.update()
sites=["indeed"]

jobs = scrape_jobs(
    site_name=["indeed"],
    search_term="project manager",
    location="Dallas, TX",
    results_wanted=1000,
    hours_old=72,
    country_indeed='USA',
    proxies=[swift.proxy()[0], "localhost"],
)


print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel
