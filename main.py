from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, HTMLResponse
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer

tracer = Tracer(
    exporter=AzureExporter(
        connection_string="InstrumentationKey=9fecf82f-83e4-4a24-8976-de12ae6f0463;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
    ),
    sampler=ProbabilitySampler(1.0),
)


# Logging Configuration
logger = logging.getLogger()
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=9fecf82f-83e4-4a24-8976-de12ae6f0463;IngestionEndpoint=https://eastus-8.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"))
logger.setLevel(logging.INFO)

app = FastAPI(title="Exception Catching API", description="API to test and catch exceptions")

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



@app.post("/items/")
async def create_item(item: Item):
    """
    Create an item.
    """
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
    """
    Read an item by name.
    """
    try:
        if item_name not in items:
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Item read: {item_name}")
        return items[item_name]
    except Exception as e:
        logger.error(f"Error reading item: {str(e)}")
        raise

@app.get("/divide-by-zero")
async def divide_by_zero():
    """
    Generate a ZeroDivisionError.
    """
    properties = {'custom_dimensions': {'key_1': 'value_1', 'key_2': 'value_2'}}
    try:
        result = 1 / 0  # Generate a ZeroDivisionError
    except Exception:
        logger.exception('Captured an exception.', extra=properties)
        raise HTTPException(status_code=400, detail="Division by zero error")

@app.get("/key-error")
async def key_error():
    """
    Generate a KeyError.
    """
    properties = {'custom_dimensions': {'key_1': 'value_1', 'key_2': 'value_2'}}
    try:
        my_dict = {'key': 'value'}
        value = my_dict['non_existent_key']  # Generate a KeyError
    except Exception:
        logger.exception('Captured an exception.', extra=properties)
        raise HTTPException(status_code=400, detail="Key error")


# Endpoint for the navigation page
@app.get("/", response_class=HTMLResponse)
async def navigation_page(request: Request):
    """
    Render the navigation page.
    """
    return templates.TemplateResponse("navigation.html", {"request": request})

# Root endpoint to render the HTML template
@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    """
    Render the home page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Generate OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Route for serving OpenAPI JSON schema
@app.get("/openapi.json")
def get_openapi_endpoint():
    return JSONResponse(content=custom_openapi())

# Route for serving Swagger UI HTML page
@app.get("/docs", response_class=HTMLResponse)
def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title,
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
