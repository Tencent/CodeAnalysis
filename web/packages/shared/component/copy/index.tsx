/**
 * 复制到剪切板
 */

import React from 'react';
import cn from 'classnames';
import CopyToClipboard from 'react-copy-to-clipboard';
import Tooltip from 'coding-oa-uikit/lib/tooltip';
import message from 'coding-oa-uikit/lib/message';
import CopyIcon from 'coding-oa-uikit/lib/icon/Copy';

import s from './style.scss';

interface CopyProps {
  /** tooltip 提示文字 */
  text: string;
  /** copy 文字，不传默认为 text */
  copyText?: string;
  /** 复制成功提示，不传默认为 “复制成功” */
  msg?: string;
  /** copy 图标的自定义 class */
  className?: string;
  /** copy 图标的自定义 style */
  style?: React.CSSProperties;
  /** 弹框的渲染父节点 */
  getPopupContainer?: (triggerNode: HTMLElement) => HTMLElement
}

const Copy = ({ text, copyText, msg, className, style, getPopupContainer }: CopyProps) => (
  <Tooltip title={text} getPopupContainer={getPopupContainer}>
    <CopyToClipboard
      text={copyText || text}
      onCopy={() => {
        message.success(msg || '复制成功');
      }}
    >
      {/* tooltip 组件会默认替换第一个子节点类名 */}
      <span >
        <CopyIcon style={style} className={cn(s.copyIcon, className)} />
      </span>
    </CopyToClipboard>
  </Tooltip>
);

export default Copy;

