from imports import *
def filter_LG(driver, category):
    try:
        driver.find_element(By.XPATH, "//label[div[contains(@class, 'filter-item-value') and contains(text(), 'LG')]]/input").click()
        print(f"{category} BRAND LG SELECTION DONE")
    except Exception as e:
        print(f"{category} BRAND LG SELECTION NOT POSSIBLE: {e}")

def alert_Nullify(driver, category):
    try:
        driver.find_element(By.ID, 'wzrk-cancel').click()
        print(f"{category} ALERT NULLIFIED")
    except Exception as e:
        print(f"{category} ALERT NHI AAYA: {e}")

def select_subcategory(driver, subcategory):
    try:
        driver.find_element(By.XPATH, f"//div[contains(@class,'filter-item-value') and normalize-space(text())='{subcategory}']/preceding-sibling::input").click()
        print(f"Done click {subcategory}")
    except Exception as e:
        print(f"{subcategory} not clicked: {e}")

def enable_drop_down(driver):
    # Check if the dropdown is closed and open it if necessary
    try:
        element = driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Display Type') or contains(@aria-label, 'Category') or contains(@aria-label, 'Washing Machine Type')]/following-sibling::div").get_attribute("class")
        if "close" in element:
            driver.find_element(By.XPATH, "//div[(contains(@aria-label, 'Display Type') or contains(@aria-label, 'Category') or contains(@aria-label, 'Washing Machine Type'))]/div[2]").click()
    except Exception as e:
        print("Dropdown enabling error:", e)

def scrape_subcategory_products(driver, category, subcategory, list_of_dict):
    numOfProduct = 0

    while True:
        time.sleep(3)  # Allow the page to load
        html = driver.page_source
        soup = bs(html, 'html.parser')
        items = soup.select(".product-card-details a")
        numOfProduct += len(items)

        # Extract product links
        for ele in items:
            product_link = 'https://www.reliancedigital.in' + ele.get('href')
            list_of_dict.append({"Link": product_link, "Category": category, "Subcategory": subcategory})

        # Find the "Next Page" button
        next_btn = soup.select_one('span[aria-label="Goto Next Page"]')
        if next_btn is None:
            break  # No more pages

        next_btn_classes = next_btn.get("class")
        if next_btn_classes is None or "disable-click" in list(next_btn_classes):
            print("Next Page button not clickable")
            break
        else:
            try:
                driver.find_element(By.CSS_SELECTOR, 'span[aria-label="Goto Next Page"]').click()
            except Exception as e:
                print("Error while clicking the Next Page button:", e)
                break

    print(f"{category} {subcategory} : {numOfProduct}")

def get_subcategory_labels(driver):
    subcategory_labelsName = []
    try:
        enable_drop_down(driver)
        subcategory_labels = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Display Type') or contains(@aria-label, 'Category') or contains(@aria-label, 'Washing Machine Type')]/following-sibling::div//div[contains(@class, 'filter-item-value')]")
        subcategory_labelsName = [label.text for label in subcategory_labels]
    except Exception as e:
        print("NO SUBCATEGORY:", e)
    return subcategory_labelsName

############################################
# Selenium Main Scraper
############################################

def run_selenium_scraper():
    start_time = time.time()
    list_of_dict = []
    
    # Define service and options for Chrome
    service_obj = Service("C:/webdrivers/chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    options.add_argument("start-maximized")  # Start browser in full screen

    driver = webdriver.Chrome(options=options, service=service_obj)
    driver.implicitly_wait(4)

    # Category URLs to be scraped
    categories_link = {
        "WashingMachine": "https://www.reliancedigital.in/collection/washing-machines?internal_source=navigation&page_no=1&page_size=12&page_type=number",
        "DishWasher": "https://www.reliancedigital.in/products?q=dishwasher&page_no=1&page_size=12&page_type=number",
        "AC": "https://www.reliancedigital.in/collection/lg-ac?page_no=1&page_size=12&page_type=number",
        "Refrigerator": "https://www.reliancedigital.in/collection/lg-refrigerators/?page_no=1&page_size=12&page_type=number",
        "TV": "https://www.reliancedigital.in/collection/lg-tv/?page_no=1&page_size=12&page_type=number",
        "Microwave": "https://www.reliancedigital.in/products?q=lg%20oven%20and%20microwaves",
        "WaterPurifier": "https://www.reliancedigital.in/collection/water-purifiers?internal_source=navigation&page_no=1&page_size=12&page_type=number",
        "SoundBar": "https://www.reliancedigital.in/products?q=SOUND%20BAR&page_no=1&page_size=12&page_type=number",
        "PartySpeakers": "https://www.reliancedigital.in/collection/party-speakers?internal_source=navigation&page_no=1&page_size=12&page_type=number"
    }

    for category, url in categories_link.items():
        driver.get(url)
        alert_Nullify(driver, category)
        filter_LG(driver, category)
        time.sleep(2)

        subcategory_labelsName = get_subcategory_labels(driver)

        if subcategory_labelsName:
            for curr_label in subcategory_labelsName:
                time.sleep(2)
                enable_drop_down(driver)
                time.sleep(1)
                select_subcategory(driver, curr_label)
                # Scrape product links for the selected subcategory
                scrape_subcategory_products(driver, category, curr_label, list_of_dict)
                # Deselect the subcategory
                enable_drop_down(driver)
                time.sleep(1)
                select_subcategory(driver, curr_label)
        else:
            scrape_subcategory_products(driver, category, "N/A", list_of_dict)

    print("Total items extracted:", len(list_of_dict))

    # Save the extracted links to a CSV file
    df = pd.DataFrame(list_of_dict)
    print(f"DataFrame shape: {df.shape}")
    print(df)
    df.to_csv('extracted_links_RD.csv', index=False)
    print(f"Total Selenium scraping time: {(time.time()-start_time)/60:.2f} minutes")
    
    time.sleep(5)
    driver.quit()


############################################
# Asynchronous Functions for Data Extraction
############################################

def parse_data(soup, row):
    data = {}
    data["Subcategory"] = row["Subcategory"]
    data["Category"] = row["Category"]
    data["Link"] = row["Link"]

    # Extract product name
    product_name_element = soup.select_one("#main-content")
    data["Product Name"] = product_name_element.text.strip() if product_name_element else "N/A"

    specifications = soup.select(".specifications-list")

    # Extract Item Code safely
    item_code_element = None
    for spec in specifications:
        cname = spec.find('span').text.strip()
        if cname == "Item Code":
            itemCode_web = spec.select_one("span span")
            item_code_element = itemCode_web.text.strip() if itemCode_web else None
            break
    data["Item Code"] = int(item_code_element) if item_code_element is not None else None

    # Extract Model Number
    model_number = "N/A"
    for spec in specifications:
        cname = spec.find('span').text.strip()
        if cname == "Model":
            element = spec.select_one("span span")
            if element:
                model_number = element.text.strip()
            break

    # If no model number found, try extracting from the title
    if model_number == 'N/A' and product_name_element:
        title = product_name_element.text.strip()
        pattern = r'\b[0-9]*[A-Za-z-]+\d+[A-Za-z.0-9]*\b'
        matches = re.findall(pattern, title)
        if matches:
            model_number = max(matches, key=len)
    data["Model Number"] = model_number

    return data

async def scrape(session, row):
    url = row['Link']
    try:
        async with session.get(url) as response:
            html = await response.text()
        soup = bs(html, 'html.parser')
        return parse_data(soup, row)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

async def run_async_scraper():
    start_time = time.time()
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        with open('extracted_links.csv') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                tasks.append(scrape(session, row))
        scraped_data = await asyncio.gather(*tasks)
        results = [data for data in scraped_data if data is not None]

    # Convert list of dicts to a Pandas DataFrame with specified column order
    df = pd.DataFrame(results)
    column_order = ["Product Name", "Subcategory", "Category", "Item Code", "Model Number", "Link"]
    df = df[column_order]
    df.to_csv("rd_extracted_data.csv", index=False)
    print(f"Scraping completed in {time.time() - start_time:.2f} seconds")

############################################
# Main Execution
############################################

def main():
    print("Starting Selenium scraping for product links...")
    run_selenium_scraper()
    print("Selenium scraping completed. Starting asynchronous product details scraping...")
    asyncio.run(run_async_scraper())
    print("Asynchronous scraping completed. All data has been saved.")

if __name__ == '__main__':
    main()
