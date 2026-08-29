@echo off
echo ==============================================================================
echo   SCCT AGENT: Victoria's Secret & Co. Global Supply Chain Control Tower
echo   Governed Conversational Analytics & Multi-Persona Metric Reconciliation
echo ==============================================================================
echo.
echo [1/3] Generating Referentially Consistent Synthetic Sourcing & Logistics Data...
python data/generate_synthetic_data.py
python data/generate_sample_docs.py
echo.
echo [2/3] Running Automated Governance & Cross-Persona Metric Regression Tests...
python -m pytest tests/
echo.
echo [3/3] Launching SCCT Agent Streamlit Control Tower Application...
streamlit run app.py
pause
