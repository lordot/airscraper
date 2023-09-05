import os

import crochet
import uvicorn

from notificator.notificator.spiders.offers import OffersSpider

crochet.setup()

from asgiref.wsgi import WsgiToAsgi
from flask import Flask, jsonify, request, redirect, url_for
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)

output_data = []
crawl_runner = CrawlerRunner()


@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        s = request.get_json()
        global ARGS
        ARGS = s

        if os.path.exists("data.json"):
            os.remove("data.json")

        return redirect(url_for('scrape'))


@app.route("/scrape")
def scrape():
    output_data.clear()

    scrape_with_crochet(ARGS)

    time.sleep(20)

    return jsonify(output_data)


@crochet.run_in_reactor
def scrape_with_crochet(ARGS):
    dispatcher.connect(_crawler_result, signal=signals.item_scraped)

    eventual = crawl_runner.crawl(OffersSpider, **ARGS)
    return eventual


def _crawler_result(item, response, spider):
    output_data.append(dict(item))


if __name__ == "__main__":
    uvicorn.run("main:asgi_app", host="0.0.0.0", port=8000, reload=True)
