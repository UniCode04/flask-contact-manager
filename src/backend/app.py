import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from src.backend.models import db, User, Contact, PhoneNumber, EmailAddress, PhysicalAddress, Category
from config.config import Config
from sqlalchemy import or_

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = ''
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all() # Створення таблиць

# --- АВТОРИЗАЦІЯ ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Захист логіну: лише A-Z, 0-9 та _
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', username):
            flash('Логін має містити від 3 до 50 символів (лише латиниця, цифри та підкреслення).', 'danger')
            return redirect(url_for('register'))

        # Захист пароля: перевірка надійності (довжина)
        if len(password) < 8 or len(password) > 100:
            flash('Пароль має містити від 8 до 100 символів.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Користувач з таким іменем вже існує.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Реєстрація успішна! Тепер увійдіть.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Швидка валідація
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', username) or not password:
            flash('Невірні дані для входу.', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        # check_password_hash безпечно порівнює введений текст із хешем у базі
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Невірні дані для входу.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def validate_contact_form(form):
    # Перевіряє дані форми на відповідність правилам безпеки.

    name_regex = re.compile(r'^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\s()0-9\-]+$')

    # Ім'я та Прізвище
    first_name = form.get('first_name', '').strip()
    if len(first_name) > 50: return "Ім'я не може перевищувати 50 символів."
    if not name_regex.match(first_name): return "Ім'я містить недопустимі символи."

    last_name = form.get('last_name', '').strip()
    if last_name:
        if len(last_name) > 50: return "Прізвище не може перевищувати 50 символів."
        if not name_regex.match(last_name): return "Прізвище містить недопустимі символи."

    # Телефони
    phone_regex = re.compile(r'^\+?\d{5,15}$')
    phone_home = form.get('phone_home', '')
    if not phone_regex.match(phone_home): return "Домашній телефон введено некоректно."

    phone_work = form.get('phone_work', '').strip()
    if phone_work and not phone_regex.match(phone_work): return "Робочий телефон введено некоректно."

    # Email
    email = form.get('email', '').strip()
    if email and len(email) > 100: return "Email не може перевищувати 100 символів."

    # Перевірка на небезпечні символи (XSS/SQLi) для текстових полів
    xss_sqli_pattern = re.compile(r'[<>="\'%;]')

    fields_to_check = {
        'Місто': (form.get('city', ''), 50),
        'Адреса': (form.get('address', ''), 200),
        'Категорія': (form.get('category', ''), 50),
        'Примітки': (form.get('notes', ''), 100)
    }

    for field_name, (value, max_length) in fields_to_check.items():
        if value:
            if len(value) > max_length:
                return f"{field_name} не може перевищувати {max_length} символів."
            if xss_sqli_pattern.search(value):
                return f"Поле '{field_name}' містить небезпечні символи."

    return None

# --- CRUD ОПЕРАЦІЇ ---
@app.route('/')
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'first_name')

    # Валідація пошукового запиту (захист від XSS та SQLi символів)
    if search_query:
        if len(search_query) > 50:
            flash('Пошуковий запит занадто довгий.', 'warning')
            search_query = search_query[:50] # Обрізаємо зайве

        if re.search(r'[<>="\'%;]', search_query):
            flash('У пошуку використано недопустимі символи.', 'danger')
            search_query = '' # Скидаємо небезпечний запит
            return redirect(url_for('index')) # Перезавантажуємо сторінку без небезпечного запиту

    query = Contact.query.filter_by(user_id=current_user.id)

    if search_query:
        query = query.filter(
            or_(
                Contact.first_name.ilike(f'%{search_query}%'),
                Contact.last_name.ilike(f'%{search_query}%')
            )
        )

    if sort_by == 'last_name':
        query = query.order_by(Contact.last_name.asc())
    elif sort_by == 'city':
        # outerjoin дозволяє сортувати за полем з іншої таблиці,
        # не втрачаючи контакти без адреси
        query = query.outerjoin(PhysicalAddress).order_by(PhysicalAddress.city.asc())
    else:
        query = query.order_by(Contact.first_name.asc())

    contacts = query.all()
    return render_template('index.html', contacts=contacts, search_query=search_query, sort_by=sort_by)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    if request.method == 'POST':
        error_msg = validate_contact_form(request.form)
        if error_msg:
            flash(error_msg, 'danger')
            return redirect(request.url)

        try:
            contact = Contact(
                user_id=current_user.id,
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                notes=request.form.get('notes')
            )
            db.session.add(contact)
            db.session.flush() # Отримуємо ID

            # Телефони
            if request.form.get('phone_home'):
                db.session.add(PhoneNumber(contact_id=contact.id, number=request.form.get('phone_home'), type='Домашній'))
            if request.form.get('phone_work'):
                db.session.add(PhoneNumber(contact_id=contact.id, number=request.form.get('phone_work'), type='Робочий'))

            # Email
            email = request.form.get('email')
            if email:
                db.session.add(EmailAddress(contact_id=contact.id, email=email))

            # Фізична адреса
            city = request.form.get('city')
            address = request.form.get('address')
            if city or address:
                db.session.add(PhysicalAddress(contact_id=contact.id, city=city or '', address=address or ''))

            # Категорія
            category_name = request.form.get('category', '').strip()
            if category_name:
                # Шукаємо існуючу категорію користувача або створюємо нову
                cat = Category.query.filter_by(user_id=current_user.id, name=category_name).first()
                if not cat:
                    cat = Category(user_id=current_user.id, name=category_name)
                    db.session.add(cat)
                contact.categories.append(cat) # SQLAlchemy сама заповнить проміжну таблицю contact_categories!

            db.session.commit()
            flash('Контакт успішно додано!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Помилка при додаванні.', 'danger')
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = db.get_or_404(Contact, id)
    if contact.user_id != current_user.id:
        return redirect(url_for('index'))

    if request.method == 'POST':
        error_msg = validate_contact_form(request.form)
        if error_msg:
            flash(error_msg, 'danger')
            return redirect(request.url)

        contact.first_name = request.form.get('first_name')
        contact.last_name = request.form.get('last_name')
        contact.notes = request.form.get('notes')

        # Оновлення телефонів
        def update_phone(phone_type, form_field_name):
            new_number = request.form.get(form_field_name)
            phone = PhoneNumber.query.filter_by(contact_id=contact.id, type=phone_type).first()
            if new_number:
                if phone: phone.number = new_number
                else: db.session.add(PhoneNumber(contact_id=contact.id, number=new_number, type=phone_type))
            elif phone: db.session.delete(phone)

        update_phone('Домашній', 'phone_home')
        update_phone('Робочий', 'phone_work')

        # Оновлення Email
        new_email = request.form.get('email')
        email_obj = EmailAddress.query.filter_by(contact_id=contact.id).first()
        if new_email:
            if email_obj: email_obj.email = new_email
            else: db.session.add(EmailAddress(contact_id=contact.id, email=new_email))
        elif email_obj: db.session.delete(email_obj)

        # Оновлення адреси
        new_city = request.form.get('city')
        new_address = request.form.get('address')
        addr_obj = PhysicalAddress.query.filter_by(contact_id=contact.id).first()
        if new_city or new_address:
            if addr_obj:
                addr_obj.city = new_city or ''
                addr_obj.address = new_address or ''
            else: db.session.add(PhysicalAddress(contact_id=contact.id, city=new_city or '', address=new_address or ''))
        elif addr_obj: db.session.delete(addr_obj)

        # Оновлення категорії
        contact.categories.clear() # Очищаємо старі зв'язки
        category_name = request.form.get('category', '').strip()
        if category_name:
            cat = Category.query.filter_by(user_id=current_user.id, name=category_name).first()
            if not cat:
                cat = Category(user_id=current_user.id, name=category_name)
                db.session.add(cat)
            contact.categories.append(cat)

        db.session.commit()
        flash('Контакт оновлено.', 'success')
        return redirect(url_for('index'))

    phone_home = next((p.number for p in contact.phones if p.type == 'Домашній'), '')
    phone_work = next((p.number for p in contact.phones if p.type == 'Робочий'), '')
    email = contact.emails[0].email if contact.emails else ''
    city = contact.addresses[0].city if contact.addresses else ''
    address = contact.addresses[0].address if contact.addresses else ''
    category = contact.categories[0].name if contact.categories else ''

    return render_template('edit.html', contact=contact, phone_home=phone_home, phone_work=phone_work,
                           email=email, city=city, address=address, category=category)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_contact(id):
    contact = db.get_or_404(Contact, id)
    # Перевірка безпеки: видаляємо лише в тому випадку, якщо контакт належить поточному користувачеві
    if contact.user_id == current_user.id:
        db.session.delete(contact)
        db.session.commit()
        flash('Контакт видалено.', 'success')
    return redirect(url_for('index'))

    phone_home = next((p.number for p in contact.phones if p.type == 'Домашній'), '')
    phone_work = next((p.number for p in contact.phones if p.type == 'Робочий'), '')

    return render_template('edit.html', contact=contact, phone_home=phone_home, phone_work=phone_work)

if __name__ == '__main__':
    app.run(debug=True)
