import datetime
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

def talentcom():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'

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
    response = requests.get(base_url)
    html_content = response.content

    # Parse the HTML with BeautifulSoup to find all job links
    soup = BeautifulSoup(html_content, 'html.parser')
    job_links = list(set([a['href'] for a in soup.find_all('a', href=True) if '/find-jobs-all/' in a['href']]))

    # Prepare the base of the RSS feed
    rss_feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<source>
    <publisher>Recruityard</publisher>
    <publisherurl>https://www.recruityard.com</publisherurl>
    <lastBuildDate>{datetime.datetime.now()}</lastBuildDate>'''

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
                employment_type = employment_type_map.get(raw_employment_type, 'Freelance') if raw_employment_type != 'undisclosed' else 'undisclosed'

                rss_feed += f'''
            <job>
              <title><![CDATA[ {data.get('title', 'undisclosed')} ]]></title>
              <company><![CDATA[ {data.get('hiringOrganization', {}).get('name', 'undisclosed')} ]]></company>
              <city><![CDATA[ {data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')} ]]></city>
              <state><![CDATA[ {data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')} ]]></state>
              <country><![CDATA[ {data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')} ]]></country>
              <dateposted><![CDATA[ {data.get('datePosted', 'undisclosed')} ]]></dateposted>
              <expirationdate><![CDATA[ {data.get('validThrough', 'undisclosed')} ]]></expirationdate>
              <referencenumber><![CDATA[ {data.get('identifier', {}).get('value', 'undisclosed')} ]]></referencenumber>
              <url><![CDATA[ {job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}&utm_source=TALENT_COM ]]></url>
              <description><![CDATA[ {data.get('description', 'undisclosed')} ]]></description>
              <salary>
                <salary_max><![CDATA[{max_salary}]]></salary_max>
                <salary_min><![CDATA[{min_salary}]]></salary_min>
                <salary_currency><![CDATA[{data.get('baseSalary', {}).get('currency', 'undisclosed')}]]></salary_currency>
                <period><![CDATA[month]]></period>
                <type><![CDATA[BASE_SALARY]]></type>
              </salary>
              <jobtype><![CDATA[ {employment_type} ]]></jobtype>
              <isremote><![CDATA[ {'yes' if data.get('jobLocationType') == 'TELECOMMUTE' else 'no'} ]]></isremote>                            
              <category><![CDATA[ {data.get('industry', {}).get('value', 'undisclosed')} ]]></category>
              <logo><![CDATA[https://framerusercontent.com/images/FiQxGZ2DDim6z4ENGAhbwOTU8E.png?scale-down-to=60]]></logo>
            </job>'''
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {job_url}")

    # Close the RSS feed
    rss_feed += '''
</source>'''

    # Save the feed to a file
    with open('talentcom.xml', 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    print("Generated talentcom.xml")

if __name__ == "__main__":
    talentcom()