/** 给window添加属性 */
export const defineWindowProperty = (key: string, value: any) => {
  Object.defineProperty(window, key, {
    enumerable: false,
    writable: true,
    value,
  });
  if (process.env.NODE_ENV === 'development') {
    console.warn(`define ${key} property in window, ${value}`);
  }
};

/** 从window获取属性 */
export const getWindowProperty = (key: any) => {
  if (window.hasOwnProperty.call(window, key)) {
    return window[key];
  }
  if (process.env.NODE_ENV === 'development') {
    console.warn(`not found ${key} property in window`);
  }
  return;
};

/** 上报事件类型 */
export type ReportEventOptions = {
  /** 事件类型。例如，链接点击、下载、出站链接和表单事件 */
  category: 'click' | 'download' | 'upload' | 'visit' | 'form' | string;
  /** 事件操作。例如点击按钮、下载日志 */
  action: string;
  /** 名称。进行相关操作的事件名称定义 */
  name: string;
  /** 数值。 */
  value?: number;
};

export type ReportCustomDimension = {
  /** 维度ID */
  index: number;
  /** 维度值 */
  value: string;
  /** 兼容自定义变量，未来可能废弃。变量名称 */
  name?: string;
  /** 兼容自定义变量，未来可能废弃。变量范围 */
  scope?: 'visit' | 'page';
};
