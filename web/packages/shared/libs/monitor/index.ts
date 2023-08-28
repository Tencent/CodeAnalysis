
/** 前端监控组件 */

import { ReportEventOptions, ReportCustomDimension } from './util';

type MonitorReportScope = 'all' | 'matomo' | 'aegis';

// eslint-disable-next-line @typescript-eslint/ban-types
type MonitorOptions = {
};

/** 事件所属一级模块 */
type EventScope = '仓库登记' | '分析项目' | '分析方案' | '方案模板' | '规则包' | '工具管理' | '节点管理' | '凭证管理' | '个人令牌' | '扩展功能' | '菜单栏';

const mergeScope = (scope: EventScope, extraScope?: string) => (extraScope ? `${scope} - ${extraScope}` : scope);

/**
 * @param name  事件名称
 * @param scope 事件所属一级模块，如分析方案、分析项目
 * @param extraScope 可选，事件所属子模块，可用 - 链接子模块，如规则配置、规则配置 - 添加规则包
 */
export const trackClickEvent = (name: string, scope: EventScope, extraScope?: string) => {
  Monitor.reportEvent({
    category: mergeScope(scope, extraScope),
    action: '点击',
    name,
  });
};

/**
 * @param name  事件名称
 * @param scope 事件所属一级模块，如分析方案、分析项目
 * @param extraScope 可选，事件所属子模块，可用 - 链接子模块，如规则配置、规则配置 - 添加规则包
 */
export const trackDownloadEvent = (name: string, scope: EventScope, extraScope?: string) => {
  Monitor.reportEvent({
    category: mergeScope(scope, extraScope),
    action: '下载',
    name,
  });
};

/**
 * @param name  事件名称
 * @param scope 事件所属一级模块，如分析方案、分析项目
 * @param extraScope 可选，事件所属子模块，可用 - 链接子模块，如规则配置、规则配置 - 添加规则包
 */
export const trackViewEvent = (name: string, scope: EventScope, extraScope?: string) => {
  Monitor.reportEvent({
    category: mergeScope(scope, extraScope),
    action: '查看',
    name,
  });
};

const Monitor = {
  /** 注册监控，仅在监控成功注册，其它方法才生效 */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-empty-function
  register: (options: MonitorOptions = {}) => {
  },
  /** 销毁 */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-empty-function
  destroy: () => {
  },
  /** 配置uid */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-empty-function
  setUserId: (uid: string | number) => {
  },
  /** 上报事件 */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-empty-function
  reportEvent: (o: ReportEventOptions, scope: MonitorReportScope = 'all') => {
  },
  /** 上报维度 */
  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-empty-function
  reportCustomDimension: (o: ReportCustomDimension, scope: MonitorReportScope = 'all') => {
  },
};


export default Monitor;
