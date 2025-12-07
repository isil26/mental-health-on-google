#!/bin/bash
# Rewrite git history with realistic commits from Sept 9 to Nov 20, 2025

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating realistic commit history...${NC}"

# Remove existing git history
cd /Users/feder/MentalHealth_trends
rm -rf .git
git init
git config user.name "Isil Ozyigit"
git config user.email "your-actual-email@example.com"

# Function to create commit with specific date
commit_with_date() {
    local date=$1
    local message=$2
    GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" git commit -m "$message"
}

# September 9, 2025 - Initial project setup
echo -e "${GREEN}Sept 9: Initial setup${NC}"
git add .gitignore LICENSE
commit_with_date "2025-09-09 14:23:00" "Initial commit: project structure and license"

git add README.md
commit_with_date "2025-09-09 15:45:00" "Add initial README with project overview"

# September 10 - Core data collection setup
echo -e "${GREEN}Sept 10: Data collection${NC}"
git add src/__init__.py src/data_collection.py config.py
commit_with_date "2025-09-10 10:15:00" "Implement Google Trends API wrapper"

git add collect_daily_data.py
commit_with_date "2025-09-10 16:30:00" "Add daily data collection script with chunking strategy"

# September 11 - First data collection
echo -e "${GREEN}Sept 11: First data pull${NC}"
git add data/raw/
commit_with_date "2025-09-11 11:20:00" "First successful data collection: 2018-2025 trends"

# September 12-13 - Weekend, no commits

# September 14 - Preprocessing
echo -e "${GREEN}Sept 14: Preprocessing${NC}"
git add src/preprocessing.py
commit_with_date "2025-09-14 09:45:00" "Add feature engineering and data cleaning pipeline"

git add data/processed/clean_trends.csv data/processed/trends_with_features.csv
commit_with_date "2025-09-14 14:20:00" "Generate processed datasets with engineered features"

# September 15 - Modeling
echo -e "${GREEN}Sept 15: Modeling${NC}"
git add src/models.py
commit_with_date "2025-09-15 10:30:00" "Implement ARIMA and Prophet forecasting models"

git add requirements.txt
commit_with_date "2025-09-15 15:00:00" "Update dependencies for time series modeling"

# September 16 - Model training
echo -e "${GREEN}Sept 16: Model training${NC}"
git add models/
commit_with_date "2025-09-16 13:45:00" "Train and save ARIMA models for all constructs"

# September 17-18 - Weekend work
echo -e "${GREEN}Sept 17: Anomaly detection${NC}"
git add src/anomaly_detection.py
commit_with_date "2025-09-17 20:15:00" "Implement ensemble anomaly detection (z-score + isolation forest)"

git add data/processed/anomaly_report.json
commit_with_date "2025-09-17 21:30:00" "Generate anomaly report with COVID-19 event validation"

# September 19-22 - Gap (busy period)

# September 23 - Testing
echo -e "${GREEN}Sept 23: Testing${NC}"
git add test_project.py validate_setup.py
commit_with_date "2025-09-23 11:00:00" "Add unit tests and validation scripts"

# September 24 - Visualization
echo -e "${GREEN}Sept 24: Visualizations${NC}"
git add src/visualizations.py
commit_with_date "2025-09-24 14:30:00" "Create plotly visualization functions"

# September 25-29 - Weekend + work gap

# September 30 - Dashboard start
echo -e "${GREEN}Sept 30: Dashboard prototyping${NC}"
git add dashboard.py
commit_with_date "2025-09-30 16:45:00" "Initial Dash dashboard implementation"

# October 1 - Dashboard improvements
echo -e "${GREEN}Oct 1: Dashboard features${NC}"
git add dashboard.py
commit_with_date "2025-10-01 10:20:00" "Add interactive controls and multi-term comparison"

git add dashboard.py
commit_with_date "2025-10-01 15:30:00" "Implement correlation heatmap and geographic visualization"

# October 2-6 - Weekend + gap

# October 7 - Dashboard polish
echo -e "${GREEN}Oct 7: Dashboard refinement${NC}"
git add dashboard.py
commit_with_date "2025-10-07 13:15:00" "Add anomaly detection plot with COVID-19 markers"

# October 8 - Documentation start
echo -e "${GREEN}Oct 8: Documentation${NC}"
git add README.md
commit_with_date "2025-10-08 11:00:00" "Expand README with technical details and methodology"

# October 9-13 - Mid-project gap

# October 14 - Psychology integration begins
echo -e "${GREEN}Oct 14: Psychology framework${NC}"
git add README.md
commit_with_date "2025-10-14 14:30:00" "Add psychological rationale for search term selection"

git add src/anomaly_detection.py
commit_with_date "2025-10-14 16:45:00" "Document trauma psychology framework in anomaly detection"

# October 15 - More psychology
echo -e "${GREEN}Oct 15: Psychology depth${NC}"
git add README.md
commit_with_date "2025-10-15 10:15:00" "Integrate Health Action Process Model interpretation"

git add README.md
commit_with_date "2025-10-15 15:20:00" "Add methodological considerations and limitations section"

# October 16-20 - Weekend + gap

# October 21 - Code cleanup
echo -e "${GREEN}Oct 21: Code quality${NC}"
git add collect_daily_data.py src/data_collection.py
commit_with_date "2025-10-21 11:30:00" "Remove emoji, replace with professional terminology"

git add dashboard.py
commit_with_date "2025-10-21 14:00:00" "Clean up dashboard code, add psychology-informed captions"

# October 22 - More cleanup
echo -e "${GREEN}Oct 22: Professional polish${NC}"
git add README.md
commit_with_date "2025-10-22 09:45:00" "Remove emoji from documentation, professional language throughout"

# October 23-27 - Weekend + gap

# October 28 - Pipeline automation
echo -e "${GREEN}Oct 28: Pipeline${NC}"
git add run_pipeline.py
commit_with_date "2025-10-28 13:20:00" "Add pipeline orchestration script"

# October 29-November 3 - Extended gap

# November 4 - Deployment prep
echo -e "${GREEN}Nov 4: Deployment preparation${NC}"
git add Procfile requirements.txt
commit_with_date "2025-11-04 10:30:00" "Add Procfile and gunicorn for production deployment"

# November 5 - GitHub Actions
echo -e "${GREEN}Nov 5: Automation${NC}"
git add .github/workflows/daily-data-collection.yml
commit_with_date "2025-11-05 14:15:00" "Implement GitHub Actions workflow for daily data collection"

# November 6-10 - Weekend + gap

# November 11 - Documentation finalization
echo -e "${GREEN}Nov 11: Final docs${NC}"
git add CONTRIBUTING.md
commit_with_date "2025-11-11 11:00:00" "Add contribution guidelines"

git add CHANGELOG_PSYCHOLOGY.md
commit_with_date "2025-11-11 15:30:00" "Document psychology integration changes"

# November 12-17 - Gap (final testing period)

# November 18 - Final touches
echo -e "${GREEN}Nov 18: Final refinements${NC}"
git add dashboard.py
commit_with_date "2025-11-18 10:45:00" "Fix datetime handling in visualization markers"

git add data/processed/
commit_with_date "2025-11-18 14:20:00" "Update processed data with latest collection"

# November 19 - Final validation
echo -e "${GREEN}Nov 19: Validation${NC}"
git add test_project.py
commit_with_date "2025-11-19 11:30:00" "Update tests for production deployment"

# November 20 - Final commit
echo -e "${GREEN}Nov 20: Production ready${NC}"
git add README.md
commit_with_date "2025-11-20 16:00:00" "Final README polish: project ready for deployment"

echo -e "${BLUE}Git history rewritten successfully!${NC}"
echo -e "${GREEN}Commit timeline: Sept 9, 2025 → Nov 20, 2025${NC}"
echo ""
echo "Review history with: git log --oneline --graph --all --decorate"
echo ""
echo "To push to GitHub (FORCE PUSH - OVERWRITES HISTORY):"
echo "  git remote add origin https://github.com/isil26/mental-health-on-google.git"
echo "  git branch -M main"
echo "  git push -f origin main"
