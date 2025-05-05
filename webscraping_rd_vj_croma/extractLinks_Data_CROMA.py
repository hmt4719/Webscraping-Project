from imports import *
# ===============================
# Section: Helper Functions
# ===============================
def croma_viewmore(driver):
    """
    Clicks on the "View More" button repeatedly until no more are available.
    """
    try:
        while True:
            time.sleep(2)
            elements = driver.find_elements(By.XPATH, "//button[normalize-space(text())='View More']")
            if len(elements) == 0:
                print("No more 'View More' button")
                break
            element = elements[0]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            element.click()
    except Exception as e:
        print(f"Error in View More: {e}")

def drop_down_croma(driver, subcategory=None):
    """
    Opens the categories dropdown and selects a given subcategory if provided.
    """
    try:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        categories_dropdown = driver.find_element(By.XPATH, "//div[contains(@class,'cp-accordian typ-sm desktop')]//p[text()='Categories']")
        categories_dropdown.click()
        time.sleep(1)
        if subcategory:    
            driver.find_element(By.XPATH, f"//span[contains(normalize-space(),'{subcategory}')]").click()
            time.sleep(1)
        categories_dropdown.click()
        time.sleep(1)
    except Exception as e:
        print(f"Drop down error: {e}")

def getsubcategory_labels(driver):
    """
    Extracts and returns a list of subcategory labels from the categories dropdown.
    """
    try:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        categories_dropdown = driver.find_element(By.XPATH, "//div[contains(@class,'cp-accordian typ-sm desktop')]//p[text()='Categories']")
        categories_dropdown.click()
        time.sleep(1)
        subcategories = driver.find_elements(By.XPATH, "//div[contains(@class,'cp-accordian typ-sm desktop')]//p[text()='Categories']/parent::div/parent::div/following-sibling::div//span[@class='text']")
        subcategory_labelnames = [label.text.strip() for label in subcategories]
        time.sleep(1)
        categories_dropdown.click()
        time.sleep(1)
        return subcategory_labelnames
    except Exception as e:
        print(f"Drop down error: {e}")
        return []

# ===============================
# Section: Link Extraction Functions
# ===============================
def scrape_data_croma(driver, category, data_list):
    """
    Extracts product links for a given category and appends them to the provided list.
    """
    time.sleep(2)
    all_product_links = driver.find_elements(By.XPATH, "//div[@class='product-info']//h3/a")
    temp_list = []
    for pdt in all_product_links:
        data = {}
        data["Link"] = pdt.get_attribute('href')
        data["Category"] = category
        temp_list.append(data)
    print(f"{category}: {len(temp_list)} products found")
    data_list.extend(temp_list)

def extract_product_links():
    """
    Extracts product links from Croma and saves them to 'extracted_Links_croma.csv'.
    """
    # Define the links for various categories
    categories_link = {
        "WashingMachine": "https://www.croma.com/searchB?q=washing+machine%3Arelevance%3ASG-ManufacturerDetails-Brand%3ALG&text=washing%20machine",
        "DishWasher": "https://www.croma.com/searchB?q=dishwasher%3Arelevance%3ASG-ManufacturerDetails-Brand%3ALG&text=dishwasher",
        "AC": "https://www.croma.com/lg-air-conditioners/bc/b-0219-46",
        "Refrigerator": "https://www.croma.com/searchB?q=LG%20FRIDGE%3Arelevance&text=LG%20FRIDGE",
        "TV": "https://www.croma.com/televisions-accessories/c/997?q=%3Arelevance%3ASG-ManufacturerDetails-Brand%3ALG",
        "Microwave": "https://www.croma.com/lg-microwaves-and-ovens/bc/b-0219-60",
        "WaterPurifier": "https://www.croma.com/searchB?q=water+purifier%3Arelevance%3ASG-ManufacturerDetails-Brand%3ALG&text=water%20purifier",
        "SoundBar": "https://www.croma.com/searchB?q=soundbar%3Arelevance%3ASG-ManufacturerDetails-Brand%3ALG&text=soundbar",
        "PartySpeakers": "https://www.croma.com/searchB?q=party+speaker%3Arelevance%3ASG-ManufacturerDetails-Brand%3ALG&text=party%20speaker"
    }

    # Set up Selenium WebDriver
    service_obj = Service("C:/webdrivers/chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.0")
    options.add_argument("start-maximized")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(options=options, service=service_obj)
    driver.implicitly_wait(4)

    list_of_dict = []
    start_time = time.time()

    for category, url in categories_link.items():
        driver.get(url)
        croma_viewmore(driver)
        scrape_data_croma(driver, category, list_of_dict)

    print(f"Total links extracted: {len(list_of_dict)}")
    df = pd.DataFrame(list_of_dict)
    print(f"DataFrame shape: {df.shape}")
    df.to_csv('extracted_links_CROMA.csv', index=False)

    print(f"Link extraction completed in {(time.time()-start_time)/60:.2f} minutes")
    time.sleep(10)
    driver.quit()

# ===============================
# Section: Product Detail Scraping Functions
# ===============================
def scrape_product_details(driver, data):
    """
    Scrapes details from a product page and adds them to the provided data dictionary.
    """
    link = data["Link"]
    driver.get(link)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception as e:
        print(f"Page load timeout for {link}: {e}")
        return None

    # Extract Item Code
    try:
        parts = link.split("/p/")
        if len(parts) > 1:
            itm_code = parts[1].split("/")[0]
            data["Item Code"] = itm_code
        else:
            data["Item Code"] = "N/A"
    except Exception as e:
        data["Item Code"] = "N/A"
        print(f"Item Code error: {e}")

    # Extract Product Name
    try:
        title_element = driver.find_element(By.XPATH, "//ul[@class='info-list']//h1")
        data["Product Name"] = title_element.text if title_element else "N/A"
    except Exception as e:
        data["Product Name"] = "N/A"
        print(f"Product name error: {e}")

    # Click "View More" Button if available
    try:
        view_more_button = driver.find_element(By.XPATH, "(//div[normalize-space(text())='View More'])[1]")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_more_button)
        view_more_button.click()
        time.sleep(0.5)
    except Exception as e:
        print(f"View more not possible for {link}: {e}")

    # Extract Model Number
    try:
        modelnum = driver.find_element(By.XPATH, "//li[*[normalize-space(text())='Model Number']]/following-sibling::li")
        data["Model Number"] = modelnum.text if modelnum else "N/A"
    except Exception as e:
        data["Model Number"] = "N/A"
        print(f"Error extracting Model Number: {e}")

    time.sleep(0.5)

    # Extract Subcategory based on various possible labels
    try:
        subcategory = driver.find_element(
            By.XPATH,
            "//li[contains(normalize-space(), 'Operation Type') or "
            "contains(normalize-space(), 'Display Resolution') or "
            "contains(normalize-space(), 'Oven Type') or "
            "contains(normalize-space(), 'Air Conditioner Type') or "
            "contains(normalize-space(), 'Dishwasher Type') or "
            "contains(normalize-space(), 'Refrigerator Type')]"
            "/following-sibling::li[1]"
        )
        data["Subcategory"] = subcategory.text if subcategory else "N/A"
    except Exception as e:
        data["Subcategory"] = "N/A"
        print(f"Error extracting Subcategory: {e}")

    # Verify URL redirection
    if driver.current_url != link:
        print(f"Redirected: {driver.current_url} != {link}")
        if data.get("Item Code", "N/A") == "N/A" and data.get("Product Name", "N/A") == "N/A":
            return None

    return data

def extract_product_details():
    """
    Reads the CSV of product links, scrapes additional details for each product,
    and saves the final data to 'croma_extracted_data.csv'.
    """
    start_time = time.time()
    scrape_data = []

    # Set up Selenium WebDriver for scraping product details
    service_obj = Service("C:/webdrivers/chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.0")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(options=options, service=service_obj)
    driver.implicitly_wait(4)

    with open('extracted_links_CROMA.csv', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for num, row in enumerate(csv_reader, start=1):
            print(f"Processing product {num}")
            result = scrape_product_details(driver, row)
            if result is not None:
                scrape_data.append(result)

    driver.quit()
    print(f"Product detail scraping completed in {(time.time() - start_time)/60:.2f} minutes")

    # Save scraped product details to CSV
    df = pd.DataFrame(scrape_data)
    column_order = ["Product Name", "Subcategory", "Category", "Item Code","Model Number","Link"]
    df = df.reindex(columns=column_order, fill_value="N/A")
    df.to_csv("extracted_data_CROMA.csv", index=False)
    return df

# ===============================
# Section: Main Execution Flow
# ===============================
def main():
    print("Starting link extraction...")
    extract_product_links()
    
    print("Starting product detail extraction...")
    results_df = extract_product_details()
    print("Scraping process completed.")

if __name__ == "__main__":
    main()