import sys
import json
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTableWidget, QTableWidgetItem, QPushButton, 
                             QFileDialog, QTabWidget, QMessageBox, QLineEdit, 
                             QComboBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt

class AHPCalculator:
    @staticmethod
    def calculate_ahp(criteria_matrix, alternative_matrices):
        # Hitung bobot kriteria
        criteria_weights = AHPCalculator.calculate_weights(criteria_matrix)
        
        # Hitung bobot alternatif untuk setiap kriteria
        alternative_weights = []
        for matrix in alternative_matrices:
            alternative_weights.append(AHPCalculator.calculate_weights(matrix))
        
        # Hitung skor akhir
        final_scores = np.zeros(len(alternative_weights[0]))
        for i, crit_weight in enumerate(criteria_weights):
            for j, alt_weight in enumerate(alternative_weights[i]):
                final_scores[j] += crit_weight * alt_weight
        
        return criteria_weights, alternative_weights, final_scores
    
    @staticmethod
    def calculate_weights(matrix):
        # Normalisasi matriks
        normalized_matrix = matrix / matrix.sum(axis=0)
        
        # Hitung rata-rata setiap baris
        weights = normalized_matrix.mean(axis=1)
        
        return weights

class AHPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Kriteria
        criteria_group = QGroupBox("Kriteria")
        criteria_layout = QVBoxLayout()
        
        self.criteria_table = QTableWidget()
        self.criteria_table.setColumnCount(3)
        self.criteria_table.setHorizontalHeaderLabels(["Kriteria 1", "Kriteria 2", "Kriteria 3"])
        self.criteria_table.setRowCount(3)
        self.criteria_table.setItem(0, 0, QTableWidgetItem("1"))
        self.criteria_table.setItem(0, 1, QTableWidgetItem("3"))
        self.criteria_table.setItem(0, 2, QTableWidgetItem("5"))
        self.criteria_table.setItem(1, 0, QTableWidgetItem("1/3"))
        self.criteria_table.setItem(1, 1, QTableWidgetItem("1"))
        self.criteria_table.setItem(1, 2, QTableWidgetItem("3"))
        self.criteria_table.setItem(2, 0, QTableWidgetItem("1/5"))
        self.criteria_table.setItem(2, 1, QTableWidgetItem("1/3"))
        self.criteria_table.setItem(2, 2, QTableWidgetItem("1"))
        
        criteria_layout.addWidget(self.criteria_table)
        criteria_group.setLayout(criteria_layout)
        
        # Alternatif
        alternatives_group = QGroupBox("Alternatif Lokasi")
        alternatives_layout = QVBoxLayout()
        
        self.tab_widget = QTabWidget()
        
        # Alternatif untuk setiap kriteria
        self.alternative_tables = []
        criteria_names = ["Harga", "Aksesibilitas", "Demografi"]
        
        for i in range(3):
            tab = QWidget()
            layout_tab = QVBoxLayout()
            
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Lokasi A", "Lokasi B", "Lokasi C"])
            table.setRowCount(3)
            
            # Isi dengan nilai default
            for row in range(3):
                for col in range(3):
                    if row == col:
                        table.setItem(row, col, QTableWidgetItem("1"))
                    else:
                        table.setItem(row, col, QTableWidgetItem(""))
            
            self.alternative_tables.append(table)
            layout_tab.addWidget(table)
            tab.setLayout(layout_tab)
            self.tab_widget.addTab(tab, criteria_names[i])
        
        alternatives_layout.addWidget(self.tab_widget)
        alternatives_group.setLayout(alternatives_layout)
        
        # Tombol Hitung
        self.calculate_btn = QPushButton("Hitung AHP")
        self.calculate_btn.clicked.connect(self.calculate_ahp)
        
        # Hasil
        self.result_label = QLabel("Hasil akan muncul di sini")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        layout.addWidget(criteria_group)
        layout.addWidget(alternatives_group)
        layout.addWidget(self.calculate_btn)
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
    
    def calculate_ahp(self):
        try:
            # Baca matriks kriteria
            criteria_matrix = np.zeros((3, 3))
            for i in range(3):
                for j in range(3):
                    item = self.criteria_table.item(i, j)
                    if item and item.text():
                        val = item.text()
                        if '/' in val:
                            numerator, denominator = val.split('/')
                            criteria_matrix[i, j] = float(numerator) / float(denominator)
                        else:
                            criteria_matrix[i, j] = float(val)
                    else:
                        criteria_matrix[i, j] = 1.0  # Default jika kosong
            
            # Baca matriks alternatif
            alternative_matrices = []
            for table in self.alternative_tables:
                matrix = np.zeros((3, 3))
                for i in range(3):
                    for j in range(3):
                        item = table.item(i, j)
                        if item and item.text():
                            val = item.text()
                            if '/' in val:
                                numerator, denominator = val.split('/')
                                matrix[i, j] = float(numerator) / float(denominator)
                            else:
                                matrix[i, j] = float(val)
                        else:
                            if i == j:
                                matrix[i, j] = 1.0  # Default diagonal
                            else:
                                # Jika kosong dan bukan diagonal, asumsikan kebalikan dari simetris
                                if j < i and table.item(j, i) and table.item(j, i).text():
                                    sym_val = table.item(j, i).text()
                                    if '/' in sym_val:
                                        numerator, denominator = sym_val.split('/')
                                        matrix[i, j] = float(denominator) / float(numerator)
                                    else:
                                        matrix[i, j] = 1.0 / float(sym_val)
                                else:
                                    matrix[i, j] = 1.0  # Default jika tidak ada nilai
                
                alternative_matrices.append(matrix)
            
            # Hitung AHP
            criteria_weights, alternative_weights, final_scores = AHPCalculator.calculate_ahp(criteria_matrix, alternative_matrices)
            
            # Tampilkan hasil
            result_text = "Hasil Perhitungan AHP:\n\n"
            result_text += "Bobot Kriteria:\n"
            for i, weight in enumerate(criteria_weights):
                result_text += f"- Kriteria {i+1}: {weight:.4f}\n"
            
            result_text += "\nBobot Alternatif per Kriteria:\n"
            for i, weights in enumerate(alternative_weights):
                result_text += f"Kriteria {i+1}:\n"
                for j, weight in enumerate(weights):
                    result_text += f"- Lokasi {chr(65+j)}: {weight:.4f}\n"
            
            result_text += "\nSkor Akhir:\n"
            for i, score in enumerate(final_scores):
                result_text += f"- Lokasi {chr(65+i)}: {score:.4f}\n"
            
            # Tentukan pemenang
            winner_index = np.argmax(final_scores)
            result_text += f"\nLokasi Terbaik: Lokasi {chr(65+winner_index)} dengan skor {final_scores[winner_index]:.4f}"
            
            self.result_label.setText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan dalam perhitungan:\n{str(e)}")

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        about_text = """
        <h2>Sistem Penunjang Keputusan AHP untuk Pemilihan Lokasi Bisnis</h2>
        <p>Aplikasi ini menggunakan metode Analytic Hierarchy Process (AHP) untuk membantu dalam pengambilan keputusan pemilihan lokasi bisnis.</p>
        
        <h3>Cara Penggunaan:</h3>
        <ol>
            <li>Masukkan matriks perbandingan kriteria pada tab AHP</li>
            <li>Masukkan matriks perbandingan alternatif untuk setiap kriteria</li>
            <li>Klik tombol "Hitung AHP" untuk melihat hasil</li>
            <li>Gunakan menu File untuk menyimpan atau membuka proyek</li>
        </ol>
        
        <h3>Tentang AHP:</h3>
        <p>Analytic Hierarchy Process (AHP) adalah metode pengambilan keputusan yang dikembangkan oleh Thomas L. Saaty. Metode ini memecah masalah kompleks menjadi hierarki dan melakukan perbandingan berpasangan untuk menentukan prioritas.</p>
        
        <p><em>Versi 1.0</em></p>
        """
        
        label = QLabel(about_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Penunjang Keputusan AHP - Pemilihan Lokasi Bisnis")
        self.setGeometry(100, 100, 800, 600)
        
        self.current_file = None
        self.initUI()
    
    def initUI(self):
        # Buat menu bar
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu('File')
        
        upload_action = file_menu.addAction('Upload')
        upload_action.triggered.connect(self.open_file)
        
        save_action = file_menu.addAction('Save')
        save_action.triggered.connect(self.save_file)
        
        save_as_action = file_menu.addAction('Save As')
        save_as_action.triggered.connect(self.save_file_as)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Menu Help
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
        # Buat tab utama
        self.tab_widget = QTabWidget()
        
        # Tambahkan tab AHP
        self.ahp_tab = AHPTab()
        self.tab_widget.addTab(self.ahp_tab, "AHP")
        
        # Tambahkan tab About
        self.about_tab = AboutTab()
        self.tab_widget.addTab(self.about_tab, "Tentang")
        
        self.setCentralWidget(self.tab_widget)
    
    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Buka File Proyek", "", "AHP Files (*.ahp);;All Files (*)", options=options)
        
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    data = json.load(file)
                
                # Load criteria matrix
                criteria_matrix = data['criteria_matrix']
                for i in range(3):
                    for j in range(3):
                        item = QTableWidgetItem(str(criteria_matrix[i][j]))
                        self.ahp_tab.criteria_table.setItem(i, j, item)
                
                # Load alternative matrices
                alternative_matrices = data['alternative_matrices']
                for k in range(3):
                    matrix = alternative_matrices[k]
                    table = self.ahp_tab.alternative_tables[k]
                    for i in range(3):
                        for j in range(3):
                            item = QTableWidgetItem(str(matrix[i][j]))
                            table.setItem(i, j, item)
                
                self.current_file = file_name
                QMessageBox.information(self, "Sukses", "Proyek berhasil dimuat!")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal memuat file:\n{str(e)}")
    
    def save_file(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Simpan Proyek", "", "AHP Files (*.ahp);;All Files (*)", options=options)
        
        if file_name:
            if not file_name.endswith('.ahp'):
                file_name += '.ahp'
            self._save_to_file(file_name)
            self.current_file = file_name
    
    def _save_to_file(self, file_name):
        try:
            # Simpan kriteria
            criteria_matrix = []
            for i in range(3):
                row = []
                for j in range(3):
                    item = self.ahp_tab.criteria_table.item(i, j)
                    if item and item.text():
                        val = item.text()
                        if '/' in val:
                            numerator, denominator = val.split('/')
                            row.append(float(numerator) / float(denominator))
                        else:
                            row.append(float(val))
                    else:
                        row.append(1.0 if i == j else 0.0)
                criteria_matrix.append(row)
            
            # Simpan alternatif
            alternative_matrices = []
            for table in self.ahp_tab.alternative_tables:
                matrix = []
                for i in range(3):
                    row = []
                    for j in range(3):
                        item = table.item(i, j)
                        if item and item.text():
                            val = item.text()
                            if '/' in val:
                                numerator, denominator = val.split('/')
                                row.append(float(numerator) / float(denominator))
                            else:
                                row.append(float(val))
                        else:
                            row.append(1.0 if i == j else 0.0)
                    matrix.append(row)
                alternative_matrices.append(matrix)
            
            data = {
                'criteria_matrix': criteria_matrix,
                'alternative_matrices': alternative_matrices
            }
            
            with open(file_name, 'w') as file:
                json.dump(data, file)
            
            QMessageBox.information(self, "Sukses", "Proyek berhasil disimpan!")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan file:\n{str(e)}")
    
    def show_about(self):
        self.tab_widget.setCurrentWidget(self.about_tab)
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Konfirmasi',
            "Apakah Anda yakin ingin keluar?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())