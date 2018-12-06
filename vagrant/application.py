# Flask framework imports
from flask import (Flask,
                   render_template,
                   request, redirect,
                   url_for, jsonify,
                   flash,
                   make_response)
from flask import session as login_session

# Database and SQLAlchemy toolkit imports
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from catalog_database import Base, Categories, CatalogItem, User

import random
import string
import httplib2
import json
import requests
import datetime

# OAuth2.0 imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Flask instance
app = Flask(__name__)

# Google OAuth 2.0 CLIENT_ID and CLIENT_secret
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
CLIENT_secret = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_secret']
print CLIENT_ID
print CLIENT_secret
APPLICATION_NAME = "Item Catalog"

# Connect to Database and create database session
engine = create_engine(
    'sqlite:///clothescategories.db', poolclass=SingletonThreadPool)
Base.metadata.bind = engine
# Create session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# login - Create Anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print state
    # return "The current session state is %s" % login_session['state']
    if 'username' not in login_session:
        return render_template('login.html', STATE=state)
    else:
        return "<script>function myFunction() {if(alert(\
        'You are logged in please logout and login with another account')){}\
        else window.location='/';}</script><body onload='myFunction()''>"


# login with Google


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
    print access_token
    # Connect to Google login API
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
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    data = answer.json()

    login_session['provider'] = 'google'
    # login_session['username'] = data['name']
    login_session['username'] = data.get('name', '')
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one_Lesson12.5
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'  # noqa
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Create a new user function
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get a user info function
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Get a user id function
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:  # noqa
        return None


# Logout according to signed user provider (Google/Facebook)
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        # chech the provider
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        # Delete the login session data
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You were successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in to begin with!.")
        redirect(url_for('showCategories'))


# Google disconnect users - logout
@app.route('/gdisconnect')
def gdisconnect():
    # check connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    # connect to Google disconnect API
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # Check the requst status
    if result['status'] == '200':
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
    return response


# Facebook login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # chech the request stat is the login stat
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Facebook App ID and Secret
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')
    print token

    # Connect to Facebook login API
    url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]  # API JSON result
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    # Save login data to login_session
    login_session['provider'] = 'facebook'
    login_session['email'] = data["email"]
    login_session['username'] = data["name"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
    -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# Facebook disconnect - logout
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    print facebook_id
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    print "access token received %s " % access_token
    # connect to Facebook disconnect API
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    print url
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return redirect(url_for('showCategories'))


# JSON APIs to view Catalog Information
# Displays all categories
@app.route('/catalog/JSON')
def showCategoriesJSON():
    categories = session.query(Categories).order_by(asc(Categories.id)).all()
    return jsonify(Categories=[i.serialize for i in categories])


# Displays items for a specific category
@app.route('/catalog/<category_name>/JSON')
def CategoryItemsJSON(category_name):
    category_items = session.query(CatalogItem).filter_by(
        category_name=category_name).all()
    return jsonify(CategoryItems=[i.serialize for i in category_items])


# Displays a specific category item.
@app.route('/catalog/<category_name>/<item_name>/JSON')
def showCategoryItemJSON(category_name, item_name):
    item = session.query(CatalogItem).filter_by(
        name=item_name, category_name=category_name).one()
    return jsonify(Item_description=item.serialize)


# Home Page - All categories with the latest added items
@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = session.query(Categories).order_by(asc(Categories.id))
    latest_items = session.query(CatalogItem).order_by(
        desc(CatalogItem.date)).limit(10)
    if 'username' not in login_session:
        return render_template('categories_public.html',
                               categories=categories,
                               latest_items=latest_items)
    else:
        return render_template('categories.html',
                               categories=categories,
                               latest_items=latest_items)


# Category items
@app.route('/catalog/<category_name>')
@app.route('/catalog/<category_name>/items')
def CategoryItems(category_name):
    categories = session.query(Categories).order_by(asc(Categories.id))
    category_items = session.query(CatalogItem).filter_by(
        category_name=category_name)
    category = session.query(Categories).filter_by(
        name=category_name).one()
    if 'username' not in login_session or category.user_id != login_session['user_id']:  # noqa
        return render_template('category_items_public.html',
                               categories=categories,
                               category_name=category_name,
                               category_items=category_items)
    else:
        return render_template('category_items.html',
                               categories=categories,
                               category_name=category_name,
                               category_items=category_items)


# Item details
@app.route('/catalog/<category_name>/<item_name>')
def showCategoryItem(category_name, item_name):
    item = session.query(CatalogItem).filter_by(
        name=item_name, category_name=category_name).one()
    if 'username' not in login_session or item.user_id != login_session['user_id']:  # noqa
        return render_template('item_public.html',
                               item=item,
                               item_name=item_name)
    else:
        return render_template('item.html',
                               item=item,
                               item_name=item_name)


# Create a new catalog
@app.route('/catalog/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    # POST Method
    if request.method == 'POST':
        if request.form['name']:
            newCatalog = Categories(
                name=request.form['name'], user_id=login_session['user_id'])
            session.add(newCatalog)
            flash('New Catalog %s Successfully added' % newCatalog.name)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
            return "<script>function myFunction() {if(alert(\
            'You must inserta catalog new to add it')){} else\
            window.location='/catalog/new';}</script>\
            <body onload='myFunction()''>"
    else:
        return render_template('newCatalog.html')


# Edit a catalog
@app.route('/catalog/<category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    editedCatalog = session.query(Categories).filter_by(
        name=category_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    # Check the loggin user is same as a creator
    if editedCatalog.user_id != login_session['user_id']:
        return "<script>function myFunction() {if(alert(\
        'You are not authorized to edit this category. Please create your own catalog in order to edite it.')){}\
        else window.location='/';}</script><body onload='myFunction()''>"  # noqa
    # POST Method
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
        session.add(editedCatalog)
        flash('Catalog %s Successfully edited' % editedCatalog.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCatalog.html',
                               category_name=category_name)


# Delete catalog
@app.route('/catalog/<category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    catalogToDelete = session.query(
        Categories).filter_by(name=category_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    # Check the loggin user is same as a creator
    if catalogToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {if(alert(\
        'You are not authorized to delete this item.')){} else \
        window.location='/';}</script><body onload='myFunction()''>"
    # POST Method
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('Catalog Item %s Successfully deleted' % catalogToDelete.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCatalog.html',
                               category_name=category_name)


# Create a new item
@app.route('/catalog/<category_name>/new', methods=['GET', 'POST'])
def newCategoryItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Categories).filter_by(name=category_name).one()
    # Check the loggin user is same as a creator
    if category.user_id != login_session['user_id']:
        return "<script>function myFunction() {if(alert(\
        'You are not authorized to add a new menu item for %s category.')){}\
        else window.location='/catalog';}</script>\
        <body onload='myFunction()''>" % category_name
    # POST Method
    if request.method == 'POST':
        # check all form fiels are filled to create a new item
        if request.form['name'] and request.form['description'] and request.form['picture']:  # noqa
            newCatalogItem = CatalogItem(
                name=request.form['name'],
                description=request.form['description'],
                category_name=request.form['category'],
                picture=request.form['picture'],
                user_id=login_session['user_id'],
                date=datetime.datetime.now())
            session.add(newCatalogItem)
            flash('New Catalog Item %s Successfully added' %
                  newCatalogItem.name)
            session.commit()
        else:
            return "<script>function myFunction() {if(alert(\
            'You must fill all fields in order to add a new item')){} else\
            window.location='http://localhost:8000/catalog/%s/new';}\
            </script><body onload='myFunction()''>" % category_name
        print newCatalogItem.description
        print newCatalogItem.category_name
        print newCatalogItem.name
        return redirect(url_for('CategoryItems',
                                category_name=newCatalogItem.category_name))
    else:
        categories = session.query(Categories).order_by(asc(Categories.id))
        return render_template('newItem.html', categories=categories)


# Edit items
@app.route('/catalog/<category_name>/<item_name>/edit', methods=['GET', 'POST'])  # noqa
def editCategoryItem(category_name, item_name):
    editedCatalogItem = session.query(CatalogItem).filter_by(
        name=item_name, category_name=category_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    # print "editCategoryItem User id"
    # print editCategoryItem.user_id
    # Check the loggin user is same as a creator
    if editedCatalogItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {if(alert(\
        'You are not authorized to edit this item. Please create your own catalog in order to edite its items.')){}\
        else window.location='/catalog/%s';}</script><body onload='myFunction()''>" % category_name  # noqa
    # POST Method
    if request.method == 'POST':
        if request.form['name']:
            editedCatalogItem.name = request.form['name']
        if request.form['description']:
            editedCatalogItem.description = request.form['description']
        if request.form['category']:
            editedCatalogItem.category_name = request.form['category']
        if request.form['picture']:
            editedCatalogItem.category_name = request.form['picture']
        editedCatalogItem.date = datetime.datetime.now()
        session.add(editedCatalogItem)
        flash('Catalog Item %s Successfully edited' % editedCatalogItem.name)
        session.commit()
        return redirect(url_for('showCategoryItem',
                                category_name=editedCatalogItem.category_name,
                                item_name=editedCatalogItem.name))
    else:
        item = session.query(CatalogItem).filter_by(name=item_name).one()
        categories = session.query(Categories).order_by(asc(Categories.id))
        return render_template('editItem.html',
                               categories=categories,
                               item=item)


# Delete itemss
@app.route('/catalog/<category_name>/<item_name>/delete', methods=['GET', 'POST'])  # noqa
def deleteCategoryItem(category_name, item_name):
    itemToDelete = session.query(
        CatalogItem).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    # Check the loggin user is same as a creator
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {if(alert('You are not authorized to delete this item.')){}\
         else window.location='/catalog/%s';}</script><body onload='myFunction()''>" % category_name  # noqa
    # POST Method
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('Catalog Item %s Successfully deleted' % itemToDelete.name)
        session.commit()
        return redirect(url_for('CategoryItems',
                                category_name=category_name))
    else:
        return render_template('deleteItem.html',
                               item_name=item_name,
                               category_name=category_name)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
