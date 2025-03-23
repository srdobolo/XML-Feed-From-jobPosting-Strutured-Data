import requests
from bs4 import BeautifulSoup
import json
import html
import datetime

def jora():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'

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
    <lastBuildDate>{datetime.datetime.now}</lastBuildDate>'''

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
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <id><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></id>
              <listed_date><![CDATA[{data.get('datePosted', 'undisclosed')}]]></listed_date>
              <closing_date><![CDATA[{data.get('validThrough', 'undisclosed')}]]></closing_date>
              <location><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></location>
              <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <postalcode><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('postalCode', 'undisclosed')}]]></postalcode>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <salary>
                <type>Monthly</type>
                <min> XXX </min>                                                                                        #arranjasr isto
                <max> XXX </max>                                                                                        #arranjar isto    
                <currency><![CDATA[{data.get('baseSalary', {}).get('currency', 'undisclosed')}]]></currency>
              </salary>
              <jobtype><![CDATA[{data.get('employmentType', 'undisclosed')}]]></jobtype>                                #arranjar isto
              <url><![CDATA[{job_url}]]></url>
            </job>'''
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {job_url}")

    # Close the RSS feed
    rss_feed += '''
</source>'''

    # Save the feed to a file
    with open('jobisjob.xml', 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    print("Generated jobisjob.xml")

if __name__ == "__main__":
    jora()