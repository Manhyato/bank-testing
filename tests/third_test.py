import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException 

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(2)
    yield driver
    driver.quit()

def open_app(driver, url_params=""):
    driver.get(f"{BASE_URL}/?{url_params}")

def click_rub_account(driver):
    rub_block = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//h2[text()='Рубли']/ancestor::div[@role='button']"))
    )
    rub_block.click()

def enter_card_and_amount(driver, card_number, amount):
    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    card_input.clear()
    card_input.send_keys(card_number)
    card_input.send_keys(Keys.ENTER)

    amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
    amount_input.clear()
    amount_input.send_keys(str(amount))
    amount_input.send_keys(Keys.ENTER)

# Тест 1: Проверка корректного расчета доступной суммы
def test_correct_transfer_flow(driver):
    open_app(driver, "balance=10000&reserved=3000")
    click_rub_account(driver)
    enter_card_and_amount(driver, "1234 5678 9012 3456", 6000)

    confirm_btn = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//button[contains(., 'Перевести')]"))
    )
    assert confirm_btn.is_displayed(), "Кнопка перевода должна быть видна при корректных данных"

# Тест 2: Успешный перевод допустимой суммы
import time
from selenium.common.exceptions import TimeoutException, NoAlertPresentException

def test_successful_transfer(driver):
    open_app(driver, "balance=10000&reserved=3000")
    click_rub_account(driver)
    enter_card_and_amount(driver, "1111 2222 3333 4444", 5000)

    # Подождём alert с таймаутом 15 секунд
    try:
        alert = WebDriverWait(driver, 15).until(EC.alert_is_present())
    except TimeoutException:
        assert False, "Alert не появился в течение 15 секунд после перевода"

    # Считаем, что alert появился — получаем текст и принимаем
    alert_text = alert.text.lower()
    alert.accept()

    # Проверяем, что в тексте alert есть нужные слова
    assert "выполнен" in alert_text or "принят банком" in alert_text, \
        f"Ожидался успешный перевод, но получили: {alert_text}"


# Тест 3: Попытка ввести буквы и спецсимволы в номер карты
def test_invalid_card_input_blocked(driver):
    open_app(driver)
    click_rub_account(driver)

    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    card_input.send_keys("abc!@#$")
    entered = card_input.get_attribute("value")

    assert entered.strip() == "", "Поле карты не должно принимать буквы или спецсимволы"

# Тест 4: Ввод текста в поле balance — ожидаемый баг
def test_invalid_balance_input(driver):
    open_app(driver, "balance=dsfs&reserved=1000")
    rub_sum_text = driver.find_element(By.ID, "rub-sum").text

    assert "NaN" not in rub_sum_text, "NaN не должен отображаться — нужна валидация на числовое значение"
    pytest.fail("BUG: Нет валидации для текстового значения balance")

# Тест 5: Ввод текста в поле reserved — ожидаемый баг
def test_invalid_reserved_input(driver):
    open_app(driver, "balance=1000&reserved=fdfd")
    reserved_text = driver.find_element(By.ID, "rub-reserved").text

    assert "NaN" not in reserved_text, "NaN не должен отображаться — нужна валидация на числовое значение"
    pytest.fail("BUG: Нет валидации для текстового значения reserved")
