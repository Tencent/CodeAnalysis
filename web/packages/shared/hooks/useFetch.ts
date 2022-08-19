/**
 * shared hooks - useFetch
 */
import { useState, useReducer } from 'react';
import useDeepEffect from './useDeepEffect';

type Action = {
  type: 'FETCH_INIT' | 'FETCH_SUCCESS' | 'FETCH_FAILURE' | 'FETCH_CANCEL',
  payload?: any
};

type State = {
  isLoading: boolean,
  isError: boolean,
  error: string
  data: any,
};

const fetchReducer = (state: State, action: Action) => {
  switch (action.type) {
    case 'FETCH_INIT':
      return {
        ...state,
        isLoading: true,
        isError: false,
      };
    case 'FETCH_SUCCESS':
      return {
        ...state,
        isLoading: false,
        isError: false,
        data: action.payload,
      };
    case 'FETCH_FAILURE':
      return {
        ...state,
        isLoading: false,
        isError: true,
        error: action.payload,
      };
    case 'FETCH_CANCEL':
      return {
        ...state,
        isLoading: false,
        isError: false,
      };
    default:
      throw new Error();
  }
};

/** FetchApi 类型  */
type FetchApi<ApiArgs extends any[]> = (...args: ApiArgs) => Promise<unknown>;

/** UseFetchOptions useFetch额外的options */
export interface UseFetchOptions {
  /** 初始化数据，默认为 null */
  initData?: any
  /** 前置处理 */
  onPreHandler?: () => void
  /** 成功的回调 */
  onSuccess?: (data: any) => void
  /** 失败的回调 */
  onFail?: (error: any) => void
  /** 最终的回调 */
  onFinnaly?: () => void
}

/**
 * useFetch
 * @param fetchApi api请求
 * @param apiArgs 请求参数
 * @param options useFetch 额外参数
 * @returns [state, reload]
 */
const useFetch = <ApiArgs extends any[]>(
  fetchApi: FetchApi<ApiArgs>,
  apiArgs: ApiArgs,
  options: UseFetchOptions = {},
): [State, () => void] => {
  const { initData = null, onPreHandler, onSuccess, onFail, onFinnaly } = options;
  const [state, dispatch] = useReducer(fetchReducer, {
    isLoading: false,
    isError: false,
    error: '',
    data: initData,
  });

  // 用于刷新请求
  const [refresh, setRefresh] = useState<boolean>(false);
  const reload = () => setRefresh(!refresh);

  useDeepEffect(() => {
    // 组件销毁时 abort 数据
    let didCancel = false;
    const fetchData = async () => {
      // 当请求中时，避免多次请求
      if (state.isLoading) return;
      // 前置处理
      onPreHandler?.();
      // fetch init
      dispatch({ type: 'FETCH_INIT' });
      try {
        const res = await fetchApi(...apiArgs);
        // 当组件销毁时，将isLoading，isError置为false
        if (didCancel) {
          dispatch({ type: 'FETCH_CANCEL' });
          return;
        }
        dispatch({ type: 'FETCH_SUCCESS', payload: res });
        onSuccess?.(res);
      } catch (error) {
        if (didCancel) {
          dispatch({ type: 'FETCH_CANCEL' });
          return;
        }
        dispatch({ type: 'FETCH_FAILURE', payload: error });
        onFail?.(error);
      } finally {
        onFinnaly?.();
      }
    };
    fetchData();
    return () => {
      didCancel = true;
    };
  }, [apiArgs, refresh]);

  return [state, reload];
};

export default useFetch;
