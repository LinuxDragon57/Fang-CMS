from flask import (
    Blueprint, request, render_template, flash, current_app, session, redirect, url_for, Markup, abort
)
from mistune import html as create_html
from os import (remove as remove_file, rename as rename_file)

from linuxdragon.commands import mkpath
from linuxdragon.auth import login_required
from linuxdragon.Models import db, Author, Entry


cms_bp = Blueprint('cms', __name__, url_prefix='/cms/')


@cms_bp.route('/')
@login_required
def index():
    all_posts = Entry.query.filter_by(author_id=session.get('user_id')).all()
    return render_template('cms/cms.html', posts=all_posts)


@cms_bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        if request.form.get('cancel') == 'Cancel':
            return redirect(url_for('cms.index'))
        elif request.form.get('create') == 'Create Post':
            post_title = request.form.get('title')
            post_desc = request.form.get('description')
            post_genre = request.form.get('genre')
            content_path = f"{current_app.config['DATA_DIRECTORY']}/{mkpath(post_genre)}/{mkpath(post_title)}.md"
            author_id = session.get('user_id')
            error = None

            if len(post_title) <= 1 or len(post_desc) <= 1:
                error = "A Title and Description are required."

            if len(request.form['entry']) < 100:
                error = "Your post content must have least 100 characters."

            if error is None:
                try:
                    markdown_file = open(content_path, 'x')
                    if Entry.query.filter_by(title=post_title).first() is not None:
                        raise ValueError
                    markdown_file.write(request.form['entry'])
                    markdown_file.close()
                except(OSError, ValueError):
                    error = "Error: A post with that title already exists."

                if error is None:
                    new_entry = Entry(
                        title=post_title,
                        description=post_desc,
                        genre=post_genre,
                        content_path=content_path,
                        author_id=author_id
                    )
                    db.session.add(new_entry)
                    db.session.commit()
                    flash(Markup(f"Successfully created post, <em>{post_title}</em>."))
                    return redirect(url_for('cms.index'))

            flash(error)

    return render_template('cms/create_post.html')


@cms_bp.route('/read')
@login_required
def read():
    post_id = request.args.get('post_id', None,  int)
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
    post_id = request.args.get('post_id', None, int)
    if request.method == "GET":
        if post_id is None:
            current_user_posts = Entry.query.filter_by(author_id=session.get('user_id')).all()
            return render_template('cms/cms.html', posts=current_user_posts, update=True)
        elif post_id is not None:
            edit_post = Entry.query.filter_by(id=post_id).first_or_404()
            content = open(edit_post.content_path, 'r').read()
            return render_template('cms/update_post.html', post_data=edit_post, post_content=content)
    elif request.method == "POST":
        if request.form.get('cancel') == 'Cancel':
            return redirect(url_for('cms.index'))
        elif request.form.get('update') == 'Update Post':
            if post_id is not None:
                update_post = Entry.query.filter_by(id=post_id).first_or_404()
                if update_post.author_id == session.get('user_id'):
                    post_title = request.form.get('title')
                    post_desc = request.form.get('description')
                    post_genre = request.form.get('genres')
                    error = None

                    if len(post_title) <= 1 or len(post_desc) <= 1:
                        error = "A Title and Description are required."

                    if len(request.form['entry']) < 100:
                        error = "Your post must have at least 100 characters."

                    if error is None:
                        if update_post.title != post_title or update_post.genre != post_genre:
                            content_path = \
                                f"{current_app.config['DATA_DIRECTORY']}/{mkpath(post_genre)}/{mkpath(post_title)}.md"
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
            return render_template('cms/cms.html', posts=current_user_posts, delete=True)
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


@cms_bp.context_processor
def cms_urls():
    return dict(is_root=False)
