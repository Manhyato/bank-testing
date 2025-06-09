import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform

# --- Общие данные и селекторы ---
BASE_URL = "http://localhost:8000/?balance=30000&reserved=20001"
CARD_NUMBER = "1234567812345678"

RUB_ACCOUNT_SELECTOR = (By.XPATH, "//div[h2/text()='Рубли']")
CARD_INPUT_SELECTOR = (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
AMOUNT_INPUT_SELECTOR = (By.XPATH, "//input[@placeholder='1000']")
TRANSFER_BUTTON_SELECTOR = (By.XPATH, "//button[contains(., 'Перевести')]")
ERROR_MESSAGE_SELECTOR = (By.XPATH, "//span[contains(text(), 'Недостаточно средств на счете')]")
COMMISSION_ELEMENT_ID = (By.ID, "comission")


def clear_input_field(element):
    control_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
    element.send_keys(control_key + "a")
    element.send_keys(Keys.BACK_SPACE)


@pytest.mark.xfail(reason="BUG-001: Комиссия для сумм < 100 некорректно рассчитывается как 0")
def test_incorrect_commission_fail(driver):
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys(CARD_NUMBER)
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))
    clear_input_field(amount_input)
    amount_input.send_keys("50")
    wait.until(EC.text_to_be_present_in_element(COMMISSION_ELEMENT_ID, "0"))
    commission_element = driver.find_element(*COMMISSION_ELEMENT_ID)
    assert commission_element.text == "5"

def test_card_input_only_digits_pass(driver):
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    card_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys("1234abcd5678!@#$")
    assert card_input.get_attribute("value") == "1234 5678"

@pytest.mark.xfail(reason="BUG-002: Приложение позволяет переводить отрицательные суммы")
def test_negative_amount_transfer_fail(driver):
    """Тест 3: Проверка реакции на ввод отрицательной суммы."""
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys(CARD_NUMBER)
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))
    clear_input_field(amount_input)
    amount_input.send_keys("-1000")

    wait.until(EC.invisibility_of_element_located(ERROR_MESSAGE_SELECTOR))

    transfer_button = driver.find_element(*TRANSFER_BUTTON_SELECTOR)
    assert transfer_button.is_displayed(), "Кнопка 'Перевести' должна быть видна для отрицательной суммы (это баг)"

def test_insufficient_funds_pass(driver):
    """Тест 4: Проходит, т.к. блокировка при нехватке средств работает."""
    driver.get(BASE_URL)
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys(CARD_NUMBER)
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))
    clear_input_field(amount_input)
    amount_input.send_keys("9500")

    error_message = wait.until(EC.visibility_of_element_located(ERROR_MESSAGE_SELECTOR))
    assert error_message.is_displayed(), "Сообщение о недостатке средств не отобразилось"

@pytest.mark.xfail(reason="BUG-003: Отрицательный резерв увеличивает доступный баланс")
def test_negative_reserved_value_fail(driver):
    """Тест 5: Проверка реакции на отрицательное значение в резерве."""
    driver.get("http://localhost:8000/?balance=10000&reserved=-1000")
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.presence_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys(CARD_NUMBER)
    amount_input = wait.until(EC.presence_of_element_located(AMOUNT_INPUT_SELECTOR))
    clear_input_field(amount_input)
    amount_input.send_keys("9500")

    wait.until(EC.invisibility_of_element_located(ERROR_MESSAGE_SELECTOR))

    transfer_button = driver.find_element(*TRANSFER_BUTTON_SELECTOR)
    assert transfer_button.is_displayed(), "Кнопка 'Перевести' должна быть видна (это баг)"