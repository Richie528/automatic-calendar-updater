import sys
import requests
from bs4 import BeautifulSoup

urlFile = open(sys.path[0] + '/../super-secret-url.txt')
requestUrl = urlFile.readline()
print(requestUrl)
r = requests.get(requestUrl, headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'})
c = "dTddCR"
soup = BeautifulSoup(r.content, "html.parser")

dateElements = soup.find_all("span", class_=c)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
dates = []
utc = "+10:00"

for dateElement in dateElements:
    dates.append(dateElement.text)

print(dates)

for i in range(0, len(dates)):
    parts = dates[i].split(", ")
    for j in range(0, len(parts)):
        parts[j] = parts[j].split(" ")

    year = int(2000 + int(parts[2][2]))
    month = months.index(parts[2][1]) + 1
    day = int(parts[2][0])
    hour = parts[0][0]
    if parts[0][1] == 'PM':
        hour = hour.split(":")
        hour[0] = int(hour[0]) % 12
        hour[0] += 12
        hour = ":".join([str(hour[0]), str(hour[1])])

    dates[i] = [year, month, day, hour]

for date in dates:
    print(date)

