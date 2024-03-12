import requests
from packaging import version

headers = {"OCS-APIRequest": "true"}


# The API is implemented as documented here: https://deck.readthedocs.io/en/latest/API/
class DeckAPI:
    def __init__(self, url, auth):
        self.url = url
        self.auth = auth

    def get(self, route):
        response = requests.get(
            f"{self.url}{route}",
            auth=self.auth,
            headers=headers,
        )
        if response.status_code != requests.codes.ok:
            print(f"The response was: {response.content}")
            response.raise_for_status()
        return response

    def post(self, route, json):
        response = requests.post(
            f"{self.url}{route}",
            auth=self.auth,
            json=json,
            headers=headers,
        )
        if response.status_code != requests.codes.ok:
            print(f"The response was: {response.content}")
            response.raise_for_status()
        return response

    def postFiles(self, route, data, files):
        response = requests.post(
            f"{self.url}{route}",
            auth=self.auth,
            data=data,
            files=files,
            headers=headers,
        )
        if response.status_code != requests.codes.ok:
            print(f"The response was: {response.content}")
            response.raise_for_status()
        return response

    def put(self, route, json):
        response = requests.put(
            f"{self.url}{route}",
            auth=self.auth,
            json=json,
            headers=headers,
        )
        if response.status_code != requests.codes.ok:
            print(f"The response was: {response.content}")
            response.raise_for_status()
        return response

    def delete(self, route):
        response = requests.delete(
            f"{self.url}{route}",
            auth=self.auth,
            headers=headers,
        )

        if response.status_code != requests.codes.ok:
            print(f"The response was: {response.content}")
            response.raise_for_status()

        return response

    def getCompatibility(self):
        result = self.get("/ocs/v1.php/cloud/capabilities?format=json").json()

        if result['ocs']['meta']['status'] != 'ok':
            return 'The compatibility check failed'

        capabilities = result['ocs']['data']['capabilities']

        if 'deck' not in capabilities:
            return 'Please install deck on your nextcloud instance'

        deck = capabilities['deck']

        if version.parse(deck['version']) < version.parse('1.1.0'):
            return 'This script only supports version 1.1.0 and above'

        return None

    def getBoards(self):
        return self.get(f"/index.php/apps/deck/api/v1.0/boards").json()

    def getBoardDetails(self, boardId):
        return self.get(f"/index.php/apps/deck/api/v1.0/boards/{boardId}").json()

    def getStacks(self, boardId):
        return self.get(f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks").json()

    def getStacksArchived(self, boardId):
        return self.get(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/archived"
        ).json()

    def createBoard(self, title, color):
        board = self.post(
            "/index.php/apps/deck/api/v1.0/boards", {"title": title, "color": color}
        ).json()
        boardId = board["id"]
        # remove all default labels
        for label in board["labels"]:
            labelId = label["id"]
            self.delete(
                f"/index.php/apps/deck/api/v1.0/boards/{boardId}/labels/{labelId}"
            )
        return board

    def createLabel(self, title, color, boardId):
        return self.post(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/labels",
            {"title": title, "color": color},
        ).json()

    def createStack(self, title, order, boardId):
        return self.post(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks",
            {"title": title, "order": order},
        ).json()

    def createCard(self, title, ctype, order, description, duedate, boardId, stackId):
        return self.post(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards",
            {
                "title": title,
                "type": ctype,
                "order": order,
                "description": description,
                "duedate": duedate.isoformat() if duedate is not None else None,
            },
        ).json()

    def assignLabel(self, labelId, cardId, boardId, stackId):
        self.put(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}/assignLabel",
            {"labelId": labelId},
        )

    def archiveCard(self, card, boardId, stackId):
        card['archived'] = True
        self.put(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{card['id']}",
            card,
        )

    def commentOnCard(self, cardId, message, parentId=None):
        self.post(
            f"/ocs/v2.php/apps/deck/api/v1.0/cards/{cardId}/comments",
            {"message": message, "parentId": parentId},
        )

    def attachToCard(self, boardId, stackId, cardId, fileName, fileObject, mimeType):
        self.postFiles(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}/attachments",
            {"type": "file"},
            {"file": (fileName, fileObject, mimeType)},
        )
