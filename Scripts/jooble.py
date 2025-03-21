import requests
from bs4 import BeautifulSoup
import json
import html
import datetime

def jooble():
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
              <link><![CDATA[{job_url}]]></link>  
              <name><![CDATA[{data.get('title', 'undisclosed')}]]></name>
              <region><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></region>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <company><![CDATA[Recruityard]]></company>
              <company_logo><![CDATA[                                     ]]></company_logo>
              <pubdate><![CDATA[{data.get('datePosted', 'undisclosed')}]]></pubdate>
              <updated><![CDATA[{datetime.datetime.now()}]]></updated>
              <expire><![CDATA[{data.get('validThrough', 'undisclosed')}]]></expire>
              <jobtype><![CDATA[{data.get('employmentType', 'undisclosed')}]]></jobtype>
              <email><![CDATA[info@recruityard.com]]></email>        
            </job>'''
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {job_url}")

    # Close the RSS feed
    rss_feed += '''
</jobs>'''

    # Save the feed to a file
    with open('jooble.xml', 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    print("Generated jooble.xml")

if __name__ == "__main__":
    jooble()