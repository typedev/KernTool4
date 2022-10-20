from mojo.smartSet import getSmartSets

# get default sets
f = CurrentFont()
# defaultSets = getSmartSets()
# print(defaultSets)
# for item in defaultSets:
#     print(item.name, '--', item.query)
#     for a in item.getQueryResult(f):
#         print(a)
        
defaultSets = getSmartSets(f)
print(defaultSets)
for item in defaultSets:
    if not item.isGroup:
        print(item.name, '--', item.query)
        for a in item.getQueryResult(f):
            print(a)

# get font sets
# f = CurrentFont()
# fontSets = getSmartSets(f)
# print(fontSets)