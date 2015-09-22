import json

from flask import Flask, jsonify, request, render_template
import sendwithus


api = sendwithus.api(api_key='test_a1352c77daceca6ad24ba21a28b071735ee53f73')
with open('templates/share_photos.html') as f:
    res = api.create_template(
        name='Email Name',
        subject='Email Subject',
        html=f.read(),
        text='Optional text content'
    )
    share_template_id = res.json()['id']

app = Flask(__name__)

with open('photos.json') as f:
    photos = json.loads(f.read())


@app.route('/')
def index():
    return render_template('index.html')


def gen_photos(q):
    for photo in photos:
        if q in photo['title']:
            yield photo


@app.route('/search')
def search():
    q = request.args['q']
    return render_template('results.html', q=q, photos=list(gen_photos(q)))


@app.route('/share')
def share():
    ids = set(int(id) for id in request.args.getlist('ids'))
    message = request.args.get('message')
    email_data = {
        'message': message,
        'photos': [photo for photo in photos if photo['id'] in ids],
    }
    r = api.send(
        email_id=share_template_id,
        email_data=email_data,
        recipient={'address': 'test@example.com'},
    )
    return render_template('share_photos.html', **email_data), r.status_code


if __name__ == '__main__':
    app.run(debug=True)
