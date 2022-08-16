# OAuth管理

- 可**创建**、**编辑**、**清除**主流代码托管平台的Oauth应用配置，为使用者提供OAuth授权支持。

- 支持平台及如何创建OAuth应用：

    - 腾讯工蜂：[创建 OAuth 应用程序](https://code.tencent.com/help/oauth2/)
    - GitHub：[创建 OAuth 应用程序](https://docs.github.com/cn/developers/apps/building-oauth-apps/creating-an-oauth-app)
    - Gitee：[创建 OAuth 应用程序](https://gitee.com/api/v5/oauth_doc#/list-item-3)
    - GitLab：[创建 OAuth 应用程序](https://docs.gitlab.com/ee/integration/oauth_provider.html)

![OAuth管理](../../../images/manage_oauth_01.png)

![OAuth管理](../../../images/manage_oauth_02.png)

::: tip
配置OAuth应用时，回调地址栏需填入当前TCA平台配置的域名或IP地址（如当前页面非80端口，需要显式指定端口号），作为Git平台上OAuth应用的回调地址。
:::
