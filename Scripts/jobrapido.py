import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from Utils.job_fetcher import fetch_all_jobs

def jobrapido(job_data_list):
    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<source>
<jobs>'''

    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
        logging.info("Fetching job URL: %s", job_url)
        rss_feed += f'''
            <job>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <location><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></location>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <postalcode><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('postalCode', 'undisclosed')}]]></postalcode>
              <company><![CDATA[Recruityard]]></company>
              <website><![CDATA[https://www.recruityard.com]]></website>
              <publishdate><![CDATA[{data.get('datePosted', 'undisclosed')}]]></publishdate>
              <expirydate><![CDATA[{data.get('validThrough', 'undisclosed')}]]></expirydate>
              <url><![CDATA[{job_url}]]></url>
              <email><![CDATA[info@recruityard.com]]></email>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <reference_id><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></reference_id>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <jobtype><![CDATA[{data.get('employmentType', 'undisclosed')}]]></jobtype>     
            </job>'''
                
    rss_feed += '''
</jobs>
</source>'''

    # Save the feed to a file
    try:
        with open('jobrapido.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jobrapido.xml")
    except IOError as e:
        logging.error("Failed to write jobrapido.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    jobrapido(job_data_list)