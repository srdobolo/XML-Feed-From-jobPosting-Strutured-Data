import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import html
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Shared session setup
def create_resilient_session():
    session = requests.Session()
    retries = Retry(
        total=3,  # Retry 3 times
        backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504],  # Retry on server errors
        allowed_methods=["GET"]
    )
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

def jobatus(session=None):
    if session is None:
        session = create_resilient_session()

    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'

    # Load the main jobs page to find all job links
    try:
        html_content = fetch_url(session, base_url)
    except requests.exceptions.RequestException:
        logging.error("Failed to load base URL, aborting jobatus feed generation.")
        return  # Exit early if the base page can’t be loaded

    # Parse the HTML with BeautifulSoup to find all job links
    soup = BeautifulSoup(html_content, 'html.parser')
    job_links = list(set([a['href'] for a in soup.find_all('a', href=True) 
                          if '/find-jobs-all/' in a['href'] and a['href'].endswith('pt')]))

    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<jobatus>'''

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
            <ad>
              <url><![CDATA[{job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}]]></url>  
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <content><![CDATA[{data.get('description', 'undisclosed')}]]></content>
              <company><![CDATA[Recruityard]]></company>
              <contract><![CDATA[{data.get('employmentType', 'undisclosed')}]]></contract>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <region><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></region>
            </ad>'''
                except json.JSONDecodeError:
                    logging.error("Error decoding JSON from %s", job_url)
        except requests.exceptions.RequestException:
            logging.warning("Skipping job link %s due to fetch error", job_url)
            continue  # Skip this job link and move to the next one

    # Close the RSS feed
    rss_feed += '''
</jobatus>'''

    # Save the feed to a file
    try:
        with open('jobatus.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jobatus.xml")
    except IOError as e:
        logging.error("Failed to write jobatus.xml: %s", e)

if __name__ == "__main__":
    jobatus()