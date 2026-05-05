$ErrorActionPreference = "Stop"
Write-Host "Cleaning up old build..."
If (Test-Path "build") { Remove-Item -Recurse -Force "build" }
If (Test-Path "lambda_package.zip") { Remove-Item "lambda_package.zip" }

Write-Host "Creating build directory..."
New-Item -ItemType Directory -Force -Path "build" | Out-Null

Write-Host "Installing dependencies..."
pip install -r requirements-lambda.txt -t ./build

Write-Host "Copying source code..."
# Copy the contents of src to build
Copy-Item -Path "src\*" -Destination "build" -Recurse

Write-Host "Zipping package..."
Compress-Archive -Path "build\*" -DestinationPath "lambda_package.zip"

Write-Host "Cleaning up build directory..."
Remove-Item -Recurse -Force "build"

Write-Host "Done! You can now upload lambda_package.zip to your AWS Lambda functions."
