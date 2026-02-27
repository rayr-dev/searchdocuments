rmdir /s /q dist
rmdir /s /q build
pyinstaller --clean --noconfirm --name Search-documents_CLI --console --icon assets/Search-documents.ico --paths src --add-data "src\utilities;utilities" --add-data "src\version_info.txt;." --distpath dist --workpath build src/cli/cli_main.py

pyinstaller --clean --noconfirm --name Search-documents_GUI --windowed --icon assets/Search-documents.ico --splash assets/Search-documents.png --paths src --add-data "src\utilities;utilities" --add-data "src\version_info.txt;." --distpath dist --workpath build src/gui/gui_main.py
REM For Linux builds src/utilities:utiliites