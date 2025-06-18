import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from Utils.job_fetcher import fetch_all_jobs


def rss(job_data_list):
    # Prepare the base of the RSS feed
    rss_feed = '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>Recruityard</title>
        <link>https://www.recruityard.com</link>
        <description>Recruityard - Current Job Openings</description>'''

    # Iterate over each job link, fetch its content, and extract the JSON
    for data in job_data_list:
        job_url = data.get('url', 'undisclosed')
        logging.info("Fetching job URL: %s", job_url)

        rss_feed += f'''  
        <item>
            <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
            <link><![CDATA[{job_url}]]></link>  
            <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
        </item>'''

    # Close the RSS feed
    rss_feed += '''
    </channel>
</rss>'''

    # Save the feed to a file
    try:
        with open('rss.xml', 'w', encoding='utf-8') as f:
            f.write(rss_feed)
        logging.info("Generated rss.xml")
    except IOError as e:
        logging.error("Failed to write rss.xml: %s", e)

if __name__ == "__main__":
    job_data_list = fetch_all_jobs()
    rss(job_data_list)