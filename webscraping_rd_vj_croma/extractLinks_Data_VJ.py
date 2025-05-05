from imports import *
############################################
# Selenium Functions for Link Extraction
############################################

def filter_LG(driver):
    """Click on the LG brand filter if available."""
    try:
        driver.find_element(By.XPATH,
            "//label[div[contains(@class, 'filter-item-value') and contains(text(), 'LG')]]/input").click()
        print("BRAND LG SELECTION DONE")
    except Exception as e:
        print("BRAND LG SELECTION NOT POSSIBLE", e)

def alert_Nullify(driver):
    """Handle alert popup and perform a hover action to dismiss."""
    try:
        driver.find_element(By.ID, 'notify-visitors-confirm-popup-btn-negative').click()
        print("ALERT NULLIFIED")
        element_to_hover = driver.find_element(By.XPATH, "//div[@class='vs-head-pri-search']")
        actions = ActionChains(driver)
        actions.move_to_element(element_to_hover).perform()
    except Exception as e:
        print("ALERT NHI AAYA", e)

def select_subcategory(driver, subcategory):
    """Select (or deselect) the subcategory filter option."""
    try:
        element = driver.find_element(By.XPATH, 
            f"//button[.//*[contains(text(), 'Resolution') or contains(text(), 'Category') or contains(text(),'Microwave Type') or contains(text(), 'AC Type')]]/following-sibling::div//input[@value=normalize-space('{subcategory}')]")
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(2)
        element.click()
        print(f"Done click {subcategory}")
    except Exception as e:
        print(f"{subcategory} not clicked", e)

def enable_drop_down(driver):
    """Check if the dropdown is closed; if so, open it."""
    try:
        element = driver.find_element(By.XPATH, 
            "//div[contains(@aria-label, 'Display Type') or contains(@aria-label, 'Category') or contains(@aria-label, 'Washing Machine Type')]/following-sibling::div").get_attribute("class")
        if "close" in element:
            driver.find_element(By.XPATH, 
                "//div[(contains(@aria-label, 'Display Type') or contains(@aria-label, 'Category') or contains(@aria-label, 'Washing Machine Type'))]/div[2]").click()
    except Exception as e:
        print("Error enabling dropdown:", e)

def scrape_subcategory_products(driver, category, subcategory):
    """Scrape all product links from a given subcategory page until there are no more pages."""
    numOfProduct = 0
    while True:
        time.sleep(3)  # Allow page to load
        try:
            ele = driver.find_element(By.XPATH, "//a[@jsname='nextBtn']")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ele)
        except Exception:
            pass
        time.sleep(3)
        cards = driver.find_elements(By.CSS_SELECTOR, "div.plp-horizontal-products.d-block div.product-card,div.plp-vertical-products.d-flex div.product-card")  # All product cards
        items = []
        print(len(cards))
        for card in cards:
            # Find all anchors with class product-card__link inside this card
            link_element = card.find_element(By.CSS_SELECTOR, "a.product-card__link")

            if link_element:
                # Grab the first link's href
                items.append(link_element)
        # items = driver.find_elements(By.XPATH, 
            # "( //div[contains(@class, 'plp-vertical-products') and contains(@class, 'd-flex')] //div[contains(@class, 'product-card')]/a[@class='product-card__link'] ) | ( //div[contains(@class, 'plp-horizontal-products') and contains(@class, 'd-block')]//div[contains(@class, 'product-card')]/a[@class='product-card__link'] )")
        numOfProduct += len(items)
        print(numOfProduct)
        for ele in items:
            product_link = ele.get_attribute("href")
            list_of_dict.append({"Link": product_link, "Category": category, "Subcategory": subcategory})

        try:
            next_btn = driver.find_element(By.XPATH, "//a[@jsname='nextBtn']")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            try:
                divs = driver.find_element(By.XPATH, "//a[@jsname='nextBtn']/parent::div").get_attribute("style")
                print(divs)
                if divs == "display: none;":
                    break
            except Exception:
                pass

            x = next_btn.get_attribute("disabled")
            print(x)
            if x:
                print("Next Page button is disabled. No more pages.")
                break
            driver.execute_script("arguments[0].click();", next_btn)
        except Exception:
            print("Next button not found or not clickable")
            break

    print(f"{category} {subcategory} : {numOfProduct}")

def get_subcategory_labels(driver):
    """Extract subcategory filter values from the page if available."""
    subcategory_labelsName = []
    try:
        subcategory_labels = driver.find_elements(By.XPATH, 
            "//button[.//*[contains(text(), 'Resolution') or contains(text(), 'Microwave Type') or contains(text(), 'Category') or contains(text(), 'AC Type')]]/following-sibling::div//input")
        subcategory_labelsName = [label.get_attribute("value") for label in subcategory_labels]
    except Exception as e:
        print("NO SUBCATEGORY", e)
    return subcategory_labelsName

############################################
# Selenium Main Scraper Function
############################################

def run_selenium_scraper():
    """Main function to run Selenium scraper and save extracted links to CSV."""
    global list_of_dict
    list_of_dict = []  # global list for storing links
    
    service_obj = Service("C:/webdrivers/chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/133.0.0.0")
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(options=options, service=service_obj)
    driver.implicitly_wait(4)

    categories_link = {
        "WashingMachine": "https://www.vijaysales.com/c/washing-machines?brand=LG",
        "DishWasher": "https://www.vijaysales.com/c/dishwashers?brand=LG",
        "AC": "https://www.vijaysales.com/search-listing?q=Air%20conditioner%20LG",
        "Refrigerator": "https://www.vijaysales.com/c/refrigerators?brand=LG",
        "TV": "https://www.vijaysales.com/search-listing?q=LG%20TV",
        "Microwave": "https://www.vijaysales.com/search-listing?q=lg%20microwave",
        "WaterPurifier": "https://www.vijaysales.com/search-listing?q=lg%20water%20purifier"
    }
    
    start_time = time.time()
    
    for category, url in categories_link.items():
        driver.get(url)
        alert_Nullify(driver)
        # filter_LG(driver)  # Uncomment if you need to apply LG filter explicitly
        time.sleep(2)
        driver.refresh()  # Reload the page
        time.sleep(2)

        subcategory_labelsName = get_subcategory_labels(driver)
        print("Subcategories found:", subcategory_labelsName)
        
        if subcategory_labelsName:
            for curr_label in subcategory_labelsName:
                time.sleep(2)
                time.sleep(1)
                select_subcategory(driver, curr_label)
                scrape_subcategory_products(driver, category, curr_label)
                time.sleep(5)
                select_subcategory(driver, curr_label)  # Deselect the subcategory
        else:
            scrape_subcategory_products(driver, category, "N/A")
    
    print("Total items extracted:", len(list_of_dict))
    
    df = pd.DataFrame(list_of_dict)
    print(f"DataFrame shape: {df.shape}")
    print(df)
    df.to_csv('extracted_links_VJ.csv', index=False)
    print(f"Total Selenium scraping time: {(time.time()-start_time)/60:.2f} minutes")
    
    time.sleep(5)
    driver.quit()


############################################
# Asynchronous Functions for Data Parsing
############################################

def parse_data(soup, row):
    """Parse product details from the page using BeautifulSoup."""
    data = {}
    data["Subcategory"] = row["Subcategory"]
    data["Category"] = row["Category"]
    data["Link"] = row["Link"]

    product_name_element = soup.select_one("span[role='name']")
    data["Product Name"] = product_name_element.text.strip() if product_name_element else "N/A"

    # Extract Item Code from the URL
    parts = data["Link"]
    matches = re.findall(r'/\d+', parts)
    if matches:
        data["Item Code"] = matches[0][1:]  # remove leading '/'
    else:
        data["Item Code"] = "N/A"

    # Extract Model Number from specifications
    model_number = "N/A"
    specifications = soup.select("#vscontainer-81b267084f li")
    for spec in specifications:
        sname = spec.select_one("span.panel-list-key").text.strip()
        sdata = spec.select_one("span.panel-list-value").text.strip()
        if sname == "MODEL NAME":
            model_number = sdata
            break
    if model_number == "N/A":
        for spec in specifications:
            sname = spec.select_one("span.panel-list-key").text.strip()
            sdata = spec.select_one("span.panel-list-value").text.strip()
            if sname == "SKU":
                model_number = sdata
                break
    data["Model Number"] = model_number
    return data

async def scrape(session, row):
    """Asynchronously scrape a single product page and return parsed data."""
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
    """Run asynchronous scraping of product details from extracted links."""
    start_time = time.time()
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        with open('extracted_links_VJ.csv') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                tasks.append(scrape(session, row))
        scraped_data = await asyncio.gather(*tasks)
        results = [data for data in scraped_data if data is not None]

    df = pd.DataFrame(results)
    column_order = ["Product Name", "Subcategory", "Category", "Item Code", "Model Number", "Link"]
    df = df[column_order]
    df.to_csv("extracted_data_VJ.csv", index=False)
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