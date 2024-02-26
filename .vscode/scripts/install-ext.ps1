echo 安装当前工作区所有推荐的VSCode扩展组件...

$Json=Get-Content ..\extensions.json | ConvertFrom-Json
$Json.recommendations | ForEach-Object {code --install-extension $_}