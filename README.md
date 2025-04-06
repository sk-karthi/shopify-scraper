
# 🛍️ Shopify Store Scraper & Visualizer

A powerful and customizable Python + Streamlit app that detects if a domain is a Shopify store, scrapes product data (including variants), and visualizes the data for analysis. Perfect for e-commerce research, competitor monitoring, and data-driven decisions.

![Streamlit Demo](https://github.com/sk-karthi/shopify-scraper/assets/your-username/demo-screenshot.png)

---

## 🚀 Live Demo

- 🔗 **[Streamlit App](https://your-deployment-link.streamlit.app)**
- 📊 **[Power BI Dashboard](https://app.powerbi.com/groups/me/dashboards/your-dashboard-id)**

---

## 📦 Features

- ✅ Detect if a website uses Shopify
- ✅ Scrape product and variant data from Shopify stores
- ✅ Generate clean product tables (title, vendor, price, rating, etc.)
- ✅ Visualize data with:
  - Bar chart of top vendors
  - Average ratings by vendor
  - Price distribution histogram
- ✅ Export data as CSV
- ✅ Optional Power BI dashboard integration

---

## 🖼️ Screenshots

### 🏠 Home Page
![Homepage](https://github.com/sk-karthi/shopify-scraper/assets/your-username/home.png)

### 📊 Product Insights
![Charts](https://github.com/sk-karthi/shopify-scraper/assets/your-username/charts.png)

---

## 🔧 Tech Stack

- **Python 3.9+**
- **Streamlit** – UI and interactions
- **Pandas** – Data processing
- **Requests** – HTTP scraping
- **Altair / Plotly** – Visualizations
- **Power BI (optional)** – External dashboard

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/sk-karthi/shopify-scraper.git
cd shopify-scraper
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run locally

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
shopify-scraper/
│
├── app.py               # Main Streamlit app
├── scraper.py           # Shopify scraping functions
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🙌 Contribute

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## ✨ Acknowledgements

Thanks to the open-source community and tools that made this possible!
