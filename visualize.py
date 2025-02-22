from plotparlament import main, plot_deputies

def visualize_parlament(parties: list, num_rows: int, initial_radius: int, radius_increment: int, point_size: int):
    num_deputies = sum(p.size for p in parties)

    deputies = main(num_rows, initial_radius, radius_increment, num_deputies)
    plot_deputies(deputies, parties, point_size)