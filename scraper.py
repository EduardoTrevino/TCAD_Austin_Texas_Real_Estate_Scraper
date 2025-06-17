import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
import time
import re
from collections import Counter

# --- 1. CONFIGURATION ---
STREETS_TO_SEARCH = [
    "Spillman Ranch Loop",
    "Bat Falcon Dr",
    "Bat Hawk Cir",
    "Aplomado",
    "Hookbilled Kite Dr",
    "Sharpshinned Hawk Cv",
    "Snake Eagle Cv"
]
OUTPUT_FILE = "tcad_neighborhood_analysis_final.csv"
# --- END OF CONFIGURATION ---

def click_element_robustly(driver, by, value):
    """A stable click function that uses JavaScript if a normal click fails."""
    try:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
        element.click()
    except (ElementClickInterceptedException, TimeoutException):
        try:
            element = driver.find_element(by, value)
            driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            print(f"  - Could not click element {value}. Error: {e}")

def get_property_ids_from_search(driver, street_name):
    """Navigates, performs a search, handles infinite scroll, and scrapes all property IDs."""
    print(f"\nSearching for properties on: {street_name}...")
    try:
        driver.get("https://travis.prodigycad.com/property-search")
        
        click_element_robustly(driver, By.CSS_SELECTOR, "div.MuiInputBase-root div.MuiSelect-root")
        click_element_robustly(driver, By.XPATH, "//li[normalize-space()='Property Address']")
        
        search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchInput")))
        search_input.clear()
        print(f"  - Typing '{street_name}' and pressing ENTER...")
        search_input.send_keys(street_name + Keys.RETURN)
        
        # Check for "No results found" message
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'No results found')]")))
            print("  -> No results found for this search term.")
            return []
        except TimeoutException:
            # This is expected if results are found
            print("  - Waiting for results grid...")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@role='row' and @row-index='0']")))

        # --- NEW: Handle infinite scroll ---
        print("  - Scrolling to load all results...")
        last_height = 0
        while True:
            # Scroll down
            prop_id_elements = driver.find_elements(By.XPATH, "//div[@role='gridcell' and @col-id='pid']")
            if not prop_id_elements:
                break
            driver.execute_script("arguments[0].scrollIntoView();", prop_id_elements[-1])
            time.sleep(1.5)  # Wait for new results to load

            # Check if we have reached the bottom
            new_height = len(driver.find_elements(By.XPATH, "//div[@role='gridcell' and @col-id='pid']"))
            if new_height == last_height:
                break
            last_height = new_height
            print(f"    - Loaded {last_height} properties so far...")
            
        # Final collection of all IDs
        all_prop_ids = [elem.text for elem in driver.find_elements(By.XPATH, "//div[@role='gridcell' and @col-id='pid']") if elem.text]
        
        print(f"  -> Found a total of {len(all_prop_ids)} properties.")
        return all_prop_ids
        
    except Exception as e:
        # This catches broader errors like page not loading
        print(f"  -> An error occurred while searching for {street_name}: {e}")
        return []

def get_property_details(driver, prop_id):
    """Navigates to a property detail page and scrapes the required information with fallbacks."""
    details = {'account_id': prop_id}
    url = f"https://travis.prodigycad.com/property-detail/{prop_id}"
    try:
        driver.get(url)
        # 1. Wait for the key element to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h3[text()='General Info']")))
        
        # <<< NEW: Add a small pause to ensure all JavaScript content has rendered >>>
        # This is the most likely fix for the N/A rows.
        time.sleep(1) 

        print(f"    - Scraping data for ID {prop_id}...")
        
        page_source = driver.page_source
        page_text = driver.find_element(By.TAG_NAME, 'body').text

        # --- Address ---
        try:
            details['address'] = driver.find_element(By.XPATH, "//p[text()='Address:']/following-sibling::p").text.strip()
        except NoSuchElementException:
            details['address'] = "Not Found"
        
        # --- Tier 1: Try to get values using robust text parsing ---
        value_pattern = re.compile(r"^2025\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)", re.MULTILINE)
        match = value_pattern.search(page_text)
        
        if match:
            groups = match.groups()
            details['appraised_value'] = groups[3]
            details['value_limit_adjustment'] = groups[4]
            details['net_appraised_value'] = groups[5]
        else:
            # --- Tier 2: Fallback to pandas table parsing if text parsing fails ---
            print("    - INFO: Text parsing for values failed. Trying table parsing as a backup.")
            try:
                page_tables = pd.read_html(page_source, flavor='lxml')
                value_history_table = next((tbl for tbl in page_tables if 'Net Appraised' in tbl.columns and 'Appraised' in tbl.columns), None)
                if value_history_table is not None and 'Year' in value_history_table.columns:
                    value_history_table['Year'] = pd.to_numeric(value_history_table['Year'])
                    year_2025_data = value_history_table[value_history_table['Year'] == 2025]
                    if not year_2025_data.empty:
                        latest_values = year_2025_data.iloc[0]
                        details['net_appraised_value'] = latest_values.get('Net Appraised', 'N/A')
                        details['appraised_value'] = latest_values.get('Appraised', 'N/A')
                        details['value_limit_adjustment'] = latest_values.get('Value Limitation Adj (-)', 'N/A')
                    else:
                        details['net_appraised_value'], details['appraised_value'], details['value_limit_adjustment'] = 'N/A', 'N/A', 'N/A'
                else:
                    details['net_appraised_value'], details['appraised_value'], details['value_limit_adjustment'] = 'N/A', 'N/A', 'N/A'
            except Exception as e_pandas:
                print(f"    - Fallback parsing also failed. Error: {e_pandas}")
                details['net_appraised_value'], details['appraised_value'], details['value_limit_adjustment'] = 'Error', 'Error', 'Error'

        # --- Get Class CD and Year Built from page text (main method) ---
        start_marker = "Type Description Class CD"
        end_marker = "Land\n"
        start_index = page_text.find(start_marker)
        end_index = page_text.find(end_marker, start_index)
        
        if start_index != -1 and end_index != -1:
            improvement_text = page_text[start_index:end_index]
            class_cds_found = re.findall(r'\b([A-Z]\d+)\b', improvement_text)
            
            if class_cds_found:
                cd_counts = Counter(class_cds_found)
                details['class_cd'] = cd_counts.most_common(1)[0][0]
            else:
                details['class_cd'] = 'Not Found'

            years_found = re.findall(r'\b(20\d{2}|19\d{2})\b', improvement_text)
            if years_found:
                details['year_built'] = years_found[0]
            else:
                details['year_built'] = 'Not Found'
        else:
            details['class_cd'], details['year_built'] = 'N/A', 'N/A'
        
        # --- Builder logic ---
        try:
            page_tables = pd.read_html(page_source, flavor='lxml')
            deeds_table = next((tbl for tbl in page_tables if 'Deed Date' in tbl.columns and 'Grantor/Seller' in tbl.columns), None)
            if deeds_table is not None:
                known_builders = ['TAYLOR MORRISON', 'RYLAND', 'DREES CUSTOM', 'RH OF TEXAS']
                builder_found = False
                for builder in known_builders:
                    builder_rows = deeds_table[
                        deeds_table['Grantor/Seller'].str.contains(builder, case=False, na=False) |
                        deeds_table['Grantee/Buyer'].str.contains(builder, case=False, na=False)
                    ]
                    if not builder_rows.empty:
                        details['builder'] = builder 
                        builder_found = True
                        break
                if not builder_found:
                    if len(deeds_table) > 1:
                        deeds_table['Deed Date'] = pd.to_datetime(deeds_table['Deed Date'])
                        details['builder'] = deeds_table.sort_values(by='Deed Date').iloc[-2]['Grantor/Seller']
                    else:
                        details['builder'] = 'N/A'
            else:
                details['builder'] = 'N/A'
        except Exception as e:
            print(f"    - Could not parse deeds table. Error: {e}")
            details['builder'] = 'Error'
            
        details['tcad_link'] = url
        return details
        
    except Exception as e:
        print(f"    - An error occurred while processing ID {prop_id}. Error: {e}")
        return {**details, 'address': 'Error', 'builder': 'Error', 'class_cd': 'Error', 
                'year_built': 'Error', 'net_appraised_value': 'Error', 'appraised_value': 'Error',
                'value_limit_adjustment': 'Error', 'tcad_link': url}

def main():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    all_property_data = []
    failed_searches = [] # To track searches with no results
    
    for street in STREETS_TO_SEARCH:
        prop_ids = get_property_ids_from_search(driver, street)
        if not prop_ids:
            failed_searches.append(street)
            continue # Move to the next street

        for i, prop_id in enumerate(prop_ids):
            print(f"  - Scraping details for property {i+1}/{len(prop_ids)} (ID: {prop_id})...")
            details = get_property_details(driver, prop_id)
            if details:
                all_property_data.append(details)
            time.sleep(0.5)

    driver.quit()

    if not all_property_data:
        print("\nNo data was collected. Please check the console for errors.")
    else:
        df = pd.DataFrame(all_property_data)
        column_order = [
            'address', 'builder', 'class_cd', 'year_built', 
            'net_appraised_value', 'appraised_value', 'value_limit_adjustment', 
            'tcad_link', 'account_id'
        ]
        df = df.reindex(columns=[col for col in column_order if col in df.columns])
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n--- SCRAPING COMPLETE! ---\nSuccess! A file named '{OUTPUT_FILE}' has been created in your folder.")

    # --- NEW: Report any failed searches at the end ---
    if failed_searches:
        print("\nThe following search terms returned no results:")
        for street in failed_searches:
            print(f"  - {street}")

if __name__ == "__main__":
    main()