import re
from flask import Blueprint, render_template, request, flash, jsonify, request, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Note, Link, Paste, User
from . import db
import json
import os
from os.path import join, dirname, realpath
from dhooks import Webhook, Embed
import requests
from requests.auth import HTTPBasicAuth
from hashids import Hashids

views = Blueprint('views', __name__)
UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/')
@login_required
def home():
    count = 0
    for note in current_user.notes:
        count += 1

    return render_template('home.html', user=current_user, count=count)

@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')
        title = request.form.get('title')

        if len(note) < 1:
            flash('Data must be at least 1 character long.', category='error')
        else:
            new_note = Note(data=note, title=title, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note created!', category='success')

    return render_template('notes.html', user=current_user)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Note Deleted', category='success')
        else:
            flash('You do not have permission to delete this note. Hacking faggot', category='error')
    else:
        flash('Note not found. Internal Server Error', category='error')
        
    return jsonify({}), render_template('notes.html', user=current_user)

@views.route("/disc-webhook", methods=['GET', 'POST'])
@login_required
def disc_webhook():
        if request.method == "POST":
            hook = request.form.get('hook').replace("app", "")
            if hook:
                hook = Webhook(hook)

                title = request.form.get('title') or ""
                content = request.form.get('content') or ""
                color = f'0x{request.form.get("color")}'.replace("#", "")
                color = int(color, 16)
                author = request.form.get('author') or ""

                embed = Embed(title=title, description=content, color=color)
                embed.set_author(name=author)

                hook.send(embed=embed)

                flash('Discord Webhook Sent!', category='success')
            else:
                flash('No Discord Webhook Provided', category='error')


        return render_template('disc-webhook.html', user=current_user)

@views.route('/insult-generator', methods=['GET', 'POST'])
@login_required
def insult_generator():
    gen_insult = ""
    if request.method == "POST":
        insult_types = ['regular', 'adjective']
        insult_type = request.form.get('insult')
        print(insult_type)

        if insult_type:
            insult_type = insult_type.lower()
            if insult_type in insult_types:
                if insult_type == "adjective":
                    insult = requests.get("https://insult.mattbas.org/api/adjective")
                    flash("", category='display')
                    gen_insult = insult.text
                elif insult_type == "regular":
                    insult = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
                    # lets put this data in some html now!
                    flash("",category='display')
                    gen_insult = insult.json()['insult']
            else:
                flash('Invalid insult type', category='error')
        else:
            flash('No insult type provided', category='error')

    return render_template('insult-generator.html', user=current_user, insult=gen_insult)

@views.route('/link-shortener', methods=['GET', 'POST'])
@login_required
def link_shortener():
    if request.method == "POST":
        url = request.form.get('link')
        if url:
            url = Link(user_id=current_user.id, original_url=url)
            url_id = url.id
                
            hashid = Hashids.encode(url_id)
            shorturl = request.host_url + hashid
            url.url = shorturl
            url.clicks = 0
            
            db.session.add(url)
            db.session.commit()


        else:
            flash('No URL Provided', category='error')

    return render_template('link-shortener.html', user=current_user)