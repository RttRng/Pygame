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



$build =  "0.1.6"
# Načti hodnotu
if (Test-Path "counter.txt") {
    $var = Get-Content "counter.txt"
      if ($var==$build) {
        $var = Read-Host "Shoda s předchozím commitem ($build), napiš nový: "
      }
}
else {
    $var = "$build"
}
$var | Set-Content "counter.txt"
Write-Output $var

git commit -a -m $var
git push