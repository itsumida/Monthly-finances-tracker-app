PRAGMA foreign_keys = ON;

CREATE TABLE member (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE income_category (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE expense_category (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE income (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  transaction_date DATE NOT NULL,
  category_id INTEGER NOT NULL,
  description TEXT,
  amount DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (member_id) REFERENCES member(id),
  FOREIGN KEY (category_id) REFERENCES income_category(id)
);

CREATE TABLE expense (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  transaction_date DATE NOT NULL,
  category_id INTEGER NOT NULL,
  description TEXT,
  amount DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY (member_id) REFERENCES member(id),
  FOREIGN KEY (category_id) REFERENCES expense_category(id)
);

INSERT INTO member VALUES (1, 'Ola');
INSERT INTO member VALUES (2, 'Kari');

INSERT INTO income_category VALUES(1, 'Salary, stipends and pension');
INSERT INTO income_category VALUES(2, 'Study loans');
INSERT INTO income_category VALUES(3, 'Investment income');
INSERT INTO income_category VALUES(4, 'Other income');

INSERT INTO expense_category VALUES(1, 'Housing');
INSERT INTO expense_category VALUES(2, 'Food and groceries');
INSERT INTO expense_category VALUES(3, 'Car and transportation');
INSERT INTO expense_category VALUES(4, 'Clothing and personal upkeep');
INSERT INTO expense_category VALUES(5, 'Utilities');
INSERT INTO expense_category VALUES(6, 'Childcare');
INSERT INTO expense_category VALUES(7, 'Travel');
INSERT INTO expense_category VALUES(8, 'Entertainment and leisure');
INSERT INTO expense_category VALUES(9, 'Healthcare');
INSERT INTO expense_category VALUES(10, 'Memberships and subscriptions');
INSERT INTO expense_category VALUES(11, 'Savings and investments');
INSERT INTO expense_category VALUES(12, 'Other insurance');
INSERT INTO expense_category VALUES(13, 'Other debts');
INSERT INTO expense_category VALUES(14, 'Other expenses');

INSERT INTO income VALUES (1, 1, '2024-03-02', 1, '', 23456);

INSERT INTO expense VALUES (1, 1, '2024-03-04', 1, '', 10000);
INSERT INTO expense VALUES (2, 2, '2024-03-05', 2, 'Kiwi', 2345);
