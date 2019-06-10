def num_to_word(num):
    # convert numbers to japanese
    nums_00_10 = ['zero','ichi','ni','san','yon','go',
                  'roku','nana','hachi', 'kyu','zyu']

    nums_dict  = {10: 'ju', 100: 'hyaku', 1000: 'sen', 10000:'man'}

    if num <= 10:
        return nums_00_10[num]

    elif num > 100000000:
        return 'too large number'

    max_key = max([key for key in nums_dict.keys() if key <= num])

    return num_to_word(num//max_key) + ' ' + nums_dict[max_key] + \
      ('' if num % max_key == 0 else ' ' + num_to_word(num % max_key))


def extract_sline(line, key1, key2):
    # extract data from single line
    data = ''

    start = line.find(key1)
    end   = line.find(key2)

    if (start != -1) and (end != 1):
        start = start + len(key1)
        line = line[start:end]
        line = line.strip()
        data = line

    return data


def extract_mline(lines, key1, key2):
    # extract data from multi lines
    data  = ''
    match = False

    for line in lines:
        if key2 in line:
            match = False

        if match:
            data += line

        if key1 in line:
            match = True
            data = ''

    return data


def filter_doc(doc):
    # filter and edit documnets

    filtered = []

    words = doc.split()
    for word in words:
        if word.isdigit():
            word = word + ' ' + num_to_word(int(word))

        filtered.append(word)

    return ' '.join(filtered)


def count_int(doc):

    tmp_doc = doc.replace('\n', '').split()
 
    counter = 0

    for word in tmp_doc:
        if word.isdigit():
            counter += int(word)

    return counter


