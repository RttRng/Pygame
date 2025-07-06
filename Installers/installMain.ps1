cd 'C:/Users/mouli/Desktop/Pygame'

# Package the game
pyinstaller --onefile main.py -w -i "Assets/icon.ico" --name=Pygame

# Copy the executable to the Game directory
Copy-Item -Path .\dist\Pygame.exe -Destination .\Game -Force

# Copy the entire Assets directory to Game
Copy-Item -Path .\Assets -Destination .\Game -Recurse -Force

# Create a ZIP file of the Game directory
Compress-Archive -Path .\Game\* -DestinationPath .\Game.zip -Force

Move-Item -Path .\Game.zip -Destination .\dist -Force

echo "Finished, Pushing to git"
$msg = Read-Host "Enter the commit msg"

git commit -a -m $msg
git push