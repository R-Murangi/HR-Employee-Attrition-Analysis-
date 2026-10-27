# HR Employee Attrition Analysis

## About the project
For my data analysis project, I looked at employee attrition using an HR dataset. I wanted to find out how many employees left and compare attrition across departments, job roles, age groups, overtime, income and job satisfaction.

## Tools I used
- Python (Pandas and Matplotlib) for analysing the data and making charts
- VS Code to run the Python code
- Power BI Desktop for creating an interactive report

## How to run it
1. Extract the ZIP folder.
2. Double-click `run_analysis.bat` to run the Python analysis. You can also open the folder in VS Code and run `python python/main.py` after installing `requirements.txt`.
3. Check the `images` folder for charts and `results` for the CSV summaries.
4. Open Power BI Desktop and import `results/hr_powerbi_ready.csv`.
5. Rename the imported table to `HR`.
6. Add the DAX measures in `powerbi/measures.dax` one at a time.
7. Follow `powerbi/DASHBOARD_BUILD_GUIDE.txt` to make the visuals.
8. Save your report as `powerbi/HR_Analytics_Dashboard.pbix`.

## Main results
The dataset has 1,470 employees. Out of these, 237 left and 1,233 stayed. The overall attrition rate was about 16.1%.

## What I learned
This project helped me practise cleaning and analysing data with Python, comparing groups using charts, and using DAX measures in Power BI.

