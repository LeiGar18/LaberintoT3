import tkinter as tk
import time

maze = [
    [1, 1, 1, 3, 0, 1, 1, 1, 4], 
    [3, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 0, 1],
    [0, 1, 0, 1, 0, 0, 1, 0, 1], 
    [1, 1, 1, 1, 1, 1, 3, 1, 1],
    [3, 0, 1, 0, 0, 0, 1, 0, 1], 
    [1, 1, 1, 1, 3, 1, 1, 1, 1], 
    [1, 0, 0, 1, 0, 1, 0, 0, 4], 
    [1, 1, 3, 1, 0, 1, 1, 1, 1]
]
N = 9
START = (0, 0)    # Rojo, arriba-izquierda
END = (8, 0)      # Verde, abajo-izquierda
directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

CELL_SIZE = 50

COLORS = {
    "wall": "#7a7a7a",
    "normal": "#ffffff",
    "bonus3": "#ffd966",
    "bonus4": "#00c853",
    "start": "#e74c3c",   # Rojo
    "end": "#2ecc40",     # Verde
    "visit": "#51a4ff",
    "backtrack": "#ffd6d6",
    "finalpath": "#ffe066",
    "altpath": "#9afffc"
}

def cell_points(i, j):
    return 3 if maze[i][j] == 3 else (4 if maze[i][j] == 4 else 0)

class MazeGUI:
    def _init_(self, maze):
        self.original_maze = [row[:] for row in maze]
        self.reset_variables()
        self.root = tk.Tk()
        self.root.title("Laberinto del Ratón - Backtracking Visual Avanzado")

        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack()
        self.canvas = tk.Canvas(self.top_frame, width=N*CELL_SIZE, height=N*CELL_SIZE+60)
        self.canvas.pack(side=tk.LEFT)
        self.controls_frame = tk.Frame(self.top_frame)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Label(self.controls_frame, text="Velocidad de animación (ms)").pack(pady=5)
        self.speed_var = tk.IntVar(value=120)
        self.speed_slider = tk.Scale(self.controls_frame, from_=10, to=1000, orient=tk.HORIZONTAL,
                                     variable=self.speed_var, length=140)
        self.speed_slider.pack(pady=5)

        self.start_btn = tk.Button(self.controls_frame, text="Iniciar Recorrido (Primer Camino)", command=self.start_search)
        self.start_btn.pack(pady=10)

        self.all_btn = tk.Button(self.controls_frame, text="Mostrar Todos los Caminos", command=self.show_all_paths)
        self.all_btn.pack(pady=10)

        self.reset_btn = tk.Button(self.controls_frame, text="Reiniciar", command=self.reset_maze)
        self.reset_btn.pack(pady=10)

        self.points_label = self.canvas.create_text(N*CELL_SIZE//2, N*CELL_SIZE+30, text="Puntos: 0", font=('Arial', 15))
        self.message_label = None

        self.point_labels = [[None]*N for _ in range(N)]
        self.draw_maze()
        self.root.mainloop()

    def reset_variables(self):
        self.maze = [row[:] for row in self.original_maze]
        self.visited = [[False]*N for _ in range(N)]
        self.visited_points = [[False]*N for _ in range(N)]
        self.path = []
        self.found = False
        self.total_points = 0
        self.all_paths = []
        self.point_labels = [[None]*N for _ in range(N)]
        self.showing_all = False

    def draw_maze(self):
        self.canvas.delete("all")
        for i in range(N):
            for j in range(N):
                x0, y0 = j*CELL_SIZE, i*CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                value = self.maze[i][j]
                if value == 0:
                    color = COLORS["wall"]
                elif value == 3:
                    color = COLORS["bonus3"]
                elif value == 4:
                    color = COLORS["bonus4"]
                else:
                    color = COLORS["normal"]
                if (i, j) == START:
                    color = COLORS["start"]
                if (i, j) == END:
                    color = COLORS["end"]
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")
                # Solo mostrar "F", "I", "3", "4"
                if (i, j) == START:
                    self.canvas.create_text(x0+CELL_SIZE//2, y0+CELL_SIZE//2, text="F", font=('Arial', 16, 'bold'))
                elif (i, j) == END:
                    self.canvas.create_text(x0+CELL_SIZE//2, y0+CELL_SIZE//2, text="I", font=('Arial', 16, 'bold'))
                elif value == 3 or value == 4:
                    self.canvas.create_text(x0+CELL_SIZE//2, y0+CELL_SIZE//2, text=str(value), font=('Arial', 14, 'bold'))
        self.points_label = self.canvas.create_text(N*CELL_SIZE//2, N*CELL_SIZE+30, text="Puntos: 0", font=('Arial', 15))
        self.point_labels = [[None]*N for _ in range(N)]
        self.root.update()

    def color_cell(self, i, j, color, show_points=None):
        x0, y0 = j*CELL_SIZE, i*CELL_SIZE
        x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")
        value = self.maze[i][j]
        if (i, j) == START:
            self.canvas.create_text(x0+CELL_SIZE//2, y0+CELL_SIZE//2, text="F", font=('Arial', 16, 'bold'))
        elif (i, j) == END:
            self.canvas.create_text(x0+CELL_SIZE//2, y0+CELL_SIZE//2, text="I", font=('Arial', 16, 'bold'))
        elif value == 3 or value == 4:
            self.canvas.create_text(x0+CELL_SIZE//2, y0+CELL_SIZE//2, text=str(value), font=('Arial', 14, 'bold'))
        if show_points is not None:
            if self.point_labels[i][j]:
                self.canvas.delete(self.point_labels[i][j])
            self.point_labels[i][j] = self.canvas.create_text(
                x0+CELL_SIZE//2, y0+CELL_SIZE-10, text=f"{show_points}", font=('Arial', 9), fill="#0b47a1"
            )
        self.root.update()

    def update_points(self, points):
        self.canvas.itemconfig(self.points_label, text=f"Puntos acumulados: {points}")

    def start_search(self):
        self.reset_maze()
        self.start_btn.config(state=tk.DISABLED)
        self.all_btn.config(state=tk.DISABLED)
        self.found = False
        self.path = []
        self.total_points = 0
        self.visited = [[False]*N for _ in range(N)]
        self.visited_points = [[False]*N for _ in range(N)]
        self.point_labels = [[None]*N for _ in range(N)]
        self.draw_maze()
        if self.message_label:
            self.canvas.delete(self.message_label)
        self.root.after(200, lambda: self.backtrack_first(START[0], START[1], 0, []))

    def backtrack_first(self, x, y, points, path):
        if self.found:
            return
        self.visited[x][y] = True
        added = 0
        # Sumar puntos solo la primera vez que piso un 3 o 4
        if not self.visited_points[x][y] and cell_points(x, y) > 0:
            added = cell_points(x, y)
            points += added
            self.visited_points[x][y] = True

        if (x, y) != START and (x, y) != END:
            self.color_cell(x, y, COLORS["visit"], show_points=points)
        self.update_points(points)
        self.root.update()
        time.sleep(self.speed_var.get()/1000.0)

        if (x, y) == END:
            if points > 23:
                self.found = True
                self.path = path + [(x, y)]
                self.total_points = points
                self.show_path(COLORS["finalpath"])
                self.message_label = self.canvas.create_text(N*CELL_SIZE//2, N*CELL_SIZE//2, text="¡Camino exitoso!", font=('Arial', 22, 'bold'), fill="blue")
            else:
                self.color_cell(x, y, COLORS["end"])
            self.visited[x][y] = False
            if added > 0:
                self.visited_points[x][y] = False
            return

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and self.maze[nx][ny] != 0 and not self.visited[nx][ny]:
                self.backtrack_first(nx, ny, points, path + [(x, y)])
                if self.found:
                    return

        if not self.found and (x, y) != START and (x, y) != END:
            self.color_cell(x, y, COLORS["backtrack"])
        self.visited[x][y] = False
        if added > 0:
            self.visited_points[x][y] = False
        if (x, y) == START and not self.found:
            self.message_label = self.canvas.create_text(N*CELL_SIZE//2, N*CELL_SIZE//2, text="No se encontró camino suficiente", font=('Arial', 19, 'bold'), fill="red")
        self.start_btn.config(state=tk.NORMAL)
        self.all_btn.config(state=tk.NORMAL)

    def show_path(self, color):
        for (i, j) in self.path:
            if (i, j) != START and (i, j) != END:
                self.color_cell(i, j, color)
            self.root.update()
            time.sleep(0.06)

    def show_all_paths(self):
        self.reset_maze()
        self.start_btn.config(state=tk.DISABLED)
        self.all_btn.config(state=tk.DISABLED)
        self.all_paths = []
        self.find_all_paths(START[0], START[1], 0, [], [[False]*N for _ in range(N)], [[False]*N for _ in range(N)])
        if not self.all_paths:
            self.message_label = self.canvas.create_text(N*CELL_SIZE//2, N*CELL_SIZE//2, text="No hay caminos suficientes", font=('Arial', 19, 'bold'), fill="red")
        else:
            for path, pts in self.all_paths:
                self.update_points(pts)
                for (i, j) in path:
                    if (i, j) != START and (i, j) != END:
                        self.color_cell(i, j, COLORS["altpath"], show_points=pts)
                    self.root.update()
                    time.sleep(self.speed_var.get()/1000.0)
                for (i, j) in path:
                    if (i, j) != START and (i, j) != END:
                        self.color_cell(i, j, COLORS["finalpath"])
                self.root.update()
                time.sleep(0.5)
            self.message_label = self.canvas.create_text(N*CELL_SIZE//2, N*CELL_SIZE//2, text=f"Total caminos: {len(self.all_paths)}", font=('Arial', 17, 'bold'), fill="purple")
        self.start_btn.config(state=tk.NORMAL)
        self.all_btn.config(state=tk.NORMAL)

    def find_all_paths(self, x, y, points, path, visited, visited_points):
        if (x, y) == END:
            if points > 23:
                self.all_paths.append((path + [(x, y)], points))
            return
        visited[x][y] = True
        added = 0
        if not visited_points[x][y] and cell_points(x, y) > 0:
            added = cell_points(x, y)
            points += added
            visited_points[x][y] = True

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and self.maze[nx][ny] != 0 and not visited[nx][ny]:
                self.find_all_paths(nx, ny, points, path + [(x, y)], visited, visited_points)
        visited[x][y] = False
        if added > 0:
            visited_points[x][y] = False

    def reset_maze(self):
        self.reset_variables()
        self.draw_maze()
        if self.message_label:
            self.canvas.delete(self.message_label)
        self.update_points(0)

if _name_ == "_main_":
    MazeGUI(maze)