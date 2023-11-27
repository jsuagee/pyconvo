

def do_no_preprocessing(line):
    return line

# Commas seem to introduce too long of a delay in the speaker's delivery.
def remove_commas(line):
    return line.replace(',', '')

def remove_markup_in_parenthesis(line):
    # Removes things like "(sighs)" in a speaker's lines. (What are these called?)
    # TODO: fill this out. Right now does nothing.
    output = []
    i = 0
    while i < len(line):
        a = line[i]
        if a == '(':
            j = i + 1
            b = line[j]
            while b != ")":
                j += 1
                b = line[j]
            i = j
        else:
            output.append(a)
        i += 1
    return "".join(output)

def remove_markup_and_commas(line):
    line = remove_markup_in_parenthesis((line))
    return remove_commas(line)

# Run test cases:
if __name__ == "__main__":
    test_cases = {"()xyz()": "xyz",
                  "xy(z)": "xy",
                  "x()()yz": "xyz",
                  "x(yz)w(xy)z": "xwz"}

    for input in test_cases.keys():
        output = remove_markup_in_parenthesis(input)
        if output == test_cases[input]:
            print(f"Passed: '{input}' mapped to '{output}'")
        else:
            print(f"Failed: '{input}' mapped to '{output}'")

