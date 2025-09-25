import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QRadioButton, 
                             QButtonGroup, QPushButton, QTextEdit, QGroupBox,
                             QMessageBox, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor
import control
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
import os

class InterfaceControle(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Systems Analyzer")
        self.setGeometry(100, 100, 800, 700)
        
        
        self.s = control.TransferFunction.s
        self.G1 = None
        self.G2 = None
        
        # Clean professional colors
        self.bg_color = "#f8f9fa"  # Light gray
        self.panel_color = "#ffffff"  # White
        self.accent_color = "#007bff"  # Blue
        self.accent_hover = "#0056b3"  # Darker blue
        self.text_dark = "#212529"  # Dark gray
        self.text_light = "#6c757d"  # Light gray
        
        self.setup_interface()
        self.setup_animations()
        
    def setup_interface(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet(f"background-color: {self.bg_color};")
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.panel_color};
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Main Title
        title_label = QLabel("Analisador de FTMF")
        title_font = QFont("Arial", 22, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {self.text_dark};
            background: transparent;
            padding: 5px;
        """)
        
        # Subtitle
        subtitle_label = QLabel("O intuito dessa aplicação é analisar funções de transferência de sistemas de controle de malha fechada")
        subtitle_font = QFont("Arial", 12, QFont.Normal)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            color: {self.text_light};
            background: transparent;
            padding: 2px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_frame)
        
        # Input Section
        input_group = QGroupBox("")
        input_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
                background: {self.panel_color};
            }}
        """)
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(20)
        input_layout.setContentsMargins(20, 20, 20, 20)
        
        # G1 Input
        g1_layout = QHBoxLayout()
        g1_label = QLabel("G₁(s) =")
        g1_label.setFont(QFont("Arial", 14, QFont.Bold))
        g1_label.setFixedWidth(80)
        g1_label.setStyleSheet(f"color: {self.text_dark}; background: transparent;")
        self.g1_entry = QLineEdit()
        self.g1_entry.setText("10 / (s^2 + 2*s + 10)")
        self.g1_entry.setFont(QFont("Consolas", 13))
        self.g1_entry.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px 15px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: {self.panel_color};
                color: {self.text_dark};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.accent_color};
                background-color: {self.panel_color};
            }}
        """)
        g1_layout.addWidget(g1_label)
        g1_layout.addWidget(self.g1_entry)
        input_layout.addLayout(g1_layout)
        
        # G2 Input
        g2_layout = QHBoxLayout()
        g2_label = QLabel("G₂(s) =")
        g2_label.setFont(QFont("Arial", 14, QFont.Bold))
        g2_label.setFixedWidth(80)
        g2_label.setStyleSheet(f"color: {self.text_dark}; background: transparent;")
        self.g2_entry = QLineEdit()
        self.g2_entry.setText("5 / (s^2 + 5)")
        self.g2_entry.setFont(QFont("Consolas", 13))
        self.g2_entry.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px 15px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: {self.panel_color};
                color: {self.text_dark};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.accent_color};
                background-color: {self.panel_color};
            }}
        """)
        g2_layout.addWidget(g2_label)
        g2_layout.addWidget(self.g2_entry)
        input_layout.addLayout(g2_layout)
        
        # Connection Type - Botafogo Style
        config_label = QLabel("Connection Type")
        config_label.setFont(QFont("Arial", 14, QFont.Bold))
        config_label.setStyleSheet(f"color: {self.text_dark}; background: transparent; margin-bottom: 10px;")
        input_layout.addWidget(config_label)
        
        # Radio buttons
        self.button_group = QButtonGroup()
        self.serie_radio = QRadioButton("Series")
        self.paralelo_radio = QRadioButton("Parallel")
        self.feedback_radio = QRadioButton("Feedback")
        
        self.serie_radio.setChecked(True)
        
        # Style radio buttons
        radio_style = f"""
            QRadioButton {{
                color: {self.text_dark};
                font-size: 13px;
                font-weight: normal;
                background: transparent;
                padding: 8px 12px;
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid #ced4da;
                border-radius: 8px;
                background: {self.panel_color};
            }}
            QRadioButton::indicator:checked {{
                background: {self.accent_color};
                border: 1px solid {self.accent_color};
            }}
            QRadioButton:hover {{
                color: {self.accent_hover};
            }}
        """
        
        self.serie_radio.setStyleSheet(radio_style)
        self.paralelo_radio.setStyleSheet(radio_style)
        self.feedback_radio.setStyleSheet(radio_style)
        
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.serie_radio)
        radio_layout.addWidget(self.paralelo_radio)
        radio_layout.addWidget(self.feedback_radio)
        radio_layout.addStretch()
        
        self.button_group.addButton(self.serie_radio, 0)
        self.button_group.addButton(self.paralelo_radio, 1)
        self.button_group.addButton(self.feedback_radio, 2)
        
        input_layout.addLayout(radio_layout)
        
        # Calculate Button
        self.calc_button = QPushButton("Calculate")
        self.calc_button.setFont(QFont("Arial Black", 14, QFont.Bold))
        self.calc_button.setFixedHeight(55)
        self.calc_button.setStyleSheet(f"""
            QPushButton {{
                background: {self.accent_color};
                color: white;
                border: 1px solid {self.accent_color};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self.accent_hover};
                border: 1px solid {self.accent_hover};
            }}
            QPushButton:pressed {{
                background: #004085;
            }}
        """)
        self.calc_button.clicked.connect(self.calcular_sistema)
        input_layout.addWidget(self.calc_button)
        
        main_layout.addWidget(input_group)
        
        # Results Section
        result_group = QGroupBox("")
        result_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
                background: {self.panel_color};
            }}
        """)
        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(20, 20, 20, 20)
        
        # Results title
        results_title = QLabel("Result")
        results_title.setFont(QFont("Arial Black", 16, QFont.Bold))
        results_title.setStyleSheet(f"color: {self.text_dark}; background: transparent; margin-bottom: 15px;")
        results_title.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(results_title)
        
        # Text area for results
        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("Consolas", 18))  # Even bigger font
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(350)  # Bigger
        self.result_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #ced4da;
                border-radius: 8px;
                background-color: {self.panel_color};
                color: {self.text_dark};
                padding: 20px;
                font-size: 16px;
                selection-background-color: {self.accent_color};
                line-height: 1.6;
            }}
            QTextEdit:focus {{
                border: 2px solid {self.accent_color};
            }}
        """)
        result_layout.addWidget(self.result_text)
        
        main_layout.addWidget(result_group)
    
    def setup_animations(self):
        """Setup animations for the interface"""
        # Create pulsing animation for the title
        self.title_animation = QPropertyAnimation(self.calc_button, b"geometry")
        self.title_animation.setDuration(2000)
        self.title_animation.setLoopCount(-1)  # Infinite loop
        self.title_animation.setEasingCurve(QEasingCurve.InOutSine)
        
    
    def processar_expressao(self, expr):
        """Processa a expressão para aceitar diferentes formatos de entrada"""
        # Remover espaços
        expr = expr.strip()
        
        # Substituir ^ por ** para potências (prioridade para s^2, s^3, etc.)
        expr = expr.replace('^', '**')
        
        # Processar múltiplos * para multiplicação implícita
        # Exemplo: s*s*s vira s**3, s*s vira s**2, etc.
        import re
        
        # Encontrar padrões de s*s*s... e converter para s**n
        def replace_multiple_stars(match):
            s_count = match.group(0).count('s')
            if s_count > 1:
                return f's**{s_count}'
            return match.group(0)
        
        # Aplicar a substituição para s*s*s... padrões
        expr = re.sub(r's(\*s)+', replace_multiple_stars, expr)
        
        return expr
        
    def calcular_sistema(self):
        """Calcula o sistema baseado na configuração selecionada"""
        # Obter as funções de transferência dos campos de entrada
        g1_expr = self.g1_entry.text().strip()
        g2_expr = self.g2_entry.text().strip()
        
        if not g1_expr or not g2_expr:
            QMessageBox.critical(self, "Erro", "Por favor, insira ambas as funções G1(s) e G2(s)")
            return
        
        try:
            # Criar as funções de transferência
            # Processar as expressões para aceitar diferentes formatos
            g1_expr_processed = self.processar_expressao(g1_expr)
            g2_expr_processed = self.processar_expressao(g2_expr)
            
            # Criar variável local s para o eval
            s = self.s
            
            self.G1 = eval(g1_expr_processed)
            self.G2 = eval(g2_expr_processed)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar as funções: {str(e)}\n\nFORMATOS ACEITOS:\n• 10 / (s^2 + 2*s + 10)\n• 5 / (s^2 + 5)\n• 1 / (s + 1)\n• s / (s^2 + 3*s + 2)\n\nUse 's' para a variável e '^' para potências.")
            return
        
        try:
            # Obter configuração selecionada
            if self.serie_radio.isChecked():
                config = "serie"
            elif self.paralelo_radio.isChecked():
                config = "paralelo"
            else:
                config = "feedback"
            
            if config == "serie":
                sistema = control.series(self.G1, self.G2)
                formula = "G_resultado(s) = G1(s) × G2(s)"
                tipo = "SÉRIE (CASCATA)"
            elif config == "paralelo":
                sistema = control.parallel(self.G1, self.G2)
                formula = "G_resultado(s) = G1(s) + G2(s)"
                tipo = "PARALELO"
            elif config == "feedback":
                sistema = control.feedback(self.G1, self.G2)
                formula = "G_resultado(s) = G1(s) / (1 + G1(s) × G2(s))"
                tipo = "REALIMENTAÇÃO"
            
            # Limpar e mostrar apenas o resultado final
            self.result_text.clear()
            # Extrair apenas a função de transferência sem informações do sistema
            sistema_str = str(sistema)
            # Remover as linhas de Inputs e Outputs
            lines = sistema_str.split('\n')
            filtered_lines = []
            for line in lines:
                if not line.startswith('Inputs') and not line.startswith('Outputs') and not line.startswith('<TransferFunction>'):
                    filtered_lines.append(line)
            
            # Juntar as linhas filtradas
            clean_result = '\n'.join(filtered_lines).strip()
            
            # Centralizar o resultado
            self.result_text.setAlignment(Qt.AlignCenter)
            self.result_text.append(clean_result)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular a associação: {str(e)}")
    

def main():
    app = QApplication(sys.argv)
    
    # Apply clean professional style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QWidget {
            font-family: 'Arial', sans-serif;
            color: #212529;
        }
        QApplication {
            background-color: #f8f9fa;
        }
    """)
    
    # Set application properties
    app.setApplicationName("Control Systems Analyzer")
    app.setApplicationVersion("1.0.0")
    
    window = InterfaceControle()
    window.show()
    
    # Print startup message
    print("=" * 50)
    print("CONTROL SYSTEMS ANALYZER")
    print("=" * 50)
    print("Ready to analyze transfer functions!")
    print("=" * 50)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
