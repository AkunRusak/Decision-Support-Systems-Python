import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QLineEdit, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

class AHPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.df_machines = None
        self.df_ahp = None
    
    def initUI(self):
        self.setWindowTitle("Analytical Hierarchy Process - Pemilihan Mesin Produksi")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Masukkan Nama Mesin:")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        self.nama_mesin_input = QLineEdit()
        self.nama_mesin_input.setPlaceholderText("Masukkan nama mesin, pisahkan dengan koma")
        layout.addWidget(self.nama_mesin_input)
        
        self.label_kriteria = QLabel("Masukkan Kriteria:")
        layout.addWidget(self.label_kriteria, alignment=Qt.AlignCenter)
        
        self.kriteria_input = QLineEdit()
        self.kriteria_input.setPlaceholderText("Masukkan kriteria, pisahkan dengan koma")
        layout.addWidget(self.kriteria_input)
        
        self.label_bobot = QLabel("Masukkan Bobot:")
        layout.addWidget(self.label_bobot, alignment=Qt.AlignCenter)
        
        self.bobot_input = QLineEdit()
        self.bobot_input.setPlaceholderText("Masukkan bobot, pisahkan dengan koma")
        layout.addWidget(self.bobot_input)
        
        self.btn_upload = QPushButton("Upload File Excel")
        self.btn_upload.clicked.connect(self.upload_excel)
        layout.addWidget(self.btn_upload)
        
        self.btn_proses = QPushButton("Proses AHP")
        self.btn_proses.clicked.connect(self.proses_ahp)
        layout.addWidget(self.btn_proses)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_form)
        layout.addWidget(self.btn_reset)
        
        self.label_hasil = QLabel("Hasil Perhitungan AHP:")
        layout.addWidget(self.label_hasil, alignment=Qt.AlignCenter)
        
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        self.btn_simpan = QPushButton("Simpan ke Excel")
        self.btn_simpan.clicked.connect(self.simpan_excel)
        layout.addWidget(self.btn_simpan)
        
        self.setLayout(layout)
    
    def upload_excel(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih File Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_name:
            self.df_machines = pd.read_excel(file_name)
            self.nama_mesin_input.setText(", ".join(self.df_machines.iloc[:, 0]))
            self.kriteria_input.setText(", ".join(self.df_machines.columns[1:]))
            QMessageBox.information(self, "Sukses", "File Excel berhasil diunggah!")
    
    def proses_ahp(self):
        if self.df_ahp is not None:
            QMessageBox.warning(self, "Peringatan", "AHP sudah diproses. Gunakan tombol Reset untuk memulai ulang.")
            return
        
        kriteria = self.kriteria_input.text().split(',')
        mesin = self.nama_mesin_input.text().split(',')
        
        if not kriteria or len(kriteria) < 2 or not mesin or len(mesin) < 2:
            QMessageBox.warning(self, "Peringatan", "Masukkan minimal dua kriteria dan dua mesin.")
            return
        
        n = len(kriteria)
        matrix = np.ones((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j] = round(np.random.uniform(1, 9), 2)
                matrix[j][i] = round(1 / matrix[i][j], 2)
        
        eig_values, eig_vectors = np.linalg.eig(matrix)
        max_idx = np.argmax(eig_values.real)
        priority_vector = eig_vectors[:, max_idx].real
        priority_vector = priority_vector / sum(priority_vector)
        
        df = pd.DataFrame({'Mesin': mesin, 'Bobot': priority_vector})
        df = df.sort_values(by='Bobot', ascending=False).reset_index(drop=True)
        df.insert(0, 'Ranking', range(1, len(df) + 1))
        
        self.df_ahp = df  # Simpan hasil agar tidak dihitung berulang
        self.tampilkan_hasil(df)
    
    def tampilkan_hasil(self, df):
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        
        for row_idx, row_data in df.iterrows():
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    def simpan_excel(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Simpan File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if file_name and self.df_ahp is not None:
            self.df_ahp.to_excel(file_name, index=False)
            QMessageBox.information(self, "Sukses", "Hasil AHP berhasil disimpan!")
    
    def reset_form(self):
        self.nama_mesin_input.clear()
        self.kriteria_input.clear()
        self.bobot_input.clear()
        self.df_ahp = None
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        QMessageBox.information(self, "Reset", "Form dan hasil telah direset.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AHPApp()
    window.show()
    sys.exit(app.exec_())