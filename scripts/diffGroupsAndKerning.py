import os, sys

def contentEqual(g1, g2):
    a = ''.join(g1)
    b = ''.join(g2)
    if a != b:
        return False
    else:
        return True


def diffGroups(oldTable, newTable, labelFrom = 'old', labelTo = 'new'):
    newGroups = {}
    delGroups = {}
    chgGroups = {}
    report = tdReport.Report(process='diffGroups')
    report.stroke('=')
    report.add('Groups report:')
    for n_group, content in newTable.items():
        if not oldTable.has_key(n_group):
            newGroups[n_group] = content
            report.add('New Group Added: %s [%s]' % (n_group, ' '.join(content)))
        elif not contentEqual(oldTable[n_group], newTable[n_group]):
            chgGroups[n_group] = [oldTable[n_group], newTable[n_group]]
            report.add('Changed Group: %s' % n_group)
            report.add('%s: [%s]' % (labelFrom, ' '.join(oldTable[n_group])), level=1)
            report.add('%s: [%s]' % (labelTo, ' '.join(newTable[n_group])), level=1)

    for o_group, content in oldTable.items():
        if not newTable.has_key(o_group):
            delGroups[o_group] = content
            report.add('Group Deleted: %s [%s]' % (o_group, ' '.join(content)))

    report.add('Groups TOTAL: Added=%i Deleted=%i Changed=%i' % (len(newGroups), len(delGroups), len(chgGroups)))
    return report.gettext()


def diffKerning(oldTable, newTable, labelFrom = 'old', labelTo = 'new'):
    newPairs = {}
    delPairs = {}
    chgPairs = {}
    nulPairs = {}
    report = tdReport.Report(process='diffKern')
    report.stroke('=')
    report.add('Kerning report:')
    for (l, r), v in newTable.items():
        if v == 0:
            nulPairs[l, r] = v
        elif not oldTable.has_key((l, r)):
            newPairs[l, r] = v
            report.add('New Pair: %s %s %i' % (l, r, v))
        elif oldTable[l, r] != newTable[l, r]:
            chgPairs[l, r] = [oldTable[l, r], newTable[l, r]]
            report.add('Changed Pair: %s %s' % (l, r))
            report.add('%s: %i\t%s: %i' % (labelFrom,
             oldTable[l, r],
             labelTo,
             newTable[l, r]), level=1)

    for (l, r), v in oldTable.items():
        if not newTable.has_key((l, r)):
            delPairs[l, r] = v
            report.add('Pair Deleted: %s %s %i' % (l, r, v))

    report.add('Pairs TOTAL: Added=%i Deleted=%i Changed=%i Null pairs (ignored)=%i' % (len(newPairs),
     len(delPairs),
     len(chgPairs),
     len(nulPairs)))
    return report.gettext()


if __name__ == '__main__':

    path = '/Users/alexander/Documents/WORKS/Paratype/!!!SBSANS/SBSansText/SBSansText_str_kern'
    font1 = OpenFont(os.path.join(path, 'SBSansText-Regular_kern.ufo'))
    font2 = OpenFont(os.path.join(path, 'SBSansText-Thin_kern.ufo'))
