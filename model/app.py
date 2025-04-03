from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
from torch import device, cuda
import joblib
from ml.util import get_class_of_sample

app = FastAPI(
    title="Simpsons Classification API",
    description="Upload an image to classify a Simpsons character",
    version="1.0.0"
)

DEVICE = device("cuda" if cuda.is_available() else "cpu")

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))


    if image.mode != "RGB":
        image = image.convert("RGB")

    pred = get_class_of_sample(image, DEVICE)[0]

    return JSONResponse({"filename": file.filename, "predicted_class": pred})
