from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import logging

from src.api.models.responses import AnalysisResponse, AnalysisStatusResponse
from src.services.analyzer import ContractAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)

analyzer = ContractAnalyzer()
analysis_results = {}

@router.post("/upload", response_model=AnalysisResponse)
async def upload_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files supported")
    
    analysis_id = str(uuid.uuid4())
    
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{analysis_id}.pdf"
    
    try:
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        analysis_results[analysis_id] = {
            "status": "processing",
            "filename": file.filename,
            "file_path": str(file_path),
            "progress": 0
        }
        
        background_tasks.add_task(run_analysis, analysis_id, file_path)
        
        logger.info(f"✅ Analysis started: {analysis_id}")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            message=f"Analysis started for {file.filename}",
            filename=file.filename
        )
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
def get_status(analysis_id: str):
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    
    return AnalysisStatusResponse(
        analysis_id=analysis_id,
        status=result["status"],
        filename=result.get("filename", ""),
        progress=result.get("progress", 0)
    )

@router.get("/{analysis_id}/results")
def get_results(analysis_id: str):
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    
    if result["status"] == "processing":
        raise HTTPException(status_code=202, detail="Still processing")
    
    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
    
    return JSONResponse(content=result["data"])

def run_analysis(analysis_id: str, file_path: Path):
    """Background task to run analysis"""
    try:
        logger.info(f"🔄 Starting analysis: {analysis_id}")
        
        analysis_results[analysis_id]["progress"] = 10
        
        results = analyzer.analyze_contract(file_path)
        
        analysis_results[analysis_id].update({
            "status": "completed",
            "progress": 100,
            "data": results
        })
        
        logger.info(f"✅ Analysis complete: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {analysis_id} - {e}")
        analysis_results[analysis_id].update({
            "status": "failed",
            "error": str(e)
        })