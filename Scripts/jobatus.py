import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from Utils.job_fetcher import fetch_all_jobs


def jobatus(job_data_list):
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
<jobatus>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
        rss_feed += f'''
            <ad>
              <url><![CDATA[{job_url}]]></url>  
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <content><![CDATA[{data.get('description', 'undisclosed')}]]></content>
              <company><![CDATA[Recruityard]]></company>
              <contract><![CDATA[{'Efetivo, tempo inteiro' 
                                  if data.get('employmentType', 'undisclosed') == 'FULL_TIME' else 'Efetivo, tempo parcial'
                                  if data.get('employmentType', 'undisclosed') == 'PART_TIME' 
                                  else data.get('employmentType', 'undisclosed')}]]></contract>
              <salary><![CDATA[{data.get('baseSalary', {}).get('value', {}).get('value', 'undisclosed')}]]></salary>
              <city><![CDATA[{'Lisboa' 
                              if data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed') == 'Lisbon' 
                              else data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'undisclosed')}]]></city>
              <region><![CDATA[{'Lisboa' 
                                if data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed') == 'Lisbon' 
                                else data.get('jobLocation', {}).get('address', {}).get('addressRegion', 'undisclosed')}]]></region>
            </ad>'''
                
    rss_feed += '''
</jobatus>'''

    # Save the feed to a file
    try:
        with open('jobatus.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated jobatus.xml")
    except IOError as e:
        logging.error("Failed to write jobatus.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    jobatus(job_data_list)