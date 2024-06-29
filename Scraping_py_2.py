
# Import the necessary modules for web scraping and data manipulation
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import random
from datetime import date


# In[2]:


# Read the CSV file containing overall job data from Scrap code 1
All_Data_All_Job_Page = pd.read_csv(r"Path to job data csv file from Scrap code 1")

# Extract the 'Link' column from the loaded DataFrame
All_Links = All_Data_All_Job_Page['hyperlink']

# Get today's date in the format 'YYYYMMDD'
today_date = date.today().strftime("%Y%m%d")

# Create an empty DataFrame to store all job details
All_Job_Details = pd.DataFrame()


# In[3]:


def driver_start():
    DRIVER_PATH = r"Replace with the actual path to the driver"  # Replace with the actual path to the driver
    driver = webdriver.Chrome()  # Create a Chrome web driver instance

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


# In[4]:


# Function to scroll through the webpage and load more content
def scroll_func():
    start = time.time()  # Record the starting time of scrolling

    # Define initial and final scroll positions
    initialScroll = 0
    finalScroll = 92

    while True:
        # Execute JavaScript to scroll the window
        driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
        
        # Update scroll positions for the next iteration
        initialScroll = finalScroll
        finalScroll += 92

        # Pause execution for a few seconds to allow data to load
        time.sleep(3)  # Adjust this based on your needs and internet speed

        end = time.time()  # Get the current time

        # Limit scrolling duration to 5 seconds
        if round(end - start) > 5:
            break  # Exit the loop if scrolling duration exceeds 5 seconds


# In[19]:


# Create an empty DataFrame to store failed links
Failed_DF = pd.DataFrame()

# Start the web driver and perform LinkedIn login
driver = driver_start()

# Iterate through the profile URLs in All_Links
for profile_url in All_Links[34:]:
    driver.get(profile_url)
    time.sleep(random.randint(5, 7))
    
    # Scroll to load more content
    scroll_func()
    
    # Get the updated page source
    src = driver.page_source
    
    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(src, "html.parser")
    
    try:
        # Extract job details from the page
        Job_Name = soup.findAll('div', {'class': 'display-flex justify-space-between align-items-center'})[0].text.strip() if soup.findAll('div', {'class': 'display-flex justify-space-between align-items-center'}) else None
        Job_Primary_Details = soup.findAll('div', {'class': 'jobs-unified-top-card__primary-description'})[0].text.strip() if soup.findAll('div', {'class': 'jobs-unified-top-card__primary-description'}) else None
        Job_Contract = soup.findAll('li', {'class': 'jobs-unified-top-card__job-insight'})[0].text.strip() if soup.findAll('li', {'class': 'jobs-unified-top-card__job-insight'}) else None
        Job_Details = soup.find("div", {"id": "job-details"}).text.strip() if soup.find("div", {"id": "job-details"}) else None
        skills = ""
        Skills_all = soup.findAll('a', {'class': 'app-aware-link job-details-how-you-match__skills-item-subtitle t-14 overflow-hidden'})
        for each in Skills_all[:2]:
            skills = skills + each.text.strip().replace(", and", ",") + " ,"
        
        # Create a DataFrame for the job details
        Job_Details_DF = pd.DataFrame({'Link': [profile_url],
                                       'Name': [Job_Name],
                                       'Primary_Detail': [Job_Primary_Details],
                                       'Contract': [Job_Contract],
                                       'Secondary_Detail': [Job_Details],
                                       'Skills': [skills]})
        
        # Concatenate the job details DataFrame with the existing data
        All_Job_Details = pd.concat([All_Job_Details, Job_Details_DF])
        
        # Remove duplicate rows based on the 'Link' column
        All_Job_Details = All_Job_Details.drop_duplicates(subset='Link')
        
        # Save the job details DataFrame to a CSV file
        All_Job_Details.to_csv("data_analyst_jobs" + today_date + ".csv", index=False)
    except Exception as e:
        # Handle failed links
        print("Failed for these links")
        print(profile_url)
        Failed_DF_url = pd.DataFrame({'Link_failed': [profile_url]})
        Failed_DF = pd.concat([Failed_DF, Failed_DF_url])
        Failed_DF = Failed_DF.drop_duplicates(subset='Link')
        Failed_DF.to_csv("Failed_DF_" + today_date + ".csv", index=False)
        time.sleep(70)
    
    # Sleep for a random time
    sleep_time = random.randint(10, 22)
    print("Sleeping for", sleep_time)
    time.sleep(sleep_time)

# Close the web driver
driver.close()
