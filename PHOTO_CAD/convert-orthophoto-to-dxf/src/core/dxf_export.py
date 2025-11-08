from ezdxf import recover

def export_lines_to_dxf(lines, output_file):
    """
    Exporte une liste de lignes vers un fichier DXF.

    :param lines: Liste de tuples représentant les lignes, où chaque tuple contient
                  les coordonnées des points (x1, y1, x2, y2).
    :param output_file: Chemin du fichier de sortie DXF.
    """
    doc = recover.DXFDocument()
    msp = doc.modelspace()

    for line in lines:
        x1, y1, x2, y2 = line
        msp.add_line(start=(x1, y1), end=(x2, y2))

    doc.saveas(output_file)