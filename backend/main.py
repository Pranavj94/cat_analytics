from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["http://localhost:3000"],
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
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}



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



class ReportRequest_PowerBI(BaseModel):
    edmValue: str
    allPortfolios: bool
    portfolios: str = None
    allAnalysis: bool
    analysis: str = None

class ReportRequest_Excel(BaseModel):
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
    uvicorn.run(app, host="0.0.0.0", port=8000)