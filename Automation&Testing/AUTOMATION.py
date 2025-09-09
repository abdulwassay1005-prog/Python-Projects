from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")

# type a message
driver.find_element(By.ID, "my-text-id").clear()
driver.find_element(By.ID, "my-text-id").send_keys("I AM EXTRA COOOOL")

# click submit
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

# verify result text
msg = driver.find_element(By.ID, "message").text
assert "Received!" in msg
print("Test passed:", msg)

driver.quit()
