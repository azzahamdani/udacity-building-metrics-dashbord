from flask import Flask

from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_prometheus_metrics import register_metrics

from jaeger_client import Config
from flask_opentracing import FlaskTracing

import logging

app = Flask(__name__)

def init_tracer(service):
    logging.getLogger("").handlers = []
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    config = Config(
        config={"sampler": {"type": "const", "param": 1,}, "logging": True, 'reporter_batch_size': 1,},
        service_name=service,
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()

jaeger_tracer = init_tracer("helloworld")

tracing = FlaskTracing(jaeger_tracer)

# provide app's version and deploy environment/config name to set a gauge metric
register_metrics(app, app_version="v0.1.2", app_config="staging")

# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

@app.route("/")
def hello():
    with jaeger_tracer.start_active_span('hello') as scope:
        return "Hello from Python!"

run_simple(hostname="0.0.0.0", port=5000, application=dispatcher)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0")
