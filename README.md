# fadio

Generate a frame-blended animation from a set of images (e.g. img2img loopback output...).

## Usage

- Install requirements: `pip install -r requirements.txt`
  - Note you'll need a working `ffmpeg` installation.
- Run e.g. `python fadio.py -i files/*.png -s -o faded.mp4 -l 400` to
  create a 400-frame animation from all PNG files in the `files` directory (in sorted order).
- See `python fadio.py -h` for more options.
