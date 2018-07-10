from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Locals, Beers, Store, User

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, make_response, flash
from flask import session as login_session
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

import httplib2
import requests
import json
import random
import string
import time

import sys

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///brewspot.db')

Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))
app = Flask(__name__)

APPLICATION_NAME = "BrewSpot Application"
CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']


@app.teardown_request
def remove_session(ex=None):
    session.remove()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user = getUser(data["email"])
    if user:
        login_session['user_id'] = user.id

    else:
        user = createUser(login_session)
        login_session['user_id'] = user.id

    return home()


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session['access_token']

    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'\
        .format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        beers_list = session.query(Beers).all()
        return render_template('home.html',
                               beers=beers_list,
                               user=login_session)
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])

    session.add(newUser)
    session.commit()
    user = getUser(login_session['email'])

    return user


def getUser(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user
    except:
        return None


@app.route('/')
@app.route('/home')
def home():
    if 'email' in login_session:
        user = session.query(User)\
            .filter_by(email=login_session['email']).one()

        try:
            local = session.query(Locals).filter_by(id=user.local_id).one()
            local_name = local.name
        except:
            local_name = 0

        login_session['local_name'] = local_name

    beers_list = session.query(Beers).all()
    return render_template('home.html',
                           beers=beers_list,
                           session=login_session)


@app.route('/beers/<string:beer_name>/')
def showBeer(beer_name):
    beer = session.query(Beers).filter_by(name=beer_name).one()
    beer_locals = getBeerLocals(beer.id)

    if 'username' in login_session:
        user_local_has_beer = userLocalHasBeer(beer.id)
    else:
        user_local_has_beer = False

    return render_template('beers.html',
                           beer=beer,
                           locals=beer_locals,
                           user=login_session,
                           hasBeer=user_local_has_beer)


# Add Beer to logged User's Local
@app.route('/beers/<string:beer_name>/addBeer')
def addBeer(beer_name):
    beer = session.query(Beers).filter_by(name=beer_name).one()
    user = getUser(login_session['email'])
    local = session.query(Locals).filter_by(id=user.local_id).one()
    new_store = Store(beer_id=beer.id, local_id=local.id, available=True)
    session.add(new_store)
    session.commit()

    return showLocal(local.name)


# Remove Beer from logged User's Local
@app.route('/beers/<string:beer_name>/deleteBeer')
def deleteBeer(beer_name):
    beer = session.query(Beers).filter_by(name=beer_name).one()
    user = getUser(login_session['email'])
    local = session.query(Locals).filter_by(id=user.local_id).one()
    store = session.query(Store)\
        .filter_by(beer_id=beer.id)\
        .filter_by(local_id=local.id).one()

    session.delete(store)
    session.commit()

    return showLocal(local.name)


# Create new Beer if not exists and add it to logged User's Local
# If the uploaded Beer already exists, is added to logged User's Local
# If no logged User or Local is not User's own, returns to home page
@app.route('/locals/<string:local_name>/newBeer/', methods=['GET', 'POST'])
def newBeer(local_name):
    if 'email' not in login_session:
        return home()
    else:
        user = getUser(login_session['email'])
        local = session.query(Locals).filter_by(name=local_name).one_or_none()

    if local is None:
        return newLocal()

    print user.local_id
    print local.id

    if user.local_id == local.id:
        print local.name
        if request.method == 'POST':
            beers_list = session.query(Beers).all()
            new_beer_exists = False

            new_beer = Beers(
                name=request.form['name'],
                description=request.form['description'],
                price=request.form['price'],
                origin=request.form['origin'],
                logo=request.form['logo'])

            for beer in beers_list:
                if (new_beer.name.lower() == beer.name.lower()):
                    new_beer_exists = True
                    break

            if not new_beer_exists:
                session.add(new_beer)
                session.commit()

                this_beer = session.query(Beers)\
                    .filter_by(name=request.form['name']).one()
                this_local = session.query(Locals)\
                    .filter_by(name=local_name).one()

                new_store = Store(
                    beer_id=this_beer.id,
                    local_id=this_local.id,
                    available=True)
                session.add(new_store)
                session.commit()

            return showLocal(local_name)
        else:
            return render_template('newBeer.html', local_name=local_name)
    else:
        return home()


@app.route('/locals/<string:local_name>/')
def showLocal(local_name):
    local = session.query(Locals).filter_by(name=local_name).one()
    local_beers = getLocalBeers(local.id)
    local_user = session.query(User).filter_by(local_id=local.id).one()

    if 'username' in login_session:
        is_users = local_user.email == login_session['email']
    else:
        is_users = False

    return render_template(
        'locals.html',
        local=local,
        beers=local_beers,
        user=login_session,
        is_users=is_users)


# Create new Local for logged User if not exists
# If the User already has a Local it redirects to the User's Local page
@app.route('/newLocal/', methods=['GET', 'POST'])
def newLocal():
    user = getUser(login_session['email'])

    if user.local_id == 0:
        if request.method == 'POST':
            newLocal = Locals(
                name=request.form['name'],
                description=request.form['description'])
            session.add(newLocal)
            session.commit()

            user.local_id = newLocal.id
            session.commit()

            local = session.query(Locals).filter_by(id=user.local_id).one()
            return showLocal(local.name)
        else:
            return render_template('newLocal.html')
    else:
        local = session.query(Locals).filter_by(id=user.local_id).one()
        return showLocal(local.name)


# Update Local if it is logged User's own
# If Local selected is not User's own redirects to home page
@app.route('/updateLocal/<string:local_name>/', methods=['GET', 'POST'])
def updateLocal(local_name):

    if 'email' not in login_session:
        return home()
    else:
        user = getUser(login_session['email'])
        local = session.query(Locals).filter_by(name=local_name).one()

    if user.local_id == local.id:
        if request.method == 'POST':
            if 'name' in request.form:
                local.description = request.form['name']
            if 'description' in request.form:
                local.description = request.form['description']
            session.commit()

            return showLocal(local.name)
        else:
            return render_template('newLocal.html')
    else:
        return home()


@app.route('/api/beers/')
def RandomBeerJSON():
    beers = session.query(Beers).all()
    beer = random.choice(beers)
    beer_locals = getBeerLocals(beer.id)

    return jsonify(
        beer=beer.serialize,
        locals=[local.serialize for local in beer_locals])


@app.route('/api/beers/<int:beer_id>')
def BeerJSON(beer_id):
    beer = session.query(Beers).filter_by(id=beer_id).one()
    beer_locals = getBeerLocals(beer.id)

    return jsonify(
        beer=beer.serialize,
        locals=[local.serialize for local in beer_locals])


@app.route('/api/locals/<int:local_id>')
def LocalJSON(local_id):
    local = session.query(Locals).filter_by(id=local_id).one()
    local_beers = getLocalBeers(local.id)

    return jsonify(
        local=local.serialize,
        beers=[beer.serialize for beer in local_beers])


def getBeerStore(beer_id):
    return session.query(Store).filter_by(beer_id=beer_id).all()


def getLocalStore(local_id):
    return session.query(Store).filter_by(local_id=local_id).all()


def getBeerLocals(beer_id):
    beer_locals_ids = []
    beer_store = getBeerStore(beer_id)
    for object in beer_store:
        beer_locals_ids.append(object.local_id)

    return session.query(Locals).filter(Locals.id.in_(beer_locals_ids)).all()


def getLocalBeers(local_id):
    local_beers_ids = []
    local_store = getLocalStore(local_id)
    for object in local_store:
        local_beers_ids.append(object.beer_id)

    return session.query(Beers).filter(Beers.id.in_(local_beers_ids)).all()


def userLocalHasBeer(beer_id):
    user = getUser(login_session['email'])
    local = session.query(Locals).filter_by(id=user.local_id).one()
    user_local_beers = getLocalBeers(local.id)
    local_has_beer = False

    for beer in user_local_beers:
        if (beer_id == beer.id):
            local_has_beer = True
            break

    return local_has_beer


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
