DROP TABLE IF EXISTS questions;
CREATE TABLE questions (
    qid INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL);

DROP TABLE IF EXISTS answer_options;
CREATE TABLE answer_options (
    oid INTEGER PRIMARY KEY,
    option_text TEXT NOT NULL);

DROP TABLE IF EXISTS answers;
CREATE TABLE answers (
    oid INTEGER PRIMARY KEY,
    qid INTEGER,
    if_correct BOOLEAN,
    FOREIGN KEY (qid) REFERENCES questions(qid) ON DELETE CASCADE);

INSERT INTO questions (qid, question_text)
VALUES (0, 'Question 1'),
       (1, 'Question 2'),
       (2, 'Question 3');

INSERT INTO answer_options (oid, option_text)
VALUES (0, 'Option 1.1'),
       (1, 'Option 1.2'),
       (2, 'Option 1.3'),
       (3, 'Option 2.1'),
       (4, 'Option 2.2'),
       (5, 'Option 2.3'),
       (6, 'Option 3.1'),
       (7, 'Option 3.2'),
       (8, 'Option 3.3');

INSERT INTO answers (oid, qid, if_correct)
VALUES (0, 0, TRUE),
       (1, 0, FALSE),
       (2, 0, FALSE),
       (3, 1, FALSE),
       (4, 1, TRUE),
       (5, 1, FALSE),
       (6, 2, FALSE),
       (7, 2, FALSE),
       (8, 2, TRUE);
