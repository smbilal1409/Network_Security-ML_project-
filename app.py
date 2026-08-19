import sys
import os

import certifi
ca = certifi.where()
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo
from Networksecurity.exception.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging
from Networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile,Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from Networksecurity.utils.main_utils.utils import load_object

from Networksecurity.utils.ml_utils.model.estimator import NetworkModel


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from Networksecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from Networksecurity.constants.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/predict-page")
async def predict_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
# @app.post("/predict", response_class=HTMLResponse)
# async def predict_route(request: Request,file: UploadFile = File(...)):
#     try:
#         df=pd.read_csv(file.file)
#         #print(df)
#         preprocesor=load_object("final_model/preprocessor.pkl")
#         final_model=load_object("final_model/model.pkl")
#         network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
#         print(df.iloc[0])
#         y_pred = network_model.predict(df)
#         print(y_pred)
#         df['predicted_column'] = y_pred
#         print(df['predicted_column'])
#         #df['predicted_column'].replace(-1, 0)
#         #return df.to_json()
#         df.to_csv('prediction_output/output.csv')
#         table_html = df.to_html(classes='table table-striped')
#         #print(table_html)
#         return templates.TemplateResponse(
#     request=request,
#     name="table.html",
#     context={
#         "request": request,
#         "table": table_html
#     }
# )
@app.post("/predict", response_class=HTMLResponse)
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:

        # Read uploaded CSV
        df = pd.read_csv(file.file)

        # Load trained preprocessing object
        preprocessor = load_object("final_model/preprocessor.pkl")

        # Load trained ML model
        final_model = load_object("final_model/model.pkl")

        # Create network model
        network_model = NetworkModel(
            preprocessor=preprocessor,
            model=final_model
        )

        # Generate predictions
        y_pred = network_model.predict(df)

        # Add prediction column
        df["predicted_column"] = y_pred

        # Convert prediction into human-readable result
        df["prediction_status"] = df["predicted_column"].apply(
            lambda x: "SAFE" if x == 1 else "UNSAFE"
        )

        # Save prediction output
        os.makedirs("prediction_output", exist_ok=True)

        df.to_csv(
            "prediction_output/output.csv",
            index=False
        )

        # Statistics
        total_records = len(df)
        safe_count = int((df["predicted_column"] == 1).sum())
        unsafe_count = int((df["predicted_column"] == 0).sum())

        # Convert dataframe to dictionary for Jinja
        records = df.to_dict(orient="records")

        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={
                "request": request,
                "records": records,
                "total_records": total_records,
                "safe_count": safe_count,
                "unsafe_count": unsafe_count
            }
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys)
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)
