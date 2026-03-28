Initial setup:
- Requires python 3

Run the following commands in the root of the workspace:
- python -m venv venv
- pip install -r requirements.txt


In order to run the API locally, you can run the following command. This will make the API available.
- flask --app api run



*** Deployment ***
The API uses gunicorn in order to run on Heroku. You'll find the basic command that is needed in the Procfile.

Simply deploy the app to heroku, and the API should work as expected.