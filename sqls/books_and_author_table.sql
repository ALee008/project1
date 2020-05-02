CREATE TABLE authors (
    author_id SERIAL,
    name VARCHAR,
    PRIMARY KEY (author_id)
);

CREATE TABLE book_details (
    isbn VARCHAR NOT NULL UNIQUE,
    title VARCHAR NOT NULL,
    author_id INTEGER REFERENCES authors(author_id) ON DELETE RESTRICT,
    year INTEGER,
    PRIMARY KEY (isbn)
);

CREATE TABLE users (
    user_id SERIAL,
    name VARCHAR UNIQUE,
    password VARCHAR,

    PRIMARY KEY(user_id)
);

CREATE TABLE reviews (
    user_id INT NOT NULL,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    text VARCHAR,
    rating SMALLINT
);



