pip install webdriver_manager
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Function to start the web driver and perform LinkedIn login
def driver_start():
    DRIVER_PATH = r"Replace with the actual path to the driver"  # Replace with the actual path to the driver
    service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=service)  # Create a Chrome web driver instance

    # Open LinkedIn's login page
    driver.get("https://linkedin.com/uas/login")

    # Wait for the page to load
    time.sleep(5)

    # Find and fill the username field
    username = driver.find_element(By.ID, "username")
    username.send_keys("username")  # Enter your email address here

    # Find and fill the password field
    pword = driver.find_element(By.ID, "password")
    pword.send_keys("password")  # Enter your password here

    # Click the login button
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    return driver  # Return the initialized driver instance

# Define the URL of the LinkedIn jobs search page
url = "https://www.linkedin.com/jobs/search/?currentJobId=3936810370&f_PP=104793846%2C104869687%2C105282602&keywords=data%20analyst&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=R"

# Start the web driver and perform LinkedIn login
driver = driver_start()

# Pause for 3 seconds before continuing
time.sleep(3)

# Initialize an empty list to store job links
job_links = []

# Set the number of job listings to extract
num_job_listings = 100

# Scroll down to the bottom of the page and extract the job links
driver.get(url)
time.sleep(4)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)
src = driver.page_source
soup = BeautifulSoup(src, "html.parser")
for element in soup.find_all('a', href=True):
    if "/jobs/view/" in element['href']:
        job_links.append("https://www.linkedin.com" + element['href'])
        if len(job_links) >= num_job_listings:
            break

# Extract more job listings by adding "&start=25" to the URL
current_start = 0
has_more_listings = True
while len(job_links) < num_job_listings and has_more_listings and current_start < 105:
    current_start += 25
    new_url = url + "&start=" + str(current_start)
    driver.get(new_url)
    time.sleep(4)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    src = driver.page_source
    soup = BeautifulSoup(src, "html.parser")
    job_elements = soup.find_all('a', href=True)
    if len(job_elements) == 0:
        has_more_listings = False
        break
    for element in job_elements:
        if "/jobs/view/" in element['href']:
            job_links.append("https://www.linkedin.com" + element['href'])
            if len(job_links) >= num_job_listings:
                break

# Close the WebDriver instance
driver.quit()

# Create a DataFrame with job links
today_date = date.today().strftime("%Y%m%d")
df = pd.DataFrame({'hyperlink': job_links, 'Date': today_date})

# Display the DataFrame
print(df)

# Save the DataFrame to a CSV file
df.to_csv("data_analyst_" + today_date + ".csv", index=False)
