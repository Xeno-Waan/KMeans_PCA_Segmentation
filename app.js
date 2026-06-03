// Model Parameters from Python
const MODEL_PARAMS = {
    s1: {
        mean: [60.56, 50.2],
        scale: [26.19897708, 25.75888196],
        centroids: [
            [-0.20091257, -0.02645617], // Cluster 0: Rata-rata
            [0.99158305, 1.23950275],   // Cluster 1: Sultan
            [-1.32954532, 1.13217788],  // Cluster 2: Boros
            [1.05500302, -1.28443907],  // Cluster 3: Hati-hati
            [-1.30751869, -1.13696536]  // Cluster 4: Hemat
        ],
        labels: [
            { name: "Rata-rata / Standar", desc: "Pendapatan dan pengeluaran tingkat menengah yang stabil.", class: "color-standard", rec: "Kampanye pemasaran reguler, diskon musiman, serta promosi produk tingkat menengah yang stabil." },
            { name: "Sultan / Pendapatan Tinggi-Pengeluaran Tinggi (Target Utama)", desc: "Pelanggan VIP dengan daya beli melimpah dan suka berbelanja.", class: "color-sultan", rec: "Target utama untuk produk premium, program loyalitas eksklusif, dan penawaran khusus bernilai tinggi." },
            { name: "Boros / Pendapatan Rendah-Pengeluaran Tinggi", desc: "Pelanggan berpendapatan rendah yang bersikap impulsif saat belanja.", class: "color-spendy", rec: "Gunakan teknik penjualan instan (flash sale), diskon menarik, bundling produk murah, dan iklan media sosial yang kekinian." },
            { name: "Hati-hati / Pendapatan Tinggi-Pengeluaran Rendah", desc: "Kelompok berkecukupan yang sangat hemat dan selektif.", class: "color-careful", rec: "Tawarkan promosi berbasis nilai (value-for-money), tunjukkan kualitas produk jangka panjang, hindari spam iklan tidak berkelas." },
            { name: "Hemat / Pendapatan Rendah-Pengeluaran Rendah", desc: "Pelanggan ekonomis dengan anggaran belanja yang sangat minim.", class: "color-frugal", rec: "Berikan penawaran harga termurah, kupon diskon dasar, dan hindari penawaran barang-barang mewah." }
        ]
    },
    s2: {
        mean: [38.85, 60.56, 50.2],
        scale: [13.93404105, 26.19897708, 25.75888196],
        pca_components: [
            [0.70638235, -0.04802398, -0.70619946], // PC1 projection
            [0.03014116, 0.9988316, -0.03777499]   // PC2 projection
        ],
        centroids: [
            [0.97771498, -0.49877873],  // Cluster 0: Senior, Hemat
            [-1.04671072, 0.65699063],  // Cluster 1: Muda, Sultan
            [-1.09453687, -1.11878664], // Cluster 2: Muda, Boros
            [0.99540827, 1.10926194]    // Cluster 3: Pendapatan Tinggi, Hati-hati
        ],
        labels: [
            { name: "Senior, Hemat / Konservatif", desc: "Pelanggan usia menengah ke atas yang berbelanja dengan bijak dan ekonomis.", class: "color-standard", rec: "Kampanye bernuansa keluarga, kenyamanan berbelanja, program loyalitas tradisional, dan pelayanan pelanggan yang ramah." },
            { name: "Muda, Sultan / Konsumtif Premium", desc: "Pelanggan muda dengan penghasilan tinggi yang konsumtif.", class: "color-sultan", rec: "Layanan VIP, concierge belanja pribadi, barang edisi terbatas." },
            { name: "Muda, Boros / Konsumtif Sedang", desc: "Pelanggan muda berpenghasilan rendah yang loyalitas belanjanya cukup tinggi.", class: "color-spendy", rec: "Gunakan tren media sosial terkini, influencer marketing, dan produk gaya hidup trendi." },
            { name: "Pendapatan Tinggi, Hati-hati / Kaya & Bijak", desc: "Pelanggan mapan yang tidak mudah tergiur promosi konsumtif biasa.", class: "color-careful", rec: "Investasi jangka panjang, penawaran properti, asuransi, barang bernilai aset tinggi." }
        ]
    }
};

document.addEventListener("DOMContentLoaded", () => {
    setupTabs();
    setupSliders();
    setupPredictor();
});

// Tab Navigation Logic
function setupTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            
            // Toggle buttons
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // Toggle panes
            tabPanes.forEach(pane => {
                pane.classList.remove("active");
                if (pane.getAttribute("id") === tabId) {
                    pane.classList.add("active");
                }
            });
        });
    });

    // Visualization sub-scenario toggle
    const toggleBtns = document.querySelectorAll(".visual-toggle");
    const displays = document.querySelectorAll(".visual-display");

    toggleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const scenario = btn.getAttribute("data-scenario");

            toggleBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            displays.forEach(d => {
                d.classList.remove("active");
                if (d.getAttribute("id") === `visuals-s${scenario}`) {
                    d.classList.add("active");
                }
            });
        });
    });
}

// Real-time slider values display
function setupSliders() {
    const sliders = [
        { id: "input-age", valId: "val-age", suffix: " tahun" },
        { id: "input-income", valId: "val-income", suffix: " k$" },
        { id: "input-spending", valId: "val-spending", suffix: "" }
    ];

    sliders.forEach(s => {
        const slider = document.getElementById(s.id);
        const valueDisplay = document.getElementById(s.valId);

        slider.addEventListener("input", (e) => {
            valueDisplay.textContent = e.target.value + s.suffix;
        });
    });
}

// Predictor calculation model logic
function setupPredictor() {
    const form = document.getElementById("prediction-form");
    const emptyResult = document.getElementById("empty-result");
    const resultContent = document.getElementById("result-content");
    const resultPanel = document.getElementById("result-panel");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        // Get inputs
        const age = parseInt(document.getElementById("input-age").value);
        const income = parseInt(document.getElementById("input-income").value);
        const spending = parseInt(document.getElementById("input-spending").value);

        // Run Scenario 1 prediction
        const s1_result = predictScenario1(income, spending);

        // Run Scenario 2 prediction
        const s2_result = predictScenario2(age, income, spending);

        // Display results
        updateResultUI(s1_result, s2_result);

        // Toggle visibility
        emptyResult.classList.add("hidden");
        resultContent.classList.remove("hidden");
        resultPanel.style.justifyContent = "flex-start";
    });
}

// Math logic for Scenario 1
function predictScenario1(income, spending) {
    const params = MODEL_PARAMS.s1;

    // Standardize features
    const scaledIncome = (income - params.mean[0]) / params.scale[0];
    const scaledSpending = (spending - params.mean[1]) / params.scale[1];

    // Find nearest centroid
    let minDistance = Infinity;
    let predictedCluster = 0;

    params.centroids.forEach((centroid, idx) => {
        const dist = Math.pow(scaledIncome - centroid[0], 2) + Math.pow(scaledSpending - centroid[1], 2);
        if (dist < minDistance) {
            minDistance = dist;
            predictedCluster = idx;
        }
    });

    return {
        cluster: predictedCluster,
        label: params.labels[predictedCluster],
        values: { income, spending }
    };
}

// Math logic for Scenario 2 (Scaling -> PCA projection -> K-Means)
function predictScenario2(age, income, spending) {
    const params = MODEL_PARAMS.s2;

    // Standardize features
    const scaledAge = (age - params.mean[0]) / params.scale[0];
    const scaledIncome = (income - params.mean[1]) / params.scale[1];
    const scaledSpending = (spending - params.mean[2]) / params.scale[2];

    // Project onto PCA components
    const pc1 = (scaledAge * params.pca_components[0][0]) + 
                (scaledIncome * params.pca_components[0][1]) + 
                (scaledSpending * params.pca_components[0][2]);

    const pc2 = (scaledAge * params.pca_components[1][0]) + 
                (scaledIncome * params.pca_components[1][1]) + 
                (scaledSpending * params.pca_components[1][2]);

    // Find nearest centroid in PCA space
    let minDistance = Infinity;
    let predictedCluster = 0;

    params.centroids.forEach((centroid, idx) => {
        const dist = Math.pow(pc1 - centroid[0], 2) + Math.pow(pc2 - centroid[1], 2);
        if (dist < minDistance) {
            minDistance = dist;
            predictedCluster = idx;
        }
    });

    return {
        cluster: predictedCluster,
        label: params.labels[predictedCluster],
        values: { age, pc1: pc1.toFixed(3), pc2: pc2.toFixed(3) }
    };
}

// Update Result interface elements
function updateResultUI(s1, s2) {
    // Skenario 1 UI update
    const s1Name = document.getElementById("s1-name");
    s1Name.className = `segment-name ${s1.label.class}`;
    s1Name.textContent = s1.label.name;

    document.getElementById("s1-income-pill").textContent = `Pendapatan: ${s1.values.income} k$`;
    document.getElementById("s1-spending-pill").textContent = `Skor Belanja: ${s1.values.spending}`;
    
    const s1RecBox = document.getElementById("s1-rec");
    s1RecBox.querySelector(".rec-text").textContent = s1.label.rec;

    // Skenario 2 UI update
    const s2Name = document.getElementById("s2-name");
    s2Name.className = `segment-name ${s2.label.class}`;
    s2Name.textContent = s2.label.name;

    document.getElementById("s2-age-pill").textContent = `Umur: ${s2.values.age} tahun`;
    document.getElementById("s2-pca-pill").textContent = `PC1: ${s2.values.pc1}, PC2: ${s2.values.pc2}`;
    
    const s2RecBox = document.getElementById("s2-rec");
    s2RecBox.querySelector(".rec-text").textContent = s2.label.rec;
}
