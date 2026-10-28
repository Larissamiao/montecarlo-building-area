import numpy as np
from matplotlib.path import Path


VERTICES = [
    (10669.9, 29260.9),
    (2535.2, 38971.6),
    (11371.3, 46632.8),
    (17100, 37562),
    (17774.627955335523, 36493.79687236939),
    (19922.633950337397, 36888.48170042025),
    (20209, 38119),
    (21986, 45754.79),
    (32456.4, 42333.4),
    (28446.7, 32389.6),
    (27828.00882402642, 30855.2853840322),
    (29027.657951197798, 29078.278184595707),
    (30672.8, 28903.9),
    (38308.95, 28094.5),
    (35312.95, 16863.4),
    (28662.2, 18624.7),
    (27492.04847879217, 18934.58803883823),
    (26249.47945163677, 17431.443379578497),
    (26710.3, 16312.1),
    (29878.9, 8615.5),
    (18930.2, 5153.22),
    (17851.9, 13078.3),
    (17686.238478122774, 14295.84689214392),
    (15723.352198096172, 14814.55518545673),
    (14894.1, 13907.8),
    (9601, 8120),
    (2823, 15224.5),
    (10669.9, 22054.9),
    (10669.9, 29260.9),
]

CODES = [
    Path.MOVETO,  # Pick up the pen and start here
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.CURVE4,  # A-B curve
    Path.CURVE4,
    Path.CURVE4,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.CURVE4,  # B-C curve
    Path.CURVE4,
    Path.CURVE4,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.CURVE4,  # C-D curve
    Path.CURVE4,
    Path.CURVE4,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.CURVE4,  # D-E curve
    Path.CURVE4,
    Path.CURVE4,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.CLOSEPOLY,  # Close the shape
]


def insert_control_points(vertices, codes):
    """
    For each CURVE4 segment, calculate and insert appropriate control points
    to create a smooth cubic Bezier curve between the start and end points.
    """
    new_vertices = []
    i = 0
    v_idx = 0

    # Tension controls how far the control point stretches.
    # 0.3 to 0.5 is standard for a smooth, natural curve.
    tension = 0.4
    while i < len(codes):
        code = codes[i]

        if code in [Path.MOVETO, Path.LINETO, Path.CLOSEPOLY]:
            # Straight lines and moves just take the exact endpoint
            new_vertices.append(vertices[v_idx])
            v_idx += 1
            i += 1

        elif code == Path.CURVE4:
            # A CURVE4 block requires 3 points: 2 control points + 1 endpoint.
            p_start = np.array(new_vertices[-1])  # Where the curve begins
            p_end = np.array(vertices[v_idx])  # Where the curve ends
            p_prev = np.array(new_vertices[-2])  # The point before the curve
            p_next = np.array(vertices[v_idx + 1])  # The point after the curve

            # Calculate normalized direction vectors
            dir_in = p_start - p_prev
            dir_in_norm = dir_in / np.linalg.norm(dir_in)

            dir_out = p_next - p_end
            dir_out_norm = dir_out / np.linalg.norm(dir_out)

            # Calculate chord length
            chord_len = np.linalg.norm(p_end - p_start)

            # Calculate control points
            cp1 = p_start + dir_in_norm * (chord_len * tension)
            cp2 = p_end - dir_out_norm * (chord_len * tension)

            # Convert them back to tuples when appending to keep the list uniform
            new_vertices.extend(
                [tuple(cp1.tolist()), tuple(cp2.tolist()), tuple(p_end.tolist())]
            )
            v_idx += 1
            i += 3
        else:
            raise ValueError(f"Unsupported path code: {code}")
    return new_vertices


def build_rough_floorplan_domain():
    """
    Constructs a roughly estimated boundary of the floor plan
    based on visual extraction (normalized 0-100 scale).
    """

    # path = Path(vertices, codes)
    vert = np.array(VERTICES)
    bbox_area = np.prod(vert.max(axis=0) - vert.min(axis=0))

    vert = (vert - vert.min(axis=0)) / (
        vert.max(axis=0) - vert.min(axis=0)
    )  # Normalize to 0-1 range
    path = Path(vert, CODES)
    return path, bbox_area.item()


if __name__ == "__main__":
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    ppath = build_rough_floorplan_domain()
    fig, ax = plt.subplots(figsize=(8, 8))
    patch = mpatches.PathPatch(ppath[0], facecolor="lightblue", edgecolor="black")
    ax.add_patch(patch)
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_aspect("equal")
    plt.title("Rough Floor Plan Domain")
    plt.show()
