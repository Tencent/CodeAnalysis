import React from 'react';
import { render, unmountComponentAtNode } from 'react-dom';
import { legacy_createStore as createStore, combineReducers } from 'redux';
import { Provider } from 'react-redux';
import { ConfigProvider } from 'coding-oa-uikit';
import Cookie from 'universal-cookie';
// import 'coding-oa-uikit/dist/coding-oa-uikit.css';
import { StoreProvider } from '../../hook-store';
import { Store, StateProps, ActionProps, Middleware } from '../../hook-store/types';
import '../../style/index.scss';
import '../../style/zhiyan.css';
import 'tdesign-react/es/style/index.css';

/**
 * 国际化资源加载
 * @returns
 */
const loadLocale = async () => {
  const cookie = new Cookie();
  const language = (cookie.get('i18next') as string ?? 'zh-CN').replace('-', '_');
  try {
    return await import(`coding-oa-uikit/lib/locale/${language}.js`);
  } catch (error) {
    return await import('coding-oa-uikit/lib/locale/zh_CN.js');
  }
};

interface MicroInitProps {
  /** 微前端外层HTMLElement id */
  id: string;
  /** 微前端唯一标识名称 */
  name: string;
  /** 入口 */
  container: JSX.Element | React.ReactNode;
  /** 微前端上层reducers */
  reducers?: InjectReducer;
}

interface MicroHookStore<State, Action> {
  /** react-hook store 状态管理 */
  hookStore?: {
    enable: boolean;
    stores: Store<State, Action>[];
    middlewares?: Middleware<Action>[];
  }
}

/**
 * 微前端初始化
 * @param microInitProps
 */
const MicroInit = <State extends StateProps = StateProps, Action extends ActionProps = ActionProps>({
  id, name, container, reducers, hookStore,
}: MicroInitProps & MicroHookStore<State, Action>) => {
  const bootstrap = () => {
    // bootstrap
  };

  const create = (rootDom: HTMLElement) => {
    if (rootDom) {
      let wrapDom = document.getElementById(name);
      if (!wrapDom) {
        wrapDom = document.createElement('div');
        wrapDom.id = name;
        wrapDom.className = `${name}-container`;
      }
      let containerDom = document.getElementById(id);
      if (!containerDom) {
        containerDom = document.createElement('div');
        containerDom.id = id;
        containerDom.appendChild(wrapDom);
        rootDom.appendChild(containerDom);
      } else {
        containerDom.appendChild(wrapDom);
      }
    }
  };

  const mount = async (props: ApplicationCustomProps) => {
    const { rootDom, injectAsyncReducer, store } = props;
    create(rootDom);
    const locale = await loadLocale();
    let renderContent = <ConfigProvider
      autoInsertSpaceInButton={false}
      locale={locale.default}
      getPopupContainer={node => (node ? node.parentNode as HTMLElement : document.body)}
    >
      {container}
    </ConfigProvider>;

    if (hookStore?.enable) {
      const { stores, middlewares } = hookStore;
      renderContent = <StoreProvider stores={stores} middlewares={middlewares}>
        {renderContent}
      </StoreProvider>;
    }

    if (store) {
      // 将reducers注入
      if (reducers && injectAsyncReducer) {
        Object.keys(reducers).forEach(key => injectAsyncReducer(key, reducers[key]));
      }
      renderContent = <Provider store={store}>
        {renderContent}
      </Provider>;
    }

    render(renderContent, document.getElementById(name));
  };

  const unmount = () => {
    const e = document.getElementById(name);
    if (e) {
      unmountComponentAtNode(e);
      e.remove();
    }
  };

  if (typeof window.microHook === 'object') {
    window.microHook.registerApp(name, {
      bootstrap,
      mount,
      unmount,
    });
  } else {
    const ASYNC_REDUCERS: InjectReducer = {};
    const { store, injectAsyncReducer } = (() => {
      const rootReducers: InjectReducer = {};
      const store = createStore(combineReducers({ ...rootReducers }));
      const injectAsyncReducer = (name: string, reducer: Reducer, override = false) => {
        if (!(ASYNC_REDUCERS[name] && !override)) {
          ASYNC_REDUCERS[name] = reducer;
          store.replaceReducer(combineReducers({ ...rootReducers, ...ASYNC_REDUCERS }));
        }
      };
      return { store, injectAsyncReducer };
    })();
    mount({
      rootDom: document.body,
      store,
      injectAsyncReducer,
    });
  }
};

export default MicroInit;
