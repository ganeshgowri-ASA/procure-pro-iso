# Procure-Pro-ISO Streamlit App

A comprehensive Streamlit-based procurement analysis application with ISO compliance features.

## Features

- **📊 Dashboard** - Real-time KPIs, budget trends, RFQ status charts
- **📦 Equipment Master** - Manage equipment with Excel import/export
- **📝 RFQ Management** - Create RFQs, track vendor responses
- **👥 Vendor Management** - Supplier directory with star ratings
- **🔬 Technical Evaluation** - CTQ matrix, vendor scoring (90.2, 88.7, 88.1)
- **💰 Commercial Evaluation** - TCO calculator, price comparison

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### Deploy to Streamlit Cloud

1. Push this folder to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `streamlit_app/app.py` as the main file
5. Click Deploy

## Project Structure

```
streamlit_app/
├── app.py                    # Main entry point
├── requirements.txt          # Dependencies
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── data/
│   └── sample_data.py        # Sample data for demo
└── pages/
    ├── 1_📊_Dashboard.py
    ├── 2_📦_Equipment_Master.py
    ├── 3_📝_RFQ_Management.py
    ├── 4_👥_Vendor_Management.py
    ├── 5_🔬_Technical_Evaluation.py
    └── 6_💰_Commercial_Evaluation.py
```

## Sample Data

The app includes realistic sample data:

| Metric | Value |
|--------|-------|
| Equipment | 12 items |
| Budget | $1.8M |
| Active RFQs | 3 |
| Vendors | 7 |

## Dependencies

- streamlit >= 1.29.0
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- plotly >= 5.18.0
- xlsxwriter >= 3.1.0

## License

MIT License
