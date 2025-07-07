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
$a = 0  # 1.0.0 by bylo vydání
$b = 1  # 0.2.0 update s velkým přepsáním kódu
#$c       0.0.1 push na git
# Načti hodnotu
if (Test-Path "counter.txt") {
    $c = Get-Content "counter.txt"
} else {
    $c = 4
}

# Inkrementuj
$c++

# Ulož zpět
$c | Set-Content "counter.txt"

$build =  "$a.$b.$c"
Write-Output $build

git commit -a -m $build
git push