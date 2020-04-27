import requests

url1 = "https://us-central1-ieor185-274323.cloudfunctions.net/update_health_model"
url2 = "https://us-central1-ieor185-274323.cloudfunctions.net/update_state_model"

requests.get(url1)
requests.get(url2)
