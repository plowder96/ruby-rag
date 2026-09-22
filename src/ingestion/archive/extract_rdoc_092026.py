# Deprecated after deciding to add classsication to 
# extracted/normalized comment types

from pathlib import Path
import re

RAW_DIR = Path("data/raw/ruby/3.4/")
PROCESSED_DIR = Path("data/processed/ruby/3.4/")

def read_source(path: Path) -> str:
    # Read a source file as UTF-8 text
    return path.read_text(encoding="utf-8")

def extract_rdoc_blocks(source: str) -> list[str]:
    # Extract C-style comment blocks from source file
    pattern = re.compile(
        r"/\*\s*(.*?)\s*\*/",
        re.DOTALL
    )

    blocks = []

    for match in pattern.finditer(source):
        block = match.group(1)

        blocks.append(block)

    return blocks

def normalize_rdoc(text: str) -> str:
    # Clean formatting from an extracted RDock Block
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = re.sub(r"^\s*\*\s?","",line)
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    text = re.sub(r"\n{3,}","\n\n",text)

    return text.strip()

def main():
    source_path = RAW_DIR / "array.c"
    output_path = PROCESSED_DIR / "array_rdoc_blocks.txt"

    print(f"Reading: {source_path}")
    print(f"Writing: {output_path}")

    source = read_source(source_path)
    blocks = extract_rdoc_blocks(source)

    PROCESSED_DIR.mkdir(parents=True,exist_ok=True)

    with output_path.open("w",encoding="utf-8") as output_file:
        output_file.write(f"Source: {source_path}\n")
        output_file.write(f"RDoc blocks found: {len(blocks)}\n\n")


        for index, block in enumerate(blocks, start=1):
            block = normalize_rdoc(block)

            output_file.write("=" * 60)
            output_file.write("\n")
            output_file.write(f"BLOCK {index}\n")
            output_file.write("=" * 60)
            output_file.write("\n")
            output_file.write(block)
            output_file.write("\n\n")

if __name__ == "__main__":
    main()
