import xml.etree.ElementTree as ET

# Path to your XML file
xml_file_path = 'path/to/feed.xml'

# Load the XML file
tree = ET.parse(xml_file_path)
root = tree.getroot()

# Example modification: changing the text of an XML element
for job in root.findall('job'):
    title = job.find('title')
    if title is not None:
        title.text = 'Updated Job Title'

# Save the updated XML file
tree.write(xml_file_path)
