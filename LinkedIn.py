from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
import sys, time, math

# input: job position, job location, number of results, LinkedIn account username, LinkedIn account password
# setting language to en as default
option = webdriver.ChromeOptions()
option.add_argument("--lang=en-US")
driver = webdriver.Chrome(chrome_options=option)
# driver = webdriver.Chrome()

wait = WebDriverWait(driver, 10)
# converting inputs to url form
jobType = sys.argv[1].strip().replace(' ', '%20')
location = sys.argv[2].strip().replace(' ', '%20').replace(',', '%2C')
# Start searching
driver.get('https://www.linkedin.com/jobs/search/?keywords=' + jobType +
           '&location=' + location)

# Sign in
wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign in")))
driver.find_element_by_link_text("Sign in").click()
time.sleep(1)
usrname = driver.find_element_by_id("username")
usrname.send_keys(sys.argv[4])
pwd = driver.find_element_by_id("password")
pwd.send_keys(sys.argv[5])
driver.find_element_by_tag_name('button').click()
# driver.find_element_by_class_name('msg-overlay-bubble-header__button').click()

# Create workbook
wb = Workbook()
ws = wb.active
# TO DO - rename sheet to searching input of job title
titles = ['Job Title', 'Company', 'Location', 'Content']
ws.append(titles)

jobCount = 0
pageIdx = 1
while jobCount < int(sys.argv[3]):
    jobContainer = wait.until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "job-card-container")))
    # jobContainer = driver.find_elements_by_class_name('job-card-container')
    while len(jobContainer) < 25:
        # TODO: sometimes this line is not working
        driver.execute_script("arguments[0].scrollIntoView();",
                              jobContainer[-1])
        jobContainer = driver.find_elements_by_class_name('job-card-container')
    for job in jobContainer:
        # TODO: need to fix the click position, sometimes it'll direct to company's website
        job.find_element_by_class_name("job-card-list__title").click()
        card = list(job.text.split('\n'))
        info = [card[0]]
        info += card[1:3] if card[1] != " Promoted" else card[2:4]
        content = driver.find_element_by_class_name(
            'jobs-description__container')
        # TODO: some jobs' decription cannot be found in 'span' tage name
        wait.until(EC.visibility_of(
            (content.find_element_by_tag_name('span'))))
        info += [content.find_element_by_tag_name('span').text]
        ws.append(info)
        jobCount += 1
        if jobCount == int(sys.argv[3]): break
    pagination = driver.find_element(By.XPATH,
                                     "//section[@aria-label='pagination']")
    pageIdx += 1
    pagination.find_element(By.XPATH, "//button[@aria-label='Page %d']" %
                            pageIdx).click()
wb.save('LinkedIn.xlsx')
driver.close()
