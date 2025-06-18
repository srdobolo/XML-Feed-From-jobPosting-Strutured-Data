import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
import logging
from Utils.job_fetcher import fetch_all_jobs



def jooble(job_data_list):

    # Employment type mapping
    employment_type_map = {
        'FULL_TIME': 'Full time',
        'PART_TIME': 'Part time',
        'CONTRACTOR': 'Contract',
        'TEMPORARY': 'Casual/Temporary',
        'INTERN': 'Internship',
        'VOLUNTEER': 'Volunteer',
        'PER_DIEM': 'Working Holiday',
        'OTHER': 'Freelance'
    }

    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<jobs>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
        logging.info("Fetching job URL: %s", job_url)

        # Map employment type
        raw_employment_type = data.get('employmentType', 'undisclosed')
            
        # If employmentType is a list, take the first value; otherwise, use as-is
        if isinstance(raw_employment_type, list):
            raw_employment_type = raw_employment_type[0] if raw_employment_type else 'undisclosed'
        employment_type = employment_type_map.get(raw_employment_type, 'Freelance') if raw_employment_type != 'undisclosed' else 'undisclosed'

        rss_feed += f'''
        <job id="{data.get('identifier', {}).get('value', 'undisclosed')}">
            <link><![CDATA[{job_url}]]></link>  
            <name><![CDATA[{data.get('title', 'undisclosed')}]]></name>
            <region><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></region>
            <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
            <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
            <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
            <company><![CDATA[Recruityard]]></company>
            <company_logo><![CDATA[https://framerusercontent.com/images/FiQxGZ2DDim6z4ENGAhbwOTU8E.png?scale-down-to=15]]></company_logo>
            <pubdate>{data.get('datePosted', 'undisclosed')}</pubdate>
            <updated>{datetime.datetime.now().isoformat()}</updated>
            <expire>{data.get('validThrough', 'undisclosed')}</expire>
            <jobtype>{employment_type}</jobtype>
            <email><![CDATA[info@recruityard.com]]></email>        
        </job>'''

    # Close the RSS feed
    rss_feed += '''
</jobs>'''

    # Save the feed to a file
    try:
        with open('jooble.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jooble.xml")
    except IOError as e:
        logging.error("Failed to write jooble.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    jooble(job_data_list)