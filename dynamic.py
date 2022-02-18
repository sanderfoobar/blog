#!/usr/bin/python3
# Flask app for comments and receiving hooks from git
from datetime import datetime
from hashlib import md5, sha256
import uuid
import io
import logging
import asyncio
import subprocess

import PIL.ImageOps
from PIL import Image, ImageFilter
from quart import Quart, session, request, abort, Response
from peewee import SqliteDatabase
import peewee as pw
from captcha.image import ImageCaptcha

from pelicanconf import SECRET_KEY, HOOK_URL

app = Quart(__name__)
app.secret_key = SECRET_KEY
logger = None
logger_fmt = "[%(levelname)s %(asctime)s] [%(pathname)s:%(lineno)d] %(funcName)s(): %(message)s"
db = SqliteDatabase("comments.sqlite3")
hook_url = HOOK_URL


@app.route(hook_url, methods=["POST"])
def hookz():
    exe = lambda k: subprocess.Popen(
        k,
        stdout=subprocess.PIPE
    ).communicate()[0]

    exe(["git", "fetch", "--all"])
    exe(["git", "reset", "--hard", "origin/master"])
    exe(["make", "html"])
    return "oki"


class Comment(pw.Model):
    id = pw.AutoField()
    article_id = pw.CharField(index=True)
    date_added = pw.DateTimeField(default=datetime.now)
    name = pw.CharField(index=True)
    body = pw.CharField()

    class Meta:
        database = db


def get_addr():
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For']
    return request.remote_addr


def get_article_uid_from_referer():
    if "referer" not in request.headers:
        return abort(404)

    referer = request.headers['referer']
    if not referer.endswith(".html"):
        return abort(404)

    try:
        article_id = referer.split("/")[-1]
        if len(article_id) <= 6:
            return abort(404)
    except:
        return abort(404)

    article_id = article_id.replace(".html", "")
    return article_id


@app.post("/")
async def post_comment():
    blob = await request.json
    if not blob:
        return abort(500)

    if "body" not in blob or "captcha" not in blob:
        return abort(500)

    body = blob['body']
    _captcha = blob['captcha']
    if len(body) > 2048:
        return abort(500, "comment too long")
    if not _captcha or len(_captcha) > 16 or session.get('captcha') != _captcha:
        return abort(500, "bad captcha")

    uid = md5(get_addr().encode()).hexdigest()[:6]
    uid = sha256(uid.encode()).hexdigest()[:6]
    article_id = get_article_uid_from_referer()

    c = Comment.create(
        body=body,
        name=uid,
        article_id=article_id
    )

    return {"data": "success"}


@app.get("/")
async def get_comments():
    article_id = get_article_uid_from_referer()

    q = Comment.select()
    q = q.filter(Comment.article_id == article_id)
    q = q.order_by(Comment.date_added.desc())

    data = []
    for comment in q:
        data.append({
            "date_added": comment.date_added.strftime("%Y-%m-%d %H:%M"),
            "name": comment.name,
            "comment": comment.body
        })

    return {"data": data}


@app.before_serving
async def startup():
    global logger
    Comment.create_table()


class HaxCaptcha(ImageCaptcha):
    def generate_image(self, chars):
        background = (0, 0, 0, 255)
        color = (255, 167, 0, 255)
        im = self.create_captcha_image(chars, color, background)
        self.create_noise_dots(im, color)
        self.create_noise_curve(im, color)
        im = im.filter(ImageFilter.SMOOTH)
        return im


@app.route("/captcha")
def captcha():
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    secret = uuid.uuid4().hex[:4]
    image = HaxCaptcha(fonts=[font])
    data = image.generate(secret)

    session['captcha'] = secret
    return Response(data, mimetype='image/jpg')


app.run(host="127.0.0.1", port=9300, use_reloader=False)
