# Copyright (C) 2018 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.

import sqlite3

conn = sqlite3.connect('database_blog.db')
c = conn.cursor()

c.execute('''
            CREATE TABLE tbl_category (
                ID   INTEGER PRIMARY KEY AUTOINCREMENT
                             NOT NULL
                             UNIQUE,
                name TEXT    NOT NULL
            );
            ''')

c.execute('''
            CREATE TABLE tbl_post (
                ID       INTEGER PRIMARY KEY AUTOINCREMENT
                                 UNIQUE
                                 NOT NULL,
                title    TEXT    NOT NULL,
                date     TEXT    NOT NULL,
                category INTEGER REFERENCES tbl_category (ID) ON DELETE SET NULL
                                                              ON UPDATE CASCADE
            );
            ''')

c.execute('''
            CREATE TABLE tbl_post_to_tags (
                post_ID INTEGER REFERENCES tbl_post (ID) ON UPDATE CASCADE,
                tag_ID  INTEGER REFERENCES tbl_tag (ID) ON UPDATE CASCADE
            );
            ''')

c.execute('''
            CREATE TABLE tbl_tag (
                ID   INTEGER PRIMARY KEY AUTOINCREMENT
                             NOT NULL
                             UNIQUE,
                name TEXT    NOT NULL
            );
            ''')

conn.commit()
conn.close()