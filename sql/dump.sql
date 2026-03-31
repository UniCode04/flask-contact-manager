PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username)
);
INSERT INTO users VALUES(1,'test_user','scrypt:32768:8:1$224144lOlfF3arzH$4de9df2542b7758853afc8edd4a0e07e439690a9795efaf5c66318d2119c9478bba2aad680847ed1c3b0b2968458dd505e676bad635b8bf533ef1eefa15821f6');
CREATE TABLE contacts (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50), 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
INSERT INTO contacts VALUES(1,1,'Віктор','Мельник','Нещодавно одружився з Лізою. Треба не забути привітати з річницею!');
INSERT INTO contacts VALUES(2,1,'Єлизавета','Мельник','Дружина Віті.');
INSERT INTO contacts VALUES(3,1,'Андрій','Коваленко','Колега з минулої роботи (разом налаштовували обладнання MikroTik). Фанат кібербезпеки та Arch Linux.');
CREATE TABLE categories (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
INSERT INTO categories VALUES(1,1,'Друзі');
INSERT INTO categories VALUES(2,1,'Робота');
CREATE TABLE contact_categories (
	contact_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	PRIMARY KEY (contact_id, category_id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE CASCADE
);
INSERT INTO contact_categories VALUES(1,1);
INSERT INTO contact_categories VALUES(2,1);
INSERT INTO contact_categories VALUES(3,2);
CREATE TABLE phone_numbers (
	id INTEGER NOT NULL, 
	contact_id INTEGER NOT NULL, 
	number VARCHAR(20) NOT NULL, 
	type VARCHAR(20), 
	PRIMARY KEY (id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE CASCADE
);
INSERT INTO phone_numbers VALUES(1,1,'+380501112233','Домашній');
INSERT INTO phone_numbers VALUES(2,2,'+380669998877','Домашній');
INSERT INTO phone_numbers VALUES(3,2,'+380440001122','Робочий');
INSERT INTO phone_numbers VALUES(4,3,'+380674445566','Домашній');
INSERT INTO phone_numbers VALUES(5,3,'+380445556677','Робочий');
CREATE TABLE email_addresses (
	id INTEGER NOT NULL, 
	contact_id INTEGER NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	type VARCHAR(20), 
	PRIMARY KEY (id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE CASCADE
);
INSERT INTO email_addresses VALUES(1,1,'vitya.m@example.com','Personal');
INSERT INTO email_addresses VALUES(2,2,'liza.melnyk@example.com','Personal');
INSERT INTO email_addresses VALUES(3,3,'admin@mikrotik-net.ua','Personal');
CREATE TABLE physical_addresses (
	id INTEGER NOT NULL, 
	contact_id INTEGER NOT NULL, 
	address VARCHAR(200) NOT NULL, 
	city VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(contact_id) REFERENCES contacts (id) ON DELETE CASCADE
);
INSERT INTO physical_addresses VALUES(1,1,'вул. Хрещатик, 15, кв. 42','Київ');
INSERT INTO physical_addresses VALUES(2,2,'вул. Хрещатик, 15, кв. 42','Київ');
INSERT INTO physical_addresses VALUES(3,3,'просп. Соборний, 100','Запоріжжя');
COMMIT;
