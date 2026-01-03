import os
import json
from pathlib import Path
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from openinference.instrumentation.langchain import LangChainInstrumentor

class JsonFileSpanExporter(SpanExporter):
    """
    Custom Exporter to write OTel spans to a JSONL file.
    """
    def __init__(self, output_dir="telemetry_logs", filename="traces.jsonl"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / filename
        print(f"🔭 OpenTelemetry: Logging traces to {self.output_file}")

    def export(self, spans):
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                for span in spans:
                    # Convert span to JSON string
                    f.write(span.to_json() + "\n")
            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f"Error exporting spans: {e}")
            return SpanExportResult.FAILURE

    def shutdown(self):
        pass

def setup_telemetry():
    """
    Configures OpenTelemetry instrumentation.
    Logs to telemetry_logs/traces.jsonl by default.
    """
    # Define resource metadata
    resource = Resource(attributes={
        "service.name": "real-estate-agent",
        "service.version": "1.0.0"
    })

    # Set up Tracer Provider
    provider = TracerProvider(resource=resource)
    
    # Configure Exporter
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    
    if otlp_endpoint:
        # Use OTLP Exporter if configured
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        print(f"🔭 OpenTelemetry enabled: Exporting to {otlp_endpoint}")
    else:
        # Use Custom JSON File Exporter
        exporter = JsonFileSpanExporter()

    # Add Processor
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # Set as global provider
    trace.set_tracer_provider(provider)

    # Instrument LangChain
    LangChainInstrumentor().instrument()
    
    return provider
