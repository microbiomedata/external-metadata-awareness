# GitHub Issue Dashboard for the Center for Cancer Data Harmonization Project

This project creates a Gantt-chart style visualization to track progress made on the Center for Cancer Data Harmonization (CCDH) project's workstream GitHub tickets. 

The live dashboard can be viewed at https://cancerdhc.github.io/dashboard. 

![image](https://user-images.githubusercontent.com/67020823/121235870-2d6a2c00-c84a-11eb-88fc-6368bcfc6ac4.png)

## Dashboard Data

The CCDH project consists of five workstreams; each workstream logs progress on goals in a GitHub repo.

Workstream Name | GitHub Repo URL
--------------- | ---------------
Operations | https://github.com/cancerDHC/operations/issues
Community Development | https://github.com/cancerDHC/community-development/issues
Data Model Harmonization | https://github.com/cancerDHC/data-model-harmonization/issues
CRDCH Model | https://github.com/cancerDHC/ccdhmodel/issues
Ontology and Terminology Ecosystem | https://github.com/cancerDHC/Terminology/issues
Tools and Data Quality | https://github.com/cancerDHC/tools/issues

This app uses the GitHub API to get all issues from each workstream. GitHub tickets are placed on the chart timeline if:

- the ticket has a Milestone that has a label indicating the Phase. The milestone label should contain the quarter the item is due (e.g., "Phase 2 - Quarter 4"; for end of Phase tickets, specify "Phase 2 - ENDS". If a quarter is not specified, the ticket will span the entire year. Note that Quarters refer to calendar quarters, not project quarters 
  - Example: Phase 2 starts on 4/1/2020. A ticket due at the end of the first quarter of Phase 2 (three months after the start of Phase 2) would have a milestone labeled "Phase 2 - Quarter 2". On the timeline, it would begin on 4/1/2020 and end on 6/30/2020.
  - Example: A ticket with the milestone "Phase 2 - ENDS" would be placed on the timeline starting on 4/1/2021 and ending on 5/31/2021.
  - Example: A ticket with the milestone "Phase 2" would be placed on the timeline starting 4/1/2020 and end on 3/31/2021.  
- the ticket is in the Operations repo and has a title indicating it is a deliverable (e.g., the title starts with "Del.E") or is a "high level" task (e.g., the title starts with the phase/task number such as "2a3")

The percent completion for each ticket is calculated based on whether the ticket is open or closed (closed tickets are 100% complete) and, if present, the proportion of checkboxes that are checked vs. unchecked.

## Features

- Click on a task to show the task title, due date, percent completion status, and link to the GitHub ticket.
- Show/hide each workstream's tickets by clicking on the workstream name at the top
- The timeline can be expanded or compressed by clicking the "Month" or "Year" buttons at the bottom. The Month view shows a half dozen or so months in the window (depending on the size of the browser window); the Year view displays a half dozen or so years in the window.
- Show/hide completed tasks by clicking the "Hide Completed Tasks" button.
- The "Create TSV" button creates a comma delimited file of all GitHub tickets for all workstreams. (See "all_cccdh_issues.tsv" for example output.) Fields include a unique issue ID, the issue title, the start and end dates for the issue, percent completion status (0 to 100), a list of dependencies, and the issue's GitHub URL. 

Task dependencies can be created by simply referencing another GitHub issue ID in the body of the text (e.g., typing "#15" in the body text assumes issue #15 is a dependency). Task dependencies are not displayed in the Gantt chart; a lack of an option to sort related tickets made the display too complex. However, a list of dependencies for each ticket is output when the data are exported using the "Create TSV" button.

## Development

The backbone of the app is based on a customized version of a Gantt chart visualation tool originally developed by [Frappe Gantt](https://frappe.io/gantt). The customized app can be found here: https://github.com/cancerDHC/frappe-gantt-custom-mod
