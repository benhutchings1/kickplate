from logging import config
from typing import Any

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from settings import Exporter, settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "Info",
        }
    },
}


def setup_otel(app: FastAPI):
    # config.dictConfig(LOGGING_CONFIG)

    resource = Resource(attributes={"SERVICE_NAME": "kickplate.api"})

    # Processors
    traces_exporter: Any = None
    metrics_exporter: Any = None

    if settings.EXPORTER == Exporter.local:
        traces_exporter = ConsoleSpanExporter()
        metrics_exporter = ConsoleMetricExporter()
    else:
        traces_exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_ENDPOINT + "/v1/traces"
        )
        metrics_exporter = OTLPMetricExporter(
            endpoint=settings.OTEL_ENDPOINT + "/v1/metrics"
        )

    processor = BatchSpanProcessor(traces_exporter)
    reader = PeriodicExportingMetricReader(metrics_exporter)

    # Providers
    traces_provider = TracerProvider(resource=resource)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])

    traces_provider.add_span_processor(processor)
    metrics.set_meter_provider(meter_provider)
    trace.set_tracer_provider(traces_provider)

    FastAPIInstrumentor.instrument_app(app)


def add_attribute(new_attributes: dict[str, str]) -> None:
    current_span = trace.get_current_span()
    if (current_span is not None) and (current_span.is_recording()):
        current_span.set_attributes(new_attributes)