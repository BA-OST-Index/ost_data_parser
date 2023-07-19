# BA_OST_Index_Parser

A parser to read and organize all the information from `BA_OST_Index/ost_data` repository.

## Contributing & Working with data

Expected file tree:
```
/BA_OST_Index
    /ost_data (cloned)
        /...
    /ost_parser (cloned)
        /...
    /ost_data_export (cloned/newly-created folder)
        (empty)
```

In order to make the `main.py` script work **out of the box**, you'll need to create two symbolic links. They are:

- `ost_parser/data`  <====> `ost_data/`
- `ost_parser_data_export` <====> `ost_data_export/`

Note: these are relative paths shown in the file tree. You may need to replace them with absolute paths to create.

On Windows, use:

```powershell
mklink /D [symlink_name] [target]
```

On Linux, use:

```shell
ln -s [target] [symlink_name]
```

## What's in it

```
/ost_parser
    /data_model
        /actual_data
            Scripts for processing JSON files carrying actual data (instead of constants, i18n, etc.)
        /constant
            Some files containing constants.
        /tool
            Some useful shared tools/code.
        /types
            Basic types for other usages.
    /main.py
        Exporting files.
```
