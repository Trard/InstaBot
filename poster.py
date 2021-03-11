import requests
from linker import getPictureUrls
from json import load
from dotenv import load_dotenv
from datetime import datetime
from subprocess import call
from os import remove, environ
from dotenv import load_dotenv, find_dotenv


def upscale(pic):
    """скачивание + апскейл"""
    call(f"ffmpeg -i \"{pic}\" -vf scale=2160:-1 -pix_fmt yuvj444p art.jpg")

def get_photo(gid, token):
    """Определяем осноные параметры"""
    mainsettings = {"access_token": token, "group_id":-gid, "v": "5.130"}
    """получаем ссылку"""
    url = requests.post(
        "https://api.vk.com/method/photos.getWallUploadServer",
        params=mainsettings
        ).json()['response']['upload_url']
    """заливаем пикчу на сервер"""
    upload = requests.post(
        url,
        params=mainsettings,
        files={
            "file": open(f"art.jpg", "rb")
        }
    ).json()
    upload = upload | mainsettings
    """сохраняем пикчу"""
    save = requests.post(
        "https://api.vk.com/method/photos.saveWallPhoto",
        params=upload
    ).json()["response"][0]
    """удаляем пикчу с пк"""
    remove("art.jpg")
    """возвращаем айдишники"""
    owner_id = save["owner_id"]
    photo_id = save["id"]
    return f"photo{owner_id}_{photo_id},"

def get_date(gid, token, dayposts):
    """Получаем посты в отложке"""
    posts = requests.post("https://api.vk.com/method/wall.get",
        params={
            "owner_id": gid,
            "count": 100,
            "filter": "postponed",
            "access_token": token,
            "v": "5.130"
        }
    ).json()['response']['items']

    if posts != []:
        last_date = posts[-1]['date']
        publish_date = last_date + 86400/dayposts #86400 - кол-во секунд в сутках
    else:
        publish_date = 0 #сейчас

    return publish_date

def post(gid, author, photos, token, date):
    """постим пост с пикчей"""
    requests.post(
        "https://api.vk.com/method/wall.post",
        params={
            "owner_id": gid,
            "message": f"by {author}",
            "attachments": photos,
            "publish_date": date,
            "topic_id": 1,
            "access_token": token,
            "v": "5.130"
        }
    )

def get_upscaled_photos(gid, token, pics):
    """апскейлим каждую пикчу и загружаем"""
    photos = ""
    for pic in pics:  
        upscale(pic)
        photos = photos + get_photo(gid, token)
    return photos

def post_author(gid, author, token, inp_pics, count_pics_post, dayposts):
    """постим пикчи 1 автора"""
    for i in range(0, len(inp_pics), count_pics_post):
        pics = inp_pics[i:count_pics_post+i]
        photos = get_upscaled_photos(gid, token, pics)
        date = get_date(gid, token, dayposts)
        post(gid, author, photos, token, date)

def post_authors(gid, author, token_u, count_pics_post, dayposts):
    """постим всех авторов"""
    for author in authors:
        inp_pics = getPictureUrls(author)
        post_author(gid, author, token_u, inp_pics, count_pics_post, dayposts)


if __name__ == "__main__":
    gid = -195075564
    """загружаем токен из окружения"""
    load_dotenv(find_dotenv())
    token_u = environ.get("token")
    """парсим авторов из authors.json"""
    authors = load(open("authors.json", "r"))
    """загружаем всех авторов в сообщество"""
    post_authors(gid, authors, token_u, 6, 4)