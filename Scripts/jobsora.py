import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import html
import logging

# Shared session setup (could be moved to a utils module)
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

def jobsora():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'

    # Load the main jobs page to find all job links
    response = requests.get(base_url)
    html_content = response.content

    # Parse the HTML with BeautifulSoup to find all job links
    soup = BeautifulSoup(html_content, 'html.parser')
    job_links = list(set([a['href'] for a in soup.find_all('a', href=True) if '/find-jobs-all/' in a['href']]))

    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<jobs>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    for job_link in job_links:
        job_url = base_url + job_link.split('/')[-1]
        response = requests.get(job_url)
        job_html_content = response.content

        job_soup = BeautifulSoup(job_html_content, 'html.parser')
        script_tag = job_soup.find('script', type='application/ld+json')

        if script_tag and script_tag.string:
            json_content = html.unescape(script_tag.string)
            try:
                data = json.loads(json_content)
                rss_feed += f'''
            <job id="{data.get('identifier', {}).get('value', 'undisclosed')}">
              <link><![CDATA[{job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}]]></link>  
              <name><![CDATA[{data.get('title', 'undisclosed')}]]></name>
              <region><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></region>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <apply_url><![CDATA[{job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}]]></apply_url>
              <email><![CDATA[info@recruityard.com]]></email>
              <phone><![CDATA[]]></phone>
              <company><![CDATA[Recruityard]]></company>
              <pubdate>{data.get('datePosted', 'undisclosed')}</pubdate>
              <updated>{data.get('dateModified', 'undisclosed')}</updated>
              <expire>{data.get('validThrough', 'undisclosed')}</expire>
              <jobtype><![CDATA[{data.get('employmentType', 'undisclosed')}]]></jobtype>
            </job>'''
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {job_url}")

    # Close the RSS feed
    rss_feed += '''
</jobs>'''

    # Save the feed to a file
    with open('jobsora.xml', 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    print("Generated jobsora.xml")

if __name__ == "__main__":
    jobsora()