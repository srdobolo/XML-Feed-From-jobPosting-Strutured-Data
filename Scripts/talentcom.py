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

def talentcom():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'
    session = create_resilient_session()

    # Employment type mapping
    employment_type_map = {
        'FULL_TIME': 'Full time',
        'PART_TIME': 'Part time',
        'CONTRACTOR': 'Contract',
        'TEMPORARY': 'Temporary',
        'INTERN': 'Internship',
        'VOLUNTEER': 'Volunteer',
        'PER_DIEM': 'Alternance',
        'OTHER': 'Other'
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
    rss_feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<source>
    <publisher>Recruityard</publisher>
    <publisherurl>https://www.recruityard.com</publisherurl>
    <lastBuildDate>{datetime.datetime.now().isoformat()}</lastBuildDate>'''

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

                    # Extract salary value
                    salary_value = data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')
                    min_salary = 'undisclosed'
                    max_salary = 'undisclosed'

                    # Process salary if it's a string
                    if isinstance(salary_value, str):
                        # Handle range format like "1050 - 1300"
                        if '-' in salary_value:
                            salary_parts = [part.strip() for part in salary_value.split('-')]
                            if len(salary_parts) == 2:
                                # Check if both parts are valid numbers
                                if (salary_parts[0].replace('.', '').isdigit() and 
                                    salary_parts[1].replace('.', '').isdigit()):
                                    min_salary = salary_parts[0]
                                    max_salary = salary_parts[1]
                        # Handle single value
                        elif salary_value.replace('.', '').isdigit():
                            min_salary = salary_value
                            max_salary = salary_value
                    elif isinstance(salary_value, (int, float)):
                        # Handle numeric values
                        min_salary = str(salary_value)
                        max_salary = str(salary_value)

                    # Map employment type
                    raw_employment_type = data.get('employmentType', 'undisclosed')
                    # If employmentType is a list, take the first value; otherwise, use as-is
                    if isinstance(raw_employment_type, list):
                        raw_employment_type = raw_employment_type[0] if raw_employment_type else 'undisclosed'
                    employment_type = employment_type_map.get(raw_employment_type, 'Other') if raw_employment_type != 'undisclosed' else 'undisclosed'

                    rss_feed += f'''
            <job>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <company><![CDATA[{data.get('hiringOrganization', {}).get('name', 'undisclosed')}]]></company>
              <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <dateposted><![CDATA[{data.get('datePosted', 'undisclosed')}]]></dateposted>
              <expirationdate><![CDATA[{data.get('validThrough', 'undisclosed')}]]></expirationdate>
              <referencenumber><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></referencenumber>
              <url><![CDATA[{job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}&utm_source=TALENT_COM]]></url>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <salary>
                <salary_max><![CDATA[{max_salary}]]></salary_max>
                <salary_min><![CDATA[{min_salary}]]></salary_min>
                <salary_currency><![CDATA[{data.get('baseSalary', {}).get('currency', 'undisclosed')}]]></salary_currency>
                <period><![CDATA[month]]></period>
                <type><![CDATA[BASE_SALARY]]></type>
              </salary>
              <jobtype><![CDATA[{employment_type}]]></jobtype>
              <isremote><![CDATA[{'yes' if data.get('jobLocationType') == 'TELECOMMUTE' else 'no'}]]></isremote>                            
              <category><![CDATA[{data.get('industry', 'undisclosed')}]]></category>
              <logo><![CDATA[https://framerusercontent.com/images/FiQxGZ2DDim6z4ENGAhbwOTU8E.png?scale-down-to=60]]></logo>
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
</source>'''

    # Save the feed to a file
    try:
        with open('talentcom.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated talentcom.xml: %d jobs processed successfully, %d failed", success_count, failure_count)
    except IOError as e:
        logging.error("Failed to write talentcom.xml: %s", e)

if __name__ == "__main__":
    talentcom()