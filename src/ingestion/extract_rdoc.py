from pathlib import Path
import re


# ------------------------------------------------------------
# STEP 1: Define where our input and output files live.
# ------------------------------------------------------------

RAW_DIR = Path("data/raw/ruby/3.4")
PROCESSED_DIR = Path("data/processed/ruby/3.4")


# ------------------------------------------------------------
# STEP 2: Read the Ruby source file into memory.
# ------------------------------------------------------------

def read_source(path: Path) -> str:
    """Read a source file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------
# STEP 3: Extract C-style comment blocks.
#
# Ruby's C source contains RDoc inside comments such as:
#
# /*
#  *  call-seq:
#  *    map {|element| ... } -> new_array
#  *
#  *  Description...
#  */
#
# At this stage we are intentionally extracting ALL
# comment blocks. We are not deciding yet whether a block
# is useful documentation.
# ------------------------------------------------------------

def extract_rdoc_blocks(source: str) -> list[str]:
    """Extract C-style comment blocks from a source file."""

    pattern = re.compile(
        r"/\*\s*(.*?)\s*\*/",
        re.DOTALL,
    )

    blocks = []

    for match in pattern.finditer(source):
        block = match.group(1)
        blocks.append(block)

    return blocks


# ------------------------------------------------------------
# STEP 4: Normalize the formatting of an extracted comment.
#
# The source looks like:
#
#     /*
#      *  call-seq:
#      *    map {|element| ... } -> new_array
#      *
#      *  Description...
#      */
#
# We don't want the leading "*" characters in our processed
# documentation.
# ------------------------------------------------------------

def normalize_rdoc(text: str) -> str:
    """Clean formatting from an extracted RDoc block."""

    # Break the comment into individual lines.
    lines = text.splitlines()

    cleaned_lines = []

    # Remove the leading "*" used by C-style comments.
    for line in lines:
        line = re.sub(r"^\s*\*\s?", "", line)
        cleaned_lines.append(line)

    # Put the cleaned lines back together.
    text = "\n".join(cleaned_lines)

    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove whitespace at the beginning/end.
    return text.strip()


# ------------------------------------------------------------
# STEP 5: Classify each documentation block.
#
# We are deliberately starting with a very small classifier.
#
# API_DOC:
#     Documentation containing "call-seq:".
#
# HIDDEN_DOC:
#     Documentation containing ":nodoc:".
#
# OTHER:
#     Everything else.
#
# IMPORTANT:
# We are NOT throwing anything away yet.
# Classification is separate from filtering.
# ------------------------------------------------------------

def classify_rdoc(text: str) -> str:
    """Classify an RDoc block based on simple structural signals."""

    # "call-seq:" is a strong indicator that the block
    # documents a public Ruby method or API.
    if "call-seq:" in text:
        return "API_DOC"

    # ":nodoc:" tells RDoc not to expose the associated
    # documentation as normal public documentation.
    if ":nodoc:" in text:
        return "HIDDEN_DOC"

    # Anything that doesn't match our current rules
    # remains available for later investigation.
    return "OTHER"


# ------------------------------------------------------------
# STEP 6: Write the extracted and classified blocks.
#
# Each block will now contain:
#
#     BLOCK number
#     CLASSIFICATION
#     documentation text
#
# This gives us an artifact we can inspect before deciding
# which categories should eventually enter the RAG corpus.
# ------------------------------------------------------------

def write_classified_blocks(
    blocks: list[str],
    output_path: Path,
    source_path: Path,
) -> None:
    """Write extracted RDoc blocks with classifications."""

    # Make sure the output directory exists.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Open the output file for writing.
    with output_path.open("w", encoding="utf-8") as output_file:

        # Write basic metadata at the top of the file.
        output_file.write(f"Source: {source_path}\n")
        output_file.write(f"RDoc blocks found: {len(blocks)}\n\n")

        # Process each extracted block.
        for index, block in enumerate(blocks, start=1):

            # Clean the extracted source formatting.
            block = normalize_rdoc(block)

            # Determine what kind of documentation block this is.
            classification = classify_rdoc(block)

            # Write a separator so blocks are easy to inspect.
            output_file.write("=" * 60)
            output_file.write("\n")

            # Identify the block.
            output_file.write(f"BLOCK {index}\n")

            # Record our classification.
            output_file.write(f"CLASSIFICATION: {classification}\n")

            output_file.write("=" * 60)
            output_file.write("\n")

            # Write the actual documentation.
            output_file.write(block)
            output_file.write("\n\n")


# ------------------------------------------------------------
# STEP 7: Program entry point.
#
# This ties the individual steps together:
#
#     read source
#          ↓
#     extract comments
#          ↓
#     classify comments
#          ↓
#     write results
# ------------------------------------------------------------

def main():

    # Identify the Ruby source file we're currently studying.
    source_path = RAW_DIR / "array.c"

    # Define the output artifact.
    output_path = PROCESSED_DIR / "array_rdoc_classified.txt"

    # Tell us what the script is doing.
    print(f"Reading: {source_path}")
    print(f"Writing: {output_path}")

    # Read the complete Ruby source file.
    source = read_source(source_path)

    # Extract all C-style comment blocks.
    blocks = extract_rdoc_blocks(source)

    # Write the extracted blocks with classifications.
    write_classified_blocks(
        blocks,
        output_path,
        source_path,
    )

    # Print a simple summary when the script finishes.
    print(f"RDoc blocks extracted: {len(blocks)}")
    print(f"Output written to: {output_path}")


# ------------------------------------------------------------
# STEP 8: Only run main() when this file is executed
# directly.
#
# This allows us to import these functions later without
# automatically running the extraction process.
# ------------------------------------------------------------

if __name__ == "__main__":
    main()
