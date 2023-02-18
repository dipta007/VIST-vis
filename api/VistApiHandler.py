from flask_restful import Api, Resource, reqparse
import json

albums = {}
album_ids = []
images_dii = {}
images_sis = {}


def get_data():
    global albums, album_ids, images_dii, images_sis
    with open("api/data/dii/train.description-in-isolation.json", "r") as fp:
        dii = json.load(fp)
    with open("api/data/sis/train.story-in-sequence.json", "r") as fp:
        sis = json.load(fp)
    print(dii.keys())
    print(sis.keys())

    for album in dii['albums'] + sis['albums']:
        album_id = album['id']
        album_ids.append(album_id)
        albums[album_id] = album
        albums[album_id]["images_dii"] = []
        albums[album_id]["images_sis"] = []
    
    album_ids = list(set(album_ids))

    for image in dii['images']:
        image_id = image['id']
        images_dii[image_id] = image
    
    for image in sis['images']:
        image_id = image['id']
        images_sis[image_id] = image
    
    for [annotation] in dii['annotations']:
        album_id = annotation['album_id']
        image_id = annotation['photo_flickr_id']
        albums[album_id]["images_dii"].append(images_dii[image_id])
        albums[album_id]["images_dii"][-1]["text"] = annotation['text']
        albums[album_id]["images_dii"][-1]["photo_order_in_story"] = annotation['photo_order_in_story']
    
    for [annotation] in sis['annotations']:
        album_id = annotation['album_id']
        image_id = annotation['photo_flickr_id']
        albums[album_id]["images_sis"].append(images_sis[image_id])
        albums[album_id]["images_sis"][-1]["text"] = annotation['text']
        albums[album_id]["images_sis"][-1]["worker_arranged_photo_order"] = annotation['worker_arranged_photo_order']

    for album_id in albums.keys():
        albums[album_id]["images_dii"] = sorted(albums[album_id]["images_dii"], key=lambda x: x["photo_order_in_story"])
        albums[album_id]["images_sis"] = sorted(albums[album_id]["images_sis"], key=lambda x: x["worker_arranged_photo_order"])

        sorted_img_ids = list(set([img['id'] for img in albums[album_id]["images_dii"]]))
        sis_img_ids = list(set([img['id'] for img in albums[album_id]["images_sis"]]))
        # print(sorted_img_ids, sis_img_ids)
        # return
        # albums[album_id]["images_sis"] = sorted(albums[album_id]["images_sis"], key=lambda x: sorted_img_ids.index(x["id"]))
        # albums[album_id]["images_sis"] = sorted(albums[album_id]["images_sis"], key=lambda x: x["worker_arranged_photo_order"])

        # albums[album_id]["images_dii"] = list({img['id']: img for img in albums[album_id]["images_dii"]}.values())
        # albums[album_id]["images_sis"] = list({img['id']: img for img in albums[album_id]["images_sis"]}.values())

    from pprint import pprint
    for id in album_ids:
        pprint(albums[id])
        break

class VistApiHandler(Resource):
    def get(self):
        get_data()
        return {"resultStatus": "SUCCESS", "message": "Hello Api Handler"}

    def post(self):
        print(self)
        parser = reqparse.RequestParser()
        parser.add_argument("type", type=str)
        parser.add_argument("message", type=str)

        args = parser.parse_args()

        print(args)
        # note, the post req from frontend needs to match the strings here (e.g. 'type and 'message')

        request_type = args["type"]
        request_json = args["message"]
        # ret_status, ret_msg = ReturnData(request_type, request_json)
        # currently just returning the req straight
        ret_status = request_type
        ret_msg = request_json

        if ret_msg:
            message = "Your Message Requested: {}".format(ret_msg)
        else:
            message = "No Msg"

        final_ret = {"status": "Success", "message": message}

        return final_ret
