def generateQuestionMarksForIn(length: int = 1):
    return f"({','.join(['?' for i in range(length)])})"
