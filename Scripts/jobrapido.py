import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import html
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Shared session setup
def create_resilient_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        connect=3,  # Retry on connection errors
        read=3,    # Retry on read errors
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    return session

def fetch_url(session, url, timeout=15):
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        logging.info("Successfully fetched %s", url)
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error("Failed to fetch %s: %s", url, e)
        raise

def jobrapido():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'
    session = create_resilient_session()

    # Load the main jobs page to find all job links
    try:
        html_content = fetch_url(session, base_url)
    except requests.exceptions.RequestException as e:
        logging.error("Failed to load base URL %s: %s", base_url, e)
        return

    # Parse the HTML with BeautifulSoup to find all job links
    soup = BeautifulSoup(html_content, 'html.parser')
    job_links = list(set([a['href'] for a in soup.find_all('a', href=True) if '/find-jobs-all/' in a['href']]))
    logging.info("Found %d unique job links", len(job_links))

    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<source>
<jobs>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    success_count = 0
    failure_count = 0
    for job_link in job_links:
        job_url = base_url + job_link.split('/')[-1]
        logging.info("Fetching job URL: %s", job_url)
        try:
            job_html_content = fetch_url(session, job_url)
            job_soup = BeautifulSoup(job_html_content, 'html.parser')
            script_tag = job_soup.find('script', type='application/ld+json')

            if script_tag and script_tag.string:
                json_content = html.unescape(script_tag.string)
                try:
                    data = json.loads(json_content)
                    rss_feed += f'''
            <job>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <location><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></location>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <postalcode><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('postalCode', 'undisclosed')}]]></postalcode>
              <company><![CDATA[Recruityard]]></company>
              <website><![CDATA[https://www.recruityard.com]]></website>
              <publishdate><![CDATA[{data.get('datePosted', 'undisclosed')}]]></publishdate>
              <expirydate><![CDATA[{data.get('validThrough', 'undisclosed')}]]></expirydate>
              <url><![CDATA[{job_url}]]></url>
              <email><![CDATA[info@recruityard.com]]></email>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <reference_id><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></reference_id>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <jobtype><![CDATA[{data.get('employmentType', 'undisclosed')}]]></jobtype>     
            </job>'''
                    success_count += 1
                except json.JSONDecodeError as e:
                    logging.warning("Error decoding JSON from %s: %s", job_url, e)
                    failure_count += 1
            else:
                logging.warning("No JSON-LD script tag found in %s", job_url)
                failure_count += 1
        except requests.exceptions.RequestException as e:
            logging.warning("Skipping job %s due to fetch error: %s", job_url, e)
            failure_count += 1
            continue
        time.sleep(1)  # Delay to avoid rate-limiting

    # Close the RSS feed
    rss_feed += '''
</jobs>
</source>'''

    # Save the feed to a file
    try:
        with open('jobrapido.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jobrapido.xml: %d jobs processed successfully, %d failed", success_count, failure_count)
    except IOError as e:
        logging.error("Failed to write jobrapido.xml: %s", e)

if __name__ == "__main__":
    jobrapido()