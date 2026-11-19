from pathlib import Path
import subprocess
import sys

folder = Path(__file__).parent
program = folder / "some.py"

data_folders = list(folder.rglob("data"))

results = []

print("Found data folders:")
for item in data_folders:
    print(item)

if not data_folders:
    print("No data folder found!")
    sys.exit(1)

for data_folder in data_folders:

    for graph_file in sorted(data_folder.iterdir()):

        if not graph_file.is_file():
            continue

        print("Running:", graph_file.name)

        process = subprocess.run(
            [sys.executable, str(program), str(graph_file)],
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            print("ERROR:", graph_file.name)
            print(process.stderr)
            results.append(graph_file.name + ": ERROR")
            continue

        result = process.stdout.strip()
        results.append(graph_file.name + ": " + result)

with open(folder / "results.txt", "w") as file:
    for result in results:
        file.write(result + "\n")

print("\nFinished!")
print("Results saved:", len(results))
print("File created: results.txt")
