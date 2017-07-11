# py3-canvaslms-api
Python 3 API wrapper for Instructure's Canvas LMS with real-world examples of use.

Simplifies tasks and reporting involving assignments, courses, enrollments, outcomes, roles, subaccounts, and users.

Also includes functions that simplify performing SIS imports and exports, querying databases, and working with CSV and XSLX files.

The "core" directory contains the scripts that the API wrapper functions are in, as well as config.json, which you'll need to edit to match your environment. (You might also need to edit config.py). 

All other directories contain scripts using the core functions to accomplish tasks, including these:

* Sync subaccount-level learning outcomes with outcomes in an external repository.
* Sync course-level learning outcomes with subaccount-level outcomes.
* Import outcomes into a course from a formatted Word document.
* List assignments that use the Turnitin API.
* Retrieve an SIS report.
* Do an SIS import on a CSV file of enrollments created by running a SQL file against the SIS.
* Assist in assessing Canvas course design best practices by generating an inventory of courses and the Canvas features they use.
* Find and replace text in Canvas pages.
* List all cross-listed courses.
* List admins at the account and subaccount level.
