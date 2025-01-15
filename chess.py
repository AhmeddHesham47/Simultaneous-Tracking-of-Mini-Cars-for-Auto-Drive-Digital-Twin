import argparse
import cv2
import numpy as np
import svgwrite


def generate_checkerboard(output, rows, cols, square_size):
    # Define A4 size in mm
    A4_WIDTH = 210
    A4_HEIGHT = 297
    
    # Compute the width and height of the checkerboard
    board_width = cols * square_size
    board_height = rows * square_size

    # Ensure it fits within A4 paper
    if board_width > A4_WIDTH or board_height > A4_HEIGHT:
        print("Error: Checkerboard size exceeds A4 dimensions. Reduce rows, columns, or square size.")
        return

    # Center the checkerboard on A4 paper
    x_offset = (A4_WIDTH - board_width) / 2
    y_offset = (A4_HEIGHT - board_height) / 2

    # Create SVG drawing
    dwg = svgwrite.Drawing(output, size=(f"{A4_WIDTH}mm", f"{A4_HEIGHT}mm"))
    dwg.add(dwg.rect(insert=(0, 0), size=(f"{A4_WIDTH}mm", f"{A4_HEIGHT}mm"), fill="white"))

    # Draw checkerboard squares
    for row in range(rows):
        for col in range(cols):
            if (row + col) % 2 == 0:  # Black square
                x0 = x_offset + col * square_size
                y0 = y_offset + row * square_size
                dwg.add(dwg.rect(insert=(f"{x0}mm", f"{y0}mm"), 
                                 size=(f"{square_size}mm", f"{square_size}mm"), 
                                 fill='black'))

    # Save the drawing
    dwg.save()
    print(f"Checkerboard pattern saved to {output}")

def main():
    parser = argparse.ArgumentParser(description="Generate a chessboard or checkerboard pattern for camera calibration.")
    parser.add_argument('-o', '--output', required=True, help='Output file name (e.g., chessboard.svg)')
    parser.add_argument('--rows', type=int, required=True, help='Number of rows in the checkerboard pattern')
    parser.add_argument('--columns', type=int, required=True, help='Number of columns in the checkerboard pattern')
    parser.add_argument('--square_size', type=float, required=True, help='Size of each square in mm')
    args = parser.parse_args()
    
    generate_checkerboard(args.output, args.rows, args.columns, args.square_size)

if __name__ == "__main__":
    main()


# Creating the chessboaard A4
# python chess.py -o chessboard_a4.svg --rows 8 --columns 5 --square_size 37
