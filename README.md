pusk

powershell: 
---
cd //expense-analyzer-mobile
---
npm install
---
$env:EAS_NO_VCS=1; eas.cmd build --platform android --profile preview
