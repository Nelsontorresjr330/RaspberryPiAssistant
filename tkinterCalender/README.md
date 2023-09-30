# Lightweight Calendar Application for Raspberry Pi

## Overview
This lightweight calendar application is designed to run continuously on a Raspberry Pi.
It integrates with Google Calendar to display events and allows users to interact with their schedule conveniently,
displays events from your Google Calendar & provides a user-friendly interface built with Tkinter and themes provided by [Brad Lanam](https://sourceforge.net/projects/tcl-awthemes/).

## Installation

### Prerequisites
Ensure you have Python installed on your Raspberry Pi. If not, you can install it using the following command:
```bash
sudo apt-get update
sudo apt-get install python3
```

### Libraries Installation
Install the required Python libraries using pip. Run the following commands in your terminal:
```bash
pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install tkcalendar pytz
```

### Google Calendar API Setup
Follow the instructions [here](https://developers.google.com/calendar/api/quickstart/python) to enable the Google Calendar API and download the credentials.json file.
Place the credentials.json file outside of the RaspberryPiAssistant folder to make sure it does not get pushed up.

### Running the Application
Navigate to the directory containing the tkinterCalender.py file and run the application using the following command:

```bash
python3 tkinterCalender.py
```

## Additional Information

### Contributing
Feel free to contribute to the development of this lightweight calendar application by creating a pull request.

### Images
<img src="tkinterCalender/welcome.png" alt="Welcome Screen" width="500"/>
<img src="tkinterCalender/eventsExample.png" alt="Events Screen" width="500"/>

### Personalization
Within the code there are a few lines you can change to personalize the experience.<br>
On line 16, change the [pytz timezone](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568) to your own `cst = pytz.timezone('America/Chicago')`<br>
On line 19, you can change `use_12hr_format = True` to `use_12hr_format = False` to enable a 24hr clock<br>
On line 20, you can change `theme = 'awdark'` to `theme = 'awlight'` to enable a light mode<br>
On line 21, you can change `check_updates_interval= 60 * 5` to any amount you desire to update your calender more or less frequently, this value is in seconds (i.e. 60 seconds * 5 = 5 minutes)<br>
