## Author: Frank Ferraro, ferraro@umbc.edu
## CC-BY-SA

import numpy
from collections import defaultdict


import os
import simplejson as json
from enum import Enum


SOS = "<SEQ>"
EOS = "</SEQ>"
OOV = "<OOV>"


class Vocab:
    def __init__(self):
        self.word2index = {}
        self.index2count = defaultdict(int)
        self.index2word = []
        self.OOV_index = 0
        self.add_word(OOV)
        self.add_word(SOS)
        self.add_word(EOS)

    @property
    def num_words(self):
        return len(self.word2index)

    def __len__(self):
        return self.num_words

    def get(self, word_str):
        return self.word2index.get(word_str, self.OOV_index)

    def add_word(self, word_str):
        if word_str not in self.word2index:
            self.word2index[word_str] = self.num_words
            self.index2word.append(word_str)
        self.index2count[self.get(word_str)] += 1


class Corpus:
    def __init__(self):
        self.vocab = Vocab()
        self.docs = defaultdict(list)
        self.labels = defaultdict(list)

    @property
    def vocab_size(self):
        return len(self.vocab)

    def add_words(self, strng):
        for w in strng.split():
            self.vocab.add_word(w)

    def see_doc(self, album, doc, label):
        key = album
        self.docs[key].append(doc)
        for x in doc:
            self.add_words(x["text"])
        self.labels[key].append(label)

    def __len__(self):
        return len(self.docs)

    def get_specific_data(self, album_id, iterate="individual"):
        key = album_id
        if key not in self.docs:
            return None
        if iterate == "individual":
            for story, label in zip(self.docs[key], self.labels[key]):
                return ([annot["text"] for annot in story], label)
        elif iterate == "paired":
            sis = filter(
                lambda x: x[1] == Label.STORYLET_SEQ,
                zip(self.docs[key], self.labels[key]),
            )
            dii = filter(
                lambda x: x[1] == Label.CAPTION_SEQ,
                zip(self.docs[key], self.labels[key]),
            )
            for paired in zip(sis, dii):
                if paired[0][0][0]['album_id'] == album_id:
                    return {
                        "sis": [{"text": annot["text"], "img_url": annot['img_url']} for annot in paired[0][0]],
                        "dii": [{"text": annot["text"], "img_url": annot['img_url']} for annot in paired[1][0]],
                        "album_id": paired[0][0][0]['album_id'],
                    }
        else:
            return None

    def get_data(self, random=False, iterate="individual"):
        lst = (
            self.docs.keys()
            if not random
            else numpy.random.permutation(list(self.docs.keys()))
        )
        for key in lst:
            if iterate == "individual":
                for story, label in zip(self.docs[key], self.labels[key]):
                    yield ([annot["text"] for annot in story], label)
            elif iterate == "paired":
                sis = filter(
                    lambda x: x[1] == Label.STORYLET_SEQ,
                    zip(self.docs[key], self.labels[key]),
                )
                dii = filter(
                    lambda x: x[1] == Label.CAPTION_SEQ,
                    zip(self.docs[key], self.labels[key]),
                )
                for paired in zip(sis, dii):
                    yield {
                        "sis": [{"text": annot["text"], "img_url": annot['img_url']} for annot in paired[0][0]],
                        "dii": [{"text": annot["text"], "img_url": annot['img_url']} for annot in paired[1][0]],
                        "album_id": paired[0][0][0]['album_id'],
                    }
            else:
                return None


class Label(Enum):
    STORYLET_SEQ = 1
    CAPTION_SEQ = 2


def read_data(folder, eval_split="val"):
    """
    Return a tuple of (Corpus, Corpus). The first is the training corpus, the second is the evaluation corpus.
    """
    train_corpus = Corpus()

    def read_sis(fp, corpus, albums2majority_ps_ptr):
        jdata = json.load(fp)
        stories = defaultdict(list)
        albums2stories = defaultdict(set)
        image2url = {}
        for annotations in jdata["annotations"]:
            annot = annotations[0]
            stories[annot["story_id"]].append(annot)
            albums2stories[annot["album_id"]].add(annot["story_id"])

        for image in jdata["images"]:
            image2url[image['id']] = image['url_o'] if "url_o" in image else image['url_m']

        for album_id in albums2stories:
            photo_seq_count = defaultdict(int)
            photo_seq_to_sid = defaultdict(list)
            for story_id in albums2stories[album_id]:
                photo_seq = tuple([s["photo_flickr_id"] for s in stories[story_id]])
                photo_seq_count[photo_seq] += 1
                photo_seq_to_sid[photo_seq].append(story_id)

            photo_seq_count = sorted(photo_seq_count.items(), key=lambda x: -x[1])
            majority_photo_seq = photo_seq_count[0][0]
            albums2majority_ps_ptr[album_id] = majority_photo_seq
            for story_id in photo_seq_to_sid[majority_photo_seq]:
                for v in stories[story_id]:
                    v['img_url'] = image2url[v['photo_flickr_id']]
                corpus.see_doc(album_id, stories[story_id], Label.STORYLET_SEQ)

    def read_dii(fp, corpus):
        jdata = json.load(fp)
        stories = defaultdict(list)
        albums2stories = defaultdict(set)
        image2url = {}
        for annotations in jdata["annotations"]:
            annot = annotations[0]
            stories[(annot["album_id"], annot["photo_flickr_id"])].append(annot)
            albums2stories[annot["album_id"]].add(
                (annot["album_id"], annot["photo_flickr_id"])
            )

        for image in jdata["images"]:
            image2url[image['id']] = image['url_o'] if "url_o" in image else image['url_m']

        for album_id in albums2stories:
            caption_stories = [[], [], []]
            for k1, photo_id in albums2stories[album_id]:
                for i, s in enumerate(stories[(k1, photo_id)]):
                    caption_stories[i].append(s)
                for i in range(3):
                    for v in caption_stories[i]:
                        v['img_url'] = image2url[v['photo_flickr_id']]
                    corpus.see_doc(album_id, caption_stories[i], Label.CAPTION_SEQ)

    albums2majority_ps_train = {}
    with open(os.path.join(folder, "sis/train.story-in-sequence.json"), "r") as fp:
        read_sis(fp, train_corpus, albums2majority_ps_train)
    with open(
        os.path.join(folder, "dii/train.description-in-isolation.json"), "r"
    ) as fp:
        read_dii(fp, train_corpus)

    eval_corpus = Corpus()
    # eval_corpus.vocab = train_corpus.vocab
    # albums2majority_ps_eval = {}
    # with open(
    #     os.path.join(folder, "sis/%s.story-in-sequence.json" % eval_split), "r"
    # ) as fp:
    #     read_sis(fp, eval_corpus, albums2majority_ps_eval)
    # with open(
    #     os.path.join(folder, "dii/%s.description-in-isolation.json" % eval_split), "r"
    # ) as fp:
    #     read_dii(fp, eval_corpus)

    return (train_corpus, eval_corpus)

if __name__ == "__main__":
    tc, ec = read_data("./")

    # %%
    # print(tc)
    # print(type(tc))
    saved_data = {}
    for o in tc.get_data(False, "paired"):
        saved_data[o["album_id"]] = o
    import json
    with open('../vist.json', 'w') as fp:
        json.dump(saved_data, fp, indent=4)
    # %%
