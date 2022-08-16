import React, { useState } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
import Cookies from 'universal-cookie';

import Constant from '@src/constant';
import DevModal from './dev-modal';

const cookies = new Cookies();

const MAC_HOT_KEY = 'ctrl+command+shift+d';
const WIN_HOT_KEY = 'ctrl+alt+shift+d';

const DevUI = () => {
  const [visible, setVisible] = useState(false);
  useHotkeys(MAC_HOT_KEY, () => setVisible(true));
  useHotkeys(WIN_HOT_KEY, () => setVisible(true));
  useHotkeys('escape', () => setVisible(false));

  const onOK = (data: string) => {
    cookies.set(Constant.MICRO_FRONTEND_API_LIST, data, {
      path: '/',
      domain: window.location.hostname,
    });
    setVisible(false);
    location.reload();
  };

  return <DevModal visible={visible} onOk={onOK} onCancel={() => setVisible(false)} />;
};

export default DevUI;
