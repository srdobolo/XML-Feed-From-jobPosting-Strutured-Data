import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import html
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_resilient_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 104])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_url(session, url, timeout=10):
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        logging.info("Successfully fetched %s", url)
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error("Failed to fetch %s: %s", url, e)
        raise

def feed():
    base_url = 'https://recruityard.com/find-jobs-all/'
    session = create_resilient_session()

    # Load the main jobs page to find all job links
    try:
        html_content = fetch_url(session, base_url)
    except Exception as e:
        logging.error("Aborting feed generation due to initial fetch failure: %s", e)
        return

    # Parse the HTML with BeautifulSoup to find all job links
    soup = BeautifulSoup(html_content, 'html.parser')
    job_links = list(set([a['href'] for a in soup.find_all('a', href=True) if '/find-jobs-all/' in a['href']]))
    logging.info("Found %d unique job links", len(job_links))

    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<source>
    <publisher>Recruityard</publisher>
    <publisherurl>https://www.recruityard.com</publisherurl>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    for job_link in job_links:
        job_url = base_url + job_link.split('/')[-1]
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
              <date><![CDATA[{data.get('datePosted', 'undisclosed')}]]></date>
              <referencenumber><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></referencenumber>
              <url><![CDATA[{job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}]]></url>
              <company><![CDATA[{data.get('hiringOrganization', {}).get('name', 'undisclosed')}]]></company>
              <location><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></location>
              <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <remote><![CDATA[ {'yes' if data.get('jobLocationType') == 'TELECOMMUTE' else 'no'} ]]></remote>
              <postalcode><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('postalCode', 'undisclosed')}]]></postalcode>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <jobtype><![CDATA[{data.get('employmentType', 'undisclosed')}]]></jobtype>
              <category><![CDATA[{data.get('industry', {}).get('value', 'undisclosed')}]]></category>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <email><![CDATA[info@recruityard.com]]></email>
            </job>'''
                except json.JSONDecodeError as e:
                    logging.warning("Error decoding JSON from %s: %s", job_url, e)
        except Exception as e:
            logging.warning("Skipping job %s due to fetch error: %s", job_url, e)
            continue

    # Close the RSS feed
    rss_feed += '''
</source>'''

    # Save the feed to a file
    try:
        with open('feed.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated feed.xml")
    except Exception as e:
        logging.error("Failed to write feed.xml: %s", e)

if __name__ == "__main__":
    feed()