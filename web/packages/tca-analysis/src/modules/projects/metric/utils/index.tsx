// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import qs from 'qs';

// 将搜索条件中的数组类型转换为以逗号分割的字符串
export const array2StrQuery = (queryArray: any) => {
  const queryStr: any = [];
  Object.keys(queryArray).forEach((key) => {
    const item = queryArray[key];
    queryStr[key] = Array.isArray(item) ? item.toString() : item;
  });
  return queryStr;
};

export const setPagerQuery = (page: number, pageSize: number) => {
  let myOffset = 0;

  if (page && page === 1) {
    myOffset = 0;
  } else if (page) {
    myOffset = (page - 1) * pageSize;
  }

  return {
    limit: pageSize,
    offset: myOffset,
  };
};

/**
 *  格式化查询参数
 */

export function formatQueryStr(query: any) {
  return query !== null ? `?${qs.stringify(query)}` : '';
}

export function parseQueryStr(queryStr: any) {
  return qs.parse(queryStr.startsWith('?') ? queryStr.slice(1, queryStr.length) : queryStr);
}
