/**
 * shared hooks - useURLSearch 获取url参数hooks
 */
import { useMemo } from 'react';

import { getURLSearch } from '../util/route';

/** 根据路由变化，获取参数 */
const useURLSearch = () => useMemo(() => getURLSearch(), [
  window.location.search,
]);

export default useURLSearch;
