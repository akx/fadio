import argparse

import ffmpeg
from PIL import Image
import numpy as np


def draw_array_histo(arr: np.array, characters: str = " ▁▂▃▄▅▆▇█") -> str:
    norm_arr = (arr - arr.min()) / (arr.max() - arr.min())
    norm_arr = (norm_arr * (len(characters) - 1)).astype(int)
    return "".join(characters[i] for i in norm_arr)


def compute_weights(
    frame_index: int,
    frame_count: int,
    weight_count: int,
    influence_width: float,
) -> np.array:
    pos = frame_index / (frame_count - 1)
    # Compute blend weights for each input frame according to `pos` (0..1) using influence_width
    weights = np.exp(
        -(((np.arange(weight_count) / (weight_count - 1) - pos) / influence_width) ** 2)
    )
    weights /= weights.sum()
    assert np.isclose(weights.sum(), 1)
    return weights


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", nargs="+", help="Input file(s)")
    ap.add_argument("-o", "--output", required=True, help="Output file")
    ap.add_argument("-r", "--frame-rate", type=int, default=24, help="Frame rate")
    ap.add_argument(
        "-l", "--length", type=int, required=True, help="Length of output in frames"
    )
    ap.add_argument("-s", "--sort-input", action="store_true", help="Sort input")
    ap.add_argument(
        "--influence-width",
        type=float,
        default=0.07,
        help="Width of influence zone (the larger, the blendier the output)",
    )
    args = ap.parse_args()
    filenames = list(args.input)
    if args.sort_input:
        filenames.sort()
    in_frames = [Image.open(f).convert("RGB") for f in filenames]
    print(f"Read {len(in_frames)} frames")
    output_size = min(f.size for f in in_frames)
    print(f"Resizing to {output_size}")
    in_frames = [np.array(f.resize(output_size)).astype(float) for f in in_frames]
    width, height = output_size
    writer = (
        ffmpeg.input("pipe:", format="rawvideo", pix_fmt="rgb24", s=f"{width}x{height}")
        .output(args.output, pix_fmt="yuv420p", r=args.frame_rate)
        .overwrite_output()
    )
    length = args.length
    with writer.run_async(pipe_stdin=True) as proc:
        for i in range(length):
            weights = compute_weights(
                frame_index=i,
                frame_count=length,
                weight_count=len(in_frames),
                influence_width=args.influence_width,
            )
            print(f"{i:4d}/{length:4d} [{draw_array_histo(weights)}]", end="\r")
            out_frame = np.tensordot(weights, in_frames, axes=1)
            proc.stdin.write(out_frame.astype(np.uint8).tobytes())


if __name__ == "__main__":
    main()
