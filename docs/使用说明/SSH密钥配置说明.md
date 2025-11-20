# 🔑 SSH 密鑰配置說明

## 📍 在哪裡輸入密碼？

當執行 SSH 連接命令時，**密碼會在終端/命令提示符窗口中輸入**。

### Windows PowerShell/CMD 中的顯示

當你看到類似以下的提示時：

```
ubuntu@165.154.233.55's password:
```

或者：

```
Password:
```

### ⚠️ 重要注意事項

1. **密碼不會顯示**：輸入密碼時，終端不會顯示任何字符（包括星號 `*`），這是正常的 SSH 安全行為
2. **直接輸入即可**：儘管看不到輸入，但密碼確實在被輸入
3. **密碼是**：`Along2025!!!`
4. **按 Enter 確認**：輸入完密碼後按 Enter 鍵

### 📝 操作步驟

#### 方法 1：使用批處理腳本（推薦）

1. 雙擊運行 `setup_ssh_key.bat`
2. 按任意鍵繼續
3. 當看到 `Password:` 或 `ubuntu@165.154.233.55's password:` 提示時
4. **直接在鍵盤輸入密碼**：`Along2025!!!`（不會顯示字符）
5. 按 `Enter` 鍵確認

#### 方法 2：手動執行命令

在 PowerShell 或 CMD 中執行：

```powershell
# 讀取公鑰
type "%USERPROFILE%\.ssh\id_rsa.pub"
```

然後複製公鑰內容，執行：

```bash
ssh ubuntu@165.154.233.55
# 在這裡輸入密碼: Along2025!!!
# （輸入時不會顯示任何字符，這是正常的）

# 登錄後執行以下命令：
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公鑰內容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

#### 方法 3：使用一行命令（推薦）

在 PowerShell 中執行：

```powershell
type "%USERPROFILE%\.ssh\id_rsa.pub" | ssh ubuntu@165.154.233.55 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo '✅ 公鑰已添加'"
```

**當提示輸入密碼時**：
- 看到 `Password:` 或類似的提示
- 直接輸入：`Along2025!!!`
- 輸入時不會顯示任何字符
- 輸入完成後按 `Enter`

### 🧪 測試配置是否成功

配置完成後，測試無密碼連接：

```bash
ssh -o "BatchMode=yes" ubuntu@165.154.233.55 "echo '✅ 連接成功'"
```

如果**不需要輸入密碼**就能執行成功，說明配置成功！

### 📸 示例截圖說明

```
PS E:\...> ssh ubuntu@165.154.233.55
ubuntu@165.154.233.55's password:          <-- 在這裡輸入密碼（不會顯示）
                                             直接輸入: Along2025!!!
                                             然後按 Enter

Welcome to Ubuntu...
```

### ❓ 常見問題

**Q: 輸入密碼時沒有反應？**  
A: 這是正常的！SSH 為了安全，輸入密碼時不會顯示任何字符。直接輸入密碼後按 Enter 即可。

**Q: 輸入錯誤怎麼辦？**  
A: 按 `Ctrl+C` 取消，然後重新執行命令。

**Q: 怎麼知道是否輸入成功？**  
A: 如果密碼正確，會立即登錄到服務器（看到服務器提示符）；如果錯誤，會提示 "Permission denied"。

---

**現在請雙擊運行 `setup_ssh_key.bat` 來配置 SSH 密鑰！**
