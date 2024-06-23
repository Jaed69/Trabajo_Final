import sys
import pandas as pd
import random
import networkx as nx
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton,
                             QComboBox, QSplitter, QDialog, QLineEdit, QFormLayout, QSpinBox, QProgressBar)
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class SubgraphWindow(QDialog):
    def __init__(self, subgraph, title='Subgraph'):
        super().__init__()
        self.subgraph = subgraph
        self.title = title
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.draw_subgraph()

    def draw_subgraph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        pos = nx.spring_layout(self.subgraph, k=0.5, iterations=100)
        nx.draw(self.subgraph, pos, with_labels=True, node_size=700, node_color='orange', edge_color='red', width=2, font_size=10, ax=ax)
        self.canvas.draw()

class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Crear el grafo desde el archivo Excel
        self.graph = self.create_graph_from_excel('nombres_personas.xlsx')
        self.names = list(self.graph.nodes)

        # Configurar la interfaz de usuario
        self.initUI()

    def create_graph_from_excel(self, excel_file):
        df = pd.read_excel(excel_file, sheet_name='Hoja1')
        personas_A = df['Personas 1'].astype(str).tolist()  # Convertir a cadenas
        personas_B = df['Personas 2'].astype(str).tolist()  # Convertir a cadenas

        G = nx.DiGraph()

        # Conexiones dentro de la columna A
        for persona in personas_A:
            num_conexiones = random.randint(2, 4)
            conexiones = random.sample(personas_A, num_conexiones)
            for conexion in conexiones:
                if persona != conexion:
                    G.add_edge(persona, conexion)

        # Conexiones dentro de la columna B
        for persona in personas_B:
            num_conexiones = random.randint(2, 4)
            conexiones = random.sample(personas_B, num_conexiones)
            for conexion in conexiones:
                if persona != conexion:
                    G.add_edge(persona, conexion)

        # Conexiones entre las columnas A y B
        for persona_A in personas_A:
            num_conexiones = random.randint(2, 4)
            conexiones = random.sample(personas_B, num_conexiones)
            for conexion in conexiones:
                G.add_edge(persona_A, conexion)

        return G

    def initUI(self):
        self.setWindowTitle('Graph Shortest Path Finder')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout()

        self.combo_1_label = QLabel('Origen')
        self.combo_box_1 = QComboBox()
        self.combo_2_label = QLabel('Destino')
        self.combo_box_2 = QComboBox()
        for name in self.names:
            self.combo_box_1.addItem(name)
            self.combo_box_2.addItem(name)

        find_button = QPushButton('Encontrar la conexión más corta')
        find_button.clicked.connect(self.find_shortest_path)

        self.result_label = QLabel('Ruta de Amigos: ')
        self.result_label.setWordWrap(True)

        # Formulario para agregar nueva persona
        form_layout = QFormLayout()
        self.new_person_input = QLineEdit()
        self.connections_spinbox = QSpinBox()
        self.connections_spinbox.setRange(1, 10)
        form_layout.addRow('Nombre de nueva persona:', self.new_person_input)
        form_layout.addRow('Numero de Amigos:', self.connections_spinbox)

        add_person_button = QPushButton('Agregar Persona')
        add_person_button.clicked.connect(self.add_person)

        # Botón para mostrar amigos
        show_friends_button = QPushButton('Mostrar Amigos')
        show_friends_button.clicked.connect(self.show_friends)

        # Barra de progreso para mostrar el porcentaje de cumplimiento de los seis grados de separación
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        # Etiquetas para mostrar el número de casos que cumplen y no cumplen con la teoría
        self.cases_label = QLabel('Casos que cumplen: 0')
        self.non_cases_label = QLabel('Casos que no cumplen: 0')

        left_layout.addWidget(self.combo_1_label)
        left_layout.addWidget(self.combo_box_1)
        left_layout.addWidget(self.combo_2_label)
        left_layout.addWidget(self.combo_box_2)
        left_layout.addWidget(find_button)
        left_layout.addWidget(self.result_label)
        left_layout.addLayout(form_layout)
        left_layout.addWidget(add_person_button)
        left_layout.addWidget(show_friends_button)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.cases_label)
        left_layout.addWidget(self.non_cases_label)

        left_widget.setLayout(left_layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        splitter.addWidget(left_widget)
        splitter.addWidget(self.canvas)

        layout.addWidget(splitter)

        central_widget.setLayout(layout)

        self.draw_graph()
        self.update_progress_bar()

    def draw_graph(self, layout_algo=nx.spring_layout, **kwargs):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        pos = layout_algo(self.graph, **kwargs)
        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color='skyblue', edge_color='gray', font_size=10, ax=ax)
        self.canvas.draw()

    def find_shortest_path(self):
        person1 = self.combo_box_1.currentText()
        person2 = self.combo_box_2.currentText()
        if person1 and person2:
            try:
                shortest_path = nx.dijkstra_path(self.graph, person1, person2)
                self.result_label.setText(f'Conexion: {" -> ".join(shortest_path)}')

                subgraph = self.graph.subgraph(shortest_path).copy()
                self.show_subgraph(subgraph, title='Ruta de Amigos')

            except nx.NetworkXNoPath:
                self.result_label.setText('No existe ruta entre las personas seleccionadas.')

            # Actualizar la barra de progreso
            self.update_progress_bar()

    def add_person(self):
        new_person = self.new_person_input.text()
        num_connections = self.connections_spinbox.value()
        if new_person and new_person not in self.graph:
            self.graph.add_node(new_person)
            self.names.append(new_person)
            self.combo_box_1.addItem(new_person)
            self.combo_box_2.addItem(new_person)
            
            existing_nodes = list(self.graph.nodes)
            existing_nodes.remove(new_person)  # Remove the new person from the list to avoid self-loops
            connections = random.sample(existing_nodes, num_connections)
            for connection in connections:
                self.graph.add_edge(new_person, connection)

            self.draw_graph()
            # Actualizar la barra de progreso
            self.update_progress_bar()

    def show_friends(self):
        selected_person = self.combo_box_1.currentText()
        if selected_person:
            friends = list(self.graph.neighbors(selected_person))
            friends.append(selected_person)  # Include the selected person in the subgraph
            subgraph = self.graph.subgraph(friends).copy()
            self.show_subgraph(subgraph, title=f'{selected_person}\'s Amigos')

    def show_subgraph(self, subgraph, title):
        self.subgraph_window = SubgraphWindow(subgraph, title=title)
        self.subgraph_window.exec_()

    def update_progress_bar(self):
        total_cases = 0
        successful_cases = 0

        for person1 in self.names:
            for person2 in self.names:
                if person1 != person2:
                    total_cases += 1
                    try:
                        if nx.shortest_path_length(self.graph, person1, person2) <= 6:
                            successful_cases += 1
                    except nx.NetworkXNoPath:
                        pass

        non_successful_cases = total_cases - successful_cases

        if total_cases > 0:
            percentage = (successful_cases / total_cases) * 100
        else:
            percentage = 0

        self.progress_bar.setValue(int(percentage))
        self.cases_label.setText(f'Casos que cumplen: {successful_cases}')
        self.non_cases_label.setText(f'Casos que no cumplen: {non_successful_cases}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GraphApp()
    ex.show()
    sys.exit(app.exec_())
