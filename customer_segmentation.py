import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Buat folder output
PLOTS_DIR = "plots"
if not os.path.exists(PLOTS_DIR):
    os.makedirs(PLOTS_DIR)

# Custom color palette yang premium untuk visualisasi
COLORS_5 = ["#FF6B6B", "#4D96FF", "#6BCB77", "#FFD93D", "#9B5DE5"]
COLORS_4 = ["#FF5E7E", "#2A9D8F", "#E9C46A", "#264653"]
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

def load_and_preprocess():
    csv_path = os.path.join("data", "Mall_Customers.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset tidak ditemukan di {csv_path}. Silakan jalankan download_data.py terlebih dahulu.")
    
    df = pd.read_csv(csv_path)
    print("=== Eksplorasi Data Awal ===")
    print(df.head())
    print("\nInformasi Dataset:")
    print(df.info())
    
    # Rename 'Genre' ke 'Gender' jika ada
    if 'Genre' in df.columns:
        df = df.rename(columns={'Genre': 'Gender'})
        
    # Cek Missing Values
    missing = df.isnull().sum()
    print("\nMissing Values per Kolom:")
    print(missing)
    if missing.sum() > 0:
        df = df.dropna()
        print("Missing values ditemukan dan baris terkait telah dihapus.")
    else:
        print("Tidak ada missing values.")
        
    return df

def find_optimal_k(data, max_k=10):
    """
    Menghitung inertia untuk K 1 s.d max_k dan mendeteksi Elbow point secara geometris
    (Jarak terjauh dari garis chord antara K=1 dan K=max_k)
    """
    inertias = []
    k_values = list(range(1, max_k + 1))
    
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(data)
        inertias.append(kmeans.inertia_)
        
    # Deteksi elbow point secara otomatis (Metode geometric chord)
    # Garis lurus menghubungkan (1, inertia[0]) dan (max_k, inertia[-1])
    p1 = np.array([k_values[0], inertias[0]])
    p2 = np.array([k_values[-1], inertias[-1]])
    
    distances = []
    for i in range(len(k_values)):
        p = np.array([k_values[i], inertias[i]])
        # Rumus jarak titik ke garis ax + by + c = 0
        # Di mana garis melewati p1 dan p2
        d = np.abs(np.cross(p2 - p1, p1 - p)) / np.linalg.norm(p2 - p1)
        distances.append(d)
        
    optimal_k = k_values[np.argmax(distances)]
    return k_values, inertias, optimal_k

def run_scenario_1(df):
    print("\n=== SKENARIO 1: Segmentasi berdasarkan Income & Spending Score ===")
    X1 = df[['Annual Income (k$)', 'Spending Score (1-100)']].copy()
    
    # Standardisasi
    scaler = StandardScaler()
    X1_scaled = scaler.fit_transform(X1)
    
    # Cari K optimal
    k_vals, inertias, opt_k = find_optimal_k(X1_scaled, max_k=10)
    print(f"Jumlah cluster (K) optimal yang terdeteksi secara otomatis: {opt_k}")
    
    # Plot Elbow Method
    plt.figure(figsize=(8, 5))
    plt.plot(k_vals, inertias, 'o-', color='#4D96FF', linewidth=2.5, markersize=8)
    plt.axvline(x=opt_k, color='#FF6B6B', linestyle='--', linewidth=2, label=f'Elbow Point (K={opt_k})')
    plt.title('Metode Elbow - Skenario 1 (Income vs Spending)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Jumlah Cluster (K)', fontsize=12)
    plt.ylabel('Inertia (WCSS)', fontsize=12)
    plt.xticks(k_vals)
    plt.legend(frameon=True, facecolor='white', edgecolor='none')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "scenario1_elbow.png"), dpi=300)
    plt.close()
    
    # Fit KMeans dengan K optimal (biasanya 5 untuk Mall Customers)
    # Kita paksa K=5 jika optimal terdeteksi di sekitarnya karena ini adalah pola standar
    k_final = opt_k if opt_k in [4, 5, 6] else 5
    print(f"Menggunakan K={k_final} untuk K-Means clustering pada Skenario 1.")
    
    kmeans = KMeans(n_clusters=k_final, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X1_scaled)
    df['Cluster_S1'] = clusters
    
    # Ambil Centroid (dalam skala asli)
    centroids_scaled = kmeans.cluster_centers_
    centroids = scaler.inverse_transform(centroids_scaled)
    
    # Analisis profil cluster untuk penamaan
    cluster_means = df.groupby('Cluster_S1')[['Annual Income (k$)', 'Spending Score (1-100)']].mean()
    print("\nRata-rata Nilai per Cluster (Skenario 1):")
    print(cluster_means)
    
    # Penamaan cluster berdasarkan posisi karakteristik
    cluster_labels = {}
    for c_id in range(k_final):
        inc = cluster_means.loc[c_id, 'Annual Income (k$)']
        spend = cluster_means.loc[c_id, 'Spending Score (1-100)']
        
        if inc < 45 and spend < 40:
            cluster_labels[c_id] = "Hemat / Pendapatan Rendah-Pengeluaran Rendah"
        elif inc < 45 and spend > 60:
            cluster_labels[c_id] = "Boros / Pendapatan Rendah-Pengeluaran Tinggi"
        elif 40 <= inc <= 75 and 40 <= spend <= 60:
            cluster_labels[c_id] = "Rata-rata / Standar"
        elif inc > 70 and spend < 40:
            cluster_labels[c_id] = "Hati-hati / Pendapatan Tinggi-Pengeluaran Rendah"
        elif inc > 70 and spend > 60:
            cluster_labels[c_id] = "Sultan / Pendapatan Tinggi-Pengeluaran Tinggi (Target Utama)"
        else:
            cluster_labels[c_id] = f"Cluster {c_id}"
            
    df['Segment_S1'] = df['Cluster_S1'].map(cluster_labels)
    
    # Plot Visualisasi Cluster Skenario 1
    plt.figure(figsize=(10, 7.5))
    palette_colors = COLORS_5[:k_final] if k_final <= 5 else sns.color_palette("husl", k_final)
    
    sns.scatterplot(
        data=df, 
        x='Annual Income (k$)', 
        y='Spending Score (1-100)', 
        hue='Segment_S1', 
        palette=palette_colors,
        s=100, 
        alpha=0.85, 
        edgecolor='black', 
        linewidth=0.8
    )
    
    # Plot Centroid
    plt.scatter(
        centroids[:, 0], 
        centroids[:, 1], 
        s=300, 
        c='black', 
        marker='X', 
        edgecolors='white', 
        linewidth=2, 
        label='Centroids'
    )
    
    plt.title('Segmentasi Pelanggan - Skenario 1\n(Annual Income vs Spending Score)', fontsize=15, fontweight='bold', pad=15)
    plt.xlabel('Annual Income (k$)', fontsize=12)
    plt.ylabel('Spending Score (1-100)', fontsize=12)
    plt.legend(title='Segmen Pelanggan', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "scenario1_clusters.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    return df

def run_scenario_2(df):
    print("\n=== SKENARIO 2: Segmentasi berdasarkan Age, Income, & Spending Score dengan PCA ===")
    X2 = df[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].copy()
    
    # Standardisasi
    scaler = StandardScaler()
    X2_scaled = scaler.fit_transform(X2)
    
    # PCA reduksi dimensi ke 2 Principal Components
    pca = PCA(n_components=2, random_state=42)
    X2_pca = pca.fit_transform(X2_scaled)
    
    print(f"Explained variance ratio oleh 2 komponen PCA: {pca.explained_variance_ratio_}")
    print(f"Total variance yang dijelaskan: {sum(pca.explained_variance_ratio_):.2%}")
    
    # Cari K optimal untuk PCA
    k_vals, inertias, opt_k = find_optimal_k(X2_pca, max_k=10)
    print(f"Jumlah cluster (K) optimal secara otomatis untuk PCA data: {opt_k}")
    
    # Plot Elbow Method PCA
    plt.figure(figsize=(8, 5))
    plt.plot(k_vals, inertias, 'o-', color='#9B5DE5', linewidth=2.5, markersize=8)
    plt.axvline(x=opt_k, color='#FF6B6B', linestyle='--', linewidth=2, label=f'Elbow Point (K={opt_k})')
    plt.title('Metode Elbow - Skenario 2 (PCA Components)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Jumlah Cluster (K)', fontsize=12)
    plt.ylabel('Inertia (WCSS)', fontsize=12)
    plt.xticks(k_vals)
    plt.legend(frameon=True, facecolor='white', edgecolor='none')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "scenario2_elbow.png"), dpi=300)
    plt.close()
    
    # Biasanya 4 atau 5 cluster optimal untuk PCA data
    k_final = opt_k if opt_k in [4, 5, 6] else 4
    print(f"Menggunakan K={k_final} untuk K-Means clustering pada Skenario 2.")
    
    kmeans = KMeans(n_clusters=k_final, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X2_pca)
    
    df['Cluster_S2'] = clusters
    df['PC1'] = X2_pca[:, 0]
    df['PC2'] = X2_pca[:, 1]
    
    # Analisis karakteristik berdasarkan data asli
    cluster_means = df.groupby('Cluster_S2')[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].mean()
    print("\nRata-rata Fitur Asli per Cluster (Skenario 2):")
    print(cluster_means)
    
    # Memberikan nama profil cluster yang berwawasan bisnis
    # Kita cari mana yang tertua, termuda, pendapatan tertinggi, dll.
    cluster_labels = {}
    for c_id in range(k_final):
        age = cluster_means.loc[c_id, 'Age']
        inc = cluster_means.loc[c_id, 'Annual Income (k$)']
        spend = cluster_means.loc[c_id, 'Spending Score (1-100)']
        
        # Logika pelabelan dinamis
        if age < 35 and spend > 60:
            if inc > 70:
                cluster_labels[c_id] = "Muda, Sultan / Konsumtif Premium"
            else:
                cluster_labels[c_id] = "Muda, Boros / Konsumtif Sedang"
        elif age > 45 and spend < 45:
            cluster_labels[c_id] = "Senior, Hemat / Konservatif"
        elif inc > 70 and spend < 35:
            cluster_labels[c_id] = "Pendapatan Tinggi, Hati-hati / Kaya & Bijak"
        elif 35 <= age <= 50 and 35 <= spend <= 65:
            cluster_labels[c_id] = "Usia Menengah, Rata-rata / Seimbang"
        else:
            # Fallback pelabelan berdasarkan dominasi fitur
            label_parts = []
            if age < 35: label_parts.append("Muda")
            elif age > 50: label_parts.append("Senior")
            else: label_parts.append("Usia Sedang")
            
            if inc > 70: label_parts.append("Pendapatan Tinggi")
            elif inc < 45: label_parts.append("Pendapatan Rendah")
            else: label_parts.append("Pendapatan Sedang")
            
            if spend > 60: label_parts.append("Skor Belanja Tinggi")
            else: label_parts.append("Skor Belanja Rendah")
            
            cluster_labels[c_id] = " & ".join(label_parts)
            
    df['Segment_S2'] = df['Cluster_S2'].map(cluster_labels)
    
    # Plot Visualisasi Cluster Skenario 2 (PCA 2D Space)
    plt.figure(figsize=(10, 7.5))
    palette_colors = COLORS_4[:k_final] if k_final <= 4 else sns.color_palette("husl", k_final)
    
    sns.scatterplot(
        data=df, 
        x='PC1', 
        y='PC2', 
        hue='Segment_S2', 
        palette=palette_colors,
        s=100, 
        alpha=0.85, 
        edgecolor='black', 
        linewidth=0.8
    )
    
    plt.title('Segmentasi Pelanggan - Skenario 2\n(2D PCA Space dari Age, Income, & Spending Score)', fontsize=15, fontweight='bold', pad=15)
    plt.xlabel('Principal Component 1 (PC1)', fontsize=12)
    plt.ylabel('Principal Component 2 (PC2)', fontsize=12)
    plt.legend(title='Segmen Pelanggan PCA', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "scenario2_clusters.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    return df

def generate_report(df_s1, df_s2):
    report_path = "customer_segmentation_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("========================================================================\n")
        f.write("             LAPORAN ANALISIS SEGMENTASI PELANGGAN MALL                 \n")
        f.write("========================================================================\n\n")
        
        f.write("1. EKSPLORASI DATASET\n")
        f.write(f"- Jumlah Pelanggan: {len(df_s1)}\n")
        f.write(f"- Rata-rata Umur: {df_s1['Age'].mean():.1f} tahun\n")
        f.write(f"- Rata-rata Pendapatan Tahunan: {df_s1['Annual Income (k$)'].mean():.1f} k$\n")
        f.write(f"- Rata-rata Skor Pengeluaran (1-100): {df_s1['Spending Score (1-100)'].mean():.1f}\n")
        f.write(f"- Distribusi Gender: Female ({df_s1['Gender'].value_counts().get('Female', 0)/len(df_s1):.1%}), Male ({df_s1['Gender'].value_counts().get('Male', 0)/len(df_s1):.1%})\n\n")
        
        f.write("2. SKENARIO 1: SEGMENTASI INCOME VS SPENDING SCORE\n")
        f.write("Skenario ini mengelompokkan pelanggan berdasarkan pendapatan tahunan dan skor pengeluaran.\n")
        f.write("Karakteristik tiap kelompok:\n")
        
        s1_summary = df_s1.groupby('Segment_S1')[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].mean()
        s1_counts = df_s1['Segment_S1'].value_counts()
        for idx, name in enumerate(s1_summary.index):
            f.write(f"\n> Segmen: {name}\n")
            f.write(f"  - Jumlah Anggota: {s1_counts[name]} pelanggan ({s1_counts[name]/len(df_s1):.1%})\n")
            f.write(f"  - Rata-rata Umur: {s1_summary.loc[name, 'Age']:.1f} tahun\n")
            f.write(f"  - Rata-rata Pendapatan: {s1_summary.loc[name, 'Annual Income (k$)']:.1f} k$\n")
            f.write(f"  - Rata-rata Skor Belanja: {s1_summary.loc[name, 'Spending Score (1-100)']:.1f}\n")
            
            # Wawasan Bisnis Rekomendasi
            if "Sultan" in name or "Pendapatan Tinggi-Pengeluaran Tinggi" in name:
                f.write("  - Rekomendasi Pemasaran: Target utama untuk produk premium, program loyalitas eksklusif, dan penawaran khusus bernilai tinggi.\n")
            elif "Hati-hati" in name or "Pendapatan Tinggi-Pengeluaran Rendah" in name:
                f.write("  - Rekomendasi Pemasaran: Tawarkan promosi berbasis nilai (value-for-money), tunjukkan kualitas produk jangka panjang, hindari spam iklan tidak berkelas.\n")
            elif "Rata-rata" in name:
                f.write("  - Rekomendasi Pemasaran: Kampanye pemasaran reguler, diskon musiman, serta promosi produk tingkat menengah yang stabil.\n")
            elif "Boros" in name or "Pendapatan Rendah-Pengeluaran Tinggi" in name:
                f.write("  - Rekomendasi Pemasaran: Gunakan teknik penjualan instan (flash sale), diskon menarik, bundling produk murah, dan iklan media sosial yang kekinian.\n")
            elif "Hemat" in name or "Pendapatan Rendah-Pengeluaran Rendah" in name:
                f.write("  - Rekomendasi Pemasaran: Berikan penawaran harga termurah, kupon diskon dasar, dan hindari penawaran barang-barang mewah.\n")
                
        f.write("\n\n3. SKENARIO 2: SEGMENTASI MULTIDIMENSI (AGE, INCOME, SPENDING) MENGGUNAKAN PCA\n")
        f.write("Skenario ini menggabungkan Umur ke dalam analisis, lalu mereduksi dimensinya menjadi 2 komponen utama sebelum dikelompokkan.\n")
        
        s2_summary = df_s2.groupby('Segment_S2')[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].mean()
        s2_counts = df_s2['Segment_S2'].value_counts()
        for idx, name in enumerate(s2_summary.index):
            f.write(f"\n> Segmen PCA: {name}\n")
            f.write(f"  - Jumlah Anggota: {s2_counts[name]} pelanggan ({s2_counts[name]/len(df_s2):.1%})\n")
            f.write(f"  - Rata-rata Umur: {s2_summary.loc[name, 'Age']:.1f} tahun\n")
            f.write(f"  - Rata-rata Pendapatan: {s2_summary.loc[name, 'Annual Income (k$)']:.1f} k$\n")
            f.write(f"  - Rata-rata Skor Belanja: {s2_summary.loc[name, 'Spending Score (1-100)']:.1f}\n")
            
            # Wawasan Bisnis Rekomendasi PCA
            if "Muda" in name and "Boros" in name:
                f.write("  - Rekomendasi Pemasaran: Gunakan tren media sosial terkini, influencer marketing, dan produk gaya hidup trendi.\n")
            elif "Sultan" in name or "Konsumtif Premium" in name:
                f.write("  - Rekomendasi Pemasaran: Layanan VIP, concierge belanja pribadi, barang edisi terbatas.\n")
            elif "Senior" in name or "Konservatif" in name:
                f.write("  - Rekomendasi Pemasaran: Kampanye bernuansa keluarga, kenyamanan berbelanja, program loyalitas tradisional, dan pelayanan pelanggan yang ramah.\n")
            elif "Pendapatan Tinggi" in name and "Hati-hati" in name:
                f.write("  - Rekomendasi Pemasaran: Investasi jangka panjang, penawaran properti, asuransi, barang bernilai aset tinggi.\n")
            else:
                f.write("  - Rekomendasi Pemasaran: Penawaran standar yang menyeimbangkan kegunaan dan harga rasional.\n")
                
        f.write("\n========================================================================\n")
        f.write("                   AKHIR LAPORAN ANALISIS PELANGGAN                     \n")
        f.write("========================================================================\n")
        
    print(f"\nLaporan tertulis telah disimpan di: {report_path}")

def main():
    print("Memulai Pipeline Segmentasi Pelanggan Mall...")
    
    # 1. Load Data
    df = load_and_preprocess()
    
    # 2. Jalankan Skenario 1
    df_s1 = run_scenario_1(df)
    
    # 3. Jalankan Skenario 2
    df_s2 = run_scenario_2(df_s1)
    
    # 4. Hasilkan Laporan
    generate_report(df_s1, df_s2)
    
    print("\nSeluruh proses segmentasi berhasil selesai! Gambar plot tersimpan di direktori 'plots/'.")

if __name__ == "__main__":
    main()
