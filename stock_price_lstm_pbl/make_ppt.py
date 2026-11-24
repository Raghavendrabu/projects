import sys
import subprocess
import os

# Ensure python-pptx is installed
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    DARK_BG = RGBColor(15, 23, 42)        # #0f172a
    CARD_BG = RGBColor(30, 41, 59)        # #1e293b
    TEXT_WHITE = RGBColor(255, 255, 255)  # #ffffff
    PURPLE_ACCENT = RGBColor(168, 85, 247)# #a855f7
    MUTED_TEXT = RGBColor(148, 163, 184)  # #94a3b8
    GREEN_TEXT = RGBColor(16, 185, 129)   # #10b981

    def set_slide_background(slide):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = DARK_BG

    def add_header(slide, title_text, category_text="UE24CS3504: SERVERLESS COMPUTING & CLOUD FUNCTIONS"):
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.8))
        tf = txBox.text_frame
        tf.word_wrap = True
        
        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = PURPLE_ACCENT

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE

    slides_data = [
        {
            "type": "title",
            "title": "Cloud Integration of Existing Applications",
            "subtitle": "Case Study: Cloud Integration & Serverless Architecture Design for StockPredict AI\n(Stacked LSTM Deep Learning & Financial Analytics Engine)",
            "meta": "Course: UE24CS3504 - Serverless Computing & Cloud Functions\nFaculty: Niveditha T Naik | Issue Date: 19-09-2026 | Submission Date: 30-09-2026\nPresenter: Pammu R. (SRN: PES1UG24CS999) - 5th Sem CSE"
        },
        {
            "type": "bullets",
            "header": "1. Selected Case Study Overview — StockPredict AI",
            "bullets": [
                "Application Name: StockPredict AI (LSTM Financial Analytics Platform).",
                "Core Functionality: Multi-feature time-series stock price forecasting using 2-Layer Stacked LSTM.",
                "Target Audience: Retail day traders, quantitative financial analysts, and academic researchers.",
                "Key Capabilities: 5-year historical OHLCV data ingestion (yfinance), 60-day sliding sequence windowing, anti-lookahead MinMaxScaler isolation, and interactive Plotly timeframe dashboards."
            ]
        },
        {
            "type": "bullets",
            "header": "2. Existing System Architecture (Non-Cloud Operation)",
            "bullets": [
                "Standalone Local Deployment: Monolithic Python application running locally on a Windows workstation.",
                "Hardware Constraints: Intel Core i7/i9 CPU, 16GB RAM, NVIDIA RTX GPU, and local SSD storage.",
                "Process Execution: Single Streamlit process executing both web UI rendering and TensorFlow model training.",
                "Data Management: Local flat CSV files, local .keras model weights, and open router port forwarding (Port 8501)."
            ]
        },
        {
            "type": "bullets",
            "header": "3. Problems & Limitations of Existing System",
            "bullets": [
                "Compute Contention & UI Lockup: Heavy LSTM training (35-50 epochs) saturates CPU/GPU, freezing web UI threads.",
                "Limited Scalability & Single Point of Failure (SPOF): Cannot handle concurrent requests; power/network outages kill app.",
                "High CapEx & OpEx: Fixed 24/7 electricity and hardware costs during off-market idle hours.",
                "Security & Access Risks: Unencrypted port forwarding exposes workstation to port scanning and DDoS attacks."
            ]
        },
        {
            "type": "table_req",
            "header": "4. Cloud Requirement Analysis & Mapping Matrix"
        },
        {
            "type": "bullets",
            "header": "5. Evaluation & Comparison of Cloud Alternatives",
            "bullets": [
                "Compute Evaluation (EC2 vs AWS Fargate): Fargate selected for serverless per-second pricing, zero OS management, and rapid task scaling.",
                "Storage Evaluation (EBS vs Amazon S3): Amazon S3 selected for 11-nines multi-AZ durability, infinite scalability, and REST API access.",
                "Cost & Elasticity Impact: Serverless architecture scales to zero when markets are closed, saving up to 75% on operating costs."
            ]
        },
        {
            "type": "bullets",
            "header": "6. Selected Cloud Services Stack & Justification",
            "bullets": [
                "AWS Fargate: Serverless containers hosting Streamlit UI tasks with multi-AZ load balancing.",
                "AWS Lambda: Serverless execution environment for TensorFlow LSTM sequence preprocessing & model inference.",
                "Amazon S3 & DynamoDB: Durable object storage for model weights alongside low-latency metrics/watchlist NoSQL storage.",
                "CloudFront & WAF: Global CDN edge distribution with enterprise Web Application Firewall protection."
            ]
        },
        {
            "type": "arch",
            "header": "7. Proposed Cloud Solution Architecture"
        },
        {
            "type": "bullets",
            "header": "8. End-to-End User Request & Inference Data Flow",
            "bullets": [
                "1. User Request: User selects stock symbol AAPL and requests next-day forecast on web UI.",
                "2. Routing & Load Balancing: CloudFront CDN delivers static assets; ALB routes request to active Fargate container.",
                "3. Serverless Inference Call: Streamlit frontend invokes AWS Lambda via API Gateway REST endpoint.",
                "4. Forecast Calculation & Output: Lambda loads S3 model weights, normalizes 60-day window, writes metrics to DynamoDB, and returns Plotly JSON forecast."
            ]
        },
        {
            "type": "bullets",
            "header": "9. Scalability, Availability & Security Design Patterns",
            "bullets": [
                "Scalability Design: Auto-scaling Fargate task containers (70% CPU threshold) & concurrent AWS Lambda invocations.",
                "High Availability (99.95% Uptime): Multi-AZ container deployment across distinct physical data centers.",
                "Enterprise Security: Private VPC subnets (no public IPv4), TLS 1.3 encryption in transit, and KMS AES-256 at rest."
            ]
        },
        {
            "type": "bullets",
            "header": "10. Cloud Migration Plan & Expected Benefits",
            "bullets": [
                "6-Phase Migration: Containerization -> Cloud Storage -> Lambda Functions -> Multi-AZ ALB -> CI/CD -> Route 53 Cutover.",
                "75% Operational Cost Reduction: Pay-per-second serverless execution eliminates 24/7 idle server billing.",
                "Sub-Second Global Latency: CloudFront CDN caching delivers visual analytics rapidly to global users."
            ]
        },
        {
            "type": "bullets",
            "header": "11. Challenges, Mitigations & Conclusion",
            "bullets": [
                "Cold Start Mitigation: Pre-warm AWS Lambda functions using Provisioned Concurrency or lightweight ONNX runtime.",
                "API Throttling Mitigation: Implement Amazon ElastiCache (Redis) to cache historical quote responses.",
                "Final Conclusion: Re-architecting StockPredict AI onto AWS serverless solves all physical hardware constraints and delivers a resilient, production-grade cloud platform."
            ]
        }
    ]

    for s_idx, data in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)
        set_slide_background(slide)

        if data["type"] == "title":
            txBox = slide.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(4.5))
            tf = txBox.text_frame
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = "PES UNIVERSITY — DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING"
            p0.font.size = Pt(12)
            p0.font.bold = True
            p0.font.color.rgb = PURPLE_ACCENT

            p1 = tf.add_paragraph()
            p1.text = data["title"]
            p1.font.size = Pt(32)
            p1.font.bold = True
            p1.font.color.rgb = TEXT_WHITE

            p2 = tf.add_paragraph()
            p2.text = data["subtitle"]
            p2.font.size = Pt(16)
            p2.font.color.rgb = MUTED_TEXT

            p3 = tf.add_paragraph()
            p3.text = "\n" + data["meta"]
            p3.font.size = Pt(12)
            p3.font.color.rgb = GREEN_TEXT

        elif data["type"] == "bullets":
            add_header(slide, data["header"])
            
            # Content Box
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
            shape.fill.solid()
            shape.fill.fore_color.rgb = CARD_BG
            shape.line.color.rgb = PURPLE_ACCENT

            tf = shape.text_frame
            tf.word_wrap = True
            
            for b_idx, bullet in enumerate(data["bullets"]):
                p = tf.paragraphs[0] if b_idx == 0 else tf.add_paragraph()
                p.text = "•  " + bullet
                p.font.size = Pt(15)
                p.font.color.rgb = TEXT_WHITE
                p.space_after = Pt(18)

        elif data["type"] == "table_req":
            add_header(slide, data["header"])
            rows, cols = 5, 4
            left, top, width, height = Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.2)
            table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
            table = table_shape.table

            headers = ["Requirement Area", "Existing Problem", "Cloud Requirement", "Target Cloud Mechanism"]
            for c_idx, h in enumerate(headers):
                cell = table.cell(0, c_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = PURPLE_ACCENT
                cell.text = h

            t_data = [
                ["Compute", "CPU/GPU saturation during LSTM model training", "Elastic, on-demand compute scaling", "AWS Lambda & AWS Fargate"],
                ["Storage", "Limited local SSD space & risk of disk failure", "Unlimited, durable 11-nines object store", "Amazon S3"],
                ["Availability", "Server crash causes total system downtime", "99.95% uptime with Multi-AZ redundancy", "ALB + Multi-AZ Containers"],
                ["Security", "Unencrypted open router port forwarding", "Enterprise TLS 1.3 & IAM role security", "AWS API Gateway + WAF + IAM"]
            ]

            for r_idx, row in enumerate(t_data):
                for c_idx, val in enumerate(row):
                    cell = table.cell(r_idx + 1, c_idx)
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = CARD_BG
                    cell.text = val

        elif data["type"] == "arch":
            add_header(slide, data["header"])
            
            txBox = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
            tf = txBox.text_frame
            tf.word_wrap = True
            
            arch_ascii = """[ User Web Browser ] ──(HTTPS/TLS 1.3)──> [ Amazon CloudFront CDN ] ──> [ AWS WAF ]
                                                                                   │
                                                                                   ▼
[ Amazon S3 Bucket ] <─── [ AWS Lambda Function ] <─── [ AWS API Gateway ] <─── [ Application Load Balancer ]
 (Model Weights & CSVs)     (Python + TensorFlow)       (REST Inferences)        (Multi-AZ Routing)
         │                                                                                 │
         ▼                                                                                 ▼
[ Amazon DynamoDB ]                                                            [ AWS Fargate Task Containers ]
(Metrics & Watchlists)                                                          (Streamlit Dashboard UI)"""
            
            p = tf.paragraphs[0]
            p.text = arch_ascii
            p.font.size = Pt(13)
            p.font.name = "Courier New"
            p.font.color.rgb = GREEN_TEXT

    output_path = os.path.join(os.getcwd(), "StockPredict_AI_Cloud_Integration_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_deck()
