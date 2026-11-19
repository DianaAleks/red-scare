# Red Scare!

This repository contains our solution to the Red Scare! algorithm design project.

## Problem: Some

The task is to determine whether there exists a simple path from the start
vertex s to the target vertex t that contains at least one red vertex.

A simple path cannot visit the same vertex more than once.

## Files

- `some.py`: Main implementation of the algorithm.
- `generate_results.py`: Runs the solution on all supplied graph instances
  and generates `results.txt`.
- `results.txt`: Results for all supplied graph instances.
- `red-scare_documents/data/`: Input graph instances.

## Requirements

- Python 3
- No external Python packages are required.

## Generate results

Run the following command from the repository root:

```bash
python generate_results.py

```
