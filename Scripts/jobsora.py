import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from Utils.job_fetcher import fetch_all_jobs

def jobsora(job_data_list):
    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<jobs>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
        logging.info("Fetching job URL: %s", job_url)
        rss_feed += f'''
            <job id="{data.get('identifier', {}).get('value', 'undisclosed')}">
              <link><![CDATA[{job_url}]]></link>  
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
        
    # Close the RSS feed
    rss_feed += '''
</jobs>'''

    # Save the feed to a file
    try:
        with open('jobsora.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jobsora.xml")
    except IOError as e:
        logging.error("Failed to write jobsora.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    jobsora(job_data_list)