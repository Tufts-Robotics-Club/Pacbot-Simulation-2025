
def load_maze(file_path):
    import json
    with open(file_path, 'r') as f:
        maze_data = json.load(f)
    return maze_data

def initialize_simulation(maze_file):
    maze = load_maze(maze_file)
    width = maze['width']
    height = maze['height']
    layout = maze['maze']
    return width, height, layout

