from flask_restful import Api, Resource, reqparse
from api.data.data_vist import read_data
import json
import random

corpus = json.load(open("api/vist.json", "r"))
album_ids = list(corpus.keys())

class CorpusApiHandler(Resource):
    def get(self, album_id):
        
        print(album_id)
        if album_id == "-1":
            album_id = random.choice(album_ids)
            return corpus[album_id]
        else:
            if album_id in corpus:
                return corpus[album_id]
            else:
                return {"album_id": ""}
