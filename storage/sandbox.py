import csv

test = ["hello", "hi", "lol", "bruh"]

file_path = 'test.csv'
with open(file_path, 'w', newline='') as csvfile:  
    writer = csv.writer(csvfile)
    writer.writerow(test)
