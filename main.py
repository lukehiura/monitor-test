from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from azure.monitor import AzureLogAnalyticsHandler
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

workspace_id = "YOUR_WORKSPACE_ID"
shared_key = "YOUR_SHARED_KEY"
instrumentation_key = "YOUR_INSTRUMENTATION_KEY"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = AzureLogAnalyticsHandler(workspace_id, shared_key)
logger.addHandler(handler)

app = FastAPI()

# Use Jinja2Templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Define a simple model for demonstration
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int

# Store items in a dictionary for this example
items = {}

# Initialize the Azure Application Insights exporter
exporter = AzureMonitorTraceExporter(
    instrumentation_key=instrumentation_key,
    connection_string=f"InstrumentationKey={instrumentation_key}"
)

# Configure the tracer provider
tracer_provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "YOUR_SERVICE_NAME"})
)
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(tracer_provider)

@app.post("/items/")
async def create_item(item: Item):
    try:
        if item.name in items:
            raise HTTPException(status_code=400, detail="Item already exists")
        items[item.name] = item
        logger.info(f"Item created: {item.name}")
        return item
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        raise

@app.get("/items/{item_name}")
async def read_item(item_name: str):
    try:
        if item_name not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Item read: {item_name}")
        return items[item_name]
    except Exception as e:
        logger.error(f"Error reading item: {str(e)}")
        raise


# Endpoint for the navigation page
@app.get("/", response_class=HTMLResponse)
async def navigation_page(request: Request):
    return templates.TemplateResponse("navigation.html", {"request": request})

# Root endpoint to render the HTML template
@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
