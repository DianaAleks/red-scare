from pathlib import Path
from some import solve_some


def main():
    project_dir = Path(__file__).resolve().parent
    data_dir = project_dir / "red-scare_documents" / "data"
    output_file = project_dir / "results.txt"

    graph_files = sorted(data_dir.glob("*.txt"))

    if not graph_files:
        raise FileNotFoundError("No graph files found in the data folder.")

    results = []
    errors = []

    for graph_file in graph_files:
        try:
            answer = solve_some(str(graph_file))
            results.append(
                f"{graph_file.name}: {str(answer).lower()}"
            )
        except Exception as error:
            errors.append((graph_file.name, str(error)))

    if errors:
        print("Errors occurred. Results file was not updated.")
        for name, error in errors:
            print(f"{name}: {error}")
        return

    output_file.write_text(
        "\n".join(results) + "\n",
        encoding="utf-8"
    )

    print(f"Processed {len(results)} graph files.")
    print(f"Results saved to {output_file.name}.")


if __name__ == "__main__":
    main()
