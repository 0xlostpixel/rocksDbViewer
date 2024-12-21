import sys
import os
import subprocess
import re
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QTextEdit, 
                           QWidget, QFileDialog, QStatusBar, QComboBox,
                           QCheckBox, QListWidget, QSplitter, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

class RocksDBGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.version = "1.0.5"
        self.build_time = "2024-12-21 06:39:03"
        self.ldb_command = self.find_ldb_command()
        self.initUI()
        

        if not self.ldb_command:
            QMessageBox.critical(
                self,
                "Error - Command Not Found",
                "Could not find 'rocksdb_ldb' or 'ldb' command.\n\n"
                "Please make sure RocksDB tools are installed and accessible in your PATH.\n\n"
                "Installation instructions:\n"
                "- Homebrew: brew install rocksdb\n"
                "- Manual: Build RocksDB from source and ensure tools are in PATH",
                QMessageBox.Ok
            )

    def find_ldb_command(self):
        """check system LDB command"""
        commands = ['rocksdb_ldb', 'ldb']
        for cmd in commands:
            if shutil.which(cmd):
                return cmd
        return None

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Select RocksDB Directory')
        if path:
            self.path_input.setText(path)
            self.status_bar.showMessage(f'Selected path: {path}')

    def clear_results(self):
        self.key_list.clear()
        self.value_text.clear()
        self.status_bar.showMessage('Results cleared')

    def on_command_changed(self, command):
        is_get = command == 'get'
        is_put = command == 'put'
        is_delete = command == 'delete'
        
        self.key_input.setEnabled(is_get or is_put)
        self.value_input.setEnabled(is_put)
        self.regex_checkbox.setEnabled(is_get)
        
        if not is_get:
            self.regex_checkbox.setChecked(False)
        if not is_put:
            self.value_input.clear()
        if not (is_get or is_put):
            self.key_input.clear()

    def initUI(self):
        self.setWindowTitle(f'RocksDB LDB Viewer v{self.version}')
        self.setGeometry(300, 300, 1000, 700)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        
        version_label = QLabel(f"Version: {self.version} (Build: {self.build_time})")
        version_label.setAlignment(Qt.AlignRight)
        version_label.setMaximumHeight(20)
        version_label.setStyleSheet("color: gray; font-size: 8pt;")
        main_layout.addWidget(version_label)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        path_label = QLabel('RocksDB Path:')
        self.path_input = QLineEdit()
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_path)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        
        main_layout.addLayout(path_layout)

        command_layout = QHBoxLayout()
        command_layout.setSpacing(5)
        

        self.command_combo = QComboBox()
        self.command_combo.addItems(['scan', 'get', 'put', 'delete'])
        self.command_combo.currentTextChanged.connect(self.on_command_changed)
        command_layout.addWidget(QLabel('Command:'))
        command_layout.addWidget(self.command_combo)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText('Enter key or regex pattern')
        self.key_input.setEnabled(False)
        command_layout.addWidget(QLabel('Key:'))
        command_layout.addWidget(self.key_input)
        
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText('Enter value for put command')
        self.value_input.setEnabled(False)
        command_layout.addWidget(QLabel('Value:'))
        command_layout.addWidget(self.value_input)
        
        self.regex_checkbox = QCheckBox('Use Regex')
        self.regex_checkbox.setEnabled(False)
        command_layout.addWidget(self.regex_checkbox)
        
        main_layout.addLayout(command_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.run_button = QPushButton('Run')
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #8A2BE2;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #9932CC;
            }
        """)
        self.run_button.clicked.connect(self.run_rocksdb_ldb)
        
        clear_button = QPushButton('Clear')
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
        """)
        clear_button.clicked.connect(self.clear_results)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(clear_button)
        main_layout.addLayout(button_layout)

        splitter = QSplitter(Qt.Horizontal)
        
        self.key_list = QListWidget()
        self.key_list.itemClicked.connect(self.on_key_selected)
        splitter.addWidget(self.key_list)
        
        self.value_text = QTextEdit()
        self.value_text.setReadOnly(True)
        splitter.addWidget(self.value_text)
        
        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter)

        self.status_bar = QStatusBar()
        self.status_bar.setMaximumHeight(25)
        self.status_bar.setStyleSheet("QStatusBar { border-top: 1px solid #CCC; }")
        main_layout.addWidget(self.status_bar)
        self.status_bar.showMessage('Ready')

        main_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(main_layout)

    def on_key_selected(self, item):
        if not item:
            return
            
        db_path = self.path_input.text()
        key = item.text().split(' ==> ')[0].strip()
        
        result = self.run_ldb_command([f'--db={db_path}', 'get', key])
        if not result:
            return
            
        if result.stderr:
            self.value_text.setPlainText(f"Error: {result.stderr}")
        else:
            self.value_text.setPlainText(result.stdout)
            
        if self.command_combo.currentText() == 'delete':
            reply = QMessageBox.question(
                self, 'Delete Confirmation',
                f'Are you sure you want to delete the key "{key}"?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                delete_result = self.run_ldb_command([f'--db={db_path}', 'delete', key])
                if delete_result:
                    if delete_result.stderr:
                        self.status_bar.showMessage(f'Error deleting key: {delete_result.stderr}')
                    else:
                        self.status_bar.showMessage(f'Successfully deleted key: {key}')
                        self.key_list.takeItem(self.key_list.row(item))
                        self.value_text.clear()

    def run_ldb_command(self, args):
        """execute LDB command and handle error"""
        if not self.ldb_command:
            QMessageBox.critical(
                self,
                "Error",
                "RocksDB command line tools are not installed or not found in PATH.",
                QMessageBox.Ok
            )
            return None

        try:
            command = [self.ldb_command] + args
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.stderr and 'no such file or directory' in result.stderr.lower():
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not access the database directory.\nPlease check if the path is correct and accessible.",
                    QMessageBox.Ok
                )
                return None
                
            return result
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error executing command: {str(e)}",
                QMessageBox.Ok
            )
            return None
    

    def run_rocksdb_ldb(self):
        db_path = self.path_input.text()
        if not db_path:
            self.status_bar.showMessage('Error: No path specified')
            return
        
        try:
            command = self.command_combo.currentText()
            
            if command == 'put':
                key = self.key_input.text()
                value = self.value_input.text()
                if not key or not value:
                    self.status_bar.showMessage('Error: Both key and value are required for put command')
                    return
                    
                result = self.run_ldb_command([f'--db={db_path}', 'put', key, value])
                if result:
                    if result.stderr:
                        self.status_bar.showMessage(f'Error: {result.stderr}')
                    else:
                        self.status_bar.showMessage(f'Successfully put key: {key}')
                        self.run_scan()
                    
            elif command == 'get':
                key_pattern = self.key_input.text()
                if not key_pattern:
                    self.status_bar.showMessage('Error: No key specified')
                    return

                if self.regex_checkbox.isChecked():
                    self.run_scan(regex_pattern=key_pattern)
                else:
                    result = self.run_ldb_command([f'--db={db_path}', 'get', key_pattern])
                    if result:
                        self.key_list.clear()
                        if result.stderr:
                            self.status_bar.showMessage(f'Error: {result.stderr}')
                        else:
                            self.key_list.addItem(key_pattern)
                            self.value_text.setPlainText(result.stdout)
                            self.status_bar.showMessage('Command executed successfully')
            
            elif command == 'scan':
                self.run_scan()
            
        except Exception as e:
            self.status_bar.showMessage(f'Error: {str(e)}')

    def run_scan(self, regex_pattern=None):
        db_path = self.path_input.text()
        result = self.run_ldb_command([f'--db={db_path}', 'scan'])
        
        if not result:
            return
            
        self.key_list.clear()
        self.value_text.clear()
        
        if result.stderr:
            self.status_bar.showMessage(f'Error: {result.stderr}')
            return
            
        for line in result.stdout.splitlines():
            if ' ==> ' in line:
                key = line.split(' ==> ')[0].strip()
                if regex_pattern:
                    try:
                        if re.search(regex_pattern, key):
                            self.key_list.addItem(key)
                    except re.error as e:
                        self.status_bar.showMessage(f'Invalid regex pattern: {str(e)}')
                        return
                else:
                    self.key_list.addItem(key)
        
        count = self.key_list.count()
        self.status_bar.showMessage(f'Found {count} keys')

def main():
    if '/usr/local/bin' not in os.environ['PATH']:
        os.environ['PATH'] = f"/usr/local/bin:/opt/homebrew/bin:{os.environ.get('PATH', '')}"
    
    app = QApplication(sys.argv)
    gui = RocksDBGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()