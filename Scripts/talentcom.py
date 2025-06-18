import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import datetime
from Utils.job_fetcher import fetch_all_jobs


def talentcom(job_data_list):

    # Employment type mapping
    employment_type_map = {
        'FULL_TIME': 'Full time',
        'PART_TIME': 'Part time',
        'CONTRACTOR': 'Contract',
        'TEMPORARY': 'Temporary',
        'INTERN': 'Internship',
        'VOLUNTEER': 'Volunteer',
        'PER_DIEM': 'Alternance',
        'OTHER': 'Other'
    }

    # Prepare the base of the RSS feed
    rss_feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<source>
    <publisher>Recruityard</publisher>
    <publisherurl>https://www.recruityard.com</publisherurl>
    <lastBuildDate>{datetime.datetime.now().isoformat()}</lastBuildDate>'''

    # Iterate over each job link, fetch its content, and extract the JSON
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
        employment_type = employment_type_map.get(raw_employment_type, 'Other') if raw_employment_type != 'undisclosed' else 'undisclosed'

        rss_feed += f'''
            <job>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <company><![CDATA[{data.get('hiringOrganization', {}).get('name', 'undisclosed')}]]></company>
              <city><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <state><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></state>
              <country><![CDATA[{data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'undisclosed')}]]></country>
              <dateposted><![CDATA[{data.get('datePosted', 'undisclosed')}]]></dateposted>
              <expirationdate><![CDATA[{data.get('validThrough', 'undisclosed')}]]></expirationdate>
              <referencenumber><![CDATA[{data.get('identifier', {}).get('value', 'undisclosed')}]]></referencenumber>
              <url><![CDATA[{job_url}]]></url>
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
              <salary>
                <salary_max><![CDATA[{max_salary}]]></salary_max>
                <salary_min><![CDATA[{min_salary}]]></salary_min>
                <salary_currency><![CDATA[{data.get('baseSalary', {}).get('currency', 'undisclosed')}]]></salary_currency>
                <period><![CDATA[month]]></period>
                <type><![CDATA[BASE_SALARY]]></type>
              </salary>
              <jobtype><![CDATA[{employment_type}]]></jobtype>
              <isremote><![CDATA[{'yes' if data.get('jobLocationType') == 'TELECOMMUTE' else 'no'}]]></isremote>                            
              <category><![CDATA[{data.get('industry', 'undisclosed')}]]></category>
              <logo><![CDATA[https://framerusercontent.com/images/FiQxGZ2DDim6z4ENGAhbwOTU8E.png?scale-down-to=60]]></logo>
            </job>'''

    # Close the RSS feed
    rss_feed += '''
</source>'''

    # Save the feed to a file
    try:
        with open('talentcom.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated talentcom.xml")
    except IOError as e:
        logging.error("Failed to write talentcom.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    talentcom(job_data_list)