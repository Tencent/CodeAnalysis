/**
 * shared hooks - useDeepEffect
 */
import React, { useEffect, useRef } from 'react';
import { isEqual } from 'lodash';

const useDeepEffect = (fn: () => void, deps: React.DependencyList) => {
  const isFirst = useRef(true);
  const preDeps = useRef(deps);
  useEffect(() => {
    const isFirstEffect = isFirst.current;
    const isSame = isEqual(preDeps.current, deps);
    isFirst.current = false;
    preDeps.current = deps;
    if (isFirstEffect || !isSame) {
      fn();
    }
  }, deps);
};

export default useDeepEffect;
