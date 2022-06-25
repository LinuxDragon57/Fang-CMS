from flask import (
    Blueprint, request, render_template, flash, current_app, session, redirect, url_for, Markup, abort
)
from sqlalchemy.exc import IntegrityError
from mistune import html as create_html
from os import (remove as remove_file, rename as rename_file)

from Fang.commands import mkpath
from Fang.auth import login_required
from Fang.Models import db, Author, Entry
from Fang.security import scrub_post_data


cms_bp = Blueprint('cms', __name__, url_prefix='/cms/')


@cms_bp.route('/')
@login_required
def index():
    all_posts = Entry.query.filter_by(author_id=session.get('user_id')).all()
    return render_template('cms/cms_landing.html', posts=all_posts)


@cms_bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    post_info = {
        'title': "",
        'description': "",
        'genre': "",
        'content': ""
    }
    if request.method == "POST":
        if request.form.get('cancel') == 'Cancel':
            return redirect(url_for('cms.index'))
        elif request.form.get('create') == 'Create Post':
            post_info['title'] = request.form.get('title')
            post_info['description'] = request.form.get('description')
            post_info['genre'] = request.form.get('genre')
            post_info['content'] = request.form.get('entry')
            content_path = f"{current_app.config['DATA_DIRECTORY']}/entries/" \
                           f"{mkpath(post_info['genre'])}/{mkpath(post_info['title'])}.md "
            author_id = session.get('user_id')

            if not scrub_post_data(post_info['title'], post_info['description'], post_info['content']):
                flash("Your input has not met the acceptable criteria for a post.")
            else:
                try:
                    markdown_file = open(content_path, 'x')
                    new_entry = Entry(
                            title=post_info['title'],
                            description=post_info['description'],
                            genre=post_info['genre'],
                            content_path=content_path,
                            author_id=author_id
                    )
                    db.session.add(new_entry)
                    db.session.commit()
                    markdown_file.write(post_info['content'])
                    markdown_file.close()
                    flash(Markup(f"Successfully created post, <em>{post_info['title']}</em>."))
                    return redirect(url_for('cms.index'))
                except OSError or IntegrityError:
                    if OSError:
                        flash("Error: A post with that title already exists.")
                    else:
                        flash("Unknown Error: Could not preserve database integrity. No post was created.")

    return render_template('cms/create_post.html', post_info=post_info)


@cms_bp.route('/read')
@login_required
def read():
    post_id = request.args.get('post_id')
    if post_id is None:
        return redirect(url_for('cms.index'))
    elif post_id is not None:
        metadata = Entry.query.filter_by(id=post_id).first_or_404()
        try:
            content = create_html(open(metadata.content_path, 'r').read())
            return render_template('cms/read_post.html', post_data=metadata, post_content=content)
        except FileNotFoundError:
            abort(404)


@cms_bp.route('/update', methods=('POST', 'GET'))
@login_required
def update():

    # Sometimes a post_id variable will be passed in as a query parameter. Initialize it here using the Flask request
    # API - setting it to None if no query parameter is passed in.
    post_id = request.args.get('post_id', None, int)

    # If the request method of the page is a GET request...
    if request.method == "GET":
        # If the client sends a GET request without supplying a post_id query parameter,
        # present a list of posts that the current logged-in user can edit.
        if post_id is None:
            current_user_posts = Entry.query.filter_by(author_id=session.get('user_id')).all()
            return render_template('cms/cms_landing.html', posts=current_user_posts, update=True)
        elif post_id is not None:
            # Else if the client sends a GET request and supplies a post_id query parameter,
            # 
            edit_post = Entry.query.filter_by(id=post_id).first_or_404()
            content = open(edit_post.content_path, 'r').read()
            return render_template('cms/update_post.html', post_data=edit_post, post_content=content)
    # If the request method of the page is a POST request...
    elif request.method == "POST":
        if request.form.get('cancel') == 'Cancel':  # The cancel button was pressed. Nothing was done.
            return redirect(url_for('cms.index'))
        elif request.form.get('update') == 'Update Post':  # The submit button was pressed.
            if post_id is not None:  # Ensure that the backend has been given a post to work with.
                # Use the supplied post_id to query the database for the rest of the post's metadata.
                update_post = Entry.query.filter_by(id=post_id).first_or_404()
                if update_post.author_id == session.get('user_id'):
                    post_title = request.form.get('title')
                    post_desc = request.form.get('description')
                    post_genre = request.form.get('genres')

                    if not scrub_post_data(post_title, post_desc, request.form.get('entry')):
                        if update_post.title != post_title or update_post.genre != post_genre:
                            content_path = f"{current_app.config['DATA_DIRECTORY']}/entries/" \
                                           f"{mkpath(post_genre)}/{mkpath(post_title)}.md"
                            rename_file(update_post.content_path, content_path)
                        else:
                            content_path = update_post.content_path

                        try:
                            markdown_file = open(content_path, 'w+')
                            if Entry.query.filter_by(title=post_title).first() is not None:
                                raise ValueError
                            if markdown_file.read() != request.form['entry']:
                                markdown_file.write(request.form['entry'])
                            markdown_file.close()
                        except ValueError:
                            error = "Error: A post with that title already exists."

                        if error is None:
                            update_post.title = post_title
                            update_post.description = post_desc
                            update_post.genre = post_genre
                            update_post.content_path = content_path
                            db.session.commit()
                            flash(Markup(f"Successfully updated post to <em>{post_title}</em>."))
                            return redirect(url_for('cms.index'))

                    flash(error)

        return render_template('cms/update_post.html')


@cms_bp.route('/delete', methods=('POST', 'GET'))
@login_required
def delete():
    post_id = request.args.get('post_id', None, int)
    if request.method == "GET":
        if post_id is None:
            current_user_posts = Entry.query.filter_by(author_id=session.get('user_id')).all()
            return render_template('cms/cms_landing.html', posts=current_user_posts, delete=True)
        elif post_id is not None:
            del_entry = Entry.query.filter_by(id=post_id).first_or_404()
            content = create_html(open(del_entry.content_path, 'r').read())
            return render_template('cms/delete_post.html', post_data=del_entry, post_content=content)
    elif request.method == "POST":
        if post_id is not None:
            del_entry = Entry.query.filter_by(id=post_id).first_or_404()
            if del_entry.author_id == session.get('user_id'):
                remove_file(del_entry.content_path)
                db.session.delete(del_entry)
                db.session.commit()
                flash(Markup(f"Successfully deleted post, <em>{del_entry.title}</em>."))
                return redirect(url_for('cms.index'))


@cms_bp.context_processor
def current_user_name():
    user_id = session.get('user_id')
    if user_id is not None:
        user_name = Author.query.get(user_id)
        return dict(current_user_name=user_name.full_name)


@cms_bp.context_processor
def display_admin_functions():
    user_id = session.get('user_id')
    if user_id is not None:
        admin_status: bool = all(db.session.execute(db.select(Author.admin).where(Author.id == user_id)).first())
        return dict(is_admin=admin_status)
