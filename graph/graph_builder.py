"""
KnightGraph Graph Builder

Converts a chess position (FEN) into a PyTorch Geometric graph.
"""

import torch
from torch_geometric.data import Data

from graph.node_features import extract_nodes
from graph.edge_builder import build_edges

from graph.graph_schema import (
    NODE_FEATURE_DIM,
    EDGE_FEATURE_DIM,
    GRAPH_FEATURE_DIM,
)


def build_graph(fen, label=None):
    """
    Build a PyTorch Geometric graph from a FEN string.

    Parameters
    ----------
    fen : str
        Chess position in Forsyth–Edwards Notation.

    label : float | int | None
        Optional Stockfish evaluation (White perspective).

    Returns
    -------
    torch_geometric.data.Data
    """

    # --------------------------------------------------
    # Extract nodes
    # --------------------------------------------------

    nodes, square_to_node, board, graph_features = extract_nodes(fen)

    # --------------------------------------------------
    # Build edges
    # --------------------------------------------------

    edges = build_edges(board, square_to_node)

    # --------------------------------------------------
    # Node feature matrix
    # --------------------------------------------------

    x = torch.tensor(
        [node["features"] for node in nodes],
        dtype=torch.float,
    )

    # --------------------------------------------------
    # Edge Index
    # --------------------------------------------------

    if edges:
        edge_index = torch.tensor(
            [
                [edge["source"] for edge in edges],
                [edge["target"] for edge in edges],
            ],
            dtype=torch.long,
        )
    else:
        edge_index = torch.empty((2, 0), dtype=torch.long)

    # --------------------------------------------------
    # Edge Attributes
    # --------------------------------------------------

    if edges:
        edge_attr = torch.tensor(
            [edge["features"] for edge in edges],
            dtype=torch.float,
        )
    else:
        edge_attr = torch.empty(
            (0, EDGE_FEATURE_DIM),
            dtype=torch.float,
        )

    # --------------------------------------------------
    # Graph Features
    # --------------------------------------------------

    graph_features = torch.tensor(
        graph_features,
        dtype=torch.float,
    )

    # --------------------------------------------------
    # Create Graph
    # --------------------------------------------------

    graph = Data(
        x=x,
        edge_index=edge_index,
        edge_attr=edge_attr,
    )

    graph.graph_features = graph_features
    graph.fen = fen

    # --------------------------------------------------
    # Optional Label
    # --------------------------------------------------

    if label is not None:
        graph.y = torch.tensor(
            [label],
            dtype=torch.float,
        )

    # --------------------------------------------------
    # Schema Validation
    # --------------------------------------------------

    assert graph.x.shape[1] == NODE_FEATURE_DIM, (
        f"Expected {NODE_FEATURE_DIM} node features, "
        f"got {graph.x.shape[1]}"
    )

    assert graph.edge_attr.shape[1] == EDGE_FEATURE_DIM, (
        f"Expected {EDGE_FEATURE_DIM} edge features, "
        f"got {graph.edge_attr.shape[1]}"
    )

    assert len(graph.graph_features) == GRAPH_FEATURE_DIM, (
        f"Expected {GRAPH_FEATURE_DIM} graph features, "
        f"got {len(graph.graph_features)}"
    )

    return graph


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    graph = build_graph(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )

    print(graph)
    print()

    print("Node Matrix")
    print(graph.x.shape)

    print()

    print("Edge Index")
    print(graph.edge_index.shape)

    print()

    print("Edge Attributes")
    print(graph.edge_attr.shape)

    print()

    print("Graph Features")
    print(graph.graph_features)

    print()

    print("FEN")
    print(graph.fen)