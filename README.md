# Packaging Batch Tracker

## Overview

The Packaging Batch Tracker is a Django-based web application designed to streamline and manage the production batches of a manufacturing process. The system allows users to create, edit, and track batches through various production stages.

* Batch Creation: Users can create new batches, specifying details such as batch number, product code, complete date target, etc.

* Bay Assignment: Batches can be assigned to specific production bays, with target start and end dates for each bay.

* Batch History Tracking: The application uses the Django Auditlog library to track and display the history of batch modifications, including changes to fields, dates, and who by.

* On-Hold: An "On-Hold" checkbox is available for batches, allowing users to indicate if a batch is currently on hold. Batches on hold are visually distinguished, changing the row colour to red and hiding from warehouse and labs pages.

* Production Check List: There is a production check list view that displays batches requiring final sign offs.

* Batch Completion Tracking: When a batch is marked as complete, the system records the completion date and the user who completed it.

## Installation

To run the batch tracker, you'll need Python 3 and Django. 

Create new Python env

```bash
python -m venv env
```

Activate env

Linux
```bash
source env/bin/activate
```

Windows
```ps1
.\env\Scripts\Activate.ps1
```

Install Requirements

```bash
pip install -r requirements.txt
```

Make migrations and then run migrations
```
python manage.py makemigrations
python manage.py migrate
```

Create a superuser
```
python manage.py createsuperuser
```

Run server
```
python manage.py runserver
```

Open website
```
http://127.0.0.1:8000/
```