import streamlit as st
import requests
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
import json
from bs4 import BeautifulSoup
import io
import matplotlib.pyplot as plt

# --- Page setup ---
st.set_page_config(page_title="Shopify Store Scraper", layout="wide")

# --- Sidebar ---
st.sidebar.header("🛠️ Scraper Settings")
st.sidebar.markdown("Enter the Shopify store domain and start scraping.")

domain_input = st.sidebar.text_input("Store Domain", placeholder="e.g. allbirds.com")
agree = st.sidebar.checkbox("I agree to use this tool responsibly", value=False)

with st.sidebar.expander("⚙️ Advanced Options"):
    include_ratings = st.checkbox("Include ratings", value=True)
    include_description = st.checkbox("Include product descriptions", value=True)

run_button = st.sidebar.button("🚀 Run Scraper", disabled=not agree)

# --- Title ---
st.markdown("""
    <h1 style='text-align: center;'>🛒 Shopify Scraper</h1>
    <p style='text-align: center;'>Scrape public product data from any Shopify store</p>
""", unsafe_allow_html=True)
st.markdown("---")

# --- Helper functions ---
def normalize_domain(domain):
    parsed = urlparse(domain if domain.startswith("http") else f"https://{domain}")
    return f"https://{parsed.netloc}"

def is_shopify_store(base_url):
    try:
        test = requests.get(f"{base_url}/products.json", timeout=10)
        return test.status_code == 200 and "products" in test.json()
    except Exception as e:
        st.error(f"❌ Store check failed: {e}")
        return False

def extract_from_products_json(products, base_url):
    results = []
    session = requests.Session()
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, product in enumerate(products):
        title = product.get("title")
        vendor = product.get("vendor")
        handle = product.get("handle")
        product_url = f"{base_url}/products/{handle}"
        body_html = product.get("body_html", "") if include_description else ""
        product_type = product.get("product_type", "")
        tags = product.get("tags", "")
        options = product.get("options", [])
        option_map = {opt["position"]: opt["name"] for opt in options}

        rating, review_count = None, None
        if include_ratings:
            try:
                page = session.get(product_url, timeout=10)
                soup = BeautifulSoup(page.text, "html.parser")
                for script in soup.find_all("script", type="application/ld+json"):
                    try:
                        ld_data = json.loads(script.string.strip())
                        if isinstance(ld_data, list):
                            for item in ld_data:
                                if isinstance(item, dict) and item.get("@type") == "Product":
                                    rating_info = item.get("aggregateRating")
                                    if rating_info:
                                        rating = round(float(rating_info.get("ratingValue", 0)), 2)
                                        review_count = int(rating_info.get("reviewCount", 0))
                                    break
                        elif isinstance(ld_data, dict) and ld_data.get("@type") == "Product":
                            rating_info = ld_data.get("aggregateRating")
                            if rating_info:
                                rating = round(float(rating_info.get("ratingValue", 0)), 2)
                                review_count = int(rating_info.get("reviewCount", 0))
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        images = {img.get("id"): img.get("src") for img in product.get("images", [])}

        for variant in product.get("variants", []):
            variant_id = variant.get("id")
            variant_url = f"{product_url}?variant={variant_id}"
            price = float(variant.get("price", 0))
            compare_price = float(variant.get("compare_at_price") or 0)
            image_url = images.get(variant.get("image_id"))
            available = variant.get("available", False)

            discount = round(((compare_price - price) / compare_price) * 100, 2) if compare_price > price else None

            row = {
                "product url": product_url,
                "variant url": variant_url,
                "title": title,
                "vendor": vendor,
                "product type": product_type,
                "tags": tags,
                "variant id": variant_id,
                "sku": variant.get("sku"),
                "price": price,
                "offer price": compare_price if compare_price > 0 else None,
                "discount (%)": discount,
                "currency": variant.get("currency") or "USD",
                "availability": available,
                "product description": body_html if include_description else None,
                "image": image_url,
                "rating": rating if include_ratings else None,
                "review count": review_count if include_ratings else None
            }

            for i in range(1, 4):
                key = option_map.get(i, f"option{i}").lower()
                val = variant.get(f"option{i}")
                if val:
                    row[key] = val

            results.append(row)

        progress = (idx + 1) / len(products)
        progress_bar.progress(progress)
        status_text.text(f"Scraping: {title} ({int(progress * 100)}%)")

    status_text.text("✅ Scraping complete.")
    return results

# --- Run Scraper ---
if run_button:
    if not domain_input.strip():
        st.warning("⚠️ Please enter a domain like `allbirds.com` or `https://allbirds.com`.")
        st.stop()

    base_url = normalize_domain(domain_input)
    st.info(f"🔍 Checking {base_url}...")

    if not is_shopify_store(base_url):
        st.error("❌ Not a valid or accessible Shopify store.")
        st.stop()

    st.success("✅ Shopify store detected. Starting scrape...")

    with st.spinner("Fetching data..."):
        all_data = []
        page = 1
        while True:
            try:
                resp = requests.get(f"{base_url}/products.json?limit=250&page={page}", timeout=10)
                if resp.status_code != 200:
                    break
                data = resp.json().get("products", [])
                if not data:
                    break
                all_data.extend(data)
                page += 1
            except Exception as e:
                st.error(f"❌ Page {page} error: {e}")
                break

    if not all_data:
        st.warning("⚠️ No products found.")
        st.stop()

    results = extract_from_products_json(all_data, base_url)
    df = pd.DataFrame(results)

    if df.empty:
        st.warning("No product variants found.")
        st.stop()

    # --- Summary ---
    st.markdown("## ✅ Results")
    col1, col2 = st.columns(2)
    col1.metric("🧩 Variants", len(df))
    col2.metric("📦 Products", len(all_data))
    st.dataframe(df, use_container_width=True, height=400)

    

    # --- Downloads ---
    st.markdown("## 📥 Download Results")
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv = df.to_csv(index=False)
    json_data = df.to_json(orient="records")
    excel_buf = io.BytesIO()
    df.to_excel(excel_buf, index=False)
    excel_buf.seek(0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📄 CSV", csv, file_name=f"shopify_scrape_{now}.csv")
    with col2:
        st.download_button("📄 Excel", excel_buf, file_name=f"shopify_scrape_{now}.xlsx")
    with col3:
        st.download_button("📄 JSON", json_data, file_name=f"shopify_scrape_{now}.json")

    # --- Data Insights ---
    st.markdown("## 📊 Insights")

    if "vendor" in df.columns:
        st.markdown("### 🔝 Top Vendors")
        top_vendors = df["vendor"].value_counts().head(10)
        st.bar_chart(top_vendors)

    if "price" in df.columns and df["price"].notna().any():
        st.markdown("### 💵 Price Distribution")
        st.subheader("💲 Price Distribution")
        fig, ax = plt.subplots()
        ax.hist(df["price"], bins=30, color='skyblue', edgecolor='black')
        ax.set_xlabel("Price")
        ax.set_ylabel("Number of Products")
        ax.set_title("Product Price Distribution")
        st.pyplot(fig)

    if "rating" in df.columns and df["rating"].notna().any():
        avg_rating = round(df["rating"].mean(), 2)
        st.metric("⭐ Average Rating", avg_rating)

# --- Footer ---
st.markdown("---")
st.caption("Data pulled from publicly accessible Shopify endpoints. Ratings may be incomplete or unavailable depending on store structure.")




with st.sidebar:
    st.markdown("---")
    st.markdown("### 📬 Contact")
    st.markdown("""
    **Name:** K Sharath Chandra Karthik  
    **Email:** [ksharathkarthik@gmail.com](mailto:ksharathkarthik@gmail.com)  
    **GitHub:** [github.com/sk-karthi](https://github.com/sk-karthi)  
    **LinkedIn:** [linkedin.com/in/sharath-karthik-482a2b321](https://www.linkedin.com/in/sharath-karthik-482a2b321/)
    """)

    st.markdown("### 🙋 About")
    st.info(
        "This app checks whether a domain is a Shopify store and scrapes product variant data "
        "from publicly available product endpoints. It provides key insights such as top vendors, "
        "average ratings, and price distributions. Built for product intelligence and e-commerce analysis."
    )
