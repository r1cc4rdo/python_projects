## Planet Granite Sunnyvale events scraper
This project:
* scrapes daily [Planet Granite website](https://planetgranite.com/sv/) for events,
* with a scheduled [AWS Lambda](https://aws.amazon.com/lambda/) function and
* publishes it to a [slick web page](https://planetgranite.github.io/) (also: [repo](https://github.com/planetgranite/planetgranite.github.io/)).

### Potential TODO items
Page load could be made faster by:

* using precompiled templates (see [handlebars runtime](https://cdnjs.cloudflare.com/ajax/libs/handlebars.js/4.4.2/handlebars.runtime.min.js))
* publish json events to a javascript file included as source instead of loading it afterwards
* compress json data
    * semantically: by recording event classes only once, and storing only start time and duration for each instance
    * literally: by using some form of compression (zip, gzip)
* remove whitespace from css, jscript, html
* remove unused css directives, jscript code [link](https://codeburst.io/capturing-unused-application-code-2b7594a9fe06)
* shrink font awesome web font [link](https://blog.webjeda.com/optimize-fontawesome/)

### Final update
As of Aug 20th, 2021 the lambda function is disabled.

The website has been updated twice, and event information can now be found without scraping within the page source:
```
<div class=“uk-container uk-container-expand”>
  <script>var elcap_calendar_config = [ …. </script>
  <script>var elcap_calendar_data = [ …. </script>
  <script>var elcap_calendar_mindbody_data = [ …. </script>
  <script>var elcap_calendar_location = “ …. </script>
  <script>var elcap_calendar_locations = { …. </script>
```
This test script shows how to pull the data: [pull_data_new_website.py](https://github.com/r1cc4rdo/python_projects/blob/main/webscraper/pull_data_new_website.py).

One could call it periodically to regenerate the json file to be included: for example by ditching Amazon's lambdas and using [GH actions](https://canovasjm.netlify.app/2020/11/29/github-actions-run-a-python-script-on-schedule-and-commit-changes/) instead.
