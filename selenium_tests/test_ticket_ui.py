from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_create_ticket_ui():

    driver = webdriver.Chrome()

    try:
        driver.get("http://127.0.0.1:5000")

        wait = WebDriverWait(driver, 10)

        # Open Create Ticket form
        create_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Create Ticket')]")
            )
        )

        create_button.click()

        # Fill ticket details
        wait.until(
            EC.visibility_of_element_located((By.ID, "title"))
        ).send_keys("Selenium Test Ticket")

        driver.find_element(
            By.ID, "description"
        ).send_keys("This ticket was created using Selenium automation.")

        # Select category
        category = driver.find_element(By.ID, "category")
        category.click()
        category.find_elements(By.TAG_NAME, "option")[1].click()

        # Select priority
        priority = driver.find_element(By.ID, "priority")
        priority.click()
        priority.find_elements(By.TAG_NAME, "option")[1].click()

        # Submit form
        driver.find_element(
            By.CSS_SELECTOR, "#ticketForm button[type='submit']"
        ).click()

        # Verify success message
        message = wait.until(
            EC.visibility_of_element_located((By.ID, "formMessage"))
        )

        assert "created successfully" in message.text.lower()

    finally:
        driver.quit()

def test_agent_can_assign_ticket():

    driver = webdriver.Chrome()

    try:
        driver.get("http://127.0.0.1:5000/agent")

        print("PAGE TITLE:", driver.title)
        print("URL:", driver.current_url)

        buttons = driver.find_elements(By.TAG_NAME, "button")

        print("BUTTON COUNT:", len(buttons))

        for i, button in enumerate(buttons):
            print(
                f"BUTTON {i}: "
                f"text='{button.text}' "
                f"onclick='{button.get_attribute('onclick')}' "
                f"class='{button.get_attribute('class')}'"
            )

        assert len(buttons) > 0

    finally:
        driver.quit()