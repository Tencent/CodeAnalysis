import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import classnames from 'classnames';
import { message, Popup } from 'tdesign-react';
import { ChevronLeftIcon } from 'tdesign-icons-react';

// 项目内
import { getTeams } from '@src/services/team';
import { OrgStatusEnum } from '@src/constant/org';
import { getTeamRouter } from '@src/utils/getRoutePath';
import s from '../style.scss';

const Org = () => {
  const [orgs, setOrgs] = useState<Array<any>>([]);
  const history = useHistory();

  const onChange = (item: any) => {
    message.loading(t('团队切换中...'), 0.3);
    const timer = setTimeout(() => {
      clearTimeout(timer);
      history.push(`${getTeamRouter(item.org_sid)}/workspace`);
    }, 300);
  };

  useEffect(() => {
    getTeams({ limit: 100 }).then(({ results }: any) => {
      setOrgs((results as any[]).filter((item: any) => !(item.status > OrgStatusEnum.ACTIVE)));
    });
  }, []);

  return (
    <Popup trigger="hover" showArrow
      placement="left"
      content={
        <div className={s.headerDropdownPopover}>
          <div className={s.title}>{t('切换团队')}</div>
          <div className={s.content}>
            {orgs.map((item: any) => (
              <div
                onClick={() => onChange(item)}
                className={classnames(s.item, s.orgTextEllipsis)}
                key={item.org_sid}
              >
                {item.name}
              </div>
            ))}
          </div>
        </div>
      }
    >
      <div className={s.headerDropItem}>
        <ChevronLeftIcon className={s.icon} />
        <span>切换团队</span>
      </div>
    </Popup>
  );
};

export default Org;
