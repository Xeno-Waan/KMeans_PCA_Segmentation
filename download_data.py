import os
import urllib.request
import pandas as pd
import numpy as np

# Konfigurasi path
DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "Mall_Customers.csv")
DATASET_URL = "https://raw.githubusercontent.com/sharmaroshan/Clustering-of-Mall-Customers/master/Mall_Customers.csv"

def download_dataset():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Membuat direktori '{DATA_DIR}'...")

    if os.path.exists(CSV_PATH):
        print(f"Dataset sudah ada di: {CSV_PATH}")
        return

    print(f"Mencoba mengunduh dataset dari: {DATASET_URL}")
    try:
        urllib.request.urlretrieve(DATASET_URL, CSV_PATH)
        print(f"Berhasil mengunduh dataset ke: {CSV_PATH}")
    except Exception as e:
        print(f"Gagal mengunduh dataset: {e}")
        print("Membuat dataset sintetis sebagai fallback agar sistem tetap berjalan...")
        generate_synthetic_data()

def generate_synthetic_data():
    # Menghasilkan data sintetis 200 pelanggan yang menyerupai sebaran asli
    np.random.seed(42)
    n_samples = 200
    
    customer_ids = np.arange(1, n_samples + 1)
    genders = np.random.choice(['Male', 'Female'], size=n_samples, p=[0.44, 0.56])
    ages = np.random.randint(18, 71, size=n_samples)
    
    # Pendapatan tahunan (k$) dan spending score (1-100) biasanya memiliki beberapa cluster
    # Kita buat 5 cluster yang mewakili pola umum Mall Customers:
    # 1. Low income, low spending
    # 2. Low income, high spending
    # 3. Average income, average spending
    # 4. High income, low spending
    # 5. High income, high spending
    
    incomes = []
    spending_scores = []
    
    cluster_definitions = [
        # (mean_income, std_income, mean_spending, std_spending)
        (25, 5, 20, 8),    # Low-income, Low-spending (Hemat)
        (25, 5, 80, 8),    # Low-income, High-spending (Boros/Impulsif)
        (55, 8, 50, 8),    # Mid-income, Mid-spending (Rata-rata)
        (85, 10, 15, 8),   # High-income, Low-spending (Hati-hati)
        (85, 10, 82, 8)    # High-income, High-spending (Sultan)
    ]
    
    # Distribusikan 200 sampel ke dalam 5 cluster secara merata
    samples_per_cluster = n_samples // len(cluster_definitions)
    for mean_inc, std_inc, mean_spend, std_spend in cluster_definitions:
        inc = np.random.normal(mean_inc, std_inc, samples_per_cluster)
        spend = np.random.normal(mean_spend, std_spend, samples_per_cluster)
        incomes.extend(inc)
        spending_scores.extend(spend)
        
    # Jika ada kekurangan sisa pembagian
    while len(incomes) < n_samples:
        mean_inc, std_inc, mean_spend, std_spend = cluster_definitions[2]
        incomes.append(np.random.normal(mean_inc, std_inc))
        spending_scores.append(np.random.normal(mean_spend, std_spend))

    incomes = np.clip(np.array(incomes), 15, 140).astype(int)
    spending_scores = np.clip(np.array(spending_scores), 1, 100).astype(int)

    df = pd.DataFrame({
        'CustomerID': customer_ids,
        'Gender': genders,
        'Age': ages,
        'Annual Income (k$)': incomes,
        'Spending Score (1-100)': spending_scores
    })
    
    df.to_csv(CSV_PATH, index=False)
    print(f"Dataset sintetis sukses dibuat di: {CSV_PATH}")

if __name__ == "__main__":
    download_dataset()
