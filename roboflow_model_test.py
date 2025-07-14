from roboflow import Roboflow

rf = Roboflow(api_key="your-api-key")
project = rf.workspace("your-workspace").project("your-project")
model = project.version("x").model  # x = version number

prediction = model.predict("your-image.jpg").json()
print(prediction)
