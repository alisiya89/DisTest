import requests


# Класс для взаимодействия с API словаря
class API:
    api_server = "https://developers.lingvolive.com/api/"
    api_key = "MWM5MjJiNWEtZjUzNC00YmRkLWFhZGYtMWNjNjM2Y2I1NzY2OmE0ZDhhNGFlNDM4NzRmNDhhYzkyOTAzMDg3MDg4NmRh"
    token = None


    def __init__(self):
         self.authorization()


    # Авторизация в API
    def authorization(self):
        headers = {"Authorization": f"Basic {self.api_key}",
                   "Content-type": "application/json"}
        response = requests.post(f"{self.api_server}v1.1/authenticate", headers=headers)
        self.token = str(response.content)[2:-1]


    # Получение перевода слова
    def get_translation(self, word):
        headers = {"Authorization": f"Bearer {self.token}",
                   "Content-type": "application/json"}
        params = {"text": word,
                  "srcLang": 1049,
                  "dstLang": 1033}
        response = requests.get(f"{self.api_server}v1/Minicard", headers=headers, params=params)
        if "401" in str(response):
            self.authorization()
            response = requests.get(f"{self.api_server}v1/Minicard", headers=headers, params=params)
        if "200" in str(response):
            json_response = response.json()
            return json_response["Translation"]["Translation"]
        return 404