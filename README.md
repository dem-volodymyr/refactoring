# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django djangorestframework drf-spectacular

# Create Django project and app
django-admin startproject slot_machine_api
cd slot_machine_api

# Load initial symbols data (after creating fixture)
python manage.py loaddata symbols

# Run the development server
python manage.py runserver

# Refactoring (Lab 2)

## Проведені зміни

1. **Виділення констант**
   - Магічні числа (кількість барабанів, мінімальна кількість символів для виграшу, початкові баланси тощо) винесено у константи на початку `services.py`.

2. **Розбиття довгих методів**
   - Метод `check_wins` класу `ReelService` розбитий: логіка перевірки виграшу для одного рядка винесена у допоміжний метод `_row_wins`.
   - У класі `SlotMachineService` виділено допоміжні методи для оновлення балансу гравця та створення запису про спін.

3. **Покращення структури класів**
   - Зменшено дублювання коду, підвищено читабельність та підтримуваність.
   - Додано коментарі до основних методів та констант.

4. **Покращення читабельності**
   - Додано пояснювальні коментарі до ключових ділянок коду.

## Як перевірити
- Всі існуючі тести мають проходити без змін.
- Функціонал гри не змінено, лише покращено структуру та читабельність коду.