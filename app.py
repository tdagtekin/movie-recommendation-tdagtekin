from numpy import load
from flask import Flask, request, jsonify, render_template, url_for
import pickle
from pandas import Series, read_csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import rbf_kernel
import requests
import bs4
from bs4 import BeautifulSoup
app = Flask(__name__)

tfidf_matrix = load('tfidf_matrix.npy', allow_pickle=True)
rbf_ker_tfidf = rbf_kernel(tfidf_matrix[()], tfidf_matrix[()])
df = read_csv('df.csv')

indices = Series(df.index, index=df['movie_title'])
df_imdb_link = df.movie_imdb_link
headers = {
    'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
}

def recommendation(title, kernel):
    idx = indices[title]
    global sim_scores
    sim_scores = list(enumerate(kernel[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    movie_indices = [i[0] for i in sim_scores]
    return df['movie_title'].iloc[movie_indices]

def scrapper(movie):
    liste_image_url_names = []
    for i in range(len(movie.index)):
        liste_image_url_names.append(movie[movie.index[i]])
    list_url_image = []
    for i in liste_image_url_names:
        list_url_image.append(df_imdb_link[df[df['movie_title'] == i].index[0]])
    photos = []
    for i in range(5):
        r = requests.get(list_url_image[i], {'headers':headers})
        soup = bs4.BeautifulSoup(r.text, 'lxml')
        image = soup.find_all('div',
                        {'class':"ipc-media ipc-media--poster-27x40 ipc-image-media-ratio--poster-27x40 ipc-media--baseAlt ipc-media--poster-l ipc-poster__poster-image ipc-media__img"})[-1].extract()
        
        child = 'src'
        for child in image:
            child
        photo = child['src']
        
        photos.append(photo)
    return photos


@app.route("/")
@app.route("/home")
@app.route("/index")

def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST','GET'])
@app.route("/home", methods=['POST','GET'])
@app.route("/index", methods=['POST','GET'])

def my_get():
    if request.method == "POST":
        movie = request.form['nm']
        not_found = 'not_found'
        if (df['movie_title'] == movie).sum() > 0:
            movie = recommendation(movie, rbf_ker_tfidf)
            imgs = scrapper(movie)
            return render_template('recommendation.html' , movie=movie, imgs=imgs)
        else:
            return render_template('index.html' , movie=not_found)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False)