import requests
from bs4 import BeautifulSoup
import json
import html

# Base URL for the find-jobs section
base_url = 'https://smart-recruitments.com/find-jobs-all/'

# Step 1: Load the main jobs page to find all job links
response = requests.get(base_url)
html_content = response.content

# Step 2: Parse the HTML with BeautifulSoup to find all job links
soup = BeautifulSoup(html_content, 'html.parser')

# Assuming job links are inside <a> tags with href pointing to the job details page
# Deduplicate links by converting to a set and back to a list
job_links = list(set([a['href'] for a in soup.find_all('a', href=True) if '/find-jobs-all/' in a['href']]))

# Prepare the base of the RSS feed
rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<source>
    <publisher>SmartRecruitments</publisher>
    <publisherurl>https://www.smart-recruitments.com</publisherurl>'''

# Step 3: Iterate over each job link, fetch its content, and extract the JSON
for job_link in job_links:
    # Full URL for each job link
    job_url = base_url + job_link.split('/')[-1]

    # Fetch the job details page
    response = requests.get(job_url)
    job_html_content = response.content

    # Parse the HTML with BeautifulSoup
    job_soup = BeautifulSoup(job_html_content, 'html.parser')

    # Locate the <script> tag containing the JSON
    script_tag = job_soup.find('script', type='application/ld+json')

    if script_tag and script_tag.string:
        json_content = script_tag.string

        try:
            # Unescape any HTML entities that may be in the JSON content
            json_content_unescaped = html.unescape(json_content)

            # Parse the JSON content
            data = json.loads(json_content_unescaped)

            # Extract fields and build the RSS feed item
            rss_feed += f'''
            <job>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <date><![CDATA[{data.get('datePosted', 'undisclosed')}]]></date>
              <referencenumber><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></referencenumber>
              <url><![CDATA[{job_url}]]></url>
              <company><![CDATA[{data.get('hiringOrganization', {}).get('name', 'undisclosed')}]]></company>
              <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <remote><![CDATA[{data.get('jobLocationType', 'WFO')}]]></remote>
              <postalcode><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('postalCode', 'undisclosed')}]]></postalcode>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <jobtype><![CDATA[{data.get('employmentType', 'undisclosed')}]]></jobtype>
              <category><![CDATA[{data.get('category', 'undisclosed')}]]></category>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <email><![CDATA[joao.lima@smart-recruitments.com]]></email>
            </job>'''

        except json.JSONDecodeError:
            print(f"Error decoding JSON from {job_url}")

# Close the RSS feed
rss_feed += '''
</source>'''

# Save the combined feed to a file with UTF-8 encoding
with open('feed.xml', 'w', encoding='utf-8') as f:
    f.write(rss_feed)

    print(rss_feed)
