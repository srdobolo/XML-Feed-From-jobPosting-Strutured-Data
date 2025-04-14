import datetime
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

def jooble():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'
    session = create_resilient_session()

    # Employment type mapping
    employment_type_map = {
        'FULL_TIME': 'Full time',
        'PART_TIME': 'Part time',
        'CONTRACTOR': 'Contract',
        'TEMPORARY': 'Casual/Temporary',
        'INTERN': 'Internship',
        'VOLUNTEER': 'Volunteer',
        'PER_DIEM': 'Working Holiday',
        'OTHER': 'Freelance'
    }

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

                    # Map employment type
                    raw_employment_type = data.get('employmentType', 'undisclosed')
                    # If employmentType is a list, take the first value; otherwise, use as-is
                    if isinstance(raw_employment_type, list):
                        raw_employment_type = raw_employment_type[0] if raw_employment_type else 'undisclosed'
                    employment_type = employment_type_map.get(raw_employment_type, 'Freelance') if raw_employment_type != 'undisclosed' else 'undisclosed'

                    rss_feed += f'''
            <job id="{data.get('identifier', {}).get('value', 'undisclosed')}">
              <link><![CDATA[{job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}]]></link>  
              <name><![CDATA[{data.get('title', 'undisclosed')}]]></name>
              <region><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></region>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <company><![CDATA[Recruityard]]></company>
              <company_logo><![CDATA[https://framerusercontent.com/images/FiQxGZ2DDim6z4ENGAhbwOTU8E.png?scale-down-to=15]]></company_logo>
              <pubdate>{data.get('datePosted', 'undisclosed')}</pubdate>
              <updated>{datetime.datetime.now().isoformat()}</updated>
              <expire>{data.get('validThrough', 'undisclosed')}</expire>
              <jobtype>{employment_type}</jobtype>
              <email><![CDATA[info@recruityard.com]]></email>        
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
</jobs>'''

    # Save the feed to a file
    try:
        with open('jooble.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jooble.xml: %d jobs processed successfully, %d failed", success_count, failure_count)
    except IOError as e:
        logging.error("Failed to write jooble.xml: %s", e)

if __name__ == "__main__":
    jooble()