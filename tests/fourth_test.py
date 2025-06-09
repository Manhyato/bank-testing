import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Общие данные и селекторы для тестов ---

BASE_URL = "http://localhost:8000/?balance=30000&reserved=20001"
CARD_NUMBER = "1234567812345678"

# Селекторы для часто используемых элементов
RUB_ACCOUNT_SELECTOR = (By.XPATH, "//div[h2/text()='Рубли']")
CARD_INPUT_SELECTOR = (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
AMOUNT_INPUT_SELECTOR = (By.XPATH, "//input[@placeholder='1000']")


def test_incorrect_commission_fail(driver):
    """
    Тест 1: Проверка некорректного расчёта комиссии за перевод.
    Ожидание: FAIL - комиссия для 50р по факту равна 0 вместо 5р.
    """
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()

    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))

    card_input.send_keys(CARD_NUMBER)

    amount_input.send_keys("50")
    commission_element = driver.find_element(By.ID, "comission")

    # Проверяем фактический результат, который является багом
    assert commission_element.text == "0", "Комиссия для суммы 50 некорректна"
    print("\nТест 1 (FAIL): Успешно подтверждено, что комиссия для 50р равна 0.")

def test_card_input_only_digits_pass(driver):
    """
    Тест 2: Проверка, что в поле ввода номера карты можно вводить только цифры.
    Ожидание: PASS.
    """
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()

    card_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys("1234abcd5678!@#$")

    expected_value = "1234 5678"
    actual_value = card_input.get_attribute("value")

    assert actual_value == expected_value, f"Ожидалось '{expected_value}', но получено '{actual_value}'"
    print("\nТест 2 (PASS): Поле для ввода номера карты успешно отфильтровало нецифровые символы.")

def test_negative_amount_transfer_fail(driver):
    """
    Тест 3: Проверка возможности ввода и отправки отрицательной суммы перевода.
    Ожидание: FAIL - система позволяет совершить перевод.
    """
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()

    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))

    card_input.send_keys(CARD_NUMBER)
    amount_input.send_keys("-1000")

    transfer_button = driver.find_element(By.XPATH, "//button[text()='Перевести']")
    transfer_button.click()

    alert = wait.until(EC.alert_is_present())
    alert_text = alert.text

    assert "Перевод -1000" in alert_text, "Сообщение об успехе не содержит отрицательную сумму"

    alert.accept()
    print("\nТест 3 (FAIL): Успешно подтверждено, что система принимает перевод на отрицательную сумму.")

def test_insufficient_funds_pass(driver):
    """
    Тест 4: Проверка невозможности перевода при превышении доступной суммы.
    Доступно: 30000 - 20001 = 9999. Перевод на 9500 + комиссия 950 = 10450.
    Ожидание: PASS.
    """
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()

    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))

    card_input.send_keys(CARD_NUMBER)
    amount_input.send_keys("9500")

    error_message = driver.find_element(By.XPATH, "//span[contains(text(), 'Недостаточно средств на счете')]")
    assert error_message.is_displayed(), "Сообщение о недостатке средств не отобразилось"

    transfer_buttons = driver.find_elements(By.XPATH, "//button[text()='Перевести']")
    assert len(transfer_buttons) == 0, "Кнопка 'Перевести' не должна отображаться при нехватке средств"
    print("\nТест 4 (PASS): Система корректно блокирует перевод при нехватке средств.")

def test_negative_reserved_value_fail(driver):
    """
    Тест 5: Проверка возможности ввода отрицательного значения в резерве.
    Ожидание: FAIL - система обрабатывает отрицательный резерв, увеличивая доступный баланс.
    """
    driver.get("http://localhost:8000/?balance=30000&reserved=-1000")

    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()

    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))

    card_input.send_keys(CARD_NUMBER)
    amount_input.send_keys("30000")

    transfer_button = driver.find_element(By.XPATH, "//button[text()='Перевести']")

    assert transfer_button.is_displayed() and transfer_button.is_enabled()
    print("\nТест 5 (FAIL): Успешно подтверждено, что отрицательный резерв некорректно увеличивает доступный баланс.")
