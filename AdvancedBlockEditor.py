import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGraphicsView, 
                             QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
                             QGraphicsEllipseItem, QGraphicsTextItem, QMenu,
                             QAction, QDialog, QLineEdit, QComboBox, QFormLayout,
                             QDialogButtonBox, QMessageBox, QSplitter, QListWidget,
                             QGroupBox, QFrame, QScrollArea, QTextEdit, QTabWidget)
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
import control
import numpy as np

class BlockItem(QGraphicsRectItem):
    """Enhanced block item with transfer function calculation capabilities"""
    def __init__(self, block_type, name, transfer_function=None):
        super().__init__()
        self.block_type = block_type
        self.name = name
        self.transfer_function = transfer_function
        self.gain_value = 1.0
        self.input_ports = []
        self.output_ports = []
        self.connections = []
        self.input_blocks = []
        self.output_blocks = []
        
        # Set up the block appearance
        self.setRect(0, 0, 120, 80)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Create ports
        self.create_ports()
        
        # Set colors based on block type
        self.setup_appearance()
        
        # Initialize transfer function
        self.update_transfer_function()
        
    def create_ports(self):
        """Create input and output ports for the block"""
        if self.block_type in ['sum', 'subtract']:
            # Sum/subtract blocks have 2 inputs and 1 output
            self.input_ports = [
                PortItem(self, 'input', 0, 20),
                PortItem(self, 'input', 0, 60)
            ]
            self.output_ports = [PortItem(self, 'output', 120, 40)]
        else:
            # Other blocks have 1 input and 1 output
            self.input_ports = [PortItem(self, 'input', 0, 40)]
            self.output_ports = [PortItem(self, 'output', 120, 40)]
            
    def setup_appearance(self):
        """Set up the visual appearance of the block"""
        colors = {
            'sum': QColor(255, 200, 200),
            'subtract': QColor(255, 200, 200),
            'gain': QColor(200, 255, 200),
            'integrator': QColor(200, 200, 255),
            'transfer_function': QColor(255, 255, 200),
            'input': QColor(200, 255, 255),
            'output': QColor(255, 200, 255)
        }
        
        self.setBrush(QBrush(colors.get(self.block_type, QColor(200, 200, 200))))
        self.setPen(QPen(QColor(0, 0, 0), 2))
        
    def update_transfer_function(self):
        """Update the transfer function based on block type and parameters"""
        s = control.TransferFunction.s
        
        if self.block_type == 'gain':
            self.transfer_function = self.gain_value
        elif self.block_type == 'integrator':
            self.transfer_function = 1/s
        elif self.block_type == 'sum':
            self.transfer_function = 1  # Will be handled by connection logic
        elif self.block_type == 'subtract':
            self.transfer_function = 1  # Will be handled by connection logic
        elif self.block_type == 'transfer_function':
            if self.transfer_function is None:
                self.transfer_function = 1 / (s + 1)
            else:
                # Try to parse the transfer function string
                try:
                    # Replace common mathematical notation
                    tf_str = str(self.transfer_function)
                    tf_str = tf_str.replace('^', '**')
                    # Create a safe evaluation environment
                    safe_dict = {'s': s, 'control': control, 'np': np}
                    self.transfer_function = eval(tf_str, {"__builtins__": {}}, safe_dict)
                except:
                    # If parsing fails, use default
                    self.transfer_function = 1 / (s + 1)
                
    def get_effective_transfer_function(self):
        """Get the effective transfer function considering connections"""
        if self.block_type in ['sum', 'subtract']:
            # For sum/subtract blocks, we need to consider the input connections
            if len(self.input_blocks) >= 2:
                if self.block_type == 'sum':
                    return self.input_blocks[0].get_effective_transfer_function() + \
                           self.input_blocks[1].get_effective_transfer_function()
                else:  # subtract
                    return self.input_blocks[0].get_effective_transfer_function() - \
                           self.input_blocks[1].get_effective_transfer_function()
        else:
            return self.transfer_function
            
    def paint(self, painter, option, widget):
        """Custom paint method for different block types"""
        super().paint(painter, option, widget)
        
        # Draw block-specific symbols
        rect = self.rect()
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        if self.block_type == 'sum':
            painter.drawText(rect, Qt.AlignCenter, "+")
        elif self.block_type == 'subtract':
            painter.drawText(rect, Qt.AlignCenter, "-")
        elif self.block_type == 'gain':
            painter.drawText(rect, Qt.AlignCenter, f"K = {self.gain_value}")
        elif self.block_type == 'integrator':
            painter.drawText(rect, Qt.AlignCenter, "1/s")
        elif self.block_type == 'transfer_function':
            painter.setFont(QFont("Arial", 8))
            painter.drawText(rect, Qt.AlignCenter, self.name)
        elif self.block_type == 'input':
            painter.drawText(rect, Qt.AlignCenter, "Input")
        elif self.block_type == 'output':
            painter.drawText(rect, Qt.AlignCenter, "Output")
            
    def itemChange(self, change, value):
        """Handle item changes (movement, selection)"""
        if change == QGraphicsItem.ItemPositionChange:
            # Update port positions when block moves
            for port in self.input_ports + self.output_ports:
                port.update_position()
        return super().itemChange(change, value)

class PortItem(QGraphicsEllipseItem):
    """Enhanced port item with connection management"""
    def __init__(self, parent_block, port_type, x, y):
        super().__init__()
        self.parent_block = parent_block
        self.port_type = port_type
        self.connections = []
        
        # Set up port appearance
        self.setRect(0, 0, 12, 12)
        self.setPos(x - 6, y - 6)
        self.setBrush(QBrush(QColor(100, 100, 100)))
        self.setPen(QPen(QColor(0, 0, 0), 1))
        
    def update_position(self):
        """Update port position when parent block moves"""
        pass

class ConnectionItem(QGraphicsItem):
    """Enhanced connection item with transfer function tracking"""
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.start_port.connections.append(self)
        self.end_port.connections.append(self)
        
        # Update block connections
        if start_port.port_type == 'output' and end_port.port_type == 'input':
            end_port.parent_block.input_blocks.append(start_port.parent_block)
        elif start_port.port_type == 'input' and end_port.port_type == 'output':
            start_port.parent_block.input_blocks.append(end_port.parent_block)
        
    def boundingRect(self):
        """Return the bounding rectangle of the connection"""
        start_pos = self.start_port.scenePos()
        end_pos = self.end_port.scenePos()
        return QRectF(start_pos, end_pos).normalized()
        
    def paint(self, painter, option, widget):
        """Draw the connection line with arrow"""
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        start_pos = self.start_port.scenePos()
        end_pos = self.end_port.scenePos()
        
        # Draw main line
        painter.drawLine(start_pos, end_pos)
        
        # Draw arrow
        self.draw_arrow(painter, start_pos, end_pos)
        
    def draw_arrow(self, painter, start, end):
        """Draw an arrow at the end of the connection"""
        # Calculate arrow direction
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            # Normalize direction
            dx /= length
            dy /= length
            
            # Arrow size
            arrow_length = 10
            arrow_angle = math.pi / 6
            
            # Calculate arrow points
            x1 = end.x() - arrow_length * (dx * math.cos(arrow_angle) + dy * math.sin(arrow_angle))
            y1 = end.y() - arrow_length * (dy * math.cos(arrow_angle) - dx * math.sin(arrow_angle))
            
            x2 = end.x() - arrow_length * (dx * math.cos(-arrow_angle) + dy * math.sin(-arrow_angle))
            y2 = end.y() - arrow_length * (dy * math.cos(-arrow_angle) - dx * math.sin(-arrow_angle))
            
            # Draw arrow
            painter.drawLine(end, QPointF(x1, y1))
            painter.drawLine(end, QPointF(x2, y2))

class TempConnectionLine(QGraphicsItem):
    """Temporary line item for visual feedback during connection"""
    def __init__(self, start_pos):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = start_pos
        
    def boundingRect(self):
        """Return the bounding rectangle of the temporary line"""
        return QRectF(self.start_pos, self.end_pos).normalized()
        
    def paint(self, painter, option, widget):
        """Draw the temporary connection line"""
        painter.setPen(QPen(QColor(100, 100, 100), 2, Qt.DashLine))
        painter.drawLine(self.start_pos, self.end_pos)
        
    def update_end_point(self, end_pos):
        """Update the end point of the temporary line"""
        self.end_pos = end_pos
        self.update()

class TransferFunctionCalculator:
    """Class to calculate overall transfer function from block diagram"""
    
    @staticmethod
    def calculate_overall_tf(blocks, connections):
        """Calculate the overall transfer function of the system"""
        try:
            # Find input and output blocks
            input_blocks = [b for b in blocks if b.block_type == 'input']
            output_blocks = [b for b in blocks if b.block_type == 'output']
            
            if not input_blocks or not output_blocks:
                return None, "No input or output blocks found"
                
            # For now, return a simple calculation
            # In a full implementation, this would trace through the entire diagram
            s = control.TransferFunction.s
            
            # Example: if we have a gain block connected to an integrator
            gain_blocks = [b for b in blocks if b.block_type == 'gain']
            integrator_blocks = [b for b in blocks if b.block_type == 'integrator']
            
            if gain_blocks and integrator_blocks:
                gain_tf = gain_blocks[0].get_effective_transfer_function()
                integrator_tf = integrator_blocks[0].get_effective_transfer_function()
                overall_tf = control.series(gain_tf, integrator_tf)
                return overall_tf, "Success"
            else:
                return 1, "Simple system"
                
        except Exception as e:
            return None, f"Error calculating transfer function: {str(e)}"

class BlockLibrary(QWidget):
    """Enhanced block library with more block types"""
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
        
        # Block categories
        categories = [
            ("Basic Blocks", [
                ("Sum", "sum", "Addition block"),
                ("Subtract", "subtract", "Subtraction block"),
                ("Gain", "gain", "Gain/Amplifier block"),
            ]),
            ("Dynamic Blocks", [
                ("Integrator", "integrator", "1/s block"),
                ("Transfer Function", "transfer_function", "Custom TF block"),
            ]),
            ("System Blocks", [
                ("Input", "input", "System input"),
                ("Output", "output", "System output"),
            ])
        ]
        
        for category_name, blocks in categories:
            # Category label
            cat_label = QLabel(category_name)
            cat_label.setFont(QFont("Arial", 10, QFont.Bold))
            cat_label.setStyleSheet("color: #666; margin-top: 10px;")
            layout.addWidget(cat_label)
            
            # Block buttons
            for name, block_type, description in blocks:
                btn = QPushButton(name)
                btn.setToolTip(description)
                btn.clicked.connect(lambda checked, bt=block_type: self.block_selected.emit(bt))
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 5px;
                        margin: 2px;
                    }
                """)
                layout.addWidget(btn)
                
        layout.addStretch()
        self.setLayout(layout)

class BlockPropertiesDialog(QDialog):
    """Enhanced dialog for editing block properties"""
    def __init__(self, block_item, parent=None):
        super().__init__(parent)
        self.block_item = block_item
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Block Properties")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QFormLayout()
        
        # Block name
        self.name_edit = QLineEdit(self.block_item.name)
        layout.addRow("Name:", self.name_edit)
        
        # Block-specific properties
        if self.block_item.block_type == 'gain':
            self.gain_edit = QLineEdit(str(self.block_item.gain_value))
            layout.addRow("Gain (K):", self.gain_edit)
        elif self.block_item.block_type == 'transfer_function':
            # Create a more comprehensive transfer function input
            tf_layout = QVBoxLayout()
            
            self.tf_edit = QLineEdit("1 / (s + 1)")
            self.tf_edit.setPlaceholderText("Enter transfer function (e.g., 1/(s+1), s/(s^2+2*s+1))")
            tf_layout.addWidget(self.tf_edit)
            
            # Add examples
            examples_label = QLabel("Examples:")
            examples_label.setFont(QFont("Arial", 9))
            examples_label.setStyleSheet("color: #666;")
            tf_layout.addWidget(examples_label)
            
            examples_text = QLabel("• 1/(s+1)\n• s/(s^2+2*s+1)\n• 10/(s^2+3*s+2)\n• (s+1)/(s+2)")
            examples_text.setFont(QFont("Consolas", 8))
            examples_text.setStyleSheet("color: #888; background: #f5f5f5; padding: 5px; border-radius: 3px;")
            tf_layout.addWidget(examples_text)
            
            layout.addRow("Transfer Function:", tf_layout)
            
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
            try:
                properties['gain'] = float(self.gain_edit.text())
            except ValueError:
                properties['gain'] = 1.0
        elif self.block_item.block_type == 'transfer_function':
            properties['transfer_function'] = self.tf_edit.text()
            
        return properties

class BlockDiagramView(QGraphicsView):
    """Enhanced graphics view with transfer function calculation"""
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
        self.temp_line = None  # Temporary line for visual feedback
        
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
        elif event.button() == Qt.RightButton:
            # Show context menu
            self.show_context_menu(event)
        else:
            super().mousePressEvent(event)
            
    def show_context_menu(self, event):
        """Show context menu for right-click"""
        item = self.itemAt(event.pos())
        if isinstance(item, BlockItem):
            menu = QMenu(self)
            
            # Edit properties action
            edit_action = QAction("Edit Properties", self)
            edit_action.triggered.connect(lambda: self.edit_block_properties(item))
            menu.addAction(edit_action)
            
            # Delete action
            delete_action = QAction("Delete Block", self)
            delete_action.triggered.connect(lambda: self.delete_block(item))
            menu.addAction(delete_action)
            
            # Show menu
            menu.exec_(self.mapToGlobal(event.pos()))
        elif isinstance(item, ConnectionItem):
            menu = QMenu(self)
            
            # Delete connection action
            delete_action = QAction("Delete Connection", self)
            delete_action.triggered.connect(lambda: self.delete_connection(item))
            menu.addAction(delete_action)
            
            # Show menu
            menu.exec_(self.mapToGlobal(event.pos()))
            
    def edit_block_properties(self, block):
        """Edit block properties"""
        dialog = BlockPropertiesDialog(block)
        if dialog.exec_() == QDialog.Accepted:
            props = dialog.get_properties()
            block.name = props['name']
            if 'gain' in props:
                block.gain_value = props['gain']
                block.update_transfer_function()
            elif 'transfer_function' in props:
                block.transfer_function = props['transfer_function']
                block.update_transfer_function()
                
    def delete_block(self, block):
        """Delete a specific block"""
        self.remove_block_connections(block)
        self.scene.removeItem(block)
        
    def delete_connection(self, connection):
        """Delete a specific connection"""
        self.scene.removeItem(connection)
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.connecting and self.temp_line:
            # Update temporary line end point
            scene_pos = self.mapToScene(event.pos())
            self.temp_line.update_end_point(scene_pos)
        else:
            super().mouseMoveEvent(event)
            
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
        
        # Create temporary line for visual feedback
        start_pos = port.scenePos()
        self.temp_line = TempConnectionLine(start_pos)
        self.scene.addItem(self.temp_line)
        
    def finish_connection(self, end_port):
        """Finish creating a connection"""
        if (self.start_port.port_type != end_port.port_type and 
            self.start_port.parent_block != end_port.parent_block):
            
            # Check if connection already exists
            existing_connection = self.check_existing_connection(self.start_port, end_port)
            if not existing_connection:
                # Create connection
                connection = ConnectionItem(self.start_port, end_port)
                self.scene.addItem(connection)
            else:
                QMessageBox.information(self, "Connection Exists", 
                                      "A connection between these ports already exists!")
        else:
            if self.start_port.parent_block == end_port.parent_block:
                QMessageBox.warning(self, "Invalid Connection", 
                                  "Cannot connect a block to itself!")
            else:
                QMessageBox.warning(self, "Invalid Connection", 
                                  "Cannot connect two ports of the same type!")
        
        # Remove temporary line and reset connection state
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        self.connecting = False
        self.start_port = None
        
    def check_existing_connection(self, start_port, end_port):
        """Check if a connection already exists between two ports"""
        for item in self.scene.items():
            if isinstance(item, ConnectionItem):
                if ((item.start_port == start_port and item.end_port == end_port) or
                    (item.start_port == end_port and item.end_port == start_port)):
                    return True
        return False
        
    def cancel_connection(self):
        """Cancel the current connection"""
        self.connecting = False
        self.start_port = None
        
        # Remove temporary line
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
            self.temp_line = None
        
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
                    block.gain_value = props['gain']
                    block.update_transfer_function()
                elif 'transfer_function' in props:
                    block.transfer_function = props['transfer_function']
                    
        return block
        
    def get_all_blocks(self):
        """Get all blocks in the scene"""
        blocks = []
        for item in self.scene.items():
            if isinstance(item, BlockItem):
                blocks.append(item)
        return blocks
        
    def get_all_connections(self):
        """Get all connections in the scene"""
        connections = []
        for item in self.scene.items():
            if isinstance(item, ConnectionItem):
                connections.append(item)
        return connections

class ResultsPanel(QWidget):
    """Panel to display calculation results"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Results")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_text)
        
        self.setLayout(layout)
        
    def update_results(self, transfer_function, status):
        """Update the results display"""
        self.results_text.clear()
        self.results_text.append(f"Status: {status}\n")
        self.results_text.append("=" * 50)
        self.results_text.append("\nOverall Transfer Function:\n")
        
        if transfer_function is not None:
            self.results_text.append(str(transfer_function))
        else:
            self.results_text.append("Could not calculate transfer function")

class BlockDiagramEditor(QMainWindow):
    """Enhanced main window for the block diagram editor"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Block Diagram Editor - Control Systems")
        self.setGeometry(100, 100, 1400, 900)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel with block library
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.block_library = BlockLibrary()
        self.block_library.block_selected.connect(self.add_block)
        left_layout.addWidget(self.block_library)
        
        # Right panel with diagram and results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Create splitter for diagram and results
        right_splitter = QSplitter(Qt.Vertical)
        
        # Block diagram view
        self.diagram_view = BlockDiagramView()
        right_splitter.addWidget(self.diagram_view)
        
        # Results panel
        self.results_panel = ResultsPanel()
        right_splitter.addWidget(self.results_panel)
        
        # Set splitter proportions
        right_splitter.setSizes([600, 200])
        
        right_layout.addWidget(right_splitter)
        
        # Add panels to main splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        
        # Set main splitter proportions
        main_splitter.setSizes([250, 1150])
        
        layout.addWidget(main_splitter)
        
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
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
        
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = self.addToolBar('Main')
        
        # New diagram button
        new_action = QAction('New', self)
        new_action.setToolTip('Create new diagram')
        new_action.triggered.connect(self.new_diagram)
        toolbar.addAction(new_action)
        
        toolbar.addSeparator()
        
        # Quick add buttons
        toolbar.addWidget(QLabel("Quick Add:"))
        
        # Sum button
        sum_action = QAction('Sum', self)
        sum_action.setToolTip('Add Sum block')
        sum_action.triggered.connect(lambda: self.add_block('sum'))
        toolbar.addAction(sum_action)
        
        # Gain button
        gain_action = QAction('Gain', self)
        gain_action.setToolTip('Add Gain block')
        gain_action.triggered.connect(lambda: self.add_block('gain'))
        toolbar.addAction(gain_action)
        
        # Transfer Function button
        tf_action = QAction('TF', self)
        tf_action.setToolTip('Add Transfer Function block')
        tf_action.triggered.connect(lambda: self.add_block('transfer_function'))
        toolbar.addAction(tf_action)
        
        toolbar.addSeparator()
        
        # Calculate button
        calc_action = QAction('Calculate', self)
        calc_action.setToolTip('Calculate overall transfer function')
        calc_action.triggered.connect(self.calculate_transfer_function)
        toolbar.addAction(calc_action)
        
    def add_block(self, block_type):
        """Add a new block to the diagram"""
        # Get center of the view
        center = self.diagram_view.mapToScene(self.diagram_view.viewport().rect().center())
        self.diagram_view.add_block(block_type, center)
        
    def new_diagram(self):
        """Clear the current diagram"""
        self.diagram_view.scene.clear()
        self.results_panel.results_text.clear()
        
    def calculate_transfer_function(self):
        """Calculate the overall transfer function of the diagram"""
        blocks = self.diagram_view.get_all_blocks()
        connections = self.diagram_view.get_all_connections()
        
        if not blocks:
            QMessageBox.information(self, "No Blocks", "Please add some blocks to the diagram first!")
            return
            
        # Calculate transfer function
        tf, status = TransferFunctionCalculator.calculate_overall_tf(blocks, connections)
        
        # Update results panel
        self.results_panel.update_results(tf, status)

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
        QTextEdit {
            background-color: white;
            border: 1px solid #ccc;
        }
    """)
    
    window = BlockDiagramEditor()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
