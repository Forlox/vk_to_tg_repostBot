import os
import asyncio
import json
import shutil
from vk import GetPosts
from tg import post

POSTS_DIR = "posts"
HISTORY_FILE = "history.json"
MAX_POSTS_TO_PROCESS = 100

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(history):
    """Сохраняет историю постов"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_posted_ids():
    history = load_history()
    return {post["id"] for post in history}


def get_new_vk_posts():
    print("Получение постов с ВК")

    posted_ids = get_posted_ids()
    print(f"Уже опубликовано: {len(posted_ids)} постов")

    vk_parser = GetPosts(n_posts=MAX_POSTS_TO_PROCESS)
    posts = vk_parser.get_last_posts(MAX_POSTS_TO_PROCESS)

    if not posts:
        print("Не удалось получить посты")
        return [], None

    new_posts = []
    for post in posts:
        if post['id'] not in posted_ids:
            new_posts.append(post)
        else:
            print(f"Пост {post['id']} уже опубликован, пропускаем")
            break

    print(f"Новых постов для обработки: {len(new_posts)}")
    return new_posts, vk_parser


async def publish_posts_directly(posts, vk_parser):
    if not posts:
        print("Нет постов для публикации")
        return

    print(f"\nПубликация {len(posts)} постов...")
    posts.sort(key=lambda x: x['id'])

    published_count = 0
    for post_data in posts:
        try:
            print(f"\nПубликую пост {post_data['id']}...")

            temp_folder = f"{POSTS_DIR}/temp_{post_data['id']}"
            os.makedirs(temp_folder, exist_ok=True)

            try:
                text_content = post_data['text'] if post_data['text'] else ""
                text_file = os.path.join(temp_folder, "text")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(text_content)

                posted_media_files = []
                media_links = []
                has_media = False
                has_text = bool(text_content.strip())

                if 'attachments' in post_data:
                    for attach in post_data['attachments']:
                        if attach['type'] == 'photo':
                            photo_url = vk_parser.get_photo_url(attach['photo'])
                            media_links.append(photo_url)

                            ext = 'jpg'
                            url_lower = photo_url.lower()
                            if '.png' in url_lower:
                                ext = 'png'
                            elif '.gif' in url_lower:
                                ext = 'gif'

                            import hashlib
                            url_hash = hashlib.md5(photo_url.encode()).hexdigest()[:8]
                            filename = f"{url_hash}.{ext}"

                            filepath = os.path.join(temp_folder, filename)
                            if vk_parser.download_file(photo_url, filepath):
                                posted_media_files.append(filename)
                                has_media = True

                        elif attach['type'] == 'video':
                            video = attach['video']
                            video_link = f"https://vk.com/video{video['owner_id']}_{video['id']}"
                            media_links.append(video_link)

                        elif attach['type'] == 'doc':
                            doc = attach['doc']
                            doc_link = f"https://vk.com/doc{doc['owner_id']}_{doc['id']}"
                            media_links.append(doc_link)

                        elif attach['type'] == 'link':
                            link = attach['link']
                            media_links.append(link['url'])

                        elif attach['type'] == 'audio':
                            audio = attach['audio']
                            audio_link = f"https://vk.com/audio{audio['owner_id']}_{audio['id']}"
                            media_links.append(audio_link)

                # Сохраняем media ссылки
                if media_links:
                    media_file = os.path.join(temp_folder, "media")
                    with open(media_file, 'w', encoding='utf-8') as f:
                        f.write("\n".join(media_links))

                if not has_text and not has_media:
                    print(f"Пост {post_data['id']} пустой (нет текста и медиа) - пропускаем отправку в Telegram")
                else:
                    await post(temp_folder)
                    print(f"Пост {post_data['id']} отправлен в Telegram")

                history = load_history()
                history.append({
                    "id": post_data['id'],
                    "date": post_data['date'],
                    "text": text_content,
                    "media": media_links,
                    "posted_media": posted_media_files
                })
                save_history(history)

                published_count += 1
                print(f"📝 Пост {post_data['id']} добавлен в историю")

            finally:
                shutil.rmtree(temp_folder, ignore_errors=True)

        except Exception as e:
            print(f"Ошибка при обработке поста {post_data['id']}: {e}")
            continue

    print(f"\nОпубликовано постов: {published_count}")


async def main():
    new_posts, vk_parser = get_new_vk_posts()
    await publish_posts_directly(new_posts, vk_parser)

if __name__ == "__main__":
    asyncio.run(main())