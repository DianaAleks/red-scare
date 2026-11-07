
from pathlib import Path

from graph_loader import load_graph
from alternate import alternate
from few import few
from many import many
from none import none
from some import solve_some

def main():
    data_folder = Path("red-scare_documents/data")
    output_file = Path("result_table.txt")
    with open(output_file, "w") as out:
            for filename in sorted(data_folder.iterdir()):
                if filename.is_file() and not filename.name.startswith("README"):
                    with open(filename) as f:
                        first_line = f.readline()
                        first_number = int(first_line.split()[0])

                    if first_number >= 500:
                        graph, s, t, red = load_graph(filename)

                        alternate_result = alternate(graph, s, t, red)
                        few_result = few(graph, s, t, red)
                        many_result = many(graph, s, t, red)
                        none_result = none(graph, s, t, red)
                        some_result = solve_some(filename)

                        line = (
                            f"{filename.stem} & "
                            f"{first_number} & "
                            f"{alternate_result} & "
                            f"{few_result} & "
                            f"{many_result} & "
                            f"{none_result} & "
                            f"{some_result} \\\\\n"
                        )

                        out.write(line)

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()