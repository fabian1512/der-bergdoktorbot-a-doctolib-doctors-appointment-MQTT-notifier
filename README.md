# Der BergdoktorBot – A Doctolib doctor's appointment MQTT notifier

Inspired by mayrs/der-bergdoktorbot-a-doctolib-doctors-appointment-telegram-notifier

Get notifications about the most recent doctor's appointments on [doctolib.de](https://www.doctolib.de/) via mqtt payload. This script will notify you **every minute** as long as appointments exist within the next `UPCOMING_DAYS`. The next appointment outside of that threshold is additionally notified **on the hour**.

If you, like me, want to be notified about new appointments via [notifications](https://www.home-assistant.io/integrations/notify/) in homeassistant, take a look at the automation provided in this fork.

ℹ️ 🔒 🔧 Remember that this static script does not know anything about your doctolib details behind your login so you have to **monitor** and **adjust** it on the go to reduce unwanted notifications.

## Setup

### MQTT-Library

On your server running the script:

```markdown
pip install gmqtt
```


### Script

1. Insert the bot `Token` into the constant `TELEGRAM_BOT_TOKEN`
1. Insert the `chat_id` into the constant `TELEGRAM_CHAT_ID`

You do **not** have to be signed in to doctolib.de in order to do do the next steps that will get your search query.

1. Navigate to [doctolib.de](https://www.doctolib.de/)
2. Use the search mask to find a doctor you want to make an appointment at and hit `search`
3. Once your on the doctor's landing page open your browsers `dev tools`, select the `Network` tab and leave it open for the next steps
4. Click on `TERMIN BUCHEN`
5. Answer the following questions in the appointment wizard until you reach the date overview that says `Wählen Sie das Datum für den Termin`
6. Copy the **URL of the browser** into the constant `BOOKING_URL`
6. Select the filter `Fetch/XHR` within the `Network` tab in order to make it easier to find the correct request URL
7. Look for a request to `availabilities.json…` and click on it in the list of requests
8. Copy the value of the `Request URL` in the detail view and paste it into the constant `AVAILABILITIES_URL`

### Cron

First of all the script has to be made executable.

```bash
chmod +x /path/to/notifyDoctolibDoctorsAppointment.py
```

Next, schedule the script execution via the cron.

```bash
crontab -e
```

E.g. this cron entry will run it every minute from 7:00 AM to 23:59 PM.

```bash
* 7-23 * * * python /path/to/notifyDoctolibDoctorsAppointment.py
```

## Settings

Adjust those constants to get the most out of your notifications.


### BOOKING_URL

Paste your doctolib booking URL in this constant. The Telegram message will contain a link to this page in case of available appointments.

Type `str`.

Default `https://www.doctolib.de/`.

### AVAILABILITIES_URL

Paste the complete URL to the Doctolib `availabilities.json` (including parameters) in this constant.

⚠️ The script will abort if you don't provide this data.

Type `str`.

Default `''`.

### APPOINTMENT_NAME

If you have multiple instances of the script running and share the same Telegram channel it's a good idea to make notifications allocatable.

Type `str|None`.

Default `None`.

### MOVE_BOOKING_URL

Provide a link to your `Termin verschieben` page behind your login to navigate fastest to the booking page and move the appointment in one go. When set, an extra link will be sent in addition to the `BOOKING_URL` link.

Type `str|None`.

Default `None`.

### UPCOMING_DAYS

Paste the number of days from today, that you want to monitor appointments for, in this constant.

ℹ️ Doctolib has a limit of 15 days.

Type `int`.

Default `15`.

### MAX_DATETIME_IN_FUTURE

If you already have an appointment within the next `UPCOMING_DAYS` you can set this date in this constant so that the script only notifies for **earlier dates**.

E.g.
```python
MAX_DATETIME_IN_FUTURE = datetime(2023, 6, 16, 12, 0, 0)
```

Type `datetime`.

Default `15 days in the future`.

### NOTIFY_HOURLY

Whether to notify late appointments (outside of the `UPCOMING_DAYS` range) hourly.

Type `bool`.

Default `False`.
