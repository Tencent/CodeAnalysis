import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import classnames from 'classnames';
import { Popover, Avatar, message } from 'coding-oa-uikit';
import AngleRight from 'coding-oa-uikit/lib/icon/AngleRight';

// 项目内
import { getTeams } from '@src/services/team';
import { OrgStatusEnum } from '@src/constant/org';
import { getTeamRouter } from '@src/utils/getRoutePath';
import s from './style.scss';

interface IProps {
  name: string
}

const OrgUI = ({ name }: IProps) => {
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
    getTeams({ limit: 100 }).then(({ results }) => {
      setOrgs((results as any[]).filter((item: any) => !(item.status > OrgStatusEnum.ACTIVE)));
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
          {name[0].toUpperCase()}
        </Avatar>
        <span className={s.curOrg}>{name}</span>
        <span className={s.curLanguage}>
          <AngleRight />
        </span>
      </div>
    </Popover>
  );
};

export default OrgUI;
