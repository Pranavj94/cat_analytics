from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
import uvicorn
import logging
from . import main_utils
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    edmValue: str = Field(..., min_length=1, description="EDM value")
    aal: bool = Field(..., description="AAL flag")


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Set a timeout for reading the file
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
            
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
            
        return JSONResponse(
            content=df.to_dict(orient="records"),
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


class DataItem(BaseModel):
    # Add your expected fields here
    pass

@app.post("/columnmapper/")
async def column_mapper(data: List[Dict[Any, Any]]):
    try:
        logging.info(f"Received data: {data}")
        df = pd.DataFrame(data)
        transformed_data, mapping = main_utils.transform_column_names(df)
        return {"transformed_data": transformed_data.to_dict(orient="records"), "mapping": mapping}
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/constructionmapper/")
async def construction_mapper(data: List[Dict[Any, Any]]):
    try:
        logging.info(f"Received data: {data}")
        df = pd.DataFrame(data)
        transformed_data, mapping = main_utils.add_construction_mapping(df)
        return {"transformed_data": transformed_data.to_dict(orient="records"), "mapping": mapping}
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/occupancymapper/")
async def occupancy_mapper(data: List[Dict[Any, Any]]):
    try:
        logging.info(f"Received data: {data}")
        df = pd.DataFrame(data)
        transformed_data, mapping = main_utils.add_occuppancy_mapping(df)
        return {"transformed_data": transformed_data.to_dict(orient="records"), "mapping": mapping}
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/geocoder/")
async def Run_Geocoder(data: List[Dict[Any, Any]]):
    try:
        df = pd.DataFrame(data)
        transformed_data = main_utils.run_geocoder(df)
        return {"data": transformed_data.to_dict(orient="records")}
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/cleaner/")
async def Run_Cleaner(data: List[Dict[Any, Any]]):
    try:
        df = pd.DataFrame(data)
        transformed_data, mapping = main_utils.add_occuppancy_mapping(df)
        return {"transformed_data": transformed_data.to_dict(orient="records")}
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))



class ReportRequest_PowerBI(BaseModel):
    reportName:str
    edmValue: str
    allPortfolios: bool
    portfolios: str = None
    allAnalysis: bool
    analysis: str = None

class ReportRequest_Excel(BaseModel):
    reportName:str
    edmValue: str
    allPortfolios: bool
    portfolios: str = None
    allAnalysis: bool
    analysis: str = None

@app.post('/generatePowerBIReport/')
async def generate_powerbi_report(request: ReportRequest_PowerBI):
    try:
        logger.info(f"Generating PowerBI report with EDM: {request.edmValue}")
        
        # Add your PowerBI report generation logic here
        # Simulate some processing time
        # await asyncio.sleep(2)
        
        logger.info("PowerBI report generated successfully")
        return {
            "status": "success",
            "message": "PowerBI report generated successfully"
        }
    except Exception as e:
        logger.error(f"Error generating PowerBI report: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PowerBI report: " + str(e)
        )

@app.post('/generateExcelReport/')
async def generate_excel_report(request: ReportRequest_Excel):
    try:
        logger.info(f"Generating Excel report with EDM: {request.edmValue}")
        
        # Add your Excel report generation logic here
        # Simulate some processing time
        # await asyncio.sleep(2)
        
        logger.info("Excel report generated successfully")
        return {
            "status": "success",
            "message": "Excel report generated successfully"
        }
    except Exception as e:
        logger.error(f"Error generating Excel report: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Failed to generate Excel report: " + str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Increase timeout settings
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=300,
        limit_concurrency=1
    )