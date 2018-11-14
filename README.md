# Item Catalog
This project is a RESTful web application using the Flask framework that provides a list of items within a variety of categories as well with a user 
registration and authentication system with a full access of editing (post, edit, update and delete) 
along with implementing third-party OAuth authentication.

## Project Steps
- Install Vagrant and VirtualBox
- Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm)
- Create [application.py](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/application.py) Flask application in the [vagrant directory](https://github.com/HanaShamatah/Item-Catalog/tree/master/vagrant)
- Route the pages with their function and URIs with flask framework
- Make HTML templates for all pages (public and registered pages) in [templates directory](https://github.com/HanaShamatah/Item-Catalog/tree/master/vagrant/templates) based on the prepared Mockup for all pages
- Setup the [database](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/catalog_database.py)
- Fill the database with a primary data using [filldatabase_clothes.py](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/filldatabase_clothes.py) file that will be editing later with application functionality
- Use CRUD (create, read, update and delete) operations that enabling us edit, add, and update database data
- Add JSON API endpoints for the all data in the application
- Add Google and Facebook login  and logout functionality with a OAuth2.0 third-party authentication in [application.py](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/application.py) and [login.html](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/templates/login.html)
- Implementing authentication mechanisms to properly secured web application that check the logging in user and Is he the creator user for the resources
- Add CSS styling functions in [static/css](https://github.com/HanaShamatah/Item-Catalog/tree/master/vagrant/static/css) directory [style.css](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/static/css/style.css)

## Google Login
- Go to [Google Dev Console](https://console.cloud.google.com/home/dashboard?project=gecoding-api)
- Sign up or Login
- Create a new project
- Go to APIs & Services section, then to credentials
- Select Create Crendentials > OAuth Client ID
- Go to configure consent screen
- Insert an application name and save it
- Select Web application type
- Insert Authorized JavaScript origins as 'http://localhost:8000'
- Insert Authorized redirect URIs as 'http://localhost:8000/login' && 'http://localhost:8000/gconnect'
- Select create
- Copy the Client ID, then paste it into the data-clientid in [login.html](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/templates/login.html) in GOOGLE PLUS SIGN IN BUTTON section
- Download JSON from the OAuth 2.0 client IDs
- Rename the file as client_secrets.json and save it in [vagrant directory](https://github.com/HanaShamatah/Item-Catalog/tree/master/vagrant)


## Facebook Login
- Go to [Facebook developers](https://developers.facebook.com/)
- Sign up or Login
- Create a new project
- insert a name in Display Name
- Select create API ID
- From the right top projects list, select create a test app
- Select Create Test App with the default name
- Select Facebook login from Add a Product list
- Go through a quick guide for Web
- Insert the URI of the application "http://localhost:8000/"
- The read all the nesxt steps to prepare the login functionality
- Go to settings in Facebook Login in the right sidebar
- Insert Valid OAuth Redirect URIs as https://localhost:8000/
- Copy APP ID and APP Secret
- Create A JSON file with [fb_client_secrets.json](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/fb_client_secrets.json) name
- Paste APP ID and APP Secret in [fb_client_secrets.json](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/fb_client_secrets.json) file
- Paste APP ID into the appID in [login.html](https://github.com/HanaShamatah/Item-Catalog/blob/master/vagrant/templates/login.html) in FACEBOOK SIGN IN section and update the version field


## JSON Endpoints

Categories JSON: /catalog/JSON

Category items JSON: /catalog/<category_name>/JSON

Category item JSON: /catalog/<category_name>/<item_name>/JSON'


## Get Started
- Launch the Vagrant VM (vagrant up)
- Login using (vagrant ssh)
- Change the current directory to vagrant shared folder using (cd /vagrant)
- Run application.py file using (python application.py)
- Access the application locally using http://localhost:8000


## Notes
- The codes are organized according to [PEP8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
 
## License
The content of this repository is licensed under an [MIT](https://choosealicense.com/licenses/mit/).
