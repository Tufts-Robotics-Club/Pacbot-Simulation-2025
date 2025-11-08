def load_maze(file_path):
    import json
    try:
        with open(file_path, 'r') as f:
            maze_data = json.load(f)
        return maze_data
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        

def initialize_simulation(maze_file):
    maze = load_maze(maze_file)
    width = maze['width']
    height = maze['height']
    layout = maze['maze']
    return width, height, layout