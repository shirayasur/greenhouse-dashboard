# Greenhouse Recruitment Dashboard
Greenhouse dashboard for an overview of an organization's recruitment processes 

## About
This dashboard tracks recruitment metrics from your greenhouse account using the Greenhouse API.

It tracks candidates' current stage, open roles, hiring speed for filled roles, and candidate source statistics.

See screenshots [here](screenshots)

![screenshot_2](https://github.com/shirayasur/greenhouse_dashboard/blob/main/screenshots/screenshot_2.png)

## How to Use
Generate a [Greenhouse API key](https://support.greenhouse.io/hc/en-us/articles/202842799-Generate-API-key-for-Greenhouse-Recruiting) and plug it in `utils.py`

Run `dashboard.py` to activate dashboard (default port is set to 8052)

### Other Options
* `UPDATE_INTERVAL` (dashboard.py) - change this to set how often the dashboard should fetch the data from Greenhouse. Default is every 5 hours.
* `stages_order` (utils.py) - change this according to your organization's recruitment pipeline 

## Credits
This dashboard was made using [Dash](https://plotly.com/dash/), [Harvest API](https://developers.greenhouse.io/harvest.html), and this [python wrapper](https://github.com/alecraso/grnhse-api) for Greenhouse API
