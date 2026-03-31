-- Дамп структури БД
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    notes TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE phone_numbers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    number VARCHAR(20) NOT NULL,
    type VARCHAR(20) DEFAULT 'Mobile',
    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

-- Seed дані (Приклад)
INSERT INTO users (username, password_hash) VALUES ('admin', 'pbkdf2:sha256:260000$...');
INSERT INTO contacts (user_id, first_name, last_name) VALUES (1, 'Іван', 'Іванов');
