from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import os.path
import pytz
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime

# Define the CST timezone
cst = pytz.timezone('America/Chicago')

# Set this variable to True for 12-hour format, False for 24-hour format
use_12hr_format = True
theme = 'awdark' #awlight also available
check_updates_interval= 60 * 5 #Update every 5 minute(s)
all_events = {}

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def fetch_events(year, month):
    """Fetch Google Calendar events."""
    creds = None
    credsPath = "../../calenderCredentials.json"

    if os.path.exists(credsPath):
        creds = Credentials.from_authorized_user_file(credsPath, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'calenderCredentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(credsPath, 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API to list all calendars
    start_date = datetime(year, month, 1)
    end_date = start_date.replace(month=month+1) if month != 12 else start_date.replace(year=year+1,month=1)
    
    time_min = start_date.isoformat() + 'Z'  # 'Z' indicates UTC time
    time_max = end_date.isoformat() + 'Z'
    
    try:
        calendar_list = service.calendarList().list().execute()
        events = []
        for calendar_list_entry in calendar_list['items']:
            calendar_id = calendar_list_entry['id']
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events.extend(events_result.get('items', []))

        key = f"{year}-{month}"
        all_events[key] = events

        return events
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def filter_events(date):
    """Filter and return events for the specified date from the all_events variable."""
    date_str = date.isoformat()
    year = date.year
    month = date.month
    
    # Create a key for the all_events dictionary based on the year and month
    key = f"{year}-{month}"
    
    # Check if there are events for the selected month in all_events
    if key in all_events:
        # Filter events for the selected date from the events for the selected month
        return [event for event in all_events[key] if date_str in event['start'].get('dateTime', '')]
    else:
        # If there are no events for the selected month in all_events, return an empty list
        return []

def on_date_select(event):
    """Callback function for date selection."""
    date = cal.selection_get()
    year = date.year
    month = date.month

    # Check if events for this month are already fetched
    key = f"{year}-{month}"
    if key not in all_events:
        # If not, fetch events for this month
        fetch_events(year, month)

    events = filter_events(date)
    listbox.delete(0, tk.END)
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event['summary']

        # Parse the date string into a datetime object
        # Handling the case when 'start' contains only date (no time)
        if 'T' in start:  # Indicates that the string contains time
            date_obj = datetime.fromisoformat(start.replace('Z', '+00:00'))  # Convert the string to a datetime object
            date_obj_cst = date_obj.astimezone(cst)  # Convert to CST timezone

            if use_12hr_format:
                # Using 12-hour time format with AM/PM
                formatted_date_str = date_obj_cst.strftime('%Y-%m-%d %I:%M:%S %p %Z')
            else:
                # Using 24-hour time format
                formatted_date_str = date_obj_cst.strftime('%Y-%m-%d %H:%M:%S %Z')  # Format the datetime object back into a string

        else:  # If the string contains only date
            formatted_date_str = start  # You might want to format the date-only string as well
        
        # Insert the formatted date string and summary into the Listbox
        listbox.insert(tk.END, f"{formatted_date_str}: {summary}")
        # listbox.insert(tk.END, f"{start}: {summary}")

def on_resize(event):
    # You can also use event.width to get the new width of the window
    listbox.config(width=root.winfo_width())

def compare_and_update(events1, events2):
    """
    Compare two lists of events and return the events that are in events2 but not in events1.
    """
    events1_ids = {event['id'] for event in events1}
    new_events = [event for event in events2 if event['id'] not in events1_ids]
    return new_events

def periodic_fetch():
    """
    Periodically fetch events, compare with existing events, and update UI if there are new events.
    """
    while True:
        print("Checking for calender changes")

        # Note: You need to adjust the parameters of fetch_events as necessary
        year, month = current_date.year, current_date.month  # Set the year and month as necessary
        new_events = fetch_events(year, month)

        # Generate a key for all_events dictionary based on year and month
        key = f"{year}-{month}"

        # If there are existing events for the month, compare and update UI
        if key in all_events:
            # Get the events that are in new_events but not in all_events[key]
            truly_new_events = compare_and_update(all_events[key], new_events)

            # If there are truly new events, update UI and all_events
            if truly_new_events:
                all_events[key].extend(truly_new_events)
                update_ui(truly_new_events)  # You need to implement update_ui function

        # If there are no existing events for the month, simply add new_events to all_events
        else:
            all_events[key] = new_events

        # Sleep for a specified interval before fetching again
        time.sleep(check_updates_interval)

def update_ui(new_events):
    """
    Update the UI with new events.
    """
    
    # Clearing the listbox
    listbox.delete(0, tk.END)

    # Iterate over new events and insert them into the listbox
    for event in new_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        
        # Parse the date string into a datetime object
        # Handling the case when 'start' contains only date (no time)
        if 'T' in start:  # Indicates that the string contains time
            date_obj = datetime.fromisoformat(start.replace('Z', '+00:00'))  # Convert the string to a datetime object
            
            # Adjust the datetime object to your local timezone (if necessary)
            date_obj_cst = date_obj.astimezone(cst)
            
            # Format the datetime object as a string in your preferred format
            if use_12hr_format:
                start_str = date_obj_cst.strftime('%Y-%m-%d %I:%M %p')  # 12-hour format
            else:
                start_str = date_obj_cst.strftime('%Y-%m-%d %H:%M')    # 24-hour format
        else:
            # If 'start' contains only date, use it as-is
            start_str = start
        
        # Construct the listbox entry string
        entry_str = f"{start_str}: {event['summary']}"
        
        # Insert the entry string into the listbox
        listbox.insert(tk.END, entry_str)

# Fetch events for the current month on program start
current_date = datetime.now()

# Tkinter GUI setup
root = tk.Tk()
root.title("Google Calendar Events")

root.tk.call('lappend', 'auto_path', 'RaspberryPiAssistant/tkinterCalender/awthemes-10.4.0')
root.tk.call('package', 'require', theme)

# # Apply a system theme
style = ttk.Style(root)
style.theme_use(theme)
style.configure('my.TButton', font=('Helvetica', 12), background='light grey')
style.configure('my.TLabelframe', background='white')

# Set firstweekday option to SUNDAY
cal = Calendar(root, selectmode='day', year=current_date.year, 
               month=current_date.month, day=current_date.day,
               firstweekday='sunday')  # Set first day of the week to Sunday
cal.pack(fill="both", expand=True)
cal.bind("<<CalendarSelected>>", on_date_select)

# Set initial geometry
root.geometry('600x400')

# Create a Frame
frame = tk.Frame(root)
frame.pack(fill='both', expand=True, pady=20)

# Create a Listbox with a horizontal scrollbar
listbox = tk.Listbox(frame, height=10, selectmode=tk.SINGLE,
                     xscrollcommand=lambda *args: scrollbar.set(*args))
scrollbar = tk.Scrollbar(frame, orient='horizontal', command=listbox.xview)

# Pack the Listbox and Scrollbar
listbox.pack(fill='both', expand=True, side="top")
scrollbar.pack(fill='x', side="bottom")

welcome_msg = ['Welcome! Select any date to get started!',
               'When moving to a new month, please allow time for ',
               'the program to make the Google API call it needs.']

for msg in welcome_msg : listbox.insert(tk.END, msg)

# Bind the resize event to the on_resize function
root.bind('<Configure>', on_resize)

# Run the periodic_fetch function in a separate thread
fetch_thread = threading.Thread(target=periodic_fetch)
fetch_thread.daemon = True  # Set as a daemon thread so it exits when the main program exits
fetch_thread.start()

root.mainloop()
