import { info } from '@src/utils';

/**
 * 微前端资源属性类型
 */
export interface MicroApplicationProps {
  /** 微前端唯一标识 */
  name: string;
  /** 描述 */
  description: string;
  /** url匹配，可正则 */
  match: string;
  /** git commit id */
  commitId?: string;
  /** 变更描述 */
  changeAt?: string;
  /** css资源路径列表 */
  css: string[];
  /** js资源路径列表 */
  js: string[];
  /** 前缀 */
  prefix: string[] | string;
}

/**
 * 微前端类接口
 */
export interface BaseMicroApplication<T> {
  props: T;
  readonly loadStyle: () => Promise<any>;
  readonly loadScript: () => Promise<any>;
  readonly loadResources: () => Promise<any>;
  readonly removeStyle: () => Promise<any>;
  readonly path: () => RegExp;
}

/**
 * 微前端定义，提供：
 * 1. 加载 css 资源
 * 2. 加载 js 资源
 * 3. 卸载 css 资源，入口 css 可以通过 moduleName 匹配卸载
 *
 */
export default class MicroApplication implements BaseMicroApplication<MicroApplicationProps> {
  public props: MicroApplicationProps;
  private pathRegexp: RegExp;

  constructor(props: MicroApplicationProps) {
    this.props = props;
    this.pathRegexp = new RegExp(props.match);
  }

  public createStyle(link: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const ele = document.createElement('link');
      ele.rel = 'stylesheet';
      ele.href = link;
      ele.dataset.moduleName = this.props.name;
      ele.onload = e => resolve(e);
      ele.onerror = (...p) => reject(p);
      document.head.appendChild(ele);
    });
  }

  /**
     * 创建 <script /> 标签
     * @param link
     */
  public createScript(link: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const ele = document.createElement('script');
      ele.type = 'text/javascript';
      ele.src = link;
      ele.dataset.moduleName = this.props.name;
      ele.onload = e => resolve(e);
      ele.onerror = (...p) => reject(p);
      document.head.appendChild(ele);
    });
  }

  /**
   * 加载 css 资源，如已加载，则不重复加载
   */
  public async loadStyle(): Promise<any> {
    return Promise.all([].concat.call(this.props.css).map((link: string) => {
      const style = this.isLoadedStyle(link);
      return style ? Promise.resolve((style.disabled = false)) : this.createStyle(link);
    }));
  }

  /**
   * 加载 js 文件，如已加载，则不重复加载
   */
  public async loadScript(): Promise<any> {
    return Promise.all([].concat.call(this.props.js)
      .map((link: string) => (this.isLoadedScript(link) ? Promise.resolve() : this.createScript(link))));
  }

  public loadResources(): Promise<any> {
    info('加载js、css资源文件');
    return Promise.all([this.loadStyle(), this.loadScript()]);
  }

  /**
   * 移除 css 文件的 <link rel="stylesheet"/> 标签
   */
  public removeStyle(): Promise<any> {
    [].slice.call(document.styleSheets).map((e: CSSStyleSheet) => e.ownerNode)
      .filter((e: HTMLScriptElement) => this.isMatched(e.dataset))
      .forEach((e: HTMLScriptElement) => e.remove());
    return Promise.resolve();
  }

  public path(): RegExp {
    return this.pathRegexp;
  }

  /**
   * 判断是否已加载 css
   * @param link
   */
  public isLoadedStyle(link: string): HTMLLinkElement {
    return [].slice.call(document.styleSheets).find((e: HTMLLinkElement) => e.href === link);
  }

  /**
   * 判断是否已加载 js
   * @param link
   */
  public isLoadedScript(link: string): HTMLScriptElement {
    return [].slice.call(document.scripts).find((e: HTMLScriptElement) => e.src === link);
  }

  /**
   * 判断是否匹配，以 href 或者 src 和 data-module-name 匹配
   * @param link
   * @param dataset
   */
  public isMatched(dataset?: DOMStringMap) {
    return this.isModuleName(dataset?.moduleName);
  }

  /**
   * 判断 app 是否符合 data-module-name 名
   * @param name
   */
  public isModuleName(name: string): boolean {
    return this.props.name === name;
  }
}
