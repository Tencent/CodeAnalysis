import { toUpper } from 'lodash';
import { getMetaEnv, warn, info } from '@src/utils';
import Constant, { DEFAULT_MICRO_FRONTEND_SETTING_API } from '@src/constant';

// 从meta中获取setting配置api/json
const SETTING_API = getMetaEnv(Constant.MICRO_FRONTEND_SETTING_API, DEFAULT_MICRO_FRONTEND_SETTING_API);

interface ISetting {
  code: string;
  value: string;
  description: string;
}

export interface SettingLoader {
  readonly loadSetting: () => Promise<void>;
}

class MicroApplicationSettingLoader implements SettingLoader {
  private url: string;
  constructor() {
    this.url = SETTING_API;
  }

  public async loadSetting() {
    try {
      info('正在加载微前端Setting配置信息 ...');
      const res = await window.fetch(`${this.url}?time=${new Date().getTime()}`, { method: 'GET' });
      const setting: ISetting[] = await res.json();
      setting.forEach(({ code, value, description }) => {
        const name = toUpper(code);
        let meta = document.querySelector(`meta[name=${name}]`);
        if (!meta) {
          meta = document.createElement('meta');
          document.head.appendChild(meta);
        }
        meta.setAttribute('name', name);
        meta.setAttribute('content', value);
        meta.setAttribute('data-description', description);
        meta.setAttribute('data-type', 'SYSTEM');
      });
      info('微前端Setting配置信息完成加载 ^ _ ^');
    } catch (e) {
      warn('微前端Setting配置信息完成加载失败... (｡ì _ í｡)');
    }
  }
}

// 加载微前端setting配置
const loader = new MicroApplicationSettingLoader();

export default loader;
