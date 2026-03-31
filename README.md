# Contact Management System

## 📌 Опис

Веб-додаток для збереження та управління контактами. Побудований за архітектурою MVT. База даних нормалізована до 3NF і містить 7 сутностей.

## ⚙️ Вимоги

- **Мова:** Python 3.11+
- **СКБД:** SQLite 3
- **Фреймворк:** Flask 3.0.2
- **ORM:** Flask-SQLAlchemy 3.1.1
- **Модулі:** Flask-Login 0.6.3, Werkzeug 3.0.1

## 🚀 Встановлення та запуск

1. **Клонування репозиторію:**
```Bash
git clone [Вставте посилання на GitHub]
cd [назва_папки]
```

2. **Створення віртуального оточення та встановлення залежностей:**
```Bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Налаштування конфігурації:**
- У config є шаблон `config.example` (без секретів).
- Скопіюйте його, перейменуйте на `config.py`.
- Відкрийте `config.py` і впишіть надійний пароль у змінну `SECRET_KEY`. _(Примітка: реальний config.py додано у .gitignore)._

4. **Запуск:**
```Bash
python src/backend/app.py
```

Додаток доступний за адресою: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 💾 Відтворення основних сценаріїв (SQL)

ORM автоматично генерує наступні запити:

**1. Створення контакту та прив'язка телефону:**
```SQL
INSERT INTO contacts (user_id, first_name, last_name) VALUES (1, 'Іван', 'Франко');
INSERT INTO phone_numbers (contact_id, number, type) VALUES (1, '+380991234567', 'Mobile');
```

**2. Прив'язка контакту до категорії (зв'язок M:N):**
```SQL
INSERT INTO contact_categories (contact_id, category_id) VALUES (1, 2);
```

**3. Пошук контактів користувача (JOIN):**
```SQL
SELECT c.first_name, c.last_name, p.number 
FROM contacts c
LEFT JOIN phone_numbers p ON c.id = p.contact_id
WHERE c.user_id = 1 AND c.first_name LIKE '%Іван%';
```
