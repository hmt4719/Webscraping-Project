# Web Scraping Project for LG Products

This project is designed to scrape product information for LG appliances from three e-commerce websites: **Croma**, **Reliance Digital**, and **Vijay Sales**. The project is split into two main parts for each website: first, scraping product links (using Selenium), and then extracting detailed product information (using either Selenium or asynchronous requests with aiohttp and BeautifulSoup).

Below is an overview of the main functions and their roles in the code.

---

## Project Overview

- **Link Extraction:**  
  Uses Selenium to navigate category pages, apply filters, and extract product links.  
  - **Functions:**  
    - `croma_viewmore(driver)`: Clicks the "View More" button repeatedly until no more are available (for Croma).  
    - `drop_down_croma(driver, subcategory)`: Opens the categories dropdown and selects a specified subcategory (for Croma).  
    - `scrape_data_croma(driver, category, data_list)`: Extracts product links from a Croma page and appends them to a list.  
    - `extract_product_links()`: Orchestrates the link extraction for Croma by iterating through different category URLs.

- **Product Detail Scraping:**  
  Once product links are extracted, this part of the code visits each product page to scrape detailed information like product name, item code, model number, and subcategory.  
  - **Functions:**  
    - `scrape_product_details(driver, data)`: Loads a product page and extracts details such as item code, product name, model number, and subcategory.  
    - `extract_product_details()`: Reads product links from a CSV file, calls `scrape_product_details` for each link, and saves the scraped data into a CSV file.

- **Reliance Digital & Vijay Sales Scrapers:**  
  The code contains similar sets of functions for these websites, with adjustments for differences in site layout and filter options.  
  - **Additional Functions:**  
    - `filter_LG(driver)`: Applies an LG brand filter (if applicable).  
    - `alert_Nullify(driver)`: Closes or nullifies any pop-up alerts that might interfere with scraping.  
    - `select_subcategory(driver, subcategory)`: Selects or deselects a subcategory filter.  
    - `enable_drop_down(driver)`: Opens dropdown menus if they are closed, ensuring the filters are visible.  
    - `scrape_subcategory_products(driver, category, subcategory, list_of_dict)`: Extracts product links for a given subcategory page and handles pagination.
    - `get_subcategory_labels(driver)`: Retrieves all available subcategory labels from the filter dropdown.

- **Asynchronous Scraping:**  
  To speed up product detail extraction, asynchronous functions using `aiohttp` and `asyncio` fetch and parse product pages concurrently.  
  - **Functions:**  
    - `parse_data(soup, row)`: Parses the HTML of a product page to extract product details.  
    - `scrape(session, row)`: Asynchronously retrieves a single product page and calls `parse_data` to extract details.  
    - `run_async_scraper()`: Manages the asynchronous scraping tasks and saves the results into a CSV file.

- **Main Execution Flow:**  
  The `main()` function in each script coordinates the overall process by calling the link extraction functions first and then the product detail extraction (either synchronously via Selenium or asynchronously).

---

## How to Use This Project

1. **Install Dependencies:**  
   Ensure you have Python 3.7+ installed. Then, install the necessary libraries:
   ```bash
   pip install selenium pandas beautifulsoup4 aiohttp
