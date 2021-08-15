<div align="center">
<h1 align="center">Timetracker</h1></div>

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup & Installation](#setup-&-installation)
* [Running The App](#running-the-app)
* [Viewing The App](#viewing-the-app)
* [Features](#features)
* [Status](#status)
* [Contact](#contact)

## General info
**Work time registration** with many features created in **Flask** to check Flask skills.

## Technologies
* HTML5
* CSS3
* Bootstrap 4
* Python 3.9.x
* Flask 1.1.x
* SQLAlchemy 1.3.x
* SQLite3

## Setup & Installation
Make sure you have the latest version of Python and pip installed

Clone the repository using the following command
```bash
git clone https://github.com/Gamattowicz/Timetracker_Flask.git
```
Create a virtual environment
```bash
python -m venv venv
```
Active the virtual environment
```bash
.\env\Scripts\activate
```
Install all the project Requirements
```bash
pip install -r requirements.txt
```
Create file with environment variables, where <secret_key_name> is your unique data. It should be hidden.
```bash
echo SECRET_KEY=<secret_key_name> > .env
```
## Running The App
```bash
python timetracker.py
```

## Viewing The App
Go to `http://127.0.0.1:5000`

## Features
* User management system
* Calculation of vacation days
* Working timer
* Adding hours of work and projects
* Projects schedule
* Calculation of overtime

## Status 
Project in progress.

## Contact
Created by [@Gamattowicz](https://github.com/Gamattowicz) - feel free to contact me!