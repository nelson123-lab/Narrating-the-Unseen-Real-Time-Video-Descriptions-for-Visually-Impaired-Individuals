import evaluate

# Load the ROUGE evaluation metric
rouge = evaluate.load('rouge')

# Define the candidate predictions and reference sentences
predictions = ["hello there", "general kenobi"]
references = ["hello there", "general kenobi"]

# Compute the ROUGE score
results = rouge.compute(predictions=predictions, references=references)

# Print the results
print(results)

# Define the candidate predictions and reference sentences
predictions = ["hello there general kenobi", "foo bar foobar"]
references = [["hello there general kenobi", "hello there !"],["foo bar foobar"]]

# Load the BLEU evaluation metric
bleu = evaluate.load("bleu")

# Compute the BLEU score
results = bleu.compute(predictions=predictions, references = references)

# Print the results
print(results)

"""
To evaluate the semantic similarity between the generated caption and the provided descriptions, I'll rate each description on a scale of 1 to 10, with 10 being a perfect match in meaning and 1 being completely unrelated.

"A child in a pink dress is climbing up a set of stairs."

Rating: 6
Reason: The description involves a child (which aligns with "little girl") and the action of climbing, which is somewhat related to standing next to a fence. The details of the dress and the stairs, however, diverge from the generated caption.
"A girl going into a wooden building."

Rating: 4
Reason: This description involves a girl and a wooden structure, which loosely aligns with the wooden fence in the caption. However, the action of going into a building is quite different from standing next to a fence.
"A little girl climbing into a wooden playhouse."

Rating: 5
Reason: This description has a little girl and a wooden element (playhouse), but the action of climbing into a playhouse differs from standing next to a fence.
"A little girl climbing the stairs to her playhouse."

Rating: 5
Reason: Similar to the previous description, it has a little girl and an implied wooden structure (playhouse), but the action (climbing stairs) is different from standing.
"A little girl in a pink dress going into a wooden playhouse."

Rating: 4
Reason: This description includes a little girl and a wooden playhouse, which is somewhat related to the wooden fence. However, the specific actions and additional details (pink dress, going into) differ significantly from the generated caption.
Average = 4.5
"""