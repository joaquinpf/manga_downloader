import os
import sys
import config
import ann
import flask
import model
import traceback

from flask import request
from flask_apscheduler import APScheduler
from plugins.factory import SiteParserFactory
from manga_downloader import MangaDownloader
from flask_blitzdb import BlitzDB

sys.path.append(
    os.path.abspath('../')
)

# Global config
BLITZDB_DATABASE = r'./manga.db'

config.proxy = None
config.all_chapters_FLAG = False
config.auto = False
config.downloadFormat = '.cbz'
config.downloadPath = 'DEFAULT_VALUE'
config.overwrite_FLAG = False
config.verbose_FLAG = True
config.maxChapterThreads = 1
config.useShortName = True
config.spaceToken = ' '
config.check_every_minutes = 1

# Scheduler config
downloader = MangaDownloader()

def check_for_new_chapters():
    print('Sarasaaaaaa')
    mangas = db.connection.filter(model.Manga, {})
    mangas_json = [manga.attributes for manga in mangas]
    if len(mangas_json) > 0:
        downloader.download_chapters_from_config(mangas_json, config.downloadPath)
        i = 0

class Config(object):
    JOBS = [
        {
            'id': 'check_for_new_chapters',
            'func': '__main__:check_for_new_chapters',
            'trigger': {
                'type': 'cron',
                'minute': '*/' + str(config.check_every_minutes)
            }
        }
    ]

    SCHEDULER_VIEWS_ENABLED = True

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 1
    }

# Flask config
app = flask.Flask(__name__)
app.config.from_object(Config())
app.debug = True

# DB config
db = BlitzDB(app)

# Scheduler initialization
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# API Endpoints
@app.route('/api/v1.0/manga', methods=['POST'])
def create_manga():
    if not request.json or not 'name' in request.json or not 'host_site' in request.json:
        flask.abort(400)

    try:
        details = ann.get_ann_details(request.json['name'], 'manga')

        site_parser = SiteParserFactory.Instance().get_instance(request.json['host_site'])
        url = site_parser.get_manga_url(request.json['name'])

        manga = {
            'name': request.json['name'],
            'url': url,
            'host_site': request.json['host_site'],
            'details': details,
            'completed': False
        }
        manga_doc = model.Manga(manga)
        db.connection.save(manga_doc)
        return flask.jsonify(manga), 201
    except Exception, err:
        traceback.print_exc()
        flask.abort(400)


@app.route('/api/v1.0/manga/<id>', methods=['GET'])
def get_manga(id):
    manga = db.connection.get(model.Manga, {'pk': id})
    return flask.jsonify(manga.attributes), 200


@app.route('/api/v1.0/manga', methods=['GET'])
def get_mangas():
    mangas = db.connection.filter(model.Manga, {})
    mangas_json = [manga.attributes for manga in mangas]
    return flask.jsonify(content=mangas_json), 200


@app.route('/api/v1.0/manga/<id>', methods=['DELETE'])
def delete_manga(id):
    manga = db.connection.delete(model.Manga, {'id': id})
    return flask.jsonify(manga.attributes), 200

# Error Handlers
@app.errorhandler(400)
def not_found(error):
    response = flask.jsonify({'code': 400, 'message': 'Bad Request'})
    response.status_code = 400
    return response

if __name__ == '__main__':
    app.run(use_reloader=False)