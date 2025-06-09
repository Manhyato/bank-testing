import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Общие данные и селекторы ---
BASE_URL = "http://localhost:8000/?balance=30000&reserved=20001"

# Селекторы, основанные на отчете о тестировании
RUB_ACCOUNT_SELECTOR = (By.XPATH, "//div[h2/text()='Рубли']")
CARD_INPUT_SELECTOR = (By.CSS_SELECTOR, "input[placeholder='0000 0000 0000 0000']")
AMOUNT_INPUT_SELECTOR = (By.CSS_SELECTOR, "input[placeholder='1000']")
TRANSFER_BUTTON_SELECTOR = (By.XPATH, "//button[contains(., 'Перевести')]")
ERROR_MESSAGE_SELECTOR = (By.XPATH, "//span[contains(text(), 'Недостаточно средств на счете')]")
COMMISSION_ELEMENT_ID = (By.ID, "comission")

@pytest.mark.xfail(reason="BUG-001: Курсор перемещается в конец поля при редактировании")
def test_cursor_position_fail(driver):
    """Тест 1: Проверяет, что курсор прыгает в конец поля после Backspace."""
    driver.get(f"{BASE_URL}?balance=30000&reserved=20001")
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.visibility_of_element_located(CARD_INPUT_SELECTOR))

    card_input.send_keys("1111222233334444")
    time.sleep(0.5)  # Даем время на форматирование

    # Перемещаем курсор в середину и нажимаем Backspace
    card_input.send_keys(Keys.ARROW_LEFT * 10)
    card_input.send_keys(Keys.BACK_SPACE)
    time.sleep(0.5)

    # Получаем позицию курсора через JS
    cursor_position = driver.execute_script("return arguments[0].selectionStart;", card_input)

    # Тест подтверждает баг: курсор должен быть в конце строки (длина 18).
    assert cursor_position > 15, "Курсор не переместился в конец поля"


@pytest.mark.parametrize(
    "card_to_paste, expected_format",
    [
        ("4000123456789010", "4000 1234 5678 9010"), # Без пробелов
        ("4000 1234 5678 9010", "4000 1234 5678 9010")  # С пробелами
    ]
)
def test_paste_card_number_pass(driver, card_to_paste, expected_format):
    """Тест 2: Проверяет, что вставка номера карты работает корректно."""
    driver.get(f"{BASE_URL}?balance=30000&reserved=20001")
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)
    card_input = wait.until(EC.visibility_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys(card_to_paste)

    assert card_input.get_attribute("value") == expected_format


def test_zero_balance_pass(driver):
    """Тест 3: Проверяет, что интерфейс корректно блокирует перевод при нулевом балансе."""
    driver.get(f"{BASE_URL}?balance=0&reserved=0")
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)

    card_input = wait.until(EC.visibility_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys("1234567812345678")

    amount_input = wait.until(EC.visibility_of_element_located(AMOUNT_INPUT_SELECTOR))
    amount_input.send_keys("100")

    # Проверяем, что появилось сообщение об ошибке
    error_message = wait.until(EC.visibility_of_element_located(ERROR_MESSAGE_SELECTOR))
    assert error_message.is_displayed()

    # Проверяем, что кнопка "Перевести" отсутствует в DOM
    buttons = driver.find_elements(*TRANSFER_BUTTON_SELECTOR)
    assert len(buttons) == 0, "Кнопка 'Перевести' не должна отображаться"


@pytest.mark.xfail(reason="BUG-002: Приложение удаляет точку в дробных числах")
def test_decimal_amount_fail(driver):
    """Тест 4: Проверяет, что приложение удаляет точку из суммы, превращая 150.50 в 15050."""
    driver.get(f"{BASE_URL}?balance=20000.75&reserved=0")
    driver.find_element(*RUB_ACCOUNT_SELECTOR).click()
    wait = WebDriverWait(driver, 5)

    card_input = wait.until(EC.visibility_of_element_located(CARD_INPUT_SELECTOR))
    card_input.send_keys("1234567812345678")

    amount_input = wait.until(EC.visibility_of_element_located(AMOUNT_INPUT_SELECTOR))
    amount_input.send_keys("150.50")

    # Тест подтверждает баг: значение в поле должно стать "15050"
    assert amount_input.get_attribute("value") == "15050"


@pytest.mark.xfail(reason="BUG-003: Потеря точности при обработке больших чисел")
def test_large_number_precision_fail(driver):
    """Тест 5: Проверяет, что баланс, превышающий MAX_SAFE_INTEGER, отображается неверно."""
    large_balance = "9007199254740993"
    expected_incorrect_balance_str = "9007199254740992" # Ожидаемое некорректное значение

    driver.get(f"{BASE_URL}?balance={large_balance}&reserved=0")

    # Находим элемент с балансом и очищаем его от лишних символов
    balance_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(BALANCE_DISPLAY_SELECTOR))
    displayed_text = balance_element.text.replace(" ", "").replace("₽", "").replace("Баланс:", "")

    # Тест подтверждает баг: отображаемое значение должно быть неточным
    assert displayed_text == expected_incorrect_balance_str