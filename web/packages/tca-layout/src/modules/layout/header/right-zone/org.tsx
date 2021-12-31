import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import classnames from 'classnames';
import AngleRight from 'coding-oa-uikit/lib/icon/AngleRight';
import { Popover, Avatar, message } from 'coding-oa-uikit';
import { getTeamRouter } from '@src/utils/getRoutePath';
import { t } from '@src/i18n/i18next';
import { getTeams } from '@src/services/team';
import { STATUS_ENUM } from '@src/constants/org';
import s from './style.scss';

interface IProps {
  org: any;
}

const OrgUI = ({ org }: IProps) => {
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
    getTeams({ limit: 100 }).then((response) => {
      setOrgs(response.results.filter((item: any) => !(item.status > STATUS_ENUM.ACTIVE)));
    });
  }, []);

  return (
    <Popover
      placement="left"
      content={
        <div className={s.popoverBody}>
          <div className={s.title}>{t('切换团队')}</div>
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
      }
    >
      <div>
        <Avatar size={24} style={{ marginRight: 8 }}>
          {org.name}
        </Avatar>
        <span className={s.curOrg}>{org.name}</span>
        <span className={s.curLanguage}>
          <AngleRight />
        </span>
      </div>
    </Popover>
  );
};

export default OrgUI;
