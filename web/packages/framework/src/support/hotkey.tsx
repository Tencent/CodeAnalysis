import React from 'react';
import ReactDOM from 'react-dom';
import { useHotkeys } from 'react-hotkeys-hook';

import Constant, { DEFAULT_MICRO_THEME_MODS } from '@src/constant';
import { getMetaEnv, getOrCreateBodyContainer } from '@src/utils';

// 变更主题
const themeAttributeName = 'theme-mode';
const changeThemeMode = () => {
  const themeModes = getMetaEnv(Constant.MICRO_THEME_MODS, DEFAULT_MICRO_THEME_MODS).split(',');
  if (themeModes.length > 1) {
    const index = themeModes.indexOf(document.documentElement.getAttribute(themeAttributeName));
    let themeMode;
    if (index <= 0) {
      [, themeMode] = themeModes;
    } else if (index === themeModes.length - 1) {
      [themeMode] = themeModes;
    } else {
      themeMode = themeModes[index + 1];
    }
    document.documentElement.setAttribute(themeAttributeName, themeMode);
  }
};

const HotKey = () => {
  // 切换主题快捷键
  useHotkeys('ctrl+alt+shift+.', changeThemeMode);
  return <></>;
};

ReactDOM.render(<HotKey />, getOrCreateBodyContainer('hotkeys'));
