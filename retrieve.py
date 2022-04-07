import requests

url = 'https://europe-west1-indigo-history-346510.cloudfunctions.net/hello_world'
myobj = {'message': 'hello'}

x = requests.post(url, data=myobj)

print(x.text)