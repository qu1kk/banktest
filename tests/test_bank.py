import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

# АВТОТЕСТ НА БАГ №1: Комиссия
def test_commission_rounding_down(driver):
    driver.get("http://localhost:8000/?balance=30000&reserved=20001")
    driver.refresh()

    driver.find_element(By.CLASS_NAME, "g-card").click()

    # Используем надежный XPath вместо поиска по индексу
    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    card_input.send_keys("1111222233334444")

    # Ждем, пока поле суммы станет видимым
    amount_input = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
    )
    amount_input.clear()
    amount_input.send_keys("99")

    # Ждем, пока на странице появится элемент, содержащий текст "Комиссия:"
    commission_element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Комиссия:')]"))
    )
    commission_text = commission_element.text

    assert "9 ₽" in commission_text, f"Баг: Неверный расчет комиссии. Ожидали 9 ₽, а получили: {commission_text}"


# АВТОТЕСТ НА БАГ №2: Отрицательная сумма
def test_negative_amount_transfer_not_allowed(driver):
    driver.get("http://localhost:8000/?balance=30000&reserved=20001")
    driver.refresh()

    driver.find_element(By.CLASS_NAME, "g-card").click()

    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    card_input.send_keys("1111222233334444")

    amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
    amount_input.clear()
    amount_input.send_keys("-5000")

    transfer_buttons = driver.find_elements(By.XPATH, "//button//span[text()='Перевести']")

    assert len(transfer_buttons) == 0, f"БАГ ПОДТВЕРЖДЕН: Кнопка 'Перевести' доступна при отрицательной сумме! Найдено кнопок: {len(transfer_buttons)}"
