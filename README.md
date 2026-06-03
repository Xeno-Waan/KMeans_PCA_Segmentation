# Mall Customers Customer Segmentation System

Proyek ini adalah sistem machine learning untuk segmentasi pelanggan menggunakan dataset 'Mall Customers' dengan algoritma K-Means Clustering dan PCA (Principal Component Analysis). Sistem ini mengelompokkan pelanggan ke dalam segmen-segmen homogen untuk mempermudah strategi pemasaran yang lebih bertarget.

## Fitur Utama
1. **Unduhan Data Otomatis & Fallback**: Skrip otomatis untuk mengunduh dataset asli atau membuat dataset sintetis berkualitas tinggi jika offline.
2. **Skenario 1 (K-Means 2D)**: Segmentasi pelanggan berdasarkan *Annual Income* dan *Spending Score*. Menghasilkan 5 klaster optimal.
3. **Skenario 2 (PCA + K-Means)**: Segmentasi pelanggan multidimensi berdasarkan *Age*, *Annual Income*, dan *Spending Score*. Menggunakan PCA untuk mereduksi 3 fitur menjadi 2 Principal Components (menjelaskan ~77.57% varians data) sebelum klasterisasi. Menghasilkan 4 klaster optimal.
4. **Visualisasi Dinamis**: Plot Elbow Method dan sebaran klaster (termasuk centroid) disimpan otomatis di folder `plots/`.
5. **Rekomendasi Strategis**: Laporan tertulis otomatis (`customer_segmentation_report.txt`) memberikan saran taktis pemasaran bagi masing-masing kelompok pelanggan.

## Persyaratan System (Libraries)
Pastikan pustaka berikut sudah terinstal di Python Anda:
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`
- `seaborn`

Instalasi:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

## Cara Menjalankan Program

1. **Unduh Dataset**:
   ```bash
   python download_data.py
   ```
2. **Jalankan Pipeline Klasterisasi**:
   ```bash
   python customer_segmentation.py
   ```

## Struktur Direktori
* `download_data.py`: Skrip untuk mengunduh/menyiapkan data.
* `customer_segmentation.py`: Pipeline utama pra-pemrosesan, clustering, PCA, dan visualisasi.
* `customer_segmentation_report.txt`: Laporan wawasan segmentasi dan rekomendasi bisnis.
* `data/`: Folder penyimpanan dataset CSV.
* `plots/`: Folder penyimpanan gambar plot hasil analisis.
* `C:\Users\Lenovo\.gemini\antigravity-ide\brain\03cce310-9d0b-4455-83a9-ba1a506ea694\walkthrough.md`: Laporan pengerjaan interaktif.

---
*Dibuat untuk tugas mata kuliah Pak Ronggo.*
