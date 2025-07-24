import base64
import json
import time
import requests

API_KEY=""
SECRET_KEY=""

class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS, timeout=60)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline_id, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }

        data = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)


def _get_quote_by_api():
    url_api = "https://quotes.to.digital/api/random"
    result = requests.get(url_api, timeout=60)
    if result.status_code==200:
        return result.json().get("quote")
    return ""
    



if __name__ == '__main__':
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', API_KEY, SECRET_KEY)
    pipeline_id = api.get_pipeline()
    quote = _get_quote_by_api()
    if not quote:
        quote = "Sun in sky"
    uuid = api.generate(quote, pipeline_id)
    images = api.check_generation(uuid)
    image_base64 = images[0]
    # Декодируем строку base64 в бинарные данные

    image_data = base64.b64decode(image_base64)

    # Открываем файл для записи бинарных данных изображения

    with open(f"{quote}.jpg", "wb") as file:
        file.write(image_data)
    print("Ready !!!")
