import urllib.request
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# The identifier of the Archive.org item
archive_id = "hillside-hermitage-audio-archive-2015-2023"

# FIX: Query the official Metadata API directly instead of the search engine
metadata_url = f"https://archive.org/metadata/{archive_id}"

try:
    with urllib.request.urlopen(metadata_url) as response:
        data = json.loads(response.read().decode())
        files = data.get('files', [])
except Exception as e:
    print(f"Error fetching archive data: {e}")
    files = []

# Build the RSS Feed Structure
rss = ET.Element("rss", version="2.0", **{"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"})
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = "Hillside Hermitage Audio Archive (2015-2023)"
ET.SubElement(channel, "link").text = f"https://archive.org/details/{archive_id}"
ET.SubElement(channel, "description").text = "Community streaming archive of older Hillside Hermitage Dhamma talks."
ET.SubElement(channel, "language").text = "en-us"

# FIX: This inserts the official cover art image tag properly into the feed header
ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image", href=f"https://archive.org/services/img/{archive_id}")
# Loop through all files and parse individual audio tracks
count = 0
for file in files:
    filename = file.get('name', '')
    # Check for raw audio formats
    if filename.endswith('.mp3') or filename.endswith('.m4a'):
        count += 1
        item = ET.SubElement(channel, "item")
        
        # Clean up filenames into scannable public titles
        clean_title = filename.replace('.mp3', '').replace('.m4a', '').replace('_', ' ').replace('-', ' ')
        ET.SubElement(item, "title").text = clean_title
        
        # Generate the direct, high-speed streaming audio link
        file_url = f"https://archive.org/download/{archive_id}/{filename}"
        ET.SubElement(item, "link").text = file_url
        
        # Enclosure node is what tells AntennaPod that this is a playable podcast track
        enclosure = ET.SubElement(item, "enclosure", url=file_url, type="audio/mpeg")
        if 'size' in file:
            enclosure.set('length', str(file['size']))
            
        ET.SubElement(item, "guid", isPermaLink="true").text = file_url

print(f"Detected and mapped {count} audio files!")

# Save the generated feed
tree = ET.ElementTree(rss)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
print("Podcast RSS feed generated successfully as feed.xml!")
