

def do_no_preprocessing(line):
    return line

# Commas seem to introduce too long of a delay in the speaker's delivery.
def remove_commas(line):
    return line.replace(',', '')

def remove_markup_in_parenthesis(line):
    # Removes things like "(sighs)" in a speaker's lines. (What are these called?)
    # TODO: fill this out. Right now does nothing.
    return line

