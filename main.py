import json
import requests
from pathlib import Path
from sys import stdout
from PIL import Image
def CreateImages(targetName, path, count):
    for index in range(1, count + 1):
        ProgressBar(targetName, 50 + (index - 1) * 50 / count)
        image1 = Image.open(path / ("thumb" + str(index) + ".png"))
        image2 = Image.open(path / ("thumb" + str((index % count) + 1) + ".png"))
        image3 = Image.open(path / ("thumb" + str(((index + 1) % count) + 1) + ".png"))
        for stage in range(0, 4):
            w = 480 * 2**stage
            h = 360 * 2**stage
            image = image1.resize((w, h), Image.ANTIALIAS).crop((w / 2 - 240, h / 2 - 180, w / 2 + 240, h / 2 + 180))
            w = 480 * 2**(stage - 4)
            h = 360 * 2**(stage - 4)
            image.paste(image2.resize(((int)(480 * 2**(stage - 4)), (int)(360 * 2**(stage - 4))), Image.ANTIALIAS), ((int)(240 - w / 2), (int)(180 - h / 2)))
            w = 480 * 2**(stage - 8)
            h = 360 * 2**(stage - 8)
            image.paste(image3.resize(((int)(480 * 2**(stage - 8)), (int)(360 * 2**(stage - 8))), Image.ANTIALIAS), ((int)(240 - w / 2), (int)(180 - h / 2)))
            image.save(path / ("frame" + str(index * 4 + stage - 3) + ".png"))
def ProgressBar(name, percent):
    n = 100
    j = percent / n
    stdout.write('\r')
    stdout.write(name + "[%-20s] %d%%" % ('='*int(20*j), 100*j))
    stdout.flush()
def ParseEndpoint(endpoint, target, isUsername):
    if isUsername:
        pathname = requests.get(endpoint).json()["username"]
        targetName = 'Username: "' + pathname + '" - '
    else:
        pathname = requests.get(endpoint).json()["title"]
        targetName = 'Studio: "' + pathname + '" - '
    endpoint += "/projects"
    projects = []
    offset = 0
    progress = 0
    Path(pathname).mkdir(exist_ok=True)
    path = Path(pathname)
    while True:
        response = requests.get(endpoint + "?offset=" + str(offset) + "&limit=40")
        if not response.json():
            break
        projects += response.json()
        offset += 40
    progressStep = 50 / len(projects)
    projectNum = 1
    for project in projects:
        response = requests.get("https://cdn2.scratch.mit.edu/get_image/project/" + str(project["id"]) + "_480x360.png")
        with (path / ("thumb" + str(projectNum) + ".png")).open("wb") as imageOutput:
            imageOutput.write(response.content)
            projectNum += 1
            progress += progressStep
            ProgressBar(targetName, progress)
    CreateImages(targetName, path, len(projects))
    ProgressBar(targetName, 100)
target = input("Enter username or studio number:")
userEndpoint = "https://api.scratch.mit.edu/users/" + target
studioEndpoint = "https://api.scratch.mit.edu/studios/" + target
response = requests.get(userEndpoint)
validUser = response.status_code == 200
validStudio = False
if target.isnumeric():
    response = requests.get(studioEndpoint)
    validStudio = response.status_code == 200
if validStudio and not validUser:
    ParseEndpoint(studioEndpoint, target, False)
elif not validStudio and validUser:
    ParseEndpoint(userEndpoint, target, True)
elif not (validStudio or validUser):
    print('"' + target + '" is not a valid username or studio id')
else:
    while True:
        targetType = input("Is this (1) a username or (2) a studio?")
        if targetType == "1":
            ParseEndPoint(userEndpoint, target, True)
            break
        elif targetType =="2":
            ParseEndpoint(studioEndpoint, target, False)
            break