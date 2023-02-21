import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import ReactPiwik, { PiwikOptions } from 'react-piwik';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';
import { setUserInfoCustomVariable } from '@plat/util';

const getMatomoOptions = (): PiwikOptions => {
  const url = getMetaContent('MATOMO_URL');
  let siteId = parseInt(getMetaContent('MATOMO_SITE_ID'), 10);
  if (isNaN(siteId)) {
    siteId = 0;
  }
  return { url, siteId };
};

export const useInitMamoto = () => {
  const history = useHistory();

  useEffect(() => {
    let piwik: ReactPiwik = null;
    const { url, siteId } = getMatomoOptions();
    if (url && siteId) {
      // 初始化matomo
      piwik = new ReactPiwik({ url, siteId });
      piwik.connectToHistory(history);
    }

    return () => {
      if (piwik) {
        piwik.disconnectFromHistory();
        piwik = null;
      }
    };
  }, []);
};

export const setPvUserInfo = (userinfo: any) => {
  const { url, siteId } = getMatomoOptions();
  if (url && siteId) {
    setUserInfoCustomVariable(userinfo);
  }
};

export const setPvOrgInfo = (orginfo: any) => {
  const { url, siteId } = getMatomoOptions();
  if (url && siteId && orginfo) {
    ReactPiwik.push(['setCustomVariable', 2, '组织', `${orginfo.org_sid} - ${orginfo.name}`, 'visit']);
  }
};
