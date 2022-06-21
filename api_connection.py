import requests

def search_in_googlebooks(keyword):
    api = 'https://www.googleapis.com/books/v1/volumes?maxResults=12&q='
    api += keyword.replace(" ", "+")
    json = requests.get(api).json()
    items = json['items'][0:12]
    books = []
    for i in items:
        id = ""
        title="" 
        authors="" 
        description="no description"
        cover = ""
        try:
            id = i['id']
            title = i['volumeInfo']['title']
            authors = i['volumeInfo']['authors']
            description = i['volumeInfo']['description']
            cover = i['volumeInfo']['imageLinks']['thumbnail']
        except KeyError:
            pass
        books.append({"id":id,"title":title,"authors":authors,"description":description,"cover":cover})
    return books
    
def search_book(id):
    api = 'https://www.googleapis.com/books/v1/volumes/'+id
    req = requests.get(api)
    json = req.json()
    if req.status_code > 400:
        return {"error": req.status_code}
    id = ""
    title="" 
    authors="" 
    description="no description"
    cover = ""
    try:
        id = json['id']
        title = json['volumeInfo']['title']
        authors = json['volumeInfo']['authors']
        description = json['volumeInfo']['description']
        cover = json['volumeInfo']['imageLinks']['thumbnail']
    except KeyError:
        pass
    return {"id":id,"title":title,"authors":authors,"description":description,"cover":cover}
    
if __name__ == "__main__":
    pass