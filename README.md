# Blogspot Tracker

Blogspot Tracker is a simple python script that can be used to keep track of your favorite blog for new updates. This is especially useful for blogs that don't have subscriptions enabled for them. When this script runs, it creates a system tray icon for windows users were one can choose to start or stop checking their blog for update. Currently the tracker is configured to check every 12 hours but this can be changed. On a detected update, the script will send an email notifying the user based on what is specified in the `config.py` file.

## Getting Started

### Dependencies

- Requires Windows and is most recently tested on Windows 10
- Requires an installation of Python

### Installing

#### Setting up the codebase

1. Clone to repository to your local machine
2. Create a virtual environment. See [here](https://docs.python.org/3/library/venv.html) for more details on how to setup virtual environments
3. Start your virtual environment and run `pip install requirements.txt` in the cmd line

#

#### Getting access to the Gmail API

In order to send automated gmails, it is necessary to get a OAuth 2.0 access token. This will allow the script to access and send emails from your account.

1. Go to this [link](https://cloud.google.com/?authuser=1) and sign up for a Google Cloud Developer account. Note it will ask you to put in your payment information for a free trial but you can skip this by clicking this [link](https://console.cloud.google.com/)
2. At the top search bar type in `Gmail Api` and select the first result
3. Click enable to activate the Gmail API
4. On the top right of the screen click `Create Credentials`
5. Select User data and click next. Type in an app name and add in your email where requested. Select save and continue.
6. On the scopes screen click `Add or Remove Scopes` and then search for `Gmail API`. Select `gmail.send` and `gmail.readonly`
7. Finally select Desktop App for Application type and click `Done`
8. After it should show you your keys and give you the option to download your token. Download your token to the project's root directory and name it `credentials.json`. 

#

#### Setting up config.py and main.py

1. In config.py replace email with your email you used for the Gmail API, replace blog with the link you want to track, and past date as the date of the most recent blog post that you are tracking.
2. Set `To` as the email address that your notifications will be going to.
3. Lastly we need to set our script to correctly find the date on the website. Use inspect element on the date of the blog's most recent post and edit line `134` in `main.py` to grab the date. You may need to edit the date formats used in the code if they differ from what the blog you are tracking has. 
4. With that when you run the program, either in python or using the provided scripts. A small email icon should appear in your status bar and you should be able to start or stop tracking the blog by right clicking the icon and selecting the corresponding setting.

## Author
[@jmho](github.com/jmho)

## Version History
- 0.1.1
  - Fixed bugs with message sending  
- 0.1
    - Initial Release

## License
This project is licensed under the MIT License - see the LICENSE.md file for details