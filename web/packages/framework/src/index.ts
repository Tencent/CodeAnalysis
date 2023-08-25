import { registerApplication, start } from 'single-spa';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';
import 'coding-oa-uikit/dist/coding-oa-uikit.css';
import 'tdesign-react/es/style/index.css';


import MicroApplication from '@src/meta/application';
import applicationLoader from '@src/loader';
import { registration } from '@src/register';
import { store, injectAsyncReducer } from '@src/store';
import createHook from '@src/hook';
import { getOrCreateBodyContainer, info, debug, LOG_DEBUG } from '@src/utils';

import '@src/ui/development';
import '@src/support';

const REGISTER_MICRO_APP_PROPS = 'microHook.registerApp';
const MAIN_CONTAINER = 'main-container';

// 配置顶部加载进度条
NProgress.configure({ showSpinner: false });

/**
 * 在window上挂载一些全局参数
 */
createHook(store, injectAsyncReducer);

/**
 * 微前端启动入口，注册微前端生命周期函数到 single-spa
 */
(async () => {
  // 执行加载器，获取资源配置
  const meta = await applicationLoader.loadMeta();
  // 将资源配置挂载到microHook
  window.microHook.meta = [...meta];
  // 创建主容器
  const rootDom = getOrCreateBodyContainer(MAIN_CONTAINER);
  const activedApps = new Set<MicroApplication>();
  meta.forEach((app: MicroApplication) => {
    const { name, commitId, changeAt = '' } = app.props;
    if (LOG_DEBUG) {
      debug('加载App', name, '配置信息', app.props);
    } else {
      info('加载App', name, '版本', commitId, '变更', changeAt);
    }
    registerApplication(
      name,
      async ({ name, singleSpa, mountParcel, ...customProps }) => {
        NProgress.start();
        // 获取微前端应用资源，并进行微前端应用注册
        await app.loadResources();
        // 判断应用是否完成注册
        const register = registration.get(name);
        if (!register) {
          throw new Error(`${name} 微前端应用未注册，请使用 window.${REGISTER_MICRO_APP_PROPS}(name, lifeCycles) 来注册微前端应用`);
        }
        // 获取微前端应用生命周期
        const { bootstrap, mount, unmount, update = Promise.resolve } = register.lifeCycles;
        NProgress.done();
        return {
          bootstrap: [
            async () => {
              debug('Bootstrap app', name);
              await bootstrap(customProps);
            },
          ],
          mount: [
            async () => {
              debug('Mount app', name);
              await mount(customProps);
            },
          ],
          update: [
            async () => {
              debug('Update app', name);
              await update(customProps);
            },
          ],
          unmount: [
            async () => {
              debug('Unmount app', name);
              await unmount(customProps);
              activedApps.delete(app);
            },
          ],
        };
      },
      (location: Location) => {
        const shouldActive = app.path().test(location.pathname);
        if (shouldActive) {
          activedApps.add(app);
        }
        return shouldActive;
      },
      {
        store,
        injectAsyncReducer,
        rootDom,
      },
    );
  });
  start();
})();
