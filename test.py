import requests
from bs4 import BeautifulSoup

event_num = 122  # example event number
response = requests.get(f"https://tmomvolunteer.org/event/{event_num}")


# OR, if you want it to be a bit more readable with BeautifulSoup:
soup = BeautifulSoup(response.content, 'html.parser')
unavailable_msg = soup.find("div", id="registration")
print(soup.prettify())
print("Registration for this event is currently unavailable." in unavailable_msg.text)