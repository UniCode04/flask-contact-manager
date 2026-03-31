from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Проміжна таблиця для зв'язку M:N (Contact <-> Category)
contact_categories = db.Table('contact_categories',
    db.Column('contact_id', db.Integer, db.ForeignKey('contacts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)

# Сутність User
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contacts = db.relationship('Contact', backref='owner', lazy=True, cascade="all, delete-orphan")
    categories = db.relationship('Category', backref='owner', lazy=True, cascade="all, delete-orphan")

# Сутність Contact
class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Зв'язки 1:N
    phones = db.relationship('PhoneNumber', backref='contact', lazy=True, cascade="all, delete-orphan")
    emails = db.relationship('EmailAddress', backref='contact', lazy=True, cascade="all, delete-orphan")
    addresses = db.relationship('PhysicalAddress', backref='contact', lazy=True, cascade="all, delete-orphan")
    # Зв'язок M:N
    categories = db.relationship('Category', secondary=contact_categories, lazy='subquery', backref=db.backref('contacts', lazy=True))

# Сутність Category
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=False)

# Сутність PhoneNumber
class PhoneNumber(db.Model):
    __tablename__ = 'phone_numbers'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), default='Mobile')

# Сутність EmailAddress
class EmailAddress(db.Model):
    __tablename__ = 'email_addresses'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), default='Personal')

# Сутність PhysicalAddress
class PhysicalAddress(db.Model):
    __tablename__ = 'physical_addresses'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
