BEGIN TRANSACTION;
CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL,
            isbn TEXT
        );
INSERT INTO "books" VALUES(1,'Clean Code','Robert C. Martin',25.5,'9780132350884');
CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        );
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('books',1);
COMMIT;