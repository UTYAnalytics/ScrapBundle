# Remember to close the browser
import tempfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd
import psycopg2
import glob
from supabase import create_client, Client
import unicodedata
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import numpy as np
from urllib.parse import urlparse
import traceback
from pyvirtualdisplay import Display
import chromedriver_autoinstaller

SUPABASE_URL = "https://sxoqzllwkjfluhskqlfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN4b3F6bGx3a2pmbHVoc2txbGZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDIyODE1MTcsImV4cCI6MjAxNzg1NzUxN30.FInynnvuqN8JeonrHa9pTXuQXMp9tE4LO0g5gj0adYE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Replace these with your Keepa username and password
username = "forheliumonly@gmail.com"
password = "qz6EvRm65L3HdjM2!!@#$"

display = Display(visible=0, size=(800, 800))
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists

with tempfile.TemporaryDirectory() as download_dir:
    # and if it doesn't exist, download it automatically,
    # then add chromedriver to path
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options = [
        # Define window size here
        "--ignore-certificate-errors",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1920,1080",
        "--remote-debugging-port=9222",
        "--disable-extensions",
    ]
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # chrome_service = Service(os.environ.get(r"C:\Program Files\Google\Chrome\Application\chrome.exe"))
    for option in options:
        chrome_options.add_argument(option)
    # Set user data and profile directory
    # chrome_options.add_argument(f"user-data-dir={profile_path}")
    # chrome_options.add_argument(f"profile-directory={profile_name}")


# Your connection string
connection_string = "postgres://postgres.sxoqzllwkjfluhskqlfl:5giE*5Y5Uexi3P2@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

# Parse the connection string
result = urlparse(connection_string)
user = result.username
passdata = result.password
database = result.path[1:]  # remove the leading '/'
hostname = result.hostname
port = result.port

conn = psycopg2.connect(
    dbname=database, user=user, password=passdata, host=hostname, port=port
)
# Create a cursor
cursor = conn.cursor()

# Execute the SQL query to retrieve distinct seller_id from the "best_seller_keepa" table
query = """
SELECT distinct a.sys_run_date,a.asin
    FROM products_smartscount a left join reverse_product_lookup_helium b on a.asin=b.asin
    where b.asin is null
"""

cursor.execute(query)


# Fetch all the rows as a list
asin_list = cursor.fetchall()
retailer_ids_list = [row[1] for row in asin_list]
subset_size = 1
subsets = [
    ", ".join(retailer_ids_list[i : i + subset_size])
    for i in range(0, len(retailer_ids_list), subset_size)
]


# Iterate over each subset
for subset in subsets:
    # Initialize the Chrome driver with the options
    driver = webdriver.Chrome(options=chrome_options)  # service=chrome_service,

    # Open Helium10
    driver.get("https://members.helium10.com/cerebro?accountId=1544526096")
    wait = WebDriverWait(driver, 30)
    print("login")
    # Login process
    try:
        username_field = wait.until(
            EC.visibility_of_element_located((By.ID, "loginform-email"))
        )
        username_field.send_keys(username)

        password_field = driver.find_element(By.ID, "loginform-password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except Exception as e:
        # raise Exception
        print("Error during login:", e)
    # Navigate to the Reverse Asin
    try:
        print("asininput")
        asin_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'input[placeholder="Enter up to 10 product identifiers for keyword comparison."]',
                )
            )
        )
        # You can also set the maximum value if needed
        asin_input.clear()
        asin_input.send_keys(subset)
        time.sleep(2)
        asin_input.send_keys(Keys.SPACE)
        print("Get Keyword Button")
        getkeyword_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@data-testid='getkeywords']")
            )
        )
        print("Get Keyword Button_click")
        getkeyword_button.click()
        time.sleep(2)

        timeout = 10
        try:
            # Wait for the popup to be visible
            popup_visible = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".sc-yRUbj.iYFpRQ"))
            )
            # If the popup is visible, find and click the "Run New Search" button
            if popup_visible:
                run_new_search_button = driver.find_element(
                    By.CSS_SELECTOR, "button[data-testid='runnewsearch']"
                )
                run_new_search_button.click()
                print("Clicked on 'Run New Search'.")
        except TimeoutException:
            # If the popup is not found within the timeout, handle it (e.g., by logging or skipping)
            print("Popup not found within the timeout period.")

        time.sleep(10)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@data-testid='export']")
            )  # Replace "element_id" with the actual ID of the element
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)

        print("Click Export data")
        export_data_button = driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='exportdata']"
        )
        # Use JavaScript to click on the element
        driver.execute_script("arguments[0].click();", export_data_button)
        time.sleep(2)

        print("Clicked the '...as a CSV file' option.")
        data_testid = "csv"
        csv_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'div[data-testid="{data_testid}"]')
            )
        )
        csv_option.click()

        time.sleep(5)
        driver.quit()
        print("newest_file")

        def get_newest_file(directory):
            files = glob.glob(os.path.join(directory, "*"))
            if not files:  # Check if the files list is empty
                return None
            newest_file = max(files, key=os.path.getmtime)
            return newest_file

        file_path = download_dir

        newest_file_path = get_newest_file(file_path)
        # Get the current UTC time
        current_utc_time = datetime.utcnow()

        # Calculate the time difference for GMT+7
        gmt7_offset = timedelta(hours=7)

        # Get the current date and time in GMT+7
        current_time_gmt7 = current_utc_time + gmt7_offset
        if newest_file_path:
            data = pd.read_csv(newest_file_path)
            # data["sys_run_date"] = current_time_gmt7.strftime("%Y-%m-%d %H:%M:%S")

            data = data.replace("-", None)
            data["sys_run_date"] = current_time_gmt7.strftime("%Y-%m-%d %H:%M:%S")
            # Proceed with the database insertion
        else:
            print("No files found in the specified directory.")

        def format_header(header):
            # Convert to lowercase
            header = header.lower()
            # Replace spaces with underscores
            header = header.replace(" ", "_")
            # Remove Vietnamese characters by decomposing and keeping only ASCII
            header = (
                unicodedata.normalize("NFKD", header)
                .encode("ASCII", "ignore")
                .decode("ASCII")
            )
            return header

        # Extract the header row
        headers = [
            "keyword_phrase",
            "aba_total_click_share",
            "aba_total_conv_share",
            "keyword_sales",
            "cerebro_iq_score",
            "search_volume",
            "search_volume_trend",
            "h10_ppc_sugg_bid",
            "h10_ppc_sugg_min_bid",
            "h10_ppc_sugg_max_bid",
            "sponsored_asins",
            "competing_products",
            "cpr",
            "title_density",
            "organic",
            "sponsored_product",
            "amazon_recommended",
            "editorial_recommendations",
            "amazon_choice",
            "highly_rated",
            "sponsored_brand_header",
            "sponsored_brand_video",
            "top_rated_from_our_brand",
            "trending_now",
            "amazon_rec_rank",
            "sponsored_rank",
            "organic_rank",
            "sys_run_date",
        ]

        data.columns = headers
        data.insert(0, "asin", "")

        try:
            # Convert rows to list of dictionaries and handle NaN values
            rows_list = data.replace({np.nan: None}).to_dict(orient="records")

            # Generate MD5 hash as the primary key for each row
            for row_dict in rows_list:
                row_dict["asin"] = str(subset)

            # Insert the rows into the database using executemany
            response = (
                supabase.table("reverse_product_lookup_helium")
                .upsert(rows_list)
                .execute()
            )

            if hasattr(response, "error") and response.error is not None:
                raise Exception(f"Error inserting rows: {response.error}")

            print(f"Rows inserted successfully")

        except Exception as e:
            print(f"Error with rows: {e}")
            # Optionally, break or continue based on your preference
        cursor.execute(query)
        # Fetch all the rows as a list
        brand_product_list = cursor.fetchall()
    except Exception as e:
        print(e)
        traceback.print_exc()
        driver.quit()
        continue
