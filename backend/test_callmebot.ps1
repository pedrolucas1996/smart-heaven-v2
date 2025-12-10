$phone = "5518991241404"
$apikey = "2781646"
$message = "Teste de notificacao Smart Heaven"

$encodedMessage = [System.Web.HttpUtility]::UrlEncode($message)
$url = "https://api.callmebot.com/whatsapp.php?phone=$phone&text=$encodedMessage&apikey=$apikey"

Write-Host "Testing CallMeBot API..." -ForegroundColor Cyan
Write-Host "URL: $url" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $url -Method POST -UseBasicParsing
    Write-Host "`nSuccess! Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "`nError!" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}
