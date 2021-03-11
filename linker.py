import requests
from bs4 import BeautifulSoup


def getPictureUrls(author):
  header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81'}
  instraw = requests.get(f'https://www.instagram.com/{author}/?__a=1', headers = header)
  instjson = instraw.json()
  posts = instjson["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]

  picture_urls = []
  for postn in posts:
    post = postn["node"]
    if post["__typename"] == "GraphVideo":
      continue
    elif post["__typename"] == "GraphSidecar":
      if post["edge_sidecar_to_children"]["edges"][0]["node"]["__typename"] != "GraphVideo":
        picture_urls.append(post["edge_sidecar_to_children"]["edges"][0]["node"]['display_url'])
    else:
      picture_urls.append(post['display_url'])
  return picture_urls


if __name__ == '__main__':
  import webbrowser

  authors = ["geoglyser"]
  for author in authors:
    links = getPictureUrls(author)
    print(len(links))
    for i in links:
      webbrowser.open(i)  