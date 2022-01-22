"""
Attempts at loading a webpage from another using jquery results in 403 Forbidden errors b/c of cross domain loads.
See: https://stackoverflow.com/questions/12032664/load-a-html-page-within-another-html-page

Data from new website can be found at:
<div class=“uk-container uk-container-expand”>
  <script>var elcap_calendar_config = [ …. </script>
  <script>var elcap_calendar_data = [ …. </script>
  <script>var elcap_calendar_mindbody_data = [ …. </script>
  <script>var elcap_calendar_location = “ …. </script>
  <script>var elcap_calendar_locations = { …. </script>
"""
import json
import re

import httpx


def get_location_data(location='sunnyvale'):
    """
    Valid locations @ 2021 Nov 26: 'san-francisco', 'belmont', 'sunnyvale', 'santa-clara'
    """
    response = httpx.get(f'https://el-cap.com/planetgranite-{location}/calendar/')
    assert response.status_code == 200

    data = {}
    expr = r'<script>var elcap_calendar_(\w*) = (.*?)</script>'
    for name, json_str in re.findall(expr, response.text, re.DOTALL):
        data[name] = json.loads(json_str)

    location_data = {}
    for location_type in data['data']:
        if not location_type['location'] == location:
            continue

        if len(location_type['data']) == 0:
            continue

        location_data[location_type['activity']] = location_type['data']

    return location_data


def repackage_data(location_data):
    data = ['title instructor substitutes cancelled start_epoch end_epoch categories recurring link'.split()]
    for activity_type, activity_data in location_data.items():
        for event in activity_data:
            if not event['isAvailable']:
                continue

            category = event["filters"]["activity"]
            if 'class-type' in event['filters']:
                category += ': ' + event['filters']['class-type']
            instructor = event['instructor'] if 'instructor' in event else ''
            data.append([event['title'], instructor, '', False,
                         event['startEpoch'], event['endEpoch'],
                         category, '', event['link']])
    return data


def collect_and_dump():
    location_data = get_location_data()
    data = repackage_data(location_data)
    with open('events.json', 'w') as json_out:
        json.dump(data, json_out)
    print(f'Wrote {len(data) - 1} events in events.json')


if __name__ == '__main__':
    collect_and_dump()
