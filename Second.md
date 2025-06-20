# Отчет о тестировании веб-приложения банка «F-Bank»

**Дата тестирования:** 08.06.2025
**Тестировщик:** Антон Шмелев
**URL для тестирования:** [http://localhost:8000/?balance=10000&reserved=3000](http://localhost:8000/?balance=10000&reserved=3000)

## Результаты тестов

#### Тест 1: Проверка корректного расчета и отображения доступной суммы для перевода

**Цель:** Убедиться, что приложение правильно рассчитывает доступную сумму для перевода (баланс минус резерв) и корректно учитывает комиссию 10%.
**Шаги:**

1. Открыть страницу по адресу: `http://localhost:8000/?balance=10000&reserved=3000`.
2. Нажать на рублевый счет.
3. Ввести корректный номер карты из 16 цифр.
4. Ввести сумму 6000 (находится в диапазоне доступных средств с учетом комиссии).
5. Нажать "Далее"/"Перевести".

   **Ожидаемый результат:** Появляется кнопка для подтверждения перевода, операция доступна.
   **Фактический результат:** Кнопка перевода появляется, перевод возможен, комиссия рассчитывается корректно.
   **Статус:** PASS
---

#### Тест 2: Попытка ввести буквы в поле ввода суммы для перевода

**Цель:** Проверить есть ли валидация вводимых данных в поле перевода.
**Шаги:**

1. Нажать на рублёвый счёт.
2. Ввести корректный номер карты из 16 цифр.
3. Ввести буквы в поле ввода перевода.

   **Ожидаемый результат:** Символы не появляются в поле (ввод блокируется).
   **Фактический результат:** Символы не появляются в поле.
   **Статус:** PASS
   **Комментарий:** Функционально работает верно, однако нет подсказки пользователю (рекомендация — добавить уведомление о разрешённых символах для улучшения UX).
---

#### Тест 3: Попытка ввести буквы и спецсимволы в поле ввода карты

**Цель:** Проверить, допускает ли поле ввода номера карты ввод букв и спецсимволов, и как система реагирует на такой ввод.
**Шаги:**

1. Открыть страницу банка.
2. Нажать на рублёвый счет для открытия поля ввода номера карты.
3. Попробовать ввести буквы (например, «abc») и спецсимволы (например, «!@#\$»).
   **Ожидаемый результат:** Символы не появляются в поле (ввод блокируется).
   **Фактический результат:** Символы не появляются в поле.
   **Статус:** PASS
   **Комментарий:** Функционально работает верно, однако нет подсказки пользователю (рекомендация — добавить уведомление о разрешённых символах для улучшения UX).
---

#### Тест 4: Проверка ввода текста в поле «balance»

**Цель:** Убедиться, что поле баланс не принимает текстовые значения.
**Шаги:**

1. В URL задать параметр: `balance=dsfs`.
   **Ожидаемый результат:** Ошибка валидации или значение по умолчанию.
   **Фактический результат:** На счёте: NaN ₽.
   **Статус:** FAIL

**Баг-репорт:**

* **Severity:** Major
* **Summary:** Нет проверки текстовых значений в параметре URL для баланса.
* **Шаги воспроизведения:**

  1. В URL указать `balance=текст`.
  2. Загрузить страницу.
* **Expected:** Отображается предупреждение или используется значение по умолчанию.
* **Actual:** Отображается некорректно: NaN ₽.
* **Workaround:** Использовать только числовые значения.
* **Fix:** Реализовать валидацию на числовые значения параметров URL.
---

#### Тест 5: Проверка ввода текста в поле «reserved»

**Цель:** Убедиться, что поле резерва не принимает текстовые значения.
**Шаги:**

1. В URL задать параметр: `reserved=fdfd`.
   **Ожидаемый результат:** Ошибка валидации или значение по умолчанию.
   **Фактический результат:** Резерв: NaN ₽.
   **Статус:** FAIL

**Баг-репорт:**

* **Severity:** Major
* **Summary:** Отсутствие проверки текстовых значений для резерва.
* **Шаги воспроизведения:**

  1. В URL указать `reserved=текст`.
  2. Загрузить страницу.
* **Expected:** Предупреждение или нулевое значение по умолчанию.
* **Actual:** Некорректное отображение NaN ₽.
* **Workaround:** Использовать числовые значения.
* **Fix:** Добавить валидацию входных данных.


