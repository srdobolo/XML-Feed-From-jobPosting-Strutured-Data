import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
import logging
from Utils.job_fetcher import fetch_all_jobs



def jora(job_data_list):
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
    rss_feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<source>
    <publisher>Recruityard</publisher>
    <lastBuildDate>{datetime.datetime.now().isoformat()}</lastBuildDate>'''


    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
        logging.info("Fetching job URL: %s", job_url)

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
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <id><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></id>
              <listed_date><![CDATA[{data.get('datePosted', 'undisclosed')}]]></listed_date>
              <closing_date><![CDATA[{data.get('validThrough', 'undisclosed')}]]></closing_date>
              <location><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></location>
              <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <postalcode>{data.get('jobLocation', {}).get('address', {}).get('postalCode', 'undisclosed')}</postalcode>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <salary>
                <type>Monthly</type>
                <min>{min_salary}</min>
                <max>{max_salary}</max>
                <currency>{data.get('baseSalary', {}).get('currency', 'undisclosed')}</currency>
              </salary>
              <jobtype><![CDATA[{employment_type}]]></jobtype>
              <url><![CDATA[{job_url}]]></url>
            </job>'''

    # Close the RSS feed
    rss_feed += '''
</source>'''

    # Save the feed to a file
    try:
        with open('jora.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jora.xml")
    except IOError as e:
        logging.error("Failed to write jora.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    jora(job_data_list)