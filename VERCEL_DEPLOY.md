# 🚀 部署 Star Office UI 到 Vercel - 查看您的AI Agents状态

这样您就能在任何地方通过网页查看您的AI助手们在做什么了！

## 🎯 快速部署步骤

### 1. Fork 或创建自己的仓库

由于需要推送代码到GitHub，您需要：

```bash
# 选项A：Fork原仓库后clone您的fork
git clone https://github.com/YOUR_USERNAME/Star-Office-UI.git

# 选项B：创建新仓库
cd /Users/touichskyer/.openclaw/workspace/Star-Office-UI
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/your-star-office.git
```

### 2. 提交Vercel配置

```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin master
```

### 3. 在Vercel部署

1. 访问 https://vercel.com
2. 登录您的账号
3. 点击 "Import Project"
4. 选择您的GitHub仓库
5. 使用以下配置：
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: 留空
   - Output Directory: 留空

### 4. 配置环境变量（可选）

在Vercel项目设置中添加：
- `STAR_OFFICE_STATUS`: 默认状态（如：working）
- `STAR_OFFICE_MESSAGE`: 默认消息
- `ASSET_DRAWER_PASS`: 侧边栏密码（默认：1234）

## 注意事项

1. **状态存储限制**：Vercel是无状态环境，每次请求都会重置状态。要持久化存储需要：
   - 使用外部数据库（如 Vercel KV）
   - 或使用 GitHub Actions 定期更新状态

2. **功能限制**：
   - 生图功能需要配置Gemini API环境变量
   - 多Agent状态同步需要外部存储
   - 文件上传功能受限

3. **性能优化**：
   - 首次冷启动可能较慢
   - 建议开启 Vercel Edge Functions 提升响应速度

## 本地测试Vercel环境

```bash
# 安装Vercel CLI
npm i -g vercel

# 本地运行
vercel dev
```

## 需要我帮您做什么？

1. 创建新的GitHub仓库？
2. 直接用Vercel CLI部署？
3. 配置外部存储方案？