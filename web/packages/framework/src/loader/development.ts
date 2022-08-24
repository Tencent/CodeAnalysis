import Cookies from 'universal-cookie';
import { isEmpty, uniqBy } from 'lodash';
import { message } from 'coding-oa-uikit';

import Constant from '@src/constant';
import { info, debug, warn } from '@src/utils';
import MicroApplication from '@src/meta/application';
import renderUI from '@src/ui/commit';

import { MicroApplicationLoader } from './loader';

const cookies = new Cookies();

/**
 * 从 localStorage 中加载，需要接口返回 MicroApplicationProps 的数据
 */
export class MicroApplicationDevelopmentLoader implements MicroApplicationLoader {
  public async enabled(): Promise<boolean> {
    return Promise.resolve(true);
  }

  public async loadMeta(production?: MicroApplication[]): Promise<MicroApplication[]> {
    try {
      const apiList = this.getApiList();
      if (isEmpty(apiList)) {
        return;
      }
      info('DEV_API_LIST: 正在加载微前端资源配置信息 ...');
      const meta: MicroApplication[] = [];
      for (const microApi of apiList) {
        try {
          const response = await window.fetch(`${microApi.url}?time=${new Date().getTime()}`, { method: 'GET' });
          const data = await response.json();
          info(`DEV_API_LIST: ${JSON.stringify(microApi)}`);
          meta.push(new MicroApplication(data));
        } catch (e) {
          debug(e);
        }
      }

      // 获取已存在的
      const devNames = meta.map(app => app.props.name);
      const newMeta = production.filter(app => !devNames.includes(app.props.name)).concat(meta);

      // 渲染UI
      this.renderUI(production || [], newMeta);
      info('DEV_API_LIST: 微前端资源配置信息完成加载 ^ _ ^');
      return newMeta;
    } catch (e) {
      message.error('DEV_API_LIST: 微前端资源配置信息加载失败... (｡ì _ í｡)');
      warn('DEV_API_LIST: 微前端资源配置信息加载失败... (｡ì _ í｡)');
      this.exit();
    }
    return [];
  }

  public renderUI(production: MicroApplication[], development: MicroApplication[]) {
    renderUI({
      title: '开发',
      production,
      development,
      onExit: () => {
        this.exit(true);
      },
      noExit: this.isPluginMode(),
      mode: this.isPluginMode() ? '[插件模式]' : '[本地模式]',
    });
  }

  public exit(reload = false) {
    // cookies中移除开发模式微前端资源配置
    cookies.remove(Constant.MICRO_FRONTEND_API_LIST, {
      path: '/',
      domain: window.location.hostname,
    });
    if (reload) {
      debug('Exit development success and reload page');
      window.location.replace(window.location.href);
    } else {
      debug('Exit development success');
    }
  }

  public getApiList() {
    const apiList: Array<MicroDevApiList> = this.isPluginMode()
      ? window.microDevApiList : cookies.get(Constant.MICRO_FRONTEND_API_LIST);
    return uniqBy(apiList, 'name');
  }

  public isPluginMode() {
    return window.microDevApiList && window.microDevApiList.length > 0;
  }
}

const loader = new MicroApplicationDevelopmentLoader();

export default loader;
