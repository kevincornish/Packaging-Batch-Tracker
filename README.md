# Packaging Batch Tracker

## Overview

The Packaging Batch Tracker was created to manage batches in a manufacturing environment using the Django framework.

## Features

### Batch Management
- View list of batches organised by bays.
- Edit target dates for batches in bays.
- Search batches by batch number.
- View schedule of upcoming batches based on manufacture dates.
- View lists of batches with bill of materials in the warehouse, awaiting samples, and pending production checks.
- View archive of fully completed batches.
- Add new batches with multiple target dates.
- Edit batch details including associated bays and target dates.
- View history / who made modifications to each batch.
- View location / bay change history of each batch.

### Bay Management
- View list of bays.
- Add new bays.
- Edit existing bays.

### Product Management
- View list of products.
- Add new products.
- Import products from a CSV file.
- Edit existing products.

### User Management
- Sign up only using set email address in .env

### Reporting
- View batches completed on a specific date range.
- View batches completed per week, per day, and before their given target dates.
- View batches completed by users per week.
- View KPIs for team leaders.

### Daily Discussion
- View and participate in daily discussions based on batches completed on the day.

### WIP Queue
- View a queue of batches currently in progress.
- Calculate working days since manufacture date.

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
pip install -r requirements-dev.txt
```

Rename ```sample.env``` to ```.env```

Make migrations and then run migrations
```
python manage.py makemigrations
python manage.py migrate
```

Create a superuser
```
python manage.py createsuperuser
```

Create user groups and bays/lines
```
python manage.py create_user_groups
python manage.py create_bays
```

For development, create test users, generate random products and then random batches (set number in args). Comments and target dates for each bay / line will also be set.
```
python manage.py create_users 2
python manage.py generate_products
python manage.py generate_batches 30
```

Run server
```
python manage.py runserver
```

Open website
```
http://127.0.0.1:8000/
```