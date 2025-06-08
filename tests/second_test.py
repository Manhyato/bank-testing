import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

URL = "http://localhost:8000/?balance=30000&reserved=20001"

def open_app(driver, url=URL):
    driver.get(url)
    time.sleep(0.7)

def test_initial_balance_and_reserved(driver):
    """Тест 1: Проверка отображения заданных баланса и резерва"""
    open_app(driver)
    rub_sum = int(driver.find_element(By.ID, "rub-sum").text.replace("'", "").replace(" ", ""))
    rub_reserved = int(driver.find_element(By.ID, "rub-reserved").text.replace("'", "").replace(" ", ""))
    assert rub_sum == 30000
    assert rub_reserved == 20001

def test_open_card_input(driver):
    """Тест 2: Проверка открытия меню ввода номера карты"""
    open_app(driver)
    rub_block = driver.find_element(By.XPATH, "//h2[text()='Рубли']/ancestor::div[@role='button']")
    rub_block.click()
    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    assert card_input.is_displayed()

def test_card_number_length_validation(driver):
    """Тест 3: Проверка валидации длины номера карты (меньше и больше 16 цифр)"""
    open_app(driver)
    rub_block = driver.find_element(By.XPATH, "//h2[text()='Рубли']/ancestor::div[@role='button']")
    rub_block.click()
    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    
    card_input.clear()
    card_input.send_keys("1234 5678 9101 112") 
    card_input.send_keys(Keys.ENTER)
    time.sleep(0.5)
    assert not driver.find_elements(By.XPATH, "//input[@placeholder='1000']"), "Поле суммы появилось при <16 цифрах"

    card_input.clear()
    card_input.send_keys("1111 1111 1111 1111 1") 
    card_input.send_keys(Keys.ENTER)
    time.sleep(0.5)
    assert not driver.find_elements(By.XPATH, "//input[@placeholder='1000']"), "Поле суммы появилось при >16 цифрах"


def test_exceeding_transfer_amount(driver):
    """Тест 4: Проверка превышения доступной суммы перевода"""
    open_app(driver)
    rub_block = driver.find_element(By.XPATH, "//h2[text()='Рубли']/ancestor::div[@role='button']")
    rub_block.click()
    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    card_input.send_keys("1111 1111 1111 1111")
    card_input.send_keys(Keys.ENTER)
    time.sleep(0.3)
    amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
    amount_input.send_keys("999999")
    amount_input.send_keys(Keys.ENTER)
    time.sleep(0.5)
    assert driver.find_element(By.XPATH, "//*[contains(text(), 'Недостаточно средств')]").is_displayed()

def test_negative_transfer_amount(driver):
    """Тест 5: Проверка обработки отрицательной суммы перевода"""
    open_app(driver)
    rub_block = driver.find_element(By.XPATH, "//h2[text()='Рубли']/ancestor::div[@role='button']")
    rub_block.click()
    card_input = driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    card_input.send_keys("2222 2222 2222 2222")
    card_input.send_keys(Keys.ENTER)
    time.sleep(0.3)
    amount_input = driver.find_element(By.XPATH, "//input[@placeholder='1000']")
    amount_input.clear()
    amount_input.send_keys("-1000")
    time.sleep(1.0)
    submit_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Перевести')]")
    assert not submit_buttons, "Кнопка 'Перевести' не должна отображаться при отрицательной сумме"
