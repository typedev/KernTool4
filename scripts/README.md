## Additional scripts for GroupsControl
### `splitGroupsByLanguage.py`
Script for separating groups and kerning based on language. 

Groups with base language (such as Latin, identified by the first glyph in the group) will remain with names like `public.kern1.A`, and for other languages will be formed classes like `public.kern1.A_cyrillic` or `public.kern1.A_greek` with the language name suffix through an underscore `_`, kerning will be transferred to all related classes accordingly, and cross-language pairs are removed.

### `removeCrossLanguagePairs.py`

The script removes cross-language pairs.

Pairs are checked for the first level of compatibility - Latin/Cyrillic, Latin/Greek, Georgian/Armenian, etc.
It is also possible to check and delete pairs according to the second level of compatibility, pairs within the same script - for example, in Latin: French / German, in Cyrillic: Abkhaz / Chuvash. But this is rarely applied in practice.

### `combineGroupsIntoParent.py`
The script collects groups with language suffixes like `_cyrillic` `_greek` and so on, will be combined with similar Latin ones.
This script is currently under development. Main problem - a lot of exceptions are thrown.

### `clearingKernAndGroups.py`
Script to check kerning and groups.

Finds and removes lost glyphs in groups, empty groups, lost pairs, pairs with None and Zero value. For pairs with a Zero value, a list will be collected for checking.

### `fixingKeyGlyphPositionInGroups.py`
The script finds and corrects the position of the KeyGlyph in the group.

It is believed that in UFO the order of glyphs in a group does not matter, however, to simplify some functions in `GroupsControl`, it was decided to consider the first glyph in the group as the key one and determine the difference in margins for the remaining glyphs, as well as the language compatibility of glyphs in the group.

Most often, the group name matches the key glyph. If this is not the case, confusion is possible. The script determines the key glyph from the group name and puts it in the first position.
```
Valid group names:
public.kern1.glyphname
public.kern1.glyphname.suffix1.suffix2...
public.kern1.glyphname_suffix1_suffix2...
```

> For these scripts to work, you need to use `ScriptsBoard` from `GroupsControl`






