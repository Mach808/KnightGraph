import chess

# -----------------------------
# Edge One-Hot Encodings
# -----------------------------

EDGE_FEATURES = {
    "attack": [1, 0],
    "defend": [0, 1],
}


def build_edges(board, square_to_node):
    """
    Builds graph edges from a chess.Board.

    Parameters
    ----------
    board : chess.Board

    square_to_node : dict
        Maps board square -> node id

    Returns
    -------
    edges : list[dict]
    """

    edges = []

    for source_square in chess.SQUARES:

        source_piece = board.piece_at(source_square)

        if source_piece is None:
            continue

        source_node = square_to_node[source_square]

        for target_square in board.attacks(source_square):

            target_piece = board.piece_at(target_square)

            if target_piece is None:
                continue

            target_node = square_to_node[target_square]

            # -------------------------
            # Determine edge type
            # -------------------------

            if source_piece.color == target_piece.color:
                edge_type = "defend"
            else:
                edge_type = "attack"

            edge = {
                "source": source_node,
                "target": target_node,
                "features": EDGE_FEATURES[edge_type],
            }

            edges.append(edge)

    return edges


def print_edges(edges):
    print("=" * 60)

    for edge in edges:
        print(
            f"{edge['source']:2d}"
            f"  --->  "
            f"{edge['target']:2d}"
            f"   {edge['features']}"
        )

    print("=" * 60)


if __name__ == "__main__":

    from node_features import extract_nodes

    nodes, square_to_node, board, graph_features = extract_nodes(
        chess.STARTING_FEN
    )

    edges = build_edges(board, square_to_node)

    print_edges(edges)