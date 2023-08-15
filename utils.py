
from textwrap import TextWrapper

'''
def wordwrap(s, line_length):
    words = s.split(" ")
    line = ""
    lines = []
    while len(words) > 0:
        while len(line) < line_length:
            word = words[0]
            if len(line) + len(word) < line_length:
                line += " " + word
                words = words[1:]
            else:

        lines.append(line)
        line = ""
    return "\n".join(lines)
'''

if __name__ == "__main__":

    s = "Juliet: Well, that's a pretty dismissive view, John. Romance literature can be quite complex and explores themes of love, identity, and societal expectations."

    tw = TextWrapper(width=80)
    print(tw.fill(s))




