import chess
from graph.graph_builder import build_graph

# --------------------------------------------------
# Test Positions
# --------------------------------------------------

TEST_POSITIONS = {
    "Starting Position":
        chess.STARTING_FEN,

    "Italian Opening":
        "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 2 3",

    "Capture Available":
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",

    "Kings Only":
        "8/8/8/3k4/8/8/4K3/8 w - - 0 1",

    "Simple Endgame":
        "8/8/8/8/8/4k3/3p4/4K3 w - - 0 1",

    "Castling Available":
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",

    "No Castling":
        "r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1",

    "En Passant":
        "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3",

    "Promotion Ready":
        "4k3/P7/8/8/8/8/7p/4K3 w - - 0 1",

    "Check Position":
        "4k3/8/8/8/8/8/4Q3/4K3 b - - 0 1",
}


def validate(name, fen):

    print("=" * 70)
    print(name)
    print("=" * 70)

    graph = build_graph(fen)

    board = chess.Board(fen)

    print(board)
    print()

    print("FEN:")
    print(fen)
    print()

    print(f"Nodes           : {graph.x.shape[0]}")
    print(f"Node Features   : {graph.x.shape}")

    print(f"Edges           : {graph.edge_index.shape[1]}")
    print(f"Edge Features   : {graph.edge_attr.shape}")

    attack_edges = 0
    defend_edges = 0

    for edge in graph.edge_attr.tolist():

        if edge == [1.0, 0.0]:
            attack_edges += 1

        elif edge == [0.0, 1.0]:
            defend_edges += 1

    print(f"Attack Edges    : {attack_edges}")
    print(f"Defend Edges    : {defend_edges}")

    print()

    print("Graph Features")

    names = [
        "Side to Move",
        "White KS",
        "White QS",
        "Black KS",
        "Black QS",
        "EP Available",
        "EP File",
    ]

    for name, value in zip(names, graph.graph_features.tolist()):
        print(f"{name:18}: {value}")

    print()


if __name__ == "__main__":

    for name, fen in TEST_POSITIONS.items():
        validate(name, fen)