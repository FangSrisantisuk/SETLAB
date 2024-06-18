# Team-8Q

## SET Lab Management Tool

This repository contains a web-based application designed for the management of lab courses within a school environment. The tool is built using the Python Dash framework and allows users to upload course data in Excel format and interactively select courses and locations to view their information as pie charts, tables, calendars and timelines.

## Features: 

File Upload: Users can upload Excel files containing course data directly into the application.

Course Selection: A dropdown menu allows users to select courses and view relevant data.

Location Selection: A dropdown menu allows users to select buildings and rooms and view relevant data.

Interactive Visualizations: Upon selecting courses or locations, the application generates pie charts, tables, calendars, and timelines to display relevant information.

## Usage

To run the application locally, follow these steps:

Ensure that Python is installed on your system.
Clone the repository to your local machine.
Install the required dependencies using pip install -r requirements.txt.
Run the application with python app.py and change parameter of run_server to run locally.

   app.run_server(debug=False, port=8080).

Visit http://127.0.0.1:8080/ in your web browser.

To run on the Cloud service: 

Visit https://mci-dash-app-iwjvfqdhnq-km.a.run.app

## Requirements
The application requires the following Python libraries:

requirements.txt

dash==2.16.1

dash-bootstrap-components==1.1.0

pandas==1.4.2

plotly==5.8.0

Flask==2.1.3

gunicorn
