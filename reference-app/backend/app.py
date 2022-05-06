from flask import Flask, render_template, request, jsonify

from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_prometheus_metrics import register_metrics

import pymongo
import logging
from flask_pymongo import PyMongo

from jaeger_client import Config
from flask_opentracing import FlaskTracing

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "example-mongodb"
app.config[
    "MONGO_URI"
] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

mongo = PyMongo(app)

def init_tracer(service):
    logging.getLogger("").handlers = []
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    config = Config(
        config={"sampler": {"type": "const", "param": 1,}, "logging": True, 'reporter_batch_size': 1,},
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

jaeger_tracer = init_tracer("backend")

tracing = FlaskTracing(jaeger_tracer)

# provide app's version and deploy environment/config name to set a gauge metric
register_metrics(app, app_version="v0.1.2", app_config="staging")

# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

@app.route("/")
def homepage():
    with jaeger_tracer.start_active_span('homepage') as scope:
        return "Hello World"


@app.route("/api")
def my_api():
    with jaeger_tracer.start_active_span('my_api') as scope:
        answer = "something"
        return jsonify(repsonse=answer)


@app.route("/star", methods=["POST"])
def add_star():
    with jaeger_tracer.start_active_span('add_star') as scope:
        star = mongo.db.stars
        scope.span.log_kv({'event': 'starting mongodb', 'value': star })

        name = request.json["name"]
        scope.span.log_kv({'event': 'getting name from request', 'value': name })

        distance = request.json["distance"]
        scope.span.log_kv({'event': 'getting distance from request', 'value': distance })

        star_id = star.insert({"name": name, "distance": distance})
        scope.span.log_kv({'event': 'insert into mongodb', 'value': star_id })

        new_star = star.find_one({"_id": star_id})
        scope.span.log_kv({'event': 'find inserted value', 'value': new_star })

        output = {"name": new_star["name"], "distance": new_star["distance"]}
        scope.span.log_kv({'event': 'output value', 'value': output })
        
        return jsonify({"result": output})

run_simple(hostname="0.0.0.0", port=8080, application=dispatcher)

# if __name__ == "__main__":
#     # app.run()
    
