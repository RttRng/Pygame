cd 'C:/Users/mouli/Desktop/Pygame/Old'
pyinstaller --onefile client.py -i "../Assets/icon.ico" --name=client
pyinstaller --onefile server.py -i "../Assets/icon.ico" --name=server
