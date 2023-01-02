# app.py updates

def instrument_tracing(app, cfg):
  from opentelemetry import trace
  from opentelemetry.instrumentation.flask import FlaskInstrumentor
  from opentelemetry.instrumentation.requests import RequestsInstrumentor
  from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
  from opentelemetry.sdk.resources import Resource, SERVICE_NAME
  from opentelemetry.sdk.trace import TracerProvider
  from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, ConsoleSpanExporter

  r = Resource(attributes={
    SERVICE_NAME: "tasty-fare",
  })

  # Initialize tracing and an exporter that can send data to Honeycomb
  provider = TracerProvider(resource=r)
  processor = BatchSpanProcessor(OTLPSpanExporter(
      endpoint=cfg.get("endpoint", None),
      headers=cfg.get("headers", None)
  ))
  #processor = SimpleSpanProcessor(ConsoleSpanExporter())

  provider.add_span_processor(processor)
  trace.set_tracer_provider(provider)
  tracer = trace.get_tracer(__name__)

  FlaskInstrumentor().instrument_app(app)
  RequestsInstrumentor().instrument()

# Initialize automatic instrumentation with Flask

from flask import Flask

app = Flask(__name__)
app.config.from_pyfile("config.py")

tr = app.config.get("TRACING", None)
if tr is not None:
  instrument_tracing(app, tr)
