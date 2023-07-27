"""
Python Flask WebApp Auth0 integration example
"""
from authlib.integrations.flask_client import OAuth

from os import environ as env
from urllib.parse import quote_plus, urlencode
from dotenv import find_dotenv, load_dotenv
from flask import redirect, render_template, session, request, Response, url_for, send_file, jsonify
import orm
import data
import urllib.parse
import base64
import datetime
from logger import logger

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = data.init_app()
admin_user_id = '6464e7ac009a56e46cc4ca4c'
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


@app.template_filter('b64encode')
def b64encode_filter(s):
    return base64.b64encode(s).decode('utf-8')

@app.route("/login")
def login():
    redirect_uri = url_for("callback", _scheme='https', _external=True)
    return oauth.auth0.authorize_redirect(redirect_uri=redirect_uri)

def require_auth(func):
    def wrapper(*args, **kwargs):
        if session.get('user'):
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/")
def home():
    if not session.get('user', None):
        return redirect('https://thegagali.com')
    user_id = session['user']['user_id']
    in_progress_entries , completed_entries = orm.get_entries(
        user_id=user_id)
    wordcloud = orm.get_wordcloud_file(user_id)
    return render_template('personal.html', in_progress_entries=in_progress_entries, completed_entries=completed_entries, wordcloud=wordcloud)

@app.route("/shared")
#@require_auth
def public_entries():
    entries = orm.get_public_entries()
    return render_template('public-entries.html', entries=entries)
  

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    session['user']['user_id'], terms_conditions, role = data.get_user_id(
        session['user']['userinfo']['email'])

    if role!='user':
        return redirect('/logout')
    # if user has not signed the agreement, this is the time
    if not terms_conditions:
        return redirect('/terms')
    else:
        return redirect("/")


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route("/register_user")
@require_auth
def register_user():
    try:
        data.register_user(session['user']['user_id'])
        return redirect("/")
    except:
        return 'please try again'


@app.route("/logout")
@require_auth
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": "https://www.thegagali.com",
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route('/chat/', defaults={'entry_id': 'new'}, methods=['GET'])
@app.route("/chat/<entry_id>")
@require_auth
def chat(entry_id):
    '''
    Create a new chat
    '''
    if entry_id=='new':
        user_id = session['user']['user_id']
        entry_id = orm.create_entry(user_id)
    entry = orm.get_entry(entry_id)
    return render_template('chat.html', entry=entry)


@app.route('/get_response', methods=['POST'])
@require_auth
def get_response():
    return data.get_response(request.json)


@ app.route("/past_entries/<entry_id>")
@ require_auth
def past_entries(entry_id):
    entry = orm.get_entry(entry_id)
    if 'private' not in entry:
        entry['private']=True
    if entry['private'] and entry['user_id']!= session['user']['user_id'] and admin_user_id!=session['user']['user_id']:
        return render_template('/')   
    return render_template('journal-entry.html', entry=entry)

@ app.route("/admin/<entry_id>")
@ require_auth
def admin(entry_id):
    # make available only for the admin
    if session['user']['user_id']!=admin_user_id:
        return redirect("/")
    if  entry_id=='all':
        entries = orm.get_admin_entries()
        return render_template('admin-entries.html', entries=entries)
    # if entry_id was provided
    return redirect("/past_entries/"+entry_id)



@app.route('/static/<folder>/<filename>')
def get_static_file(folder, filename):
    return send_file('./static/'+folder+'/'+filename)


@app.route('/analyze/<analysis_type>/<entry_id>')
@require_auth
def analyze(entry_id, analysis_type):
    """
    return a json like {'text':'......'}
    """
    return data.analyze(entry_id, analysis_type)


@app.route('/entry-done/<entry_id>')
@require_auth
def entry_done(entry_id):
    """
    run analyziz and change the completed field in the entry doc
    """
    logger.info('request received to close entry ')
    try:
        data.close_entry(entry_id)
    except Exception as e:
        logger.exception('error occured in entry_done')
    return {'success':True}

@app.route('/email_content',  methods=['POST'])
@require_auth
def email_content():
    try:
        payload = request.get_json()
        entry_id = payload.get('entry_id')
        email = payload.get('email')
        entry = orm.get_entry(entry_id)
        # Call the send_email function from the email module
        data.send_email(entry, email)

        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/entry-title', methods=['POST'])
@ require_auth
def update_entry_title():
    entry_title = request.json['title']
    entry_id = request.json['entry_id']
    orm.update_entry(entry_id, {'title': entry_title})
    return {'success':True}


@app.route('/delete-entry/<entry_id>', methods=['DELETE'])
@ require_auth
def delte_entry(entry_id):
    orm.delete_entry(entry_id)
    return {'success':True}



@app.route('/change-to-in-progress', methods=['POST'])
@ require_auth
def change_to_in_progress():
    entry_id = request.json['entry_id']
    orm.update_entry(entry_id, {'completed':False})
    return {'success':True}


@ app.route("/update-privacy", methods=['POST'])
@ require_auth
def update_privacy():
    entry_id = request.json['entry_id']
    private = request.json['private']
    orm.update_entry(entry_id, {'private':private})
    return 'success'


@app.template_filter('timestamp_to_local_time')
def timestamp_to_local_time(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')


@app.route('/chat-feedback', methods=['POST'])
@require_auth
def chat_feedback():
    content = request.json['content']
    entry_id = request.json['entry_id']
    feedback = request.json['feedback']
    orm.insert_chat_feedback({'entry_id': entry_id, 'content':content, 'feedback':feedback })
    return {'success':True}


@app.route('/like_comment/<comment_id>')
def like_comment(comment_id):
    user_id = '123'
    entry_id = orm.like_comment(comment_id, user_id)
    return redirect(f'/public-entry/{entry_id}')

@app.route('/add_comment', methods=['POST'])
def add_comment():
    entry_id = request.form['entry_id']
    user_id = '123'
    content = request.form['content']
    orm.insert_comment(entry_id, user_id, content)
    
    return redirect(f'/public-entry/{entry_id}')


@app.route('/public-entry/<entry_id>')
@require_auth
def get_public_entry(entry_id):
    entry=data.get_public_entry(entry_id)
    comments = orm.get_comments(entry_id)
    return render_template('public-entry.html', entry=entry, comments=comments)


@app.route('/profile')
@ require_auth
def profile():
    user_id = '6464e7ac009a56e46cc4ca4c'
    profile = orm.get_profile(user_id)

    return render_template('profile.html', profile=profile)


@app.route('/update-profile', methods=['POST'])
def update_profile():
    user_id = '6464e7ac009a56e46cc4ca4c'
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    receive_email = request.form['receive_email']
    therapist_email = request.form['therapist_email']

    orm.update_profile( user_id,{'first_name':first_name,'last_name':last_name,'receive_email':receive_email, 'therapist_email':therapist_email})
    
    return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 8000), debug=True)
