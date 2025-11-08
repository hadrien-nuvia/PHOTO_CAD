def snap_to_grid(lines, grid_size):
    snapped_lines = []
    for line in lines:
        snapped_line = []
        for point in line:
            snapped_point = (
                round(point[0] / grid_size) * grid_size,
                round(point[1] / grid_size) * grid_size
            )
            snapped_line.append(snapped_point)
        snapped_lines.append(snapped_line)
    return snapped_lines

def snap_to_angles(lines, angles):
    snapped_lines = []
    for line in lines:
        snapped_line = []
        for point in line:
            closest_angle = min(angles, key=lambda angle: abs(angle - point[0]))
            snapped_point = (closest_angle, point[1])
            snapped_line.append(snapped_point)
        snapped_lines.append(snapped_line)
    return snapped_lines

def adjust_lines(lines, grid_size, angles):
    lines = snap_to_grid(lines, grid_size)
    lines = snap_to_angles(lines, angles)
    return lines