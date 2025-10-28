import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

# --- Configuration ---
BASE_URL = "https://engineering.purdue.edu"
FACULTY_LIST_URL = "https://engineering.purdue.edu/ECE/People/Faculty"
LOG_FILE = "faculty_scraper.log"
# --- End Configuration ---

def log_message(message, log_mode):
    """Write a message to both console and log file"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    with open(LOG_FILE, log_mode, encoding='utf-8') as f:
        f.write(log_entry + "\n")

def scrape_faculty_directory():
    """
    Scrapes the Purdue ECE faculty directory to extract basic profile info.
    Returns a list of dictionaries containing faculty name and profile URL.
    """

    log_message(f"--- Starting scrape of: {FACULTY_LIST_URL} ---", "a")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(FACULTY_LIST_URL, headers=headers)
        response.raise_for_status()
        log_message(f"Successfully fetched faculty list (Status: {response.status_code})", "a")
    except requests.exceptions.RequestException as e:
        log_message(f"ERROR: Failed to fetch the faculty list page: {e}", "a")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all faculty entries - they're in divs with class 'list-name'
    faculty_name_divs = soup.find_all('div', class_='list-name')
    
    if not faculty_name_divs:
        log_message("ERROR: Could not find faculty name containers. Check the HTML structure.", "a")
        return []

    log_message(f"Found {len(faculty_name_divs)} faculty name containers", "a")
    faculty_data = []

    for idx, name_div in enumerate(faculty_name_divs, 1):
        try:
            # Find the anchor tag with the profile link
            link_tag = name_div.find('a', href=True)
            
            if not link_tag:
                log_message(f"WARNING: No link found in container {idx}, skipping", "a")
                continue
            
            # Extract the profile URL
            profile_url = f"{BASE_URL}{link_tag['href']}" if link_tag['href'].startswith('/') else link_tag['href']
            
            # Extract the name - it's inside the anchor tag
            # HTML structure: "Name" then <strong>LastName</strong>
            name_parts = []
            for content in link_tag.contents:
                if isinstance(content, str):
                    name_parts.append(content.strip())
                elif content.name == 'strong':
                    name_parts.append(content.text.strip())
            
            full_name = ' '.join(name_parts).strip()
            
            if not full_name:
                log_message(f"WARNING: Empty name found in container {idx}, skipping", "a")
                continue
            
            data = {
                "name": full_name,
                "profile_url": profile_url,
                "personal_webpage": None,  # To be filled in next step
                "research_interests": None  # To be filled in next step
            }
            
            faculty_data.append(data)
            log_message(f"[{idx}/{len(faculty_name_divs)}] {full_name}", "a")
            log_message(f"    Profile URL: {profile_url}", "a")
            
        except Exception as e:
            log_message(f"ERROR: Failed to parse container {idx}: {e}", "a")
            continue

    log_message(f"--- Scrape complete. Successfully extracted {len(faculty_data)} faculty entries ---", "a")
    
    # Save to JSON file as well
    output_file = "faculty_data.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(faculty_data, f, indent=2, ensure_ascii=False)
        log_message(f"Data saved to {output_file}", "a")
    except Exception as e:
        log_message(f"ERROR: Failed to save JSON file: {e}", "a")
    
    return faculty_data

def scrape_faculty_profile(profile_url, name):
    """
    Scrapes an individual faculty profile page to extract:
    - Personal webpage URL
    - Research interests
    
    Returns a tuple: (personal_webpage, research_interests)
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log_message(f"    ERROR: Failed to fetch profile for {name}: {e}", "a")
        return None, None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract Personal Webpage
    personal_webpage = None
    # Look for the div containing "Webpage:" label
    webpage_divs = soup.find_all('div')
    for div in webpage_divs:
        strong_tag = div.find('strong')
        if strong_tag and 'Webpage:' in strong_tag.text:
            # Find the anchor tag in the same div
            link_tag = div.find('a', href=True)
            if link_tag:
                personal_webpage = link_tag['href']
                break
    
    # Extract Research Interests
    research_interests = None
    research_p = soup.find('p', class_='profile-research')
    if research_p:
        research_interests = research_p.text.strip()
    
    return personal_webpage, research_interests

def enrich_faculty_data(faculty_list):
    """
    Takes the initial faculty list and enriches it by scraping each profile page
    for personal webpage and research interests.
    """
    
    log_message("="*60, "a")
    log_message("FACULTY SCRAPER - STEP 2: Enriching with Profile Details", "a")
    log_message("="*60, "a")
    
    total = len(faculty_list)
    
    for idx, faculty in enumerate(faculty_list, 1):
        name = faculty['name']
        profile_url = faculty['profile_url']
        
        log_message(f"[{idx}/{total}] Scraping profile for: {name}", "a")
        
        # Scrape the individual profile page
        webpage, interests = scrape_faculty_profile(profile_url, name)
        
        # Update the faculty data
        faculty['personal_webpage'] = webpage
        faculty['research_interests'] = interests
        
        if webpage:
            log_message(f"    Webpage: {webpage}", "a")
        else:
            log_message(f"    Webpage: Not found", "a")
            
        if interests:
            # Truncate for logging if too long
            interests_preview = interests[:100] + "..." if len(interests) > 100 else interests
            log_message(f"    Research: {interests_preview}", "a")
        else:
            log_message(f"    Research: Not found", "a")
        
        # Be polite to the server - add a small delay
        time.sleep(0.5)
    
    log_message(f"--- Profile enrichment complete ---", "a")
    
    # Save updated data to JSON
    output_file = "faculty_data_complete.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(faculty_list, f, indent=2, ensure_ascii=False)
        log_message(f"Complete data saved to {output_file}", "a")
    except Exception as e:
        log_message(f"ERROR: Failed to save complete JSON file: {e}", "a")
    
    return faculty_list

if __name__ == "__main__":
    log_message("="*60, "w")
    log_message("FACULTY SCRAPER - STEP 1: Collecting Names and Profile URLs", "a")
    log_message("="*60, "a")
    
    faculty_list = scrape_faculty_directory()
    
    log_message("="*60, "a")
    log_message(f"SUMMARY: Collected {len(faculty_list)} faculty profiles", "a")
    log_message("="*60, "a")
    
    if faculty_list:
        enriched_list = enrich_faculty_data(faculty_list)
        
        # Final summary
        log_message("="*60, "a")
        log_message("FINAL SUMMARY", "a")
        log_message("="*60, "a")
        log_message(f"Total faculty scraped: {len(enriched_list)}", "a")
        
        with_webpage = sum(1 for f in enriched_list if f['personal_webpage'])
        with_research = sum(1 for f in enriched_list if f['research_interests'])
        
        log_message(f"Faculty with personal webpage: {with_webpage}/{len(enriched_list)}", "a")
        log_message(f"Faculty with research interests: {with_research}/{len(enriched_list)}", "a")
        log_message("="*60, "a")
    else:
        log_message("No faculty data to enrich. Exiting.", "a")