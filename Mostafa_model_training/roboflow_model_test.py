from IPython.display import Image, display
from inference_sdk import InferenceHTTPClient
import base64
from io import BytesIO
from PIL import Image as PILImage
import IPython.display as display


client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="hx4EjAbVwf5pqWFMDWUx"
)

result = client.run_workflow(
    workspace_name="rana-djciu",
    workflow_id="detect-and-classify-2",
    images={
        "image": "/test1.jpeg"
    },
    use_cache=True # cache workflow definition for 15 minutes
)


image_data = base64.b64decode(result[0]['output'])

# Load it into PIL and display
image = PILImage.open(BytesIO(image_data))
display.display(image)

# print(result[0]['output'])

