
from app.services.embedding_service import split_into_batches


# Test normal batching.
items = list(range(10))

batches = split_into_batches(items, batch_size=3)

assert len(batches) == 4
assert batches[0] == [0, 1, 2]
assert batches[1] == [3, 4, 5]
assert batches[2] == [6, 7, 8]
assert batches[3] == [9]

# Test that no items are lost or duplicated.
flattened = [
    item
    for batch in batches
    for item in batch
]

assert flattened == items

# Test empty input.
assert split_into_batches([], batch_size=3) == []

# Test invalid batch size.
try:
    split_into_batches(items, batch_size=0)
except ValueError:
    pass
else:
    raise AssertionError("Invalid batch size should fail.")

print("Embedding batch offline tests passed!")
