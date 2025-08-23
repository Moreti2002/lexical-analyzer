

def read_file(name: str) -> list:
    """
    Read txt file
    """
    file = open(file=name).readlines()

    return file

def validate_parentheses(expression: str) -> bool:
    """
    Validate if the parentheses in the expression are balanced
    """
    counter = 0
    for char in expression:
        if char == "(":
            counter += 1
        elif char == ")":
            counter -= 1
            if counter < 0:
                return False
    return counter == 0

if __name__ == "__main__":
    file = "rpn.txt"
    print(read_file(file))