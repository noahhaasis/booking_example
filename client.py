# importing the requests library
import requests
 
# example of sending a request to list the rooms
r = requests.get(url = "http://127.0.0.1:5000/rooms")
print(r.text) 

# example of sending a request to book room HW.003
r = requests.post(url = "http://127.0.0.1:5000/rooms/HW.003")
print(r.text) 

# example of sending a request to book room K.001
r = requests.post(url = "http://127.0.0.1:5000/rooms/K.001")
print(r.text) 
