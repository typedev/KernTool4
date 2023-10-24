t = "􀈂􀈃􀈄"

names = """
square.and.arrow.up
square.and.arrow.up.fill
square.and.arrow.down
"""

names = [n.strip() for n in names.split("\n") if n]

assert len(t) == len(names)

symbolNamesMap = dict()

print("sfSymbolMap = {")
for c, n in zip(t, names):
	print(f'    "{c}" : "{n}",')
print("}")

print(symbolNamesMap)