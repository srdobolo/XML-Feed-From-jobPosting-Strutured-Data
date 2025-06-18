import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from Utils.job_fetcher import fetch_all_jobs


def careerjet(job_data_list):
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<jobs>'''

    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
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
              <apply_url><![CDATA[{job_url}?id={data.get('identifier', {}).get('value', 'undisclosed')}&utm_source=CAREERJET]]></apply_url>
            </job>'''

    rss_feed += '''
</jobs>'''

    try:
        with open('careerjet.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated careerjet.xml")
    except IOError as e:
        logging.error("Failed to write careerjet.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    careerjet(job_data_list)