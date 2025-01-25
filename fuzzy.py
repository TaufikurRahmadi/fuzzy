from flask import Flask, request, render_template_string
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Fuzzy Logic Input</title>
</head>
<body>
    <h1>Fuzzy Logic Program</h1>
    <form method="post">
        <label for="j_inventory">Jumlah Inventory:</label><br>
        <input type="number" id="j_inventory" name="j_inventory" required><br><br>

        <label for="j_permintaan">Jumlah Permintaan:</label><br>
        <input type="number" id="j_permintaan" name="j_permintaan" required><br><br>

        <button type="submit">Submit</button>
    </form>

    {% if result %}
        <h2>Results</h2>
        <p>Fuzzy Inventory Minim: {{ result['finventory_minim'] }}</p>
        <p>Fuzzy Inventory Sedang: {{ result['finventory_sedang'] }}</p>
        <p>Fuzzy Inventory Banyak: {{ result['finventory_banyak'] }}</p>
        <p>Fuzzy Permintaan Rendah: {{ result['fpermintaan_rendah'] }}</p>
        <p>Fuzzy Permintaan Sedang: {{ result['fpermintaan_sedang'] }}</p>
        <p>Fuzzy Permintaan Tinggi: {{ result['fpermintaan_tinggi'] }}</p>
        <p>Prediksi Jumlah Produksi: {{ result['prediksi_produksi'] }}</p>

        <h2>Graphs</h2>
        <img src="data:image/png;base64,{{ result['inventory_graph'] }}" alt="Inventory Graph"><br>
        <img src="data:image/png;base64,{{ result['permintaan_graph'] }}" alt="Permintaan Graph"><br>
        <img src="data:image/png;base64,{{ result['produksi_graph'] }}" alt="Produksi Graph">
    {% endif %}
</body>
</html>
'''

def inventori_minim(x):
    if x <= 30:
        return 1
    elif 30 < x <= 40:
        return (40 - x) / 10
    else:
        return 0

def inventori_sedang(x):
    if 35 <= x <= 40:
        return (x - 35) / 5
    elif 40 < x <= 45:
        return (45 - x) / 5
    else:
        return 0

def inventori_banyak(x):
    if 40 <= x <= 45:
        return (x - 40) / 5
    elif x > 45:
        return 1
    else:
        return 0

def permintaan_minim(x):
    if x <= 10:
        return 1
    elif 10 < x <= 30:
        return (30 - x) / 20
    else:
        return 0

def permintaan_sedang(x):
    if 10 <= x <= 20:
        return (x - 10) / 10
    elif 20 < x <= 40:
        return (40 - x) / 20
    else:
        return 0

def permintaan_banyak(x):
    if 20 <= x <= 40:
        return (x - 20) / 20
    elif x > 40:
        return 1
    else:
        return 0

@app.route('/', methods=['GET', 'POST'])
def fuzzy_logic():
    result = None
    if request.method == 'POST':
        j_inventory = int(request.form['j_inventory'])
        j_permintaan = int(request.form['j_permintaan'])

        # Fuzzifikasi Inventory
        finventory_minim = inventori_minim(j_inventory)
        finventory_sedang = inventori_sedang(j_inventory)
        finventory_banyak = inventori_banyak(j_inventory)

        # Fuzzifikasi Permintaan
        fpermintaan_rendah = permintaan_minim(j_permintaan)
        fpermintaan_sedang = permintaan_sedang(j_permintaan)
        fpermintaan_tinggi = permintaan_banyak(j_permintaan)

        # Inferensi
        fproduksi_tidak = max(min(fpermintaan_sedang, finventory_banyak),
                              min(fpermintaan_rendah, finventory_sedang),
                              min(fpermintaan_rendah, finventory_banyak))

        fproduksi_kecil = max(min(fpermintaan_rendah, finventory_minim),
                              min(fpermintaan_sedang, finventory_sedang),
                              min(fpermintaan_tinggi, finventory_banyak))

        fproduksi_sedang = max(min(fpermintaan_sedang, finventory_minim),
                               min(fpermintaan_tinggi, finventory_sedang))

        fproduksi_besar = min(fpermintaan_tinggi, finventory_minim)

        # Defuzzifikasi
        numerator = ((0 * fproduksi_tidak) +
                     (10 * fproduksi_kecil) +
                     (25 * fproduksi_sedang) +
                     (40 * fproduksi_besar))
        denominator = (fproduksi_tidak + fproduksi_kecil + fproduksi_sedang + fproduksi_besar)
        prediksi_produksi = numerator / denominator if denominator != 0 else 0

        # Generate Graphs
        def generate_graph(x_values, y_values, title, xlabel, ylabel):
            plt.figure(figsize=(8, 6))
            plt.plot(x_values, y_values[0], label='Minim', color='blue')
            plt.plot(x_values, y_values[1], label='Sedang', color='green')
            plt.plot(x_values, y_values[2], label='Banyak', color='red')
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.legend()
            plt.grid()
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            return graph_url

        # Inventory Graph
        jumlah_inventori = np.arange(0, 80, 1)
        inventory_values = [ [inventori_minim(x) for x in jumlah_inventori],
                             [inventori_sedang(x) for x in jumlah_inventori],
                             [inventori_banyak(x) for x in jumlah_inventori] ]
        inventory_graph = generate_graph(jumlah_inventori, inventory_values,
                                          "Fuzzy Membership Function (Jumlah Inventori)",
                                          "Jumlah Inventori", "Keanggotaan")

        # Permintaan Graph
        jumlah_permintaan = np.arange(0, 80, 1)
        permintaan_values = [ [permintaan_minim(x) for x in jumlah_permintaan],
                              [permintaan_sedang(x) for x in jumlah_permintaan],
                              [permintaan_banyak(x) for x in jumlah_permintaan] ]
        permintaan_graph = generate_graph(jumlah_permintaan, permintaan_values,
                                           "Fuzzy Membership Function (Jumlah Permintaan)",
                                           "Jumlah Permintaan", "Keanggotaan")

        # Produksi Graph
                # Produksi Graph
       # Produksi Graph
        produksi = np.array([0, 10, 25, 40])  # Titik-titik grafik
        keanggotaan = np.array([fproduksi_tidak, fproduksi_kecil, fproduksi_sedang, fproduksi_besar])  # Derajat keanggotaan

        # Use the predicted production as the midpoint
        midpoint = prediksi_produksi

        plt.figure(figsize=(8, 4))

        # Plot bars for each production category
        for i, p in enumerate(produksi):
            plt.bar(p, keanggotaan[i], width=5, color='black')  # Use the membership value as the height

        # Garis horizontal
        plt.hlines(y=1, xmin=0, xmax=80, color='black', linewidth=2)  # Garis horizontal atas

        # Menambahkan label variabel di atas titik
        for i, p in enumerate(produksi):
            plt.text(p, keanggotaan[i] + 0.05, ['No Produksi', 'Kecil', 'Sedang', 'Besar'][i],
                    ha='center', fontsize=10, color='black')  # Label di atas titik

        # Menambahkan nilai angka di bawah titik
        for i, p in enumerate(produksi):
            plt.text(p, -0.15, f"{keanggotaan[i]:.2f}", ha='center', fontsize=10, color='black')  # Nilai di bawah titik

        # Add midpoint marker based on predicted production
        plt.axvline(x=midpoint, color='orange', linestyle='--', label='Prediksi Produksi', linewidth=2)
        plt.text(midpoint, 1.1, f'Prediksi: {midpoint:.2f}', ha='center', fontsize=10, color='orange')

        # Penyesuaian tampilan
        plt.xticks([])  # Hilangkan label default pada sumbu X
        plt.yticks(np.arange(0, 1.2, 0.2), labels=['0', '0.2', '0.4', '0.6', '0.8', '1'], fontsize=10)  # Label sumbu Y
        plt.ylabel('(Jumlah Produksi)', fontsize=12)
        plt.title('Fungsi Keanggotaan Produksi', fontsize=14)
        plt.ylim(0, 1.2)  # Rentang sumbu Y untuk memberi ruang pada teks
        plt.xlim(0, 80)  # Rentang sumbu X
        plt.axhline(y=0, color='black', linewidth=1)  
        # Garis dasar horizontal
        plt.grid(False)  # Tidak ada grid
        plt.tight_layout()
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        produksi_graph = base64.b64encode(img.getvalue()).decode()
        plt.xlabel('Jumlah Produksi (Jmlh)', fontsize=12)
        plt.close()

        result = {
            'finventory_minim': finventory_minim,
            'finventory_sedang': finventory_sedang,
            'finventory_banyak': finventory_banyak,
            'fpermintaan_rendah': fpermintaan_rendah,
            'fpermintaan_sedang': fpermintaan_sedang,
            'fpermintaan_tinggi': fpermintaan_tinggi,
            'prediksi_produksi': prediksi_produksi,
            'inventory_graph': inventory_graph,
            'permintaan_graph': permintaan_graph,
            'produksi_graph': produksi_graph
        }

    return render_template_string(html_template, result=result)

if __name__ == '__main__':
    app.run(debug=True)