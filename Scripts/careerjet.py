import requests
from bs4 import BeautifulSoup
import json
import html

def careerjet():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'

    # Load the main jobs page to find all job links
    response = requests.get(base_url)
    html_content = response.content

    # Parse the HTML with BeautifulSoup to find all job links
    soup = BeautifulSoup(html_content, 'html.parser')
    job_links = list(set([a['href'] for a in soup.find_all('a', href=True) if '/find-jobs-all/' in a['href']]))

    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8" ?>
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
            <job> 
              <id><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></id>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <url><![CDATA[{job_url}]]></url>
              <location>
                <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
                <region><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></region>
                <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              </location>  
              <company><![CDATA[Recruityard]]></company>
              <company_url><![CDATA[https://www.recruityard.com]]></company_url>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <contract_type><![CDATA[permanent]]></contract_type>
              <working_hours><![CDATA[{data.get('employmentType', 'undisclosed')}]]></working_hours>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <application_email><![CDATA[info@recruityard.com]]></application_email>
              <apply_url><![CDATA[{job_url}]]></apply_url>
            </job>'''
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {job_url}")

    # Close the RSS feed
    rss_feed += '''
</jobs>'''

    # Save the feed to a file
    with open('careerjet.xml', 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    print("Generated careerjet.xml")

if __name__ == "__main__":
    careerjet()