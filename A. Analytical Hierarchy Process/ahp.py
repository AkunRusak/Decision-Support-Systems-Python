import sys
import json
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTableWidget, QTableWidgetItem, QPushButton, 
                             QFileDialog, QMessageBox, QTabWidget, QLineEdit, 
                             QComboBox, QSpinBox, QTextEdit)
from PyQt5.QtCore import Qt

class AHPCalculator:
    @staticmethod
    def calculate_ahp(criteria_matrix, alternative_matrices):
        # Hitung bobot kriteria
        criteria_weights = AHPCalculator.calculate_weights(criteria_matrix)
        
        # Hitung bobot untuk setiap alternatif pada setiap kriteria
        alternative_weights = []
        for matrix in alternative_matrices:
            weights = AHPCalculator.calculate_weights(matrix)
            alternative_weights.append(weights)
        
        # Hitung skor akhir
        final_scores = np.zeros(len(alternative_weights[0]))
        for i, crit_weight in enumerate(criteria_weights):
            for j, alt_weight in enumerate(alternative_weights[i]):
                final_scores[j] += crit_weight * alt_weight
        
        return criteria_weights, alternative_weights, final_scores
    
    @staticmethod
    def calculate_weights(matrix):
        # Normalisasi matriks
        normalized = matrix / matrix.sum(axis=0)
        
        # Hitung rata-rata setiap baris
        weights = normalized.mean(axis=1)
        
        # Hitung consistency ratio
        n = matrix.shape[0]
        lambda_max = (matrix @ weights / weights).mean()
        ci = (lambda_max - n) / (n - 1)
        ri = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        cr = ci / ri.get(n, 1.49)
        
        return weights, cr

class CriteriaTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        
        self.criteria_count = 0
        self.alternative_count = 0
        
        # Input jumlah kriteria dan alternatif
        self.setup_input_section()
        
        # Tabel perbandingan kriteria
        self.criteria_table = QTableWidget()
        self.layout.addWidget(self.criteria_table)
        
        # Tombol hitung
        self.calculate_btn = QPushButton("Hitung Bobot Kriteria")
        self.calculate_btn.clicked.connect(self.calculate_criteria_weights)
        self.layout.addWidget(self.calculate_btn)
        
        # Hasil perhitungan
        self.results_label = QLabel("")
        self.layout.addWidget(self.results_label)
        
        self.setLayout(self.layout)
    
    def setup_input_section(self):
        input_layout = QHBoxLayout()
        
        # Input jumlah kriteria
        criteria_layout = QVBoxLayout()
        criteria_layout.addWidget(QLabel("Jumlah Kriteria:"))
        self.criteria_spin = QSpinBox()
        self.criteria_spin.setMinimum(2)
        self.criteria_spin.setMaximum(10)
        self.criteria_spin.valueChanged.connect(self.update_criteria_count)
        criteria_layout.addWidget(self.criteria_spin)
        input_layout.addLayout(criteria_layout)
        
        # Input jumlah alternatif
        alternative_layout = QVBoxLayout()
        alternative_layout.addWidget(QLabel("Jumlah Alternatif:"))
        self.alternative_spin = QSpinBox()
        self.alternative_spin.setMinimum(2)
        self.alternative_spin.setMaximum(10)
        self.alternative_spin.valueChanged.connect(self.update_alternative_count)
        alternative_layout.addWidget(self.alternative_spin)
        input_layout.addLayout(alternative_layout)
        
        self.layout.addLayout(input_layout)
    
    def update_criteria_count(self):
        self.criteria_count = self.criteria_spin.value()
        self.setup_criteria_table()
        self.parent.update_tabs()
    
    def update_alternative_count(self):
        self.alternative_count = self.alternative_spin.value()
        self.parent.update_tabs()
    
    def setup_criteria_table(self):
        self.criteria_table.clear()
        self.criteria_table.setRowCount(self.criteria_count)
        self.criteria_table.setColumnCount(self.criteria_count + 1)
        
        # Set header
        headers = ["Kriteria"] + [f"Kriteria {i+1}" for i in range(self.criteria_count)]
        self.criteria_table.setHorizontalHeaderLabels(headers)
        
        # Set kriteria names
        for i in range(self.criteria_count):
            item = QTableWidgetItem(f"Kriteria {i+1}")
            self.criteria_table.setItem(i, 0, item)
            
            # Set diagonal to 1
            diag_item = QTableWidgetItem("1")
            diag_item.setFlags(Qt.ItemIsEnabled)
            self.criteria_table.setItem(i, i+1, diag_item)
            
            # Setup other cells
            for j in range(self.criteria_count):
                if i != j:
                    combo = QComboBox()
                    values = ["1/9", "1/8", "1/7", "1/6", "1/5", "1/4", "1/3", "1/2", "1", 
                             "2", "3", "4", "5", "6", "7", "8", "9"]
                    combo.addItems(values)
                    combo.setCurrentIndex(8)  # Default to 1
                    self.criteria_table.setCellWidget(i, j+1, combo)
    
    def calculate_criteria_weights(self):
        try:
            # Build matrix
            matrix = np.ones((self.criteria_count, self.criteria_count))
            
            for i in range(self.criteria_count):
                for j in range(self.criteria_count):
                    if i == j:
                        continue
                    elif i < j:
                        # Get value from combo box
                        combo = self.criteria_table.cellWidget(i, j+1)
                        value_str = combo.currentText()
                        
                        if '/' in value_str:
                            num, denom = map(float, value_str.split('/'))
                            value = num / denom
                        else:
                            value = float(value_str)
                            
                        matrix[i, j] = value
                        matrix[j, i] = 1 / value
            
            # Calculate weights
            weights, cr = AHPCalculator.calculate_weights(matrix)
            
            # Display results
            result_text = "Bobot Kriteria:\n"
            for i, weight in enumerate(weights):
                result_text += f"Kriteria {i+1}: {weight:.4f}\n"
            
            result_text += f"\nConsistency Ratio: {cr:.4f}\n"
            if cr > 0.1:
                result_text += "PERINGATAN: Nilai CR > 0.1, perbandingan mungkin tidak konsisten!"
            else:
                result_text += "Nilai CR dapat diterima (≤ 0.1)"
            
            self.results_label.setText(result_text)
            
            # Save to parent
            self.parent.criteria_matrix = matrix
            self.parent.criteria_weights = weights
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan dalam perhitungan: {str(e)}")

class AlternativeTab(QWidget):
    def __init__(self, crit_index, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.crit_index = crit_index
        self.layout = QVBoxLayout()
        
        self.label = QLabel(f"Perbandingan Alternatif untuk Kriteria {crit_index+1}")
        self.layout.addWidget(self.label)
        
        self.alternative_table = QTableWidget()
        self.setup_alternative_table()
        self.layout.addWidget(self.alternative_table)
        
        # Tombol hitung
        self.calculate_btn = QPushButton(f"Hitung Bobot Alternatif untuk Kriteria {crit_index+1}")
        self.calculate_btn.clicked.connect(self.calculate_alternative_weights)
        self.layout.addWidget(self.calculate_btn)
        
        # Hasil perhitungan
        self.results_label = QLabel("")
        self.layout.addWidget(self.results_label)
        
        self.setLayout(self.layout)
    
    def setup_alternative_table(self):
        alt_count = self.parent.criteria_tab.alternative_count
        self.alternative_table.clear()
        self.alternative_table.setRowCount(alt_count)
        self.alternative_table.setColumnCount(alt_count + 1)
        
        # Set header
        headers = ["Alternatif"] + [f"Alt {i+1}" for i in range(alt_count)]
        self.alternative_table.setHorizontalHeaderLabels(headers)
        
        # Set alternatif names
        for i in range(alt_count):
            item = QTableWidgetItem(f"Alternatif {i+1}")
            self.alternative_table.setItem(i, 0, item)
            
            # Set diagonal to 1
            diag_item = QTableWidgetItem("1")
            diag_item.setFlags(Qt.ItemIsEnabled)
            self.alternative_table.setItem(i, i+1, diag_item)
            
            # Setup other cells
            for j in range(alt_count):
                if i != j:
                    combo = QComboBox()
                    values = ["1/9", "1/8", "1/7", "1/6", "1/5", "1/4", "1/3", "1/2", "1", 
                             "2", "3", "4", "5", "6", "7", "8", "9"]
                    combo.addItems(values)
                    combo.setCurrentIndex(8)  # Default to 1
                    self.alternative_table.setCellWidget(i, j+1, combo)
    
    def calculate_alternative_weights(self):
        try:
            alt_count = self.parent.criteria_tab.alternative_count
            
            # Build matrix
            matrix = np.ones((alt_count, alt_count))
            
            for i in range(alt_count):
                for j in range(alt_count):
                    if i == j:
                        continue
                    elif i < j:
                        # Get value from combo box
                        combo = self.alternative_table.cellWidget(i, j+1)
                        value_str = combo.currentText()
                        
                        if '/' in value_str:
                            num, denom = map(float, value_str.split('/'))
                            value = num / denom
                        else:
                            value = float(value_str)
                            
                        matrix[i, j] = value
                        matrix[j, i] = 1 / value
            
            # Calculate weights
            weights, cr = AHPCalculator.calculate_weights(matrix)
            
            # Display results
            result_text = f"Bobot Alternatif untuk Kriteria {self.crit_index+1}:\n"
            for i, weight in enumerate(weights):
                result_text += f"Alternatif {i+1}: {weight:.4f}\n"
            
            result_text += f"\nConsistency Ratio: {cr:.4f}\n"
            if cr > 0.1:
                result_text += "PERINGATAN: Nilai CR > 0.1, perbandingan mungkin tidak konsisten!"
            else:
                result_text += "Nilai CR dapat diterima (≤ 0.1)"
            
            self.results_label.setText(result_text)
            
            # Save to parent
            if not hasattr(self.parent, 'alternative_matrices'):
                self.parent.alternative_matrices = []
            if len(self.parent.alternative_matrices) <= self.crit_index:
                self.parent.alternative_matrices.append(matrix)
            else:
                self.parent.alternative_matrices[self.crit_index] = matrix
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan dalam perhitungan: {str(e)}")

class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Hasil Perhitungan AHP")
        self.layout.addWidget(self.label)
        
        # Tombol hitung akhir
        self.final_calculate_btn = QPushButton("Hitung Skor Akhir")
        self.final_calculate_btn.clicked.connect(self.calculate_final_scores)
        self.layout.addWidget(self.final_calculate_btn)
        
        # Area hasil
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.layout.addWidget(self.results_text)
        
        self.setLayout(self.layout)
    
    def calculate_final_scores(self):
        try:
            if not hasattr(self.parent, 'criteria_weights') or not hasattr(self.parent, 'alternative_matrices'):
                QMessageBox.warning(self, "Peringatan", "Harap hitung bobot kriteria dan alternatif terlebih dahulu!")
                return
            
            # Get all alternative matrices
            alternative_matrices = []
            for i in range(len(self.parent.alternative_matrices)):
                if i < len(self.parent.alternative_matrices):
                    alternative_matrices.append(self.parent.alternative_matrices[i])
                else:
                    # If not calculated, create identity matrix
                    alt_count = self.parent.criteria_tab.alternative_count
                    alternative_matrices.append(np.ones((alt_count, alt_count)))
            
            # Calculate final scores
            criteria_weights = self.parent.criteria_weights
            alternative_weights = []
            for matrix in alternative_matrices:
                weights, _ = AHPCalculator.calculate_weights(matrix)
                alternative_weights.append(weights)
            
            final_scores = np.zeros(len(alternative_weights[0]))
            for i, crit_weight in enumerate(criteria_weights):
                for j, alt_weight in enumerate(alternative_weights[i]):
                    final_scores[j] += crit_weight * alt_weight
            
            # Display results
            result_text = "HASIL AKHIR PERHITUNGAN AHP\n\n"
            result_text += "Bobot Kriteria:\n"
            for i, weight in enumerate(criteria_weights):
                result_text += f"- Kriteria {i+1}: {weight:.4f}\n"
            
            result_text += "\nBobot Alternatif:\n"
            for crit_idx, weights in enumerate(alternative_weights):
                result_text += f"Untuk Kriteria {crit_idx+1}:\n"
                for alt_idx, weight in enumerate(weights):
                    result_text += f"  - Alternatif {alt_idx+1}: {weight:.4f}\n"
            
            result_text += "\nSkor Akhir Alternatif:\n"
            sorted_indices = np.argsort(final_scores)[::-1]
            for idx in sorted_indices:
                result_text += f"Alternatif {idx+1}: {final_scores[idx]:.4f}\n"
            
            result_text += "\nREKOMENDASI:\n"
            best_alt = np.argmax(final_scores) + 1
            result_text += f"Alternatif terbaik adalah Alternatif {best_alt} dengan skor {final_scores[best_alt-1]:.4f}"
            
            self.results_text.setPlainText(result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan dalam perhitungan akhir: {str(e)}")

class AHPMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Penunjang Keputusan - Metode AHP")
        self.setGeometry(100, 100, 800, 600)
        
        # Data storage
        self.criteria_matrix = None
        self.criteria_weights = None
        self.alternative_matrices = []
        
        # Setup UI
        self.init_ui()
        
        # Current file
        self.current_file = None
    
    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add criteria tab
        self.criteria_tab = CriteriaTab(self)
        self.tab_widget.addTab(self.criteria_tab, "Kriteria")
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Siap")
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        upload_action = file_menu.addAction("Upload Data")
        upload_action.triggered.connect(self.upload_data)
        
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.save_data)
        
        save_as_action = file_menu.addAction("Save As")
        save_as_action.triggered.connect(self.save_as_data)
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = help_menu.addAction("Tentang AHP")
        about_action.triggered.connect(self.show_about)
        
        guide_action = help_menu.addAction("Panduan Penggunaan")
        guide_action.triggered.connect(self.show_guide)
    
    def update_tabs(self):
        # Remove all tabs except criteria tab
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(1)
        
        # Add alternative tabs
        crit_count = self.criteria_tab.criteria_count
        for i in range(crit_count):
            alt_tab = AlternativeTab(i, self)
            self.tab_widget.addTab(alt_tab, f"Alternatif Kriteria {i+1}")
        
        # Add results tab
        results_tab = ResultsTab(self)
        self.tab_widget.addTab(results_tab, "Hasil")
    
    def upload_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload Data AHP", "", 
                                                  "JSON Files (*.json);;All Files (*)", 
                                                  options=options)
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    data = json.load(f)
                
                # Set criteria count
                self.criteria_tab.criteria_spin.setValue(data['criteria_count'])
                self.criteria_tab.alternative_spin.setValue(data['alternative_count'])
                
                # Set criteria matrix
                for i in range(data['criteria_count']):
                    for j in range(data['criteria_count']):
                        if i != j and i < j:
                            combo = self.criteria_tab.criteria_table.cellWidget(i, j+1)
                            value = data['criteria_matrix'][i][j]
                            if value < 1:
                                text = f"1/{int(1/value)}"
                            else:
                                text = str(int(value))
                            index = combo.findText(text)
                            if index >= 0:
                                combo.setCurrentIndex(index)
                
                # Set alternative matrices
                for crit_idx, matrix_data in enumerate(data['alternative_matrices']):
                    if crit_idx < self.tab_widget.count() - 2:  # -2 for criteria and results tabs
                        alt_tab = self.tab_widget.widget(crit_idx + 1)  # +1 for criteria tab
                        for i in range(data['alternative_count']):
                            for j in range(data['alternative_count']):
                                if i != j and i < j:
                                    combo = alt_tab.alternative_table.cellWidget(i, j+1)
                                    value = matrix_data[i][j]
                                    if value < 1:
                                        text = f"1/{int(1/value)}"
                                    else:
                                        text = str(int(value))
                                    index = combo.findText(text)
                                    if index >= 0:
                                        combo.setCurrentIndex(index)
                
                self.current_file = file_name
                self.status_bar.showMessage(f"Data berhasil diupload dari {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mengupload data: {str(e)}")
    
    def save_data(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_data()
    
    def save_as_data(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Simpan Data AHP", "", 
                                                  "JSON Files (*.json);;All Files (*)", 
                                                  options=options)
        if file_name:
            if not file_name.endswith('.json'):
                file_name += '.json'
            self._save_to_file(file_name)
            self.current_file = file_name
    
    def _save_to_file(self, file_name):
        try:
            # Prepare criteria matrix
            crit_count = self.criteria_tab.criteria_count
            alt_count = self.criteria_tab.alternative_count
            criteria_matrix = np.ones((crit_count, crit_count))
            
            for i in range(crit_count):
                for j in range(crit_count):
                    if i == j:
                        continue
                    elif i < j:
                        combo = self.criteria_tab.criteria_table.cellWidget(i, j+1)
                        value_str = combo.currentText()
                        
                        if '/' in value_str:
                            num, denom = map(float, value_str.split('/'))
                            value = num / denom
                        else:
                            value = float(value_str)
                            
                        criteria_matrix[i, j] = value
                        criteria_matrix[j, i] = 1 / value
            
            # Prepare alternative matrices
            alternative_matrices = []
            for crit_idx in range(crit_count):
                if crit_idx < self.tab_widget.count() - 2:  # -2 for criteria and results tabs
                    alt_tab = self.tab_widget.widget(crit_idx + 1)  # +1 for criteria tab
                    matrix = np.ones((alt_count, alt_count))
                    
                    for i in range(alt_count):
                        for j in range(alt_count):
                            if i == j:
                                continue
                            elif i < j:
                                combo = alt_tab.alternative_table.cellWidget(i, j+1)
                                value_str = combo.currentText()
                                
                                if '/' in value_str:
                                    num, denom = map(float, value_str.split('/'))
                                    value = num / denom
                                else:
                                    value = float(value_str)
                                    
                                matrix[i, j] = value
                                matrix[j, i] = 1 / value
                    
                    alternative_matrices.append(matrix.tolist())
            
            # Create data dictionary
            data = {
                'criteria_count': crit_count,
                'alternative_count': alt_count,
                'criteria_matrix': criteria_matrix.tolist(),
                'alternative_matrices': alternative_matrices
            }
            
            # Save to file
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=4)
            
            self.status_bar.showMessage(f"Data berhasil disimpan ke {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {str(e)}")
    
    def show_about(self):
        about_text = """
        <h2>Sistem Penunjang Keputusan dengan AHP</h2>
        <p>Aplikasi ini mengimplementasikan metode Analytic Hierarchy Process (AHP) 
        untuk membantu pengambilan keputusan multi-kriteria.</p>
        <p>AHP dikembangkan oleh Thomas L. Saaty pada tahun 1970-an dan merupakan 
        metode yang kuat untuk mengambil keputusan kompleks.</p>
        <p>Versi: 1.0</p>
        """
        QMessageBox.about(self, "Tentang AHP", about_text)
    
    def show_guide(self):
        guide_text = """
        <h2>Panduan Penggunaan AHP</h2>
        <ol>
            <li><b>Input Kriteria:</b>
                <ul>
                    <li>Masukkan jumlah kriteria dan alternatif</li>
                    <li>Isi matriks perbandingan berpasangan untuk kriteria</li>
                    <li>Hitung bobot kriteria</li>
                </ul>
            </li>
            <li><b>Input Alternatif:</b>
                <ul>
                    <li>Untuk setiap kriteria, isi matriks perbandingan alternatif</li>
                    <li>Hitung bobot alternatif untuk setiap kriteria</li>
                </ul>
            </li>
            <li><b>Hasil:</b>
                <ul>
                    <li>Lihat tab Hasil untuk perhitungan akhir</li>
                    <li>Hitung skor akhir untuk mendapatkan rekomendasi</li>
                </ul>
            </li>
        </ol>
        <p><b>Tips:</b></p>
        <ul>
            <li>Consistency Ratio (CR) harus ≤ 0.1 untuk hasil yang konsisten</li>
            <li>Gunakan skala 1-9 untuk perbandingan (1 = sama penting, 9 = jauh lebih penting)</li>
            <li>Anda dapat menyimpan dan memuat data untuk digunakan kembali</li>
        </ul>
        """
        msg = QMessageBox()
        msg.setWindowTitle("Panduan Penggunaan")
        msg.setTextFormat(Qt.RichText)
        msg.setText(guide_text)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AHPMainWindow()
    window.show()
    sys.exit(app.exec_())