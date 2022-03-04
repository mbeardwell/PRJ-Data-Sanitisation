pattern = ['A', 'D', 'D', 'B']
print("Pattern:\n", pattern)
sequence = ['A', 'D', 'D', 'B', 'C', 'D', 'E', 'G', 'D', 'D', 'E', 'A', 'B', 'D', 'C', 'E', 'F', 'G', 'G', 'C', 'B',
            'E', 'D', 'G']
print("Sequence:\n", sequence)

# remove symbols not used in the pattern
seq_cleaned = []
for sym in sequence:
    if sym in pattern:
        seq_cleaned.append(sym)
print("Removed symbols not used in pattern:\n", seq_cleaned)
