from flask import Flask, send_from_directory
from flask_restful import Api, Resource, reqparse
# from flask_cors import CORS #comment this on deployment
from api.CorpusApiHandler import CorpusApiHandler

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
# CORS(app) #comment this on deployment
api = Api(app)
api.add_resource(CorpusApiHandler, '/api/vist/<album_id>')

@app.route("/", defaults={'path':''})
@app.route("/<path:path>")
def serve(path):
    return send_from_directory(app.static_folder,'index.html')