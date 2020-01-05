from decouple import config
import requests, json, os, io, shutil

# set req vars
clientID = config("clientID")
clientSecret = config("clientSecret")
authURL = config("authURL")
baseURL = config("baseURL")

# prepare the target directory
if 'assets' not in os.listdir(os.getcwd()):
    os.makedirs('assets')
print("\n/**** SFMC ASSET PULL ****/\n")
# get asset id for api call
assetID = int(input("\nENTER ASSET ID: "))
# get folder name in order to build path
folderName = input("\nENTER FOLDER NAME: ")
filePath = "assets/" + folderName + "/"
if filePath not in os.listdir(os.getcwd()):
    os.makedirs(filePath)
#get access token for api call
def getToken():
    payload = {
        "clientSecret": clientSecret,
        "clientId":clientID
    }
    print("\nAuthenticating...\n")
    res = requests.post(authURL, data=payload)
    res.raise_for_status()
    return json.loads(res.text)["accessToken"]
    print("Done.")

accessToken = getToken()
headers = {
    'content-type': 'application/json',
    'Authorization': 'Bearer ' + accessToken
}
# content request payload
contentRequest = {
    "query": {
        "property": "assetType.id",
        "simpleOperator": "equals",
        "valueType": "int",
        "value": assetID
    },
    "page": {
        "pageSize": 5000
    }
}
print("Getting assets...\n")
# get asset data from content builder rest api
res = requests.post(baseURL + 'asset/v1/content/assets/query', data=json.dumps(contentRequest, separators=(',', ':')), headers=headers)
res.raise_for_status()
print("Done\n")

assetsJSON = res.text
assetLoad = []
numOfAssetsFound = 0
print("Downloading Library\n")
assetsList = json.loads(assetsJSON)["items"]
for asset in assetsList:
    # append html extension if asset id greater than 200
    fileIDExt = filePath + asset["name"].replace("/","_")
    if assetID > 194:
        fileID = fileIDExt + ".html"
    else:
        fileID = fileIDExt
    targetFile = io.open(fileID, 'w+', encoding="utf-8")
    # if template-based, html or text email
    if assetID == "207" or assetID == "208" or assetID == "209":
        if "content" in asset:
            # write asset to local storage
            targetFile.write(str(asset["views"]["html"]["content"]))
    # if not in the criteria above but asset id is of type "block"
    elif (assetID != "207" and assetID != "208") and (assetID > 194):
        if "content" in asset:
            # write asset to local storage
            targetFile.write(str(asset["content"]))
    else:
        assetURL = str(asset["fileProperties"]["publishedURL"])
        # retrieve asset from the web and download to local storage
        response = requests.get(assetURL, stream=True)
        with open(fileID, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    targetFile.close()
    numOfAssetsFound += 1
print(str(numOfAssetsFound) + " assets found\n")
print("Data successfully pulled to local storage")
exit()