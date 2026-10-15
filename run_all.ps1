Write-Host "Starting StockSense AI pipeline..."
python scripts/run_pipeline.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pipeline failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "Pipeline completed." -ForegroundColor Green
Write-Host "To open the web dashboard, run: streamlit run dashboard/app.py"
