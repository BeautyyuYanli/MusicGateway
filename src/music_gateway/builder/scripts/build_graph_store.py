import logging
import os
import uuid
import time
import re
import json

from typing import Set, Dict

from dotenv import load_dotenv
from nebula3.Config import Config
from nebula3.gclient.net import ConnectionPool, Session

from music_gateway.spec import MusicInfo, AlbumInfo, ArtistInfo

load_dotenv()
logger = logging.getLogger(__name__)


def get_session():
    conn_pool = ConnectionPool()
    ip, port = os.getenv("NEBULA_ADDRESS").split(":")
    conn_pool.init(((ip, int(port)),), Config())
    session = conn_pool.get_session(
        os.getenv("NEBULA_USER"), os.getenv("NEBULA_PASSWORD")
    )
    return session


def escape_str(s: str):
    return s.encode("unicode_escape").decode("utf-8").replace('"', '\\"')


def insert_music(session: Session, music: MusicInfo):
    query = f'INSERT VERTEX music(name, url, ytb_url, wiki) VALUES "{uuid.UUID(music.mbid).hex}":("{escape_str(music.name)}", "{escape_str(music.url)}", "{escape_str(music.ytb_url)}", "{escape_str(music.wiki)}");'
    resp = session.execute(query)
    if not resp.is_succeeded():
        raise Exception(resp.error_msg())


def insert_artist(session: Session, artist: ArtistInfo):
    query = f'INSERT VERTEX artist(name, bio_content) VALUES "{uuid.UUID(artist.mbid).hex}":("{escape_str(artist.name)}", "{escape_str(artist.bio_content)}");'
    resp = session.execute(query)
    if not resp.is_succeeded():
        raise Exception(resp.error_msg())


def insert_album(session: Session, album: AlbumInfo):
    query = f'INSERT VERTEX album(name, wiki_content, image_url) VALUES "{uuid.UUID(album.mbid).hex}":("{escape_str(album.name)}", "{escape_str(album.wiki_content)}", "{escape_str(album.image_url)}");'
    resp = session.execute(query)
    if not resp.is_succeeded():
        raise Exception(resp.error_msg())


def insert_emotion(session: Session, name: str, emo_id: str):
    query = f'INSERT VERTEX emotions(name) VALUES "{emo_id}":("{escape_str(name)}");'
    resp = session.execute(query)
    if not resp.is_succeeded():
        raise Exception(resp.error_msg())


def insert_hashtag(session: Session, name: str, tag_id: str):
    query = f'INSERT VERTEX hashtags(name) VALUES "{tag_id}":("{escape_str(name)}");'
    resp = session.execute(query)
    if not resp.is_succeeded():
        raise Exception(resp.error_msg())


def insert_edge(
    session: Session,
    music: MusicInfo,
    emo_dict: Dict[str, str],
    tag_dict: Dict[str, str],
):
    q1 = f'INSERT EDGE created_by () VALUES "{uuid.UUID(music.mbid).hex}"->"{uuid.UUID(music.artiest_mbid).hex}":();'
    resp1 = session.execute(q1)
    q2 = f'INSERT EDGE belong_to () VALUES "{uuid.UUID(music.mbid).hex}"->"{uuid.UUID(music.album_mbid).hex}":();'
    resp2 = session.execute(q2)
    if not resp1.is_succeeded():
        raise Exception(resp1.error_msg())
    if not resp2.is_succeeded():
        raise Exception(resp2.error_msg())
    for emo in music.emotions:
        q3 = f'INSERT EDGE with_tag () VALUES "{uuid.UUID(music.mbid).hex}"->"{emo_dict[emo]}":();'
        resp3 = session.execute(q3)
        if not resp3.is_succeeded():
            raise Exception(resp3.error_msg())
    for tag in music.tags:
        q4 = f'INSERT EDGE with_tag () VALUES "{uuid.UUID(music.mbid).hex}"->"{tag_dict[tag]}":();'
        resp4 = session.execute(q4)
        if not resp4.is_succeeded():
            raise Exception(resp4.error_msg())


def batch_insert_music():
    emotions: Dict[str, str] = {}
    hashtags: Dict[str, str] = {}
    with open("data/mbids_done_13899.jsonl", "r") as f:
        session = get_session()
        session.execute("USE music_gateway;")
        cnt = 0
        while line := f.readline():
            cnt += 1
            # if cnt == 5:
            #     break
            music = MusicInfo.model_validate_json(line)
            try:
                insert_music(session, music)
                for emotion in music.emotions:
                    if emotion not in emotions:
                        emo_id = uuid.uuid4().hex
                        emotions[emotion] = emo_id
                        insert_emotion(session, emotion, emo_id)
                for hashtag in music.tags:
                    if hashtag not in hashtags:
                        tag_id = uuid.uuid4().hex
                        hashtags[hashtag] = tag_id
                        insert_hashtag(session, hashtag, tag_id)
                insert_edge(session, music, emotions, hashtags)

            except Exception as e:
                print(f"Error: {e}")
                with open("data/error_music_13899.jsonl", "a") as f1:
                    f1.write(music.model_dump_json())
                    f1.write("\n")
        session.release()
    with open("data/emotions_13899.json", "w") as f:
        f.write(json.dumps(emotions, indent=2))
    with open("data/hashtags_13899.json", "w") as f:
        f.write(json.dumps(hashtags, indent=2))


def batch_insert_artist():
    with open("data/artists_13899.jsonl", "r") as f:
        session = get_session()
        session.execute("USE music_gateway;")
        cnt = 0
        while line := f.readline():
            cnt += 1
            artist = ArtistInfo.model_validate_json(line)
            try:
                insert_artist(session, artist)
            except Exception as e:
                print(f"Error: {e}")
                with open("data/error_artists_13899.jsonl", "a") as f1:
                    f1.write(artist.model_dump_json())
                    f1.write("\n")
        session.release()


def batch_insert_album():
    with open("data/album_13899.jsonl", "r") as f:
        session = get_session()
        session.execute("USE music_gateway;")
        cnt = 0
        while line := f.readline():
            cnt += 1
            album = AlbumInfo.model_validate_json(line)
            try:
                insert_album(session, album)
            except Exception as e:
                print(f"Error: {e}")
                with open("data/error_album_13899.jsonl", "a") as f1:
                    f1.write(album.model_dump_json())
                    f1.write("\n")
        session.release()


batch_insert_artist()
batch_insert_album()
batch_insert_music()
