# tests/test_settings.py

from config.settings import settings

def test_proxy_settings():
    assert settings.proxy.api_url == "https://api.proxy-cheap.com/proxies"
    assert settings.proxy.api_key 
    assert settings.proxy.api_secret 

def test_scraper_settings():
    assert settings.scraper.request_timeout == 30
    assert settings.scraper.max_retries == 3
    assert isinstance(settings.scraper.user_agent, str)
    assert settings.scraper.delay_between_requests == 2.0

def test_storage_settings():
    assert settings.storage.output_format == "csv"
    assert settings.storage.output_directory == "data"
    assert settings.storage.filename_prefix == "jobs_"