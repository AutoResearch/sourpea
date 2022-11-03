from sourpea.primitives import Level, Factor, Design

# counterbalance 1
# sequence to test on
test_sequence_1 = [
    {'word': 'red', 'color': 'red'},
    {'word': 'green', 'color': 'red'},
    {'word': 'red', 'color': 'green'},
    {'word': 'green', 'color': 'green'},
]

# defining the factors
word = Factor('word', ['red', 'green'])
color = Factor('color', ['red', 'green'])

# defining the design (counterbalancing)
design = Design([word, color])

# getting the results
chisquare = design.test(test_sequence_1)
print('sequence1, design1: ', chisquare.pvalue)

# counterbalance with weighted factors
# sequence to test on
test_sequence_2 = [
    {'word': 'red', 'color': 'red'},
    {'word': 'green', 'color': 'red'},
    {'word': 'red', 'color': 'red'},
    {'word': 'green', 'color': 'green'},
    {'word': 'red', 'color': 'green'},
    {'word': 'red', 'color': 'green'}
]

# defining the factors
word_2 = Factor('word', [Level('red', 2), 'green'])
color_2 = Factor('color', ['red', 'green'])

# defining the design
design_2 = Design([color_2, word_2])

# getting the result
chisquare_2 = design_2.test(test_sequence_2)
print('sequence2, design2: ', chisquare_2.pvalue)

# counterbalance with more weights
# sequence to test on
test_sequence_3 = [
    {'word': 'red', 'color': 'green'},
    {'word': 'red', 'color': 'green'},
    {'word': 'red', 'color': 'green'},
    {'word': 'red', 'color': 'green'},
    {'word': 'red', 'color': 'green'},
    {'word': 'red', 'color': 'green'},
    {'word': 'red', 'color': 'red'},
    {'word': 'red', 'color': 'red'},
    {'word': 'red', 'color': 'red'},
    {'word': 'red', 'color': 'red'},
    {'word': 'green', 'color': 'green'},
    {'word': 'green', 'color': 'green'},
    {'word': 'green', 'color': 'green'},
    {'word': 'green', 'color': 'red'},
    {'word': 'green', 'color': 'red'},
]

# defining factors
word_3 = Factor('word', [Level('red', 2), Level('green', 1)])
color_3 = Factor('color', [Level('red', 2), Level('green', 3)])

# defining design
design_3 = Design([word_3, color_3])

# getting the results
chisquare_3 = design_3.test(test_sequence_3)
print('sequence3, design3: ', chisquare_3.pvalue)

# cross validating (this should result in lower p-values)
chisquare_ = design.test(test_sequence_2)
print('sequence2, design1: ', chisquare_.pvalue, 'not balanced')

chisquare_2_ = design_2.test(test_sequence_1)
print('sequence1, design2: ', chisquare_2_.pvalue, 'not balanced')
