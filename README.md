# Loan Defaulters Analytical Dashboard 🏦

The project transforms a traditional Exploratory Data Analysis (EDA) on loan defaulter datasets into a premium, interactive Streamlit dashboard. By analyzing various demographic, financial, and behavioral attributes, this tool helps understand the characteristics of loan defaulters versus non-defaulters.

## Summary
This project involves an in-depth EDA on a dataset containing information about loan applicants and their previous applications. The primary goal is to identify key factors that influence loan defaults, assisting financial institutions in making informed lending decisions via a highly interactive visual interface.

## 🚀 The Dashboard Experience
The traditional Jupyter Notebook analysis has been overhauled into a powerful web application featuring:
- **Strict Dark Mode:** For a premium analytical aesthetic.
- **Tabbed Architecture:** Navigate easily between Business Overviews, Demographic Insights, Financials, and Multivariate Correlations.
- **Actionable Insights:** A dedicated engine highlighting top risk categories and a dynamic filterable explorer to cross-reference actual defaulter profiles.
- **Optimized Plotly Visuals:** Sub-sampling strategies ensure the browser does not hang when calculating complex distributions across 300,000+ rows of data.

## Project Structure
- `app.py`: The main Streamlit dashboard application UI.
- `data_processor.py`: Backend data ingestion, missing-value imputation, aggregation, and caching logic.
- `requirements.txt`: Lightweight dependency map for easy deployment.
- `EDA Loan Defaulters.ipynb`: The original static exploratory notebook pipeline.

## Benefits to Others
1. **Better Decision-Making:** Financial institutions can use the insights to refine their loan approval processes, reducing the risk of defaults.
2. **Risk Mitigation:** By quickly identifying high-risk applicants, lenders can take preventive measures or offer customized loan products.
3. **Educational Resource:** The project serves as a valuable resource for data science enthusiasts looking to bridge the gap between static EDA and production-ready interactive dashboard applications.

## How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>
   cd EDA_Loan_Defaulters_Analysis
   ```

2. **Provide the Datasets:**
   Download the Kaggle `loan-defaulter` dataset and place the following files directly in the root directory:
   - `application_data.csv`
   - `previous_application.csv`

3. **Install Dependencies:**
   Ensure you are using Python 3.8+ and run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Dashboard:**
   ```bash
   streamlit run app.py
   ```
   The application will automatically open in your default browser at `http://localhost:8501`.

## Contributing
Feel free to fork this project, make improvements, and submit pull requests. Contributions are always welcome!

## License
This project is licensed under the MIT License.
