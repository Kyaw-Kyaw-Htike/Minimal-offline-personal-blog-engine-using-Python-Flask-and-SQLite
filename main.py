# Copyright (C) 2018 Kyaw Kyaw Htike @ Ali Abdul Ghafur. All rights reserved.

from flask import Flask, render_template, request
import utils_DB

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    pp = utils_DB.cls_utils_DB()
    category_list = pp.get_list_of_categories()
    tag_list = pp.get_list_of_tags()
    txt_rendered = render_template('index.html', category_list=category_list, tag_list=tag_list)
    return txt_rendered

@app.route('/posts_in_given_category/<category_name>')
def posts_in_given_category(category_name):
    pp = utils_DB.cls_utils_DB()
    kk = pp.get_info_posts_given_category(category_name)
    tt = ['<ul>']
    for post_info in kk:
        tt.append('<li>')
        tt.append('<a href=/posts/{}>{}</a>'.format(post_info[0], post_info[1]))
        tt.append('</li>')
    tt.append('</ul>')
    tt = ''.join(tt)
    return render_template('posts_in_given_category.html', tt = tt)

@app.route('/posts_in_given_tag/<tag_name>')
def posts_in_given_tag(tag_name):
    pp = utils_DB.cls_utils_DB()
    kk = pp.get_info_posts_given_tag(tag_name)
    tt = ['<ul>']
    for post_info in kk:
        tt.append('<li>')
        tt.append('<a href=/posts/{}>{}</a>'.format(post_info[0], post_info[1]))
        tt.append('</li>')
    tt.append('</ul>')
    tt = ''.join(tt)
    return render_template('posts_in_given_tag.html', tt = tt)

@app.route('/posts/<post_name>')
def post_domain_adaptation(post_name):
    pp = utils_DB.cls_utils_DB()
    info_post = pp.get_info_post(post_name)

    title_post = info_post[2]
    date_post = info_post[3]
    content_post = info_post[4]

    list_tags = info_post[0]
    tags_post = []
    for t in list_tags:
        tags_post.append(t)
        tags_post.append(', ')
    tags_post = ''.join(tags_post)

    category_post = info_post[1]

    return render_template('post_template.html', title_post=title_post, date_post=date_post, tags_post=tags_post, category_post=category_post, content_post=content_post)

#app.run(host='0.0.0.0', port=5000)
app.run(debug=True)


