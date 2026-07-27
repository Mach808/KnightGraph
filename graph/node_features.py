import chess

# -----------------------------
# Piece One-Hot Encodings
# -----------------------------
PIECE_TO_ONEHOT = {
    chess.PAWN:   [1, 0, 0, 0, 0, 0],
    chess.KNIGHT: [0, 1, 0, 0, 0, 0],
    chess.BISHOP: [0, 0, 1, 0, 0, 0],
    chess.ROOK:   [0, 0, 0, 1, 0, 0],
    chess.QUEEN:  [0, 0, 0, 0, 1, 0],
    chess.KING:   [0, 0, 0, 0, 0, 1],
}

PIECE_NAMES = {
    chess.PAWN: "Pawn",
    chess.KNIGHT: "Knight",
    chess.BISHOP: "Bishop",
    chess.ROOK: "Rook",
    chess.QUEEN: "Queen",
    chess.KING: "King",
}


def extract_nodes(fen: str):
    """
    Converts a FEN position into graph nodes.

    Returns
    -------
    nodes : list[dict]
        List of node dictionaries.

    square_to_node : dict
        Maps python-chess square -> node id.

    board : chess.Board
        Board object used by edge_builder.

    graph_features : list
        Graph-level features.
    """

    board = chess.Board(fen)

    nodes = []
    square_to_node = {}

    # -----------------------------
    # Graph Features
    # -----------------------------

    side_to_move = 1 if board.turn == chess.WHITE else 0

    white_kingside = int(board.has_kingside_castling_rights(chess.WHITE))
    white_queenside = int(board.has_queenside_castling_rights(chess.WHITE))

    black_kingside = int(board.has_kingside_castling_rights(chess.BLACK))
    black_queenside = int(board.has_queenside_castling_rights(chess.BLACK))

    if board.ep_square is not None:
        ep_available = 1
        ep_file = chess.square_file(board.ep_square) / 7.0
    else:
        ep_available = 0
        ep_file = -1.0

    graph_features = [
        side_to_move,
        white_kingside,
        white_queenside,
        black_kingside,
        black_queenside,
        ep_available,
        ep_file,
    ]

    # -----------------------------
    # Node Extraction
    # -----------------------------

    node_id = 0

    for square in chess.SQUARES:

        piece = board.piece_at(square)

        if piece is None:
            continue

        file = chess.square_file(square) / 7.0
        rank = chess.square_rank(square) / 7.0

        color = 1 if piece.color == chess.WHITE else 0

        features = (
            PIECE_TO_ONEHOT[piece.piece_type]
            + [
                color,
                file,
                rank,
            ]
        )

        node = {
            "node_id": node_id,
            "piece_type": piece.piece_type,
            "piece_name": PIECE_NAMES[piece.piece_type],
            "color": piece.color,
            "color_name": "White" if piece.color else "Black",
            "square": square,
            "file": file,
            "rank": rank,
            "features": features,
        }

        nodes.append(node)
        square_to_node[square] = node_id

        node_id += 1

    return nodes, square_to_node, board, graph_features


def print_nodes(nodes):
    print("=" * 70)

    for node in nodes:
        print(
            f"Node {node['node_id']:2d} | "
            f"{node['color_name']:5s} "
            f"{node['piece_name']:6s} | "
            f"{chess.square_name(node['square'])} | "
            f"{node['features']}"
        )

    print("=" * 70)


if __name__ == "__main__":

    START_FEN = chess.STARTING_FEN

    nodes, square_to_node, board, graph_features = extract_nodes(START_FEN)

    print_nodes(nodes)

    print("\nGraph Features")
    print(graph_features)