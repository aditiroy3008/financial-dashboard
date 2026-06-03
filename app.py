from flask import Flask, render_template, request, send_file
import pandas as pd
import plotly.express as px
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# -------------------------
# Folder Setup
# -------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Store report data
latest_report_data = {}

# -------------------------
# Home Page
# -------------------------

@app.route('/')
def home():
    return render_template('index.html')


# -------------------------
# Upload Route
# -------------------------

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    global latest_report_data

    if request.method == 'POST':

        if 'file' not in request.files:
            return "No file selected!"

        file = request.files['file']

        if file.filename == '':
            return "Please select a file!"

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            file.filename
        )

        file.save(filepath)

        # Read CSV

        df = pd.read_csv(filepath)

        # Create Table

        table = df.to_html(
            classes='table table-bordered table-striped',
            index=False
        )

        # -------------------------
        # Revenue Chart
        # -------------------------

        revenue_fig = px.line(
            df,
            x='Year',
            y='Revenue',
            title='Revenue Trend (₹ Crore)'
        )

        revenue_graph = revenue_fig.to_html(
            full_html=False
        )

        revenue_chart_path = os.path.join(
            UPLOAD_FOLDER,
            "revenue_chart.png"
        )

        revenue_fig.write_image(
            revenue_chart_path
        )

        # -------------------------
        # Profit Chart
        # -------------------------

        profit_fig = px.line(
            df,
            x='Year',
            y='Profit',
            title='Profit Trend (₹ Crore)'
        )

        profit_graph = profit_fig.to_html(
            full_html=False
        )

        profit_chart_path = os.path.join(
            UPLOAD_FOLDER,
            "profit_chart.png"
        )

        profit_fig.write_image(
            profit_chart_path
        )

        # -------------------------
        # Financial Data
        # -------------------------

        latest_revenue = df['Revenue'].iloc[-1]
        latest_profit = df['Profit'].iloc[-1]
        latest_assets = df['Assets'].iloc[-1]

        latest_liabilities = df['Liabilities'].iloc[-1]
        latest_equity = df['Equity'].iloc[-1]

        # -------------------------
        # Financial Ratios
        # -------------------------

        profit_margin = round(
            (latest_profit / latest_revenue) * 100,
            2
        )

        debt_equity_ratio = round(
            latest_liabilities / latest_equity,
            2
        )

        roa = round(
            (latest_profit / latest_assets) * 100,
            2
        )

        # -------------------------
        # Health Score
        # -------------------------

        if profit_margin >= 25:
            health_score = 90
        elif profit_margin >= 20:
            health_score = 80
        elif profit_margin >= 15:
            health_score = 70
        else:
            health_score = 60

        # -------------------------
        # AI Insights
        # -------------------------

        insights = []

        if profit_margin >= 30:
            insights.append(
                "Excellent profitability with a strong profit margin."
            )
        elif profit_margin >= 20:
            insights.append(
                "Good profitability and healthy earnings."
            )
        else:
            insights.append(
                "Profitability needs improvement."
            )

        if debt_equity_ratio < 1:
            insights.append(
                "Low debt risk and strong financial stability."
            )
        else:
            insights.append(
                "Debt levels are relatively high."
            )

        if roa >= 15:
            insights.append(
                "Assets are being utilized efficiently."
            )
        else:
            insights.append(
                "Asset utilization can be improved."
            )

        insights.append(
            "Revenue growth is supporting business expansion."
        )

        # -------------------------
        # Store Data
        # -------------------------

        latest_report_data = {
            "tables": table,
            "revenue_graph": revenue_graph,
            "profit_graph": profit_graph,
            "latest_revenue": latest_revenue,
            "latest_profit": latest_profit,
            "latest_assets": latest_assets,
            "health_score": health_score,
            "profit_margin": profit_margin,
            "debt_equity_ratio": debt_equity_ratio,
            "roa": roa,
            "insights": insights,
            "revenue_chart": revenue_chart_path,
            "profit_chart": profit_chart_path
        }

        return render_template(
            'result.html',
            **latest_report_data
        )

    return render_template('upload.html')


# -------------------------
# PDF Download Route
# -------------------------

@app.route('/download_dashboard_pdf')
def download_dashboard_pdf():

    pdf_file = "Financial_Report.pdf"

    doc = SimpleDocTemplate(
        pdf_file
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Financial Dashboard Report",
            styles['Title']
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            f"Revenue : Rs. {latest_report_data['latest_revenue']:,} Cr",
            styles['Normal']
        )
    )

    story.append(
        Paragraph(
            f"Profit : Rs. {latest_report_data['latest_profit']:,} Cr",
            styles['Normal']
        )
    )

    story.append(
        Paragraph(
            f"Assets : Rs. {latest_report_data['latest_assets']:,} Cr",
            styles['Normal']
        )
    )

    story.append(
        Paragraph(
            f"Health Score : {latest_report_data['health_score']}/100",
            styles['Normal']
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Financial Ratios",
            styles['Heading2']
        )
    )

    story.append(
        Paragraph(
            f"Profit Margin : {latest_report_data['profit_margin']}%",
            styles['Normal']
        )
    )

    story.append(
        Paragraph(
            f"Debt Equity Ratio : {latest_report_data['debt_equity_ratio']}",
            styles['Normal']
        )
    )

    story.append(
        Paragraph(
            f"ROA : {latest_report_data['roa']}%",
            styles['Normal']
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "AI Financial Insights",
            styles['Heading2']
        )
    )

    for insight in latest_report_data['insights']:

        story.append(
            Paragraph(
                "• " + insight,
                styles['Normal']
            )
        )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Revenue Trend Chart",
            styles['Heading2']
        )
    )

    story.append(
        Image(
            latest_report_data['revenue_chart'],
            width=450,
            height=250
        )
    )

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Profit Trend Chart",
            styles['Heading2']
        )
    )

    story.append(
        Image(
            latest_report_data['profit_chart'],
            width=450,
            height=250
        )
    )

    doc.build(story)

    return send_file(
        pdf_file,
        as_attachment=True
    )


# -------------------------
# Run App
# -------------------------

if __name__ == '__main__':
    app.run(debug=True)

