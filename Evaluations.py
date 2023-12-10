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
results = bleu.compute(predictions=predictions, references=references)

# Print the results
print(results)