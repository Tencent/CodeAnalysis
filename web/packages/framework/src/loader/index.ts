import isEmpty from 'lodash/isEmpty';
import { message } from 'coding-oa-uikit';
// 项目内
import MicroApplication from '@src/meta/application';
import { debug } from '@src/utils';
import { MicroApplicationLoader } from './loader';
import apiLoader from './api';
import developmentLoader from './development';
import settingLoader, { SettingLoader } from './setting';

/**
 * 组合加载器
 */
class CombineLoader implements MicroApplicationLoader {
  private productionLoader: MicroApplicationLoader;
  private developmentLoader: MicroApplicationLoader;
  private settingLoader: SettingLoader;
  constructor(
    pLoader: MicroApplicationLoader,
    dLoader: MicroApplicationLoader,
    sLoader: SettingLoader,
  ) {
    this.productionLoader = pLoader;
    this.developmentLoader = dLoader;
    this.settingLoader = sLoader;
  }

  public async enabled(): Promise<boolean> {
    return Promise.resolve(true);
  }

  public async loadMeta(): Promise<MicroApplication[]> {
    if (await this.productionLoader.enabled()) {
      // 加载微前端资源配置
      const production = await this.productionLoader.loadMeta();
      // 加载微前端设置配置
      await this.settingLoader.loadSetting();
      // 如果启用开发者模式，则加载开发者微前端资源配置
      if (await this.developmentLoader.enabled()) {
        const dev = await this.developmentLoader.loadMeta(production);
        if (!isEmpty(dev)) {
          debug('MicroApplicationDevelopmentLoader meta config mount');
          return dev;
        }
      }
      debug('MicroApplicationAPILoader meta config mount');
      return production;
    }
    message.error('微前端启动失败', 0);
    throw new Error('微前端启动失败');
  }
}

const loader = new CombineLoader(apiLoader, developmentLoader, settingLoader);

export default loader;
