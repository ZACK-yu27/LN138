long_text = """Life is a journey filled with countless twists and turns, //
moments of joy and sorrow, success and failure. //
Along the way, we meet different people, //
experience various things, and learn valuable lessons that shape who we are. //
Every challenge we face is not meant to break us but to build our strength and resilience. //
Every mistake teaches us to be more careful and thoughtful in the future. //
We often rush through days without pausing to appreciate the small beauties around us—the warm sunlight through the window, //
the sound of birds singing in the morning, the smile of a friend, //
or the quiet peace of a calm evening. //
It is important to slow down, breathe deeply, and cherish the present moment because time passes quickly and never returns. //
No matter how difficult the road may seem, there is always hope ahead. We should keep moving forward with courage, //
kindness, and a positive attitude, believing that better days are coming and that every effort we make will eventually pay off."""

words = long_text.split()
import string
punctuation = string.punctuation +string.whitespace
words = [word.strip(punctuation) for word in words]
print("单词列表:", words)
print(f"总字数为{len(words)}个")