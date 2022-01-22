# tweepy-test
I wrote this to programmatically populate Twitter lists.
When run, it will create the lists contained in *lists.json*
using credentials from *secrets.json*.

At the time this is being committed, there is no way to
import or export data without using the api.

### To setup
```bash
pip install tweepy
```

### To run
Unzip *secrets.json.zip* to *secrets.json* or provide another with this format:
```json
{
  "api_key": "<your_api_key>",
  "api_secret_key": "<your_api_secret_key>",
  "bearer_token": "<your_bearer_token>",
  "access_token": "<your_access_token>",
  "access_secret_token": "<your_access_secret_token>"
}
```