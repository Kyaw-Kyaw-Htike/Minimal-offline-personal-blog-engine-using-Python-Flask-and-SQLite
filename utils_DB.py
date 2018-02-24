# Copyright (C) 2018 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.

import sqlite3

class cls_utils_DB:

    path_db = 'database_blog.db'

    def open(self):
        self.conn = sqlite3.connect(self.path_db)
        self.c = self.conn.cursor()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def create_new_db(self):
        self.open()
        self.c.execute('''
                    CREATE TABLE tbl_category (
                        ID   INTEGER PRIMARY KEY AUTOINCREMENT
                                     NOT NULL
                                     UNIQUE,
                        name TEXT    NOT NULL
                    );
                    ''')

        self.c.execute('''
                    CREATE TABLE tbl_post (
                        ID       INTEGER PRIMARY KEY AUTOINCREMENT
                                         UNIQUE
                                         NOT NULL,
                        name    TEXT    NOT NULL,
                        title    TEXT    NOT NULL,
                        content    TEXT    NOT NULL,
                        date     TEXT    NOT NULL,
                        category INTEGER REFERENCES tbl_category (ID) ON DELETE SET NULL
                                                                      ON UPDATE CASCADE
                    );
                    ''')

        self.c.execute('''
                    CREATE TABLE tbl_post_to_tags (
                        post_ID INTEGER REFERENCES tbl_post (ID) ON UPDATE CASCADE,
                        tag_ID  INTEGER REFERENCES tbl_tag (ID) ON UPDATE CASCADE
                    );
                    ''')

        self.c.execute('''
                    CREATE TABLE tbl_tag (
                        ID   INTEGER PRIMARY KEY AUTOINCREMENT
                                     NOT NULL
                                     UNIQUE,
                        name TEXT    NOT NULL
                    );
                    ''')

        self.close()

    def replace_str(self, str_in):
        str_out = str_in
        str_out = str_out.replace(' ', '-')
        str_out = str_out.replace('_', '-')
        str_out = str_out.replace('?', '-')
        str_out = str_out.replace('!', '-')
        str_out = str_out.replace('+', 'p')
        str_out = str_out.lower()
        return str_out

    def create_new_post(self, name_post, title_post, category_post, tags_post, date_post, content_post):

        name_post = self.replace_str(name_post)
        category_post = self.replace_str(category_post)
        for i in range(0, len(tags_post)):
            tags_post[i] = self.replace_str(tags_post[i])

        self.open()

        # ========================================
        # if given category is not already present in the category table,
        # need to insert a new record in the category table
        # ========================================

        # get entire table as list of tuples where each row is a tuple
        data_tbl_category = self.c.execute('SELECT * from tbl_category').fetchall()
        # get a list of ID values where the category == given category
        # note: the length the resulting list will always be either empty (category not present either due
        # to the table being empty or there are categories, but not one of them is the given category)
        # or 1 (category already present)
        list_IDs_matched = [cur_tuple[0] for (idx_tuple, cur_tuple) in enumerate(data_tbl_category) if cur_tuple[1] == category_post]
        if len(list_IDs_matched) == 0:  # if no match, then a new entry needs to be inserted
            self.c.execute('INSERT INTO tbl_category (name) VALUES (?)', (category_post,))
            id_category_post = self.c.lastrowid
        else:  # category already exist, therefore, no need to insert anything, just record the ID
            id_category_post = list_IDs_matched[0]

        # insert new post in the post table
        self.c.execute('''
                        INSERT INTO tbl_post(name, title, date, category, content)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (name_post, title_post, date_post, id_category_post, content_post)
                       )

        # get ID of the post
        id_post = self.c.lastrowid

        # go through each of the given tags and for each of them,
        # (1) if it's already in the tag table, don't insert anything in the tag table,
        # simply get the tag ID, go to the tbl_post_to_tags and insert a new row
        # with the post_ID and tag_ID.
        # (2) if it's not already in the tag table, insert it into the tag table,
        # get the tag ID of the asserted row, go to the tbl_post_to_tags and insert a new row
        # with the post_ID and tag_ID.

        data_tbl_tag = self.c.execute('SELECT * from tbl_tag').fetchall()

        for tag_post in tags_post:
            list_IDs_matched = [cur_tuple[0] for (idx_tuple, cur_tuple) in enumerate(data_tbl_tag) if
                                cur_tuple[1] == tag_post]
            if len(list_IDs_matched) == 0:  # if no match, then a new entry needs to be inserted
                self.c.execute('INSERT INTO tbl_tag (name) VALUES (?)', (tag_post,))
                id_tag_post = self.c.lastrowid
            else:  # tag already exist, therefore, no need to insert anything, just record the ID
                id_tag_post = list_IDs_matched[0]
            self.c.execute('INSERT INTO tbl_post_to_tags (post_ID, tag_ID) VALUES (?, ?)', (id_post, id_tag_post))

        self.close()

    def get_list_of_categories(self):
        self.open()
        data_tbl_category = self.c.execute('SELECT name from tbl_category').fetchall()
        self.close()
        return [cur_tuple[0] for (idx_tuple, cur_tuple) in enumerate(data_tbl_category)]

    def get_list_of_tags(self):
        self.open()
        data_tbl_tag = self.c.execute('SELECT name from tbl_tag').fetchall()
        self.close()
        return [cur_tuple[0] for (idx_tuple, cur_tuple) in enumerate(data_tbl_tag)]

    def get_info_posts_given_category(self, category_name):

        self.open()

        data_tbl_post = self.c.execute('''
                        SELECT tbl_post.name, tbl_post.title, tbl_post.date
                        FROM tbl_post
                        WHERE tbl_post.category =  
                        (
                        SELECT tbl_category.ID
                        FROM tbl_category
                        WHERE tbl_category.name = ?
                        )
                        ''', (category_name,)
                       ).fetchall()

        self.close()

        return data_tbl_post

    def get_info_posts_given_tag(self, tag_name):

        self.open()

        data_tbl_tag = self.c.execute('''
                                        SELECT tbl_post.name, tbl_post.title, tbl_post.date
                                        FROM tbl_post_to_tags
                                        INNER JOIN tbl_tag 
                                        ON tbl_post_to_tags.tag_ID = tbl_tag.ID
                                        INNER JOIN tbl_post
                                        ON tbl_post.ID = tbl_post_to_tags.post_ID
                                        WHERE tbl_tag.name = ?
                                        ''', (tag_name,)
                                      ).fetchall()

        self.close()

        return data_tbl_tag

    def get_info_post(self, name_post):

        self.open()

        # get unique tags corresponding to given post
        data_view = self.c.execute('''
                                    SELECT DISTINCT tbl_tag.name
                                    FROM tbl_post_to_tags
                                    INNER JOIN tbl_tag 
                                    ON tbl_post_to_tags.tag_ID = tbl_tag.ID
                                    INNER JOIN tbl_post
                                    ON tbl_post.ID = tbl_post_to_tags.post_ID
                                    INNER JOIN tbl_category
                                    ON tbl_post.category = tbl_category.ID
                                    WHERE tbl_post.name = ?
                                        ''', (name_post,)
                                      ).fetchall()
        list_tags_this_post = [cur_tuple[0] for (idx_tuple, cur_tuple) in enumerate(data_view)]

        # get the category corresponding to given post
        data_view = self.c.execute('''
                                        SELECT DISTINCT tbl_category.name
                                        FROM tbl_post
                                        INNER JOIN tbl_category
                                        ON tbl_post.category = tbl_category.ID
                                        WHERE tbl_post.name = ?
                                         ''', (name_post,)
                                   ).fetchall()
        category_this_post = data_view[0][0]

        # get the title, content and date corresponding to given post
        data_view = self.c.execute('''
                                        SELECT title, date, content
                                        FROM tbl_post
                                        WHERE name = ?
                                         ''', (name_post,)
                                   ).fetchall()
        title_this_post = data_view[0][0]
        date_this_post = data_view[0][1]
        content_this_post = data_view[0][2]

        self.close()

        return (list_tags_this_post, category_this_post, title_this_post, date_this_post, content_this_post)






