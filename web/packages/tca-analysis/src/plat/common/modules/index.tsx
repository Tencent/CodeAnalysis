import React from 'react';

import { getToolsRouter } from '@src/utils/getRoutePath';

export interface ToolInfoLinkProps {
  orgSid: string;
  checktool: any;
  disableLink?: boolean;
}

/** 工具详情Link组件，提供点击跳转 */
export const ToolInfoLink = ({ orgSid, checktool, disableLink = false }: ToolInfoLinkProps) => {
  if (disableLink) {
    return <>{checktool?.display_name}</>;
  }
  return <a
    target="_blank"
    href={`${getToolsRouter(orgSid, checktool?.id, 'baseinfo')}`} rel="noreferrer"
  >
    {checktool?.display_name}
  </a>;
};

/** 关闭代码库成员配置，默认不关闭 */
export const CLOSE_REPO_MEMBER_CONF = false;

/** 分析方案模板权限管理是否开放 label描述 */
export const TMPL_SCHEME_PERM_OPEN_LABEL = '是否团队内公开';
