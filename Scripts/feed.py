import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from Utils.job_fetcher import fetch_all_jobs


def feed(job_data_list):
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<source>
    <publisher>Recruityard</publisher>
    <publisherurl>https://www.recruityard.com</publisherurl>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
        rss_feed += f'''
            <job>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <date><![CDATA[{data.get('datePosted', 'undisclosed')}]]></date>
              <referencenumber><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></referencenumber>
              <url><![CDATA[{job_url}]]></url>
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
    job_data_list = fetch_all_jobs()
    feed(job_data_list)