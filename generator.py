import chess
import chess.svg
import random
import cairosvg
import os
import csv
import shutil

folder = "chess_positions"
annotations_file = os.path.join(folder, "annotations.csv")

os.remove(annotations_file) if os.path.exists(annotations_file) else None
shutil.rmtree(folder, ignore_errors=True)
os.makedirs(folder)

def generate_random_position():
    board = chess.Board()
    board.clear_board()
    
    pieces = "RNBQKBNRPPPPPPPP" + "rnbqkbnrpppppppp"
    
    for piece in pieces:
        square = random.choice([sq for sq in chess.SQUARES if board.piece_at(sq) is None])
        board.set_piece_at(square, chess.Piece.from_symbol(piece))
    
    return board.fen()

def fen_to_png(fen, png_file_name):
    board = chess.Board(fen)
    svg = chess.svg.board(board=board, coordinates=False, size=400).encode("utf-8")
    path = os.path.join(folder, f"{png_file_name}.png")
    cairosvg.svg2png(bytestring=svg, write_to=path)

def write_annotations(annotations, annotations_file):
    with open(annotations_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["image", "fen"])
        for image_name, fen in annotations:
            writer.writerow([image_name, fen])

def main():
    annotations = []
    
    for i in range(1000):
        fen = generate_random_position()
        png_file_name = f"chess_position_{i+1}"
        
        fen_to_png(fen, png_file_name)
        annotations.append((png_file_name + ".png", fen))
        
        print(f"Generated {png_file_name}.png")
    
    write_annotations(annotations, annotations_file)

if __name__ == "__main__":
    main()
