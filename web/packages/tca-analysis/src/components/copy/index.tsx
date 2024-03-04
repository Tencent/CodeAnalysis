// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 复制到剪切板
 */

import React from 'react';
import cn from 'classnames';
import CopyToClipboard from 'react-copy-to-clipboard';
import { Tooltip, message } from 'coding-oa-uikit';
import CopyIcon from 'coding-oa-uikit/lib/icon/Copy';

import copyStyle from './style.scss';

interface CopyProps {
  text: string; // tooltip 提示文字
  copyText?: string; // copy 文字，不传默认为 text
  msg?: string; // 复制成功提示，不传默认为 “复制成功”
  className?: any;
  style?: any;
  getPopupContainer?: any;
}

const Copy = (props: CopyProps) => {
  const { text, copyText, msg, className, style, getPopupContainer } = props;

  return (
    <Tooltip title={text} getPopupContainer={getPopupContainer}>
      <CopyToClipboard
        text={copyText || text}
        onCopy={() => {
          message.success(msg || '复制成功');
        }}
      >
        {/* tooltip 组件会默认替换第一个子节点类名 */}
        <span>
          <CopyIcon
            style={style}
            className={cn(copyStyle.copyIcon, className)}
          />
        </span>
      </CopyToClipboard>
    </Tooltip>
  );
};

export default Copy;
