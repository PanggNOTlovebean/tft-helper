import json
augment_rank_map = {}
with open('../../data/stat/augments.json', 'r', encoding='utf-8') as f:
    augment_rank_map = json.load(f)

word_dict = set()
for key in augment_rank_map.keys():
    for c in key:
        word_dict.add(c)

print(word_dict)
for i in range(10):
    word_dict.add(str(i))

word_dict.add('-')
word_dict.remove(' ')
with open('../../data/stat/rapid_ocr_dict.txt', 'w', encoding='utf-8') as f:
    for word in sorted(word_dict):
        f.write(f"{word}\n")

