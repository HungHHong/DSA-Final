
# use to make small sample of rating for testing
input_file = "../data/ratings.csv"
output_file = "../data/ratings_sample.csv"


with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for i, line in enumerate(infile):
        if i > 10000:
            break
        outfile.write(line)

print("ratings_sample.csv created!")