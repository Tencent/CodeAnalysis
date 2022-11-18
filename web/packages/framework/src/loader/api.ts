import isEmpty from 'lodash/isEmpty';
import { message } from 'coding-oa-uikit';

import Constant, { DEFAULT_MICRO_FRONTEND_API } from '@src/constant';
import { getMetaEnv, debug, info, warn } from '@src/utils';
import MicroApplication from '@src/meta/application';

import { MicroApplicationLoader } from './loader';

// 从meta中获取微前端配置api/json
const MICRO_FRONTEND_API = getMetaEnv(Constant.MICRO_FRONTEND_API, DEFAULT_MICRO_FRONTEND_API);

/**
 * 从 API 中加载，需要接口返回 MicroApplicationProps 的数据
 */
export class MicroApplicationAPILoader implements MicroApplicationLoader {
  private url: string;
  constructor() {
    this.url = MICRO_FRONTEND_API;
  }

  public async enabled(): Promise<boolean> {
    const enable = !isEmpty(this.url);
    if (enable) {
      debug('MicroApplicationAPILoader is enabled');
    }
    return Promise.resolve(enable);
  }

  public async loadMeta(): Promise<MicroApplication[]> {
    try {
      info('API: 正在加载微前端资源配置信息 ...');
      const response = await window.fetch(`${this.url}?time=${new Date().getTime()}`, { method: 'GET' });
      const app = await response.json();
      const meta = app.map((props: any) => new MicroApplication(props));
      info('API: 微前端资源配置信息完成加载 ^ _ ^');
      return meta;
    } catch (e) {
      // 增加 reload，首次获取失败时默认刷新页面进行一次重试
      const loadMicroFrontendFailed = 'loadMicroFrontendFailed';
      const firstRecord = sessionStorage.getItem(loadMicroFrontendFailed);
      if (!firstRecord) {
        sessionStorage.setItem(loadMicroFrontendFailed, 'true');
        window.location.reload();
        return;
      }
      sessionStorage.removeItem(loadMicroFrontendFailed);
      message.error('微前端资源配置信息加载失败，请刷新页面重试或联系系统管理员', 0);
      warn('API: 微前端资源配置信息加载失败，请检查 MICRO_FRONTEND_API ... (｡ì _ í｡)');
      throw new Error(e);
    }
  }
}

const loader = new MicroApplicationAPILoader();

export default loader;
