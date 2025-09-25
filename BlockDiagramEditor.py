import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGraphicsView, 
                             QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
                             QGraphicsEllipseItem, QGraphicsTextItem, QMenu,
                             QAction, QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QMessageBox, QSplitter, QListWidget,
                             QGroupBox, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
import control
import numpy as np

class BlockItem(QGraphicsRectItem):
    """Represents a transfer function block in the diagram"""
    def __init__(self, block_type, name, transfer_function=None):
        super().__init__()
        self.block_type = block_type
        self.name = name
        self.transfer_function = transfer_function
        self.input_ports = []
        self.output_ports = []
        self.connections = []
        
        # Set up the block appearance
        self.setRect(0, 0, 120, 80)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Create ports
        self.create_ports()
        
        # Set colors based on block type
        self.setup_appearance()
        
    def create_ports(self):
        """Create input and output ports for the block"""
        if self.block_type in ['sum', 'subtract']:
            # Sum/subtract blocks have 2 inputs and 1 output
            self.input_ports = [
                PortItem(self, 'input', 0, 20),
                PortItem(self, 'input', 0, 60)
            ]
            self.output_ports = [PortItem(self, 'output', 120, 40)]
        elif self.block_type == 'gain':
            # Gain block has 1 input and 1 output
            self.input_ports = [PortItem(self, 'input', 0, 40)]
            self.output_ports = [PortItem(self, 'output', 120, 40)]
        elif self.block_type == 'integrator':
            # Integrator has 1 input and 1 output
            self.input_ports = [PortItem(self, 'input', 0, 40)]
            self.output_ports = [PortItem(self, 'output', 120, 40)]
        elif self.block_type == 'transfer_function':
            # Transfer function has 1 input and 1 output
            self.input_ports = [PortItem(self, 'input', 0, 40)]
            self.output_ports = [PortItem(self, 'output', 120, 40)]
            
    def setup_appearance(self):
        """Set up the visual appearance of the block"""
        colors = {
            'sum': QColor(255, 200, 200),
            'subtract': QColor(255, 200, 200),
            'gain': QColor(200, 255, 200),
            'integrator': QColor(200, 200, 255),
            'transfer_function': QColor(255, 255, 200)
        }
        
        self.setBrush(QBrush(colors.get(self.block_type, QColor(200, 200, 200))))
        self.setPen(QPen(QColor(0, 0, 0), 2))
        
    def paint(self, painter, option, widget):
        """Custom paint method for different block types"""
        super().paint(painter, option, widget)
        
        # Draw block-specific symbols
        rect = self.rect()
        center = rect.center()
        
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        if self.block_type == 'sum':
            # Draw + symbol
            painter.drawText(rect, Qt.AlignCenter, "+")
        elif self.block_type == 'subtract':
            # Draw - symbol
            painter.drawText(rect, Qt.AlignCenter, "-")
        elif self.block_type == 'gain':
            # Draw K symbol
            painter.drawText(rect, Qt.AlignCenter, f"K\n{self.name}")
        elif self.block_type == 'integrator':
            # Draw 1/s symbol
            painter.drawText(rect, Qt.AlignCenter, "1/s")
        elif self.block_type == 'transfer_function':
            # Draw transfer function name
            painter.setFont(QFont("Arial", 8))
            painter.drawText(rect, Qt.AlignCenter, self.name)
            
    def itemChange(self, change, value):
        """Handle item changes (movement, selection)"""
        if change == QGraphicsItem.ItemPositionChange:
            # Update port positions when block moves
            for port in self.input_ports + self.output_ports:
                port.update_position()
        return super().itemChange(change, value)

class PortItem(QGraphicsEllipseItem):
    """Represents input/output ports on blocks"""
    def __init__(self, parent_block, port_type, x, y):
        super().__init__()
        self.parent_block = parent_block
        self.port_type = port_type
        self.connections = []
        
        # Set up port appearance
        self.setRect(0, 0, 12, 12)
        self.setPos(x - 6, y - 6)  # Center the port
        self.setBrush(QBrush(QColor(100, 100, 100)))
        self.setPen(QPen(QColor(0, 0, 0), 1))
        
    def update_position(self):
        """Update port position when parent block moves"""
        # This will be called when the parent block moves
        pass

class ConnectionItem(QGraphicsItem):
    """Represents a connection between two ports"""
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.start_port.connections.append(self)
        self.end_port.connections.append(self)
        
    def boundingRect(self):
        """Return the bounding rectangle of the connection"""
        start_pos = self.start_port.scenePos()
        end_pos = self.end_port.scenePos()
        return QRectF(start_pos, end_pos).normalized()
        
    def paint(self, painter, option, widget):
        """Draw the connection line"""
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        start_pos = self.start_port.scenePos()
        end_pos = self.end_port.scenePos()
        painter.drawLine(start_pos, end_pos)

class BlockLibrary(QWidget):
    """Widget containing available blocks for the diagram"""
    block_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Block Library")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Block buttons
        blocks = [
            ("Sum", "sum", "Addition block"),
            ("Subtract", "subtract", "Subtraction block"),
            ("Gain", "gain", "Gain/Amplifier block"),
            ("Integrator", "integrator", "1/s block"),
            ("Transfer Function", "transfer_function", "Custom TF block")
        ]
        
        for name, block_type, description in blocks:
            btn = QPushButton(name)
            btn.setToolTip(description)
            btn.clicked.connect(lambda checked, bt=block_type: self.block_selected.emit(bt))
            layout.addWidget(btn)
            
        layout.addStretch()
        self.setLayout(layout)

class BlockPropertiesDialog(QDialog):
    """Dialog for editing block properties"""
    def __init__(self, block_item, parent=None):
        super().__init__(parent)
        self.block_item = block_item
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Block Properties")
        self.setModal(True)
        
        layout = QFormLayout()
        
        # Block name
        self.name_edit = QLineEdit(self.block_item.name)
        layout.addRow("Name:", self.name_edit)
        
        # Block-specific properties
        if self.block_item.block_type == 'gain':
            self.gain_edit = QLineEdit("1")
            layout.addRow("Gain (K):", self.gain_edit)
        elif self.block_item.block_type == 'transfer_function':
            self.tf_edit = QLineEdit("1 / (s + 1)")
            layout.addRow("Transfer Function:", self.tf_edit)
            
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
    def get_properties(self):
        """Get the edited properties"""
        properties = {'name': self.name_edit.text()}
        
        if self.block_item.block_type == 'gain':
            properties['gain'] = self.gain_edit.text()
        elif self.block_item.block_type == 'transfer_function':
            properties['transfer_function'] = self.tf_edit.text()
            
        return properties

class BlockDiagramView(QGraphicsView):
    """Main graphics view for the block diagram editor"""
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Set up the scene
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        
        # Connection state
        self.connecting = False
        self.start_port = None
        
        # Enable focus to receive key events
        self.setFocusPolicy(Qt.StrongFocus)
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, PortItem):
                self.start_connection(item)
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton and self.connecting:
            item = self.itemAt(event.pos())
            if isinstance(item, PortItem) and item != self.start_port:
                self.finish_connection(item)
            else:
                self.cancel_connection()
        else:
            super().mouseReleaseEvent(event)
            
    def start_connection(self, port):
        """Start creating a connection from a port"""
        self.connecting = True
        self.start_port = port
        
    def finish_connection(self, end_port):
        """Finish creating a connection"""
        if self.start_port.port_type != end_port.port_type:
            # Create connection
            connection = ConnectionItem(self.start_port, end_port)
            self.scene.addItem(connection)
            
        self.cancel_connection()
        
    def cancel_connection(self):
        """Cancel the current connection"""
        self.connecting = False
        self.start_port = None
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)
            
    def delete_selected_items(self):
        """Delete all selected items"""
        selected_items = self.scene.selectedItems()
        
        for item in selected_items:
            if isinstance(item, BlockItem):
                # Remove all connections to this block
                self.remove_block_connections(item)
                # Remove the block from scene
                self.scene.removeItem(item)
            elif isinstance(item, ConnectionItem):
                # Remove the connection
                self.scene.removeItem(item)
                
    def remove_block_connections(self, block):
        """Remove all connections related to a block"""
        # Get all connections in the scene
        all_connections = []
        for item in self.scene.items():
            if isinstance(item, ConnectionItem):
                all_connections.append(item)
                
        # Remove connections that involve this block
        for connection in all_connections:
            if (connection.start_port.parent_block == block or 
                connection.end_port.parent_block == block):
                self.scene.removeItem(connection)
        
    def add_block(self, block_type, position=None):
        """Add a new block to the diagram"""
        if position is None:
            position = QPointF(100, 100)
            
        block = BlockItem(block_type, f"{block_type}_{len(self.scene.items())}")
        block.setPos(position)
        self.scene.addItem(block)
        
        # Show properties dialog for certain block types
        if block_type in ['gain', 'transfer_function']:
            dialog = BlockPropertiesDialog(block)
            if dialog.exec_() == QDialog.Accepted:
                props = dialog.get_properties()
                block.name = props['name']
                if 'gain' in props:
                    block.gain = props['gain']
                elif 'transfer_function' in props:
                    block.transfer_function = props['transfer_function']
                    
        return block

class BlockDiagramEditor(QMainWindow):
    """Main window for the block diagram editor"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Block Diagram Editor - Control Systems")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Block library
        self.block_library = BlockLibrary()
        self.block_library.block_selected.connect(self.add_block)
        splitter.addWidget(self.block_library)
        
        # Block diagram view
        self.diagram_view = BlockDiagramView()
        splitter.addWidget(self.diagram_view)
        
        # Set splitter proportions
        splitter.setSizes([200, 1000])
        
        layout.addWidget(splitter)
        
        # Menu bar
        self.create_menu_bar()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.triggered.connect(self.new_diagram)
        file_menu.addAction(new_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        calculate_action = QAction('Calculate Transfer Function', self)
        calculate_action.triggered.connect(self.calculate_transfer_function)
        tools_menu.addAction(calculate_action)
        
    def add_block(self, block_type):
        """Add a new block to the diagram"""
        # Get center of the view
        center = self.diagram_view.mapToScene(self.diagram_view.viewport().rect().center())
        self.diagram_view.add_block(block_type, center)
        
    def new_diagram(self):
        """Clear the current diagram"""
        self.diagram_view.scene.clear()
        
    def calculate_transfer_function(self):
        """Calculate the overall transfer function of the diagram"""
        # This is where we would implement the transfer function calculation
        # For now, just show a message
        QMessageBox.information(self, "Transfer Function", 
                              "Transfer function calculation will be implemented here!")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #e0e0e0;
            border: 1px solid #ccc;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
    """)
    
    window = BlockDiagramEditor()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
