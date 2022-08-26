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

