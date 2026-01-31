# Google 登录（仅限 @cobo.com）

前端使用 Firebase Authentication 实现 Google 登录，并限制为 **@cobo.com** 企业邮箱。

## 行为

- 未配置 Firebase 时：不显示登录，所有人可访问（便于本地开发）。
- 配置 Firebase 后：未登录或非 @cobo.com 邮箱会看到登录页；登录成功后进入应用，侧栏显示当前用户和「退出登录」。

## 配置步骤

1. 打开 [Firebase Console](https://console.firebase.google.com/)，创建或选择项目。
2. 在 **Authentication → Sign-in method** 中启用 **Google** 提供商。
3. 在 **Project settings → General** 中找到「Your apps」，添加 Web 应用（若尚未添加），记下 `apiKey`、`authDomain`、`projectId`、`appId`。
4. 在 **Authentication → Settings → Authorized domains** 中确保包含你的 Pages 域名（如 `your-org.github.io` 和 `*.github.io` 若需）。
5. 本地开发：在 `stablecoin-intel-web-source` 下新建 `.env`，参考 `.env.example` 填入：
   - `VITE_FIREBASE_API_KEY`
   - `VITE_FIREBASE_AUTH_DOMAIN`
   - `VITE_FIREBASE_PROJECT_ID`
   - `VITE_FIREBASE_APP_ID`
6. GitHub Pages 部署：在仓库 **Settings → Secrets and variables → Actions** 中新增同名 secrets；`deploy-pages.yml` 会在构建时注入，构建出的前端即启用登录。

## 修改允许的邮箱域名

在 [client/src/contexts/AuthContext.tsx](client/src/contexts/AuthContext.tsx) 中修改 `ALLOWED_DOMAIN`（当前为 `cobo.com`）。
