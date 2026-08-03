"""
API Endpoint for WebSentinel - Production Ready REST API
Allows programmatic access to testing capabilities
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
import json
import sys
import os

# Add project root to sys.path so local packages (browser_use, utils, core) resolve
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
os.chdir(str(_PROJECT_ROOT))

from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from utils.model_provider import get_llm
from core.comprehensive_tester import ComprehensiveTester
from core.enhanced_pdf_generator import EnhancedPDFReportGenerator
from core.ai_analyzer import AIAnalyzer
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="WebSentinel API",
    description="REST API for comprehensive website testing",
    version="1.0.0"
)

# Store test jobs
test_jobs = {}


class TestRequest(BaseModel):
    """Test request model"""
    url: HttpUrl
    task_description: Optional[str] = ""
    run_comprehensive_tests: bool = True
    headless: bool = True


class TestResponse(BaseModel):
    """Test response model"""
    job_id: str
    status: str
    message: str


class TestResult(BaseModel):
    """Test result model"""
    job_id: str
    status: str
    url: str
    test_results: Optional[Dict] = None
    pdf_path: Optional[str] = None
    json_path: Optional[str] = None
    error: Optional[str] = None


async def run_test_job(job_id: str, url: str, task: str, run_tests: bool, headless: bool):
    """Background job to run tests"""
    try:
        test_jobs[job_id]['status'] = 'running'
        
        # Setup browser
        browser_config = BrowserConfig(
            headless=headless,
            chrome_remote_debugging_port=9222,
            extra_browser_args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        browser = Browser(config=browser_config)
        context_config = BrowserContextConfig()
        context = await browser.new_context(config=context_config)
        
        # Navigate
        page = await context.get_current_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        except Exception as nav_error:
            error_str = str(nav_error).lower()
            await context.close()
            await browser.close()
            if 'net::err_name_not_resolved' in error_str or 'dns' in error_str:
                raise RuntimeError(f"DNS resolution failed for {url}. Check the URL spelling and your internet connection.")
            elif 'timeout' in error_str:
                raise RuntimeError(f"Connection timed out for {url}. The site may be down or very slow.")
            elif 'net::err_connection_refused' in error_str:
                raise RuntimeError(f"Connection refused by {url}. The server may be down.")
            else:
                raise RuntimeError(f"Failed to navigate to {url}: {nav_error}")
        
        # Run tests if requested
        results = None
        pdf_path = None
        json_path = None
        
        if run_tests:
            tester = ComprehensiveTester(url, context)
            results = await tester.run_all_tests()
            
            # Save results
            json_path = tester.save_results('test_results')
            
            # AI Analysis
            ai_analyzer = AIAnalyzer()
            ai_insights = await ai_analyzer.analyze_results(results)
            
            # Generate Enhanced PDF
            screenshots_dir = Path("agent_screenshots")
            pdf_generator = EnhancedPDFReportGenerator(
                results=results,
                screenshots_dir=screenshots_dir,
                ai_insights=ai_insights
            )
            pdf_path = pdf_generator.generate('reports')
        
        # Cleanup
        await context.close()
        await browser.close()
        
        # Update job
        test_jobs[job_id].update({
            'status': 'completed',
            'test_results': results,
            'pdf_path': pdf_path,
            'json_path': json_path
        })
        
    except Exception as e:
        test_jobs[job_id].update({
            'status': 'failed',
            'error': str(e)
        })


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "WebSentinel API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/test": "Submit a new test job",
            "GET /api/test/{job_id}": "Get test job status and results",
            "GET /api/test/{job_id}/pdf": "Download PDF report",
            "GET /api/test/{job_id}/json": "Download JSON results",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/test", response_model=TestResponse)
async def create_test(request: TestRequest, background_tasks: BackgroundTasks):
    """Create a new test job"""
    job_id = str(uuid.uuid4())
    
    test_jobs[job_id] = {
        'status': 'pending',
        'url': str(request.url),
        'task': request.task_description,
        'created_at': datetime.now().isoformat()
    }
    
    # Start background task
    background_tasks.add_task(
        run_test_job,
        job_id,
        str(request.url),
        request.task_description,
        request.run_comprehensive_tests,
        request.headless
    )
    
    return TestResponse(
        job_id=job_id,
        status="pending",
        message="Test job created successfully"
    )


@app.get("/api/test/{job_id}", response_model=TestResult)
async def get_test_result(job_id: str):
    """Get test result by job ID"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_jobs[job_id]
    
    return TestResult(
        job_id=job_id,
        status=job['status'],
        url=job['url'],
        test_results=job.get('test_results'),
        pdf_path=job.get('pdf_path'),
        json_path=job.get('json_path'),
        error=job.get('error')
    )


@app.get("/api/test/{job_id}/pdf")
async def download_pdf(job_id: str):
    """Download PDF report"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Test not completed yet")
    
    pdf_path = job.get('pdf_path')
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF report not found")
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=Path(pdf_path).name
    )


@app.get("/api/test/{job_id}/json")
async def download_json(job_id: str):
    """Download JSON results"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = test_jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Test not completed yet")
    
    json_path = job.get('json_path')
    if not json_path or not Path(json_path).exists():
        raise HTTPException(status_code=404, detail="JSON results not found")
    
    return FileResponse(
        json_path,
        media_type='application/json',
        filename=Path(json_path).name
    )


@app.delete("/api/test/{job_id}")
async def delete_test(job_id: str):
    """Delete a test job"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del test_jobs[job_id]
    return {"message": "Job deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting WebSentinel API Server...")
    print("📡 API will be available at http://localhost:8000")
    print("📚 API documentation at http://localhost:8000/docs")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
