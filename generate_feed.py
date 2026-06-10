import urllib.request
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# The identifier of the Archive.org item
archive_id = "hillside-hermitage-audio-archive-2015-2023"

# Metadata for your community podcast
rss_url = "https://archive.org/advancedsearch.php?q=identifier%3A" + archive_id + "&fl[]=files&output=json"

try:
    with urllib.request.urlopen(rss_url) as response:
        data = json.loads(response.read().decode())
        files = data['response']['docs'][0]['files']
except Exception as e:
    print(f"Error fetching archive data: {e}")
    files = []

# Build the RSS Feed Structure
rss = ET.Element("rss", version="2.0", xmlnsitunes="http://www.itunes.com/dtds/podcast-1.0.dtd")
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = "Hillside Hermitage Audio Archive (2015-2023)"
ET.SubElement(channel, "link").text = f"https://archive.org/details/{archive_id}"
ET.SubElement(channel, "description").text = "Community streaming archive of older Hillside Hermitage Dhamma talks."
ET.SubElement(channel, "language").text = "en-us"

# Loop through all 410 files and format them as individual podcast episodes
for file in files:
    if file['name'].endswith('.mp3') or file['name'].endswith('.m4a'):
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = file['name'].replace('.mp3', '').replace('.m4a', '').replace('_', ' ')
        
        # Point the play button directly to the Internet Archive download link
        file_url = f"https://archive.org/download/{archive_id}/{file['name']}"
        ET.SubElement(item, "link").text = file_url
        
        # Enclosure tag tells AntennaPod this is a playable streaming file
        enclosure = ET.SubElement(item, "enclosure", url=file_url, type="audio/mpeg")
        if 'size' in file:
            enclosure.set('length', str(file['size']))
            
        ET.SubElement(item, "guid", isPermaLink="true").text = file_url

# Save the generated feed
tree = ET.ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
print("Podcast RSS feed generated successfully as feed.xml!")
