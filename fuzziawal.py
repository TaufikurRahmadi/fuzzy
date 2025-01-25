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
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        form {
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            color: #555;
        }
        input {
            width: calc(100% - 22px);
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            display: block;
            margin: 0 auto;
        }
        button:hover {
            background-color: #45a049;
        }
        .results {
            margin-top: 20px;
        }
        .results h2 {
            color: #333;
        }
        .results p {
            background: #f9f9f9;
            padding: 10px;
            border-left: 4px solid #4CAF50;
            margin: 10px 0;
            color: #555;
        }
        .graphs {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .graphs img {
            max-width: 100%;
            height: auto;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PERAMALAN PRODUKSI</h1>
        <form method="post">
            <label for="j_inventory">Jumlah STOK:</label><br>
            <input type="number" id="j_inventory" name="j_inventory" required value="{{ request.form.get('j_inventory', '') }}"><br><br>

            <label for="j_permintaan">Jumlah REQ:</label><br>
            <input type="number" id="j_permintaan" name="j_permintaan" required value="{{ request.form.get('j_permintaan', '') }}"><br><br>

            <button type="submit">Submit</button>
        </form>

        {% if result %}
            <div class="results">
                <h2>Results</h2>
                <p>Fuzzy STOK Minim: {{ result['finventory_minim'] }} <br>
                Fuzzy STOK Sedang: {{ result['finventory_sedang'] }} <br>
                Fuzzy STOK Banyak: {{ result['finventory_banyak'] }}</p>

                <p>Fuzzy REQ Rendah: {{ result['fpermintaan_rendah'] }}<br>
                Fuzzy REQ Sedang: {{ result['fpermintaan_sedang'] }}<br>
                Fuzzy REQ Tinggi: {{ result['fpermintaan_tinggi'] }}</p>

                <p>Prediksi Jumlah Produksi: {{ result['prediksi_produksi'] }}</p>
            </div>

            <div class="graphs">
                <h2>CHART</h2>
                <img src="data:image/png;base64,{{ result['inventory_graph'] }}" alt="Inventory Graph"><br>
                <img src="data:image/png;base64,{{ result['permintaan_graph'] }}" alt="Permintaan Graph">
                <img src="data:image/png;base64,{{ result['produksi_graph'] }}" alt="Produksi Graph">
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def fuzzy_logic():
    result = None
    if request.method == 'POST':
        j_inventory = int(request.form['j_inventory'])
        j_permintaan = int(request.form['j_permintaan'])

        # Fuzzifikasi Inventory
        if j_inventory >= 0 and j_inventory <= 30:
            finventory_minim = 1
            finventory_sedang = 0
            finventory_banyak = 0
        elif j_inventory >= 31 and j_inventory <= 35:
            finventory_minim = (40 - j_inventory) / (40 - 30)
            finventory_sedang = 0
            finventory_banyak = 0
        elif j_inventory >= 35 and j_inventory <= 40:
            finventory_minim = (40 - j_inventory) / (40 - 30)
            finventory_sedang = (j_inventory - 35) / (40 - 35)
            finventory_banyak = 0
        elif j_inventory >= 40 and j_inventory <= 45:
            finventory_minim = 0
            finventory_sedang = (45 - j_inventory) / (45 - 40)
            finventory_banyak = (j_inventory - 40) / (45 - 40)
        else:
            finventory_minim = 0
            finventory_sedang = 0
            finventory_banyak = 1

        # Fuzzifikasi Permintaan
        if j_permintaan >= 0 and j_permintaan <= 10:
            fpermintaan_rendah = 1
            fpermintaan_sedang = 0
            fpermintaan_tinggi = 0
        elif j_permintaan >= 10 and j_permintaan <= 20:
            fpermintaan_rendah = (30 - j_permintaan) / (30 - 10)
            fpermintaan_sedang = (j_permintaan - 10) / (20 - 10)
            fpermintaan_tinggi = 0
        elif j_permintaan >= 20 and j_permintaan <= 30:
            fpermintaan_rendah = (30 - j_permintaan) / (30 - 10)
            fpermintaan_sedang = (40 - j_permintaan) / (40 - 20)
            fpermintaan_tinggi = (j_permintaan - 20) / (40 - 20)
        elif j_permintaan >= 30 and j_permintaan <= 40:
            fpermintaan_rendah = 0
            fpermintaan_sedang = (40 - j_permintaan) / (40 - 20)
            fpermintaan_tinggi = (j_permintaan - 20) / (40 - 20)
        else:
            fpermintaan_rendah = 0
            fpermintaan_sedang = 0
            fpermintaan_tinggi = 1

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
        def generate_graph_inventory():
            inventory_values = np.arange(0, 80, 1)

            def inventory_minim(x):
                if x <= 30:
                    return 1
                elif 30 < x <= 40:
                    return (40 - x) / 10
                else:
                    return 0

            def inventory_sedang(x):
                if 35 <= x <= 40:
                    return (x - 35) / 5
                elif 40 < x <= 45:
                    return (45 - x) / 5
                else:
                    return 0

            def inventory_banyak(x):
                if 40 <= x <= 45:
                    return (x - 40) / 5
                elif x > 45:
                    return 1
                else:
                    return 0

            minim_values = [inventory_minim(x) for x in inventory_values]
            sedang_values = [inventory_sedang(x) for x in inventory_values]
            banyak_values = [inventory_banyak(x) for x in inventory_values]

            plt.figure(figsize=(8, 6))
            plt.plot(inventory_values, minim_values, label='Minim', color='blue')
            plt.plot(inventory_values, sedang_values, label='Sedang', color='green')
            plt.plot(inventory_values, banyak_values, label='Banyak', color='red')

            # Tambahkan garis horizontal untuk nilai keanggotaan fuzzy
            plt.axhline(finventory_minim, color='blue', linestyle='--', label=f'Minim: {finventory_minim:.2f}')
            plt.axhline(finventory_sedang, color='green', linestyle='--', label=f'Sedang: {finventory_sedang:.2f}')
            plt.axhline(finventory_banyak, color='red', linestyle='--', label=f'Banyak: {finventory_banyak:.2f}')
            plt.axvline(j_inventory, color='black', linestyle='--', label=f'Banyak: {j_inventory:.2f}')

            plt.title('Fuzzy Membership Function (STOK)')
            plt.xlabel('Jumlah stok')
            plt.ylabel('Keanggotaan')
            plt.legend()
            plt.grid()
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            return graph_url


        def generate_graph_permintaan():
            permintaan_values = np.arange(0, 80, 1)

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

            minim_values = [permintaan_minim(x) for x in permintaan_values]
            sedang_values = [permintaan_sedang(x) for x in permintaan_values]
            banyak_values = [permintaan_banyak(x) for x in permintaan_values]

            plt.figure(figsize=(8, 6))
            plt.plot(permintaan_values, minim_values, label='Minim', color='blue')
            plt.plot(permintaan_values, sedang_values, label='Sedang', color='green')
            plt.plot(permintaan_values, banyak_values, label='Banyak', color='red')

            # Tambahkan garis horizontal untuk menunjukkan nilai keanggotaan
            plt.axhline(fpermintaan_rendah, color='blue', linestyle='--', label=f'Rendah: {fpermintaan_rendah:.2f}')
            plt.axhline(fpermintaan_sedang, color='green', linestyle='--', label=f'Sedang: {fpermintaan_sedang:.2f}')
            plt.axhline(fpermintaan_tinggi, color='red', linestyle='--', label=f'Tinggi: {fpermintaan_tinggi:.2f}')
            plt.axvline(j_permintaan, color='yellow', linestyle='--', label=f'Tinggi: {j_permintaan:.2f}')

            plt.title('Fuzzy Membership Function (REQ)')
            plt.xlabel('Jumlah req')
            plt.ylabel('Keanggotaan')
            plt.legend()
            plt.grid()
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            return graph_url

        inventory_graph = generate_graph_inventory()
        permintaan_graph = generate_graph_permintaan()

        produksi = np.array([0, 10, 25, 40])
        keanggotaan = np.array([fproduksi_tidak, fproduksi_kecil, fproduksi_sedang, fproduksi_besar])

        midpoint = prediksi_produksi

        plt.figure(figsize=(8, 4))

        for i, p in enumerate(produksi):
            plt.bar(p, keanggotaan[i], width=5, color='black')

        plt.hlines(y=1, xmin=0, xmax=80, color='black', linewidth=2)

        for i, p in enumerate(produksi):
            plt.text(p, keanggotaan[i] + 0.05, ['No Produksi', 'Kecil', 'Sedang', 'Besar'][i],
                     ha='center', fontsize=10, color='black')

        for i, p in enumerate(produksi):
            plt.text(p, -0.15, f"{keanggotaan[i]:.2f}", ha='center', fontsize=10, color='black')



        plt.axvline(x=midpoint, color='orange', linestyle='--', label='Prediksi Produksi', linewidth=2)
        plt.text(midpoint, 1.1, f'Prediksi: {midpoint:.2f}', ha='center', fontsize=10, color='orange')

        plt.xticks([])
        plt.yticks(np.arange(0, 1.2, 0.2), labels=['0', '0.2', '0.4', '0.6', '0.8', '1'], fontsize=10)
        plt.ylabel('μ(Jumlah Produksi)', fontsize=12)
        plt.title('Fungsi Keanggotaan Produksi', fontsize=14)
        plt.ylim(0, 1.2)
        plt.xlim(0, 80)
        plt.axhline(y=0, color='black', linewidth=1)
        plt.grid(False)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        produksi_graph = base64.b64encode(img.getvalue()).decode()
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
