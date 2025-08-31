def perpendicular_unit_vector(x1, y1, x2, y2, px, py):
    # Direction vector of the segment
    dx = x2 - x1
    dy = y2 - y1

    # Perpendicular vector (normal)
    normal1 = (-dy, dx)   # 90° rotation CCW
    normal2 = (dy, -dx)   # 90° rotation CW

    # Unit normals
    mag = math.hypot(normal1[0], normal1[1])
    if mag == 0:
        raise ValueError("Line segment has zero length")

    unit1 = (normal1[0]/mag, normal1[1]/mag)
    unit2 = (normal2[0]/mag, normal2[1]/mag)

    # Choose the unit vector that points away from (px, py)
    # Vector from (px, py) to (x1, y1)
    to_segment = (x1 - px, y1 - py)
    dot1 = to_segment[0]*unit1[0] + to_segment[1]*unit1[1]
    dot2 = to_segment[0]*unit2[0] + to_segment[1]*unit2[1]

    # You may choose the one with the larger dot product (pointing more "outward")
    if dot1 > dot2:
        result = unit1
    else:
        result = unit2

    return result

def angle_between_lines(x1, y1, x2, y2, px, py):
    # Vector 1: from (x1, y1) to (x2, y2)
    v1 = (x2 - x1, y2 - y1)
    # Vector 2: from (x1, y1) to (px, py)
    v2 = (px - x1, py - y1)
    
    # Calculate dot product and magnitudes
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    
    # Prevent division by zero
    if mag1 == 0 or mag2 == 0:
        raise ValueError("Zero-length vector: cannot define angle")
    
    # Calculate angle in radians
    cos_angle = dot / (mag1 * mag2)
    # Clamp value to avoid floating point errors
    cos_angle = max(min(cos_angle, 1), -1)
    angle_rad = math.acos(cos_angle)
    
    return angle_rad


def find_farthest_side(points, px, py, vx, vy):
    """
    Given a polygon as a list of (x, y) tuples, a point (px, py), and a vector (vx, vy),
    find the side of the polygon that is intersected farthest from (px, py) along the reverse of (vx, vy).
    Returns a tuple (i, j, ix, iy) where (points[i], points[j]) is the farthest side and
    (ix, iy) is the intersection point.
    If no intersection is found, returns None.
    """
    max_t = None
    farthest_side = None
    intersection_point = None
    n = len(points)

    # Reverse the vector
    dir_x, dir_y = -vx, -vy

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]

        # Calculate intersection of ray (px, py) + t*(dir_x, dir_y) with segment (x1, y1)-(x2, y2)
        denom = (dir_x * (y1 - y2) - dir_y * (x1 - x2))
        if abs(denom) < 1e-12:
            continue  # Parallel, skip

        # Solve for t (ray parameter) and u (segment parameter)
        t = ((x1 - px) * (y1 - y2) - (y1 - py) * (x1 - x2)) / denom
        u = ((x1 - px) * dir_y - (y1 - py) * dir_x) / denom

        # For ray, t >= 0 means intersection is along the ray direction (here reversed)
        # For segment, u in [0, 1]
        if t >= 0 and 0 <= u <= 1:
            if max_t is None or t > max_t:
                max_t = t
                farthest_side = (i, (i + 1) % n)
                ix = px + t * dir_x
                iy = py + t * dir_y
                intersection_point = (ix, iy)

    if farthest_side is not None:
        return (*farthest_side, *intersection_point)
    else:
        return None

# Example usage:
if __name__ == "__main__":
    polygon = [(0,0), (4,0), (4,4), (0,4)]
    px, py = 5, 5
    vx, vy = -1, -1  # Ray goes to the left (reverse of vx=1 is -1)
    result = find_farthest_side(polygon, px, py, vx, vy)
    if result:
        i, j, ix, iy = result
        print(f"Farthest side: {polygon[i]} -> {polygon[j]}, intersection at ({ix:.2f}, {iy:.2f})")
    else:
        print("No intersection found")


