text = "வணக்கம் hello"
has_tamil = any('\u0B80' <= c <= '\u0BFF' for c in text)
print("HAS TAMIL:", has_tamil)
