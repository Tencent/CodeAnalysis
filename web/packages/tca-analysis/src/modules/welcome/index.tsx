import React from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { Button } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
// 项目内
import repoLogo from '@src/images/repo.svg';
import { t } from '@src/i18n/i18next';
import { getReposRouter } from '@src/utils/getRoutePath';
import s from './style.scss';

const Welcome = () => {
  const history = useHistory();
  const { org_sid: orgSid, team_name: teamName }: any = useParams();

  return (
        <div className={s.welcomeContainer}>
            <div className={s.header}>
                <h2>{t('欢迎使用代码库登记')}</h2>
                <p className={s.desc}>
                    {t('登记仓库以便进行代码分析，支持')}
                    <strong> GIT、SVN </strong>
                    {t('代码库。支持可配置认证、选择成员等。')}
                </p>
            </div>
            <img src={repoLogo} width={168} height={128} alt={t('代码库登记')} />
            <div className={s.footer}>
                <Button
                    type="primary"
                    icon={<PlusIcon />}
                    onClick={() => history.push(`${getReposRouter(orgSid, teamName)}/create`)}
                >
                    {t('登记代码库')}
                </Button>
            </div>
        </div>
  );
};
export default Welcome;
