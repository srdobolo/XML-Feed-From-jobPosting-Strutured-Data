import requests
from bs4 import BeautifulSoup
import json
import html
import os

def generate_feed3():
    # Base URL for the find-jobs section
    base_url = 'https://recruityard.com/find-jobs-all/'

    # Load the main jobs page to find all job links
    response = requests.get(base_url)
    html_content = response.content

    # Parse the HTML with BeautifulSoup to find all job links
    soup = BeautifulSoup(html_content, 'html.parser')
    job_links = list(set([a['href'] for a in soup.find_all('a', href=True) if '/find-jobs-all/' in a['href']]))

    # Prepare the base of the RSS feed
    rss_feed = '''
    <rss>
        <channel>
            <title>Recruityard</title>
            <link>https://www.recruityard.com</link>
            <description>Recruityard - Current Job Openings</description>'''

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
            <item>
              <title><![CDATA[{data.get('title', 'undisclosed')}]]></title>
              <link><![CDATA[{job_url}]]></link>  
              <description><![CDATA[{data.get('description', 'undisclosed')}]]></description>
            </item>'''

            except json.JSONDecodeError:
                print(f"Error decoding JSON from {job_url}")

    # Close the RSS feed
    rss_feed += '''
    </channel>
</rss>
'''

    # Save to folder
    folder_path = "job_feeds" 
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, 'rss.xml')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(rss_feed)
    print(f"Generated {file_path}")

if __name__ == "__main__":
    generate_feed3()