$body = @{
    username = "testuser" + (Get-Random -Maximum 9999)
    email = "test" + (Get-Random -Maximum 9999) + "@example.com"
    password = "123456"
} | ConvertTo-Json

Write-Host "Sending request with body:" -ForegroundColor Cyan
Write-Host $body

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/register" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body
    Write-Host "`nSuccess:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Depth 10)
} catch {
    Write-Host "`nError:" -ForegroundColor Red
    Write-Host "Status Code:" $_.Exception.Response.StatusCode.value__
    if ($_.ErrorDetails.Message) {
        Write-Host "Error Details:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message
    }
}
