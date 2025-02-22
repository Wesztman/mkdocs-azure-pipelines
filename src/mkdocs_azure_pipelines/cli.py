import argparse
from collections.abc import Sequence

from .ado_pipe_to_md import process_pipeline_file


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="input file")
    parser.add_argument("-o", "--output", help="output file")
    args = parser.parse_args(argv)

    md = process_pipeline_file(args.filename)
    # Write the Markdown content to the output file
    if args.output and md is not None:
        with open(args.output, "w") as output_file:
            output_file.write(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
