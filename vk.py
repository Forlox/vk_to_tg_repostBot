import requests
import os
import json

VK_TIMINGS = {
    'DELAY_BETWEEN_REQUESTS': 0.5,  # Задержка между запросами к VK API (сек)
    'CONNECTION_TIMEOUT': 5,  # Таймаут подключения (сек)
    'READ_TIMEOUT': 1,  # Таймаут чтения (сек)
    'DOWNLOAD_TIMEOUT': 1,  # Таймаут скачивания файлов (сек)
}

with open('API_KEYS.json', 'r', encoding='utf-8') as f:
    API = json.load(f)

GROUP_ID = API['vk']['GROUP_ID']
ACCESS_TOKEN = API['vk']['ACCESS_TOKEN']
VK_API_VERSION = API['vk']['VK_API_VERSION']


class GetPosts:
    def __init__(self, n_posts):
        self.n_posts = n_posts
        self.posts_dir = "posts"

        if not os.path.exists(self.posts_dir):
            os.makedirs(self.posts_dir)

    def get_last_posts(self, count):
        url = "https://api.vk.com/method/wall.get"
        params = {
            "owner_id": f"-{GROUP_ID}",
            "count": count,
            "access_token": ACCESS_TOKEN,
            "v": VK_API_VERSION
        }
        try:
            response = requests.get(
                url,
                params=params,
                timeout=(VK_TIMINGS['CONNECTION_TIMEOUT'], VK_TIMINGS['READ_TIMEOUT'])
            )
            data = response.json()
            if "error" in data:
                print(f"Ошибка ВК: {data['error']['error_msg']}")
                return None
            return data["response"]["items"]
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return None

    def download_file(self, url, filepath):
        try:
            response = requests.get(
                url,
                timeout=VK_TIMINGS['DOWNLOAD_TIMEOUT']
            )
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            return False
        except:
            return False

    def get_photo_url(self, photo):
        sizes = photo['sizes']
        priority = ['w', 'z', 'y', 'x', 'r', 'q', 'p', 'o', 'm']
        for size_type in priority:
            for size in sizes:
                if size['type'] == size_type:
                    return size['url']
        return sizes[-1]['url']