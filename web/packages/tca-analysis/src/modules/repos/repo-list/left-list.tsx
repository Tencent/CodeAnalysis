// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { Link, useParams, useHistory } from 'react-router-dom';
import classnames from 'classnames';
import { toNumber } from 'lodash';

import { Col, Input, Tag, Tooltip } from 'coding-oa-uikit';
import SearchIcon from 'coding-oa-uikit/lib/icon/Search';
import QuestionCircleIcon from 'coding-oa-uikit/lib/icon/QuestionCircle';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import GitBranchIcon from 'coding-oa-uikit/lib/icon/GitBranch';
import partnerIcon from '@src/images/partner.svg';
// 项目内
import { t } from '@src/i18n/i18next';
import { getReposRouter } from '@src/utils/getRoutePath';
// 模块内
import s from './style.scss';
import { getRepoRouter } from '../routes';

interface IProps {
  repos: Array<any>;
}

const LeftList = ({ repos }: IProps) => {
  const [searchValue, setSearchValue] = useState('');
  const params: any = useParams();
  const { org_sid: orgSid, team_name: teamName }: any = params;
  const repoId = toNumber(params.repoId);
  const history = useHistory();

  // 模糊匹配
  const searchRepos = repos.filter(item => item.scm_url.indexOf(searchValue) > -1
            || (item.name && item.name.indexOf(searchValue) > -1));

  return (
        <Col flex="300px" className={classnames(s.leftContainer)}>
            <div className={s.header}>
                <span className=" text-weight-medium fs-18">{t('仓库登记')}</span>
                <span>
                    <Tooltip
                        placement="rightBottom"
                        title={
                            <div className="" style={{ width: '500px' }}>
                                {t('登记代码库是使用代码分析的前置步骤。建议您录入仓库权限高（如Owner、Master）的凭据完成登记。此外还可以控制用户权限等。')}
                            </div>
                        }
                    >
                        <QuestionCircleIcon className={s.icon} />
                    </Tooltip>
                </span>
                <Link
                    className={s.iconPlusButton}
                    to={`${getReposRouter(orgSid, teamName)}/create`}
                >
                    <PlusIcon className={s.iconPlus} />
                </Link>
                <Input
                    className=" mt-20"
                    onChange={e => setSearchValue(e.target.value)}
                    value={searchValue}
                    placeholder={t('搜索代码库')}
                    suffix={<SearchIcon />}
                />
            </div>
            <div className={s.content}>
                {searchRepos.length === 0 && (
                    <div className=" px-20 py-12 fs-12 text-grey-6 text-center">
                        {t('未匹配到任何代码仓库')}
                    </div>
                )}
                {searchRepos.map(item => (
                        <div
                            key={item.id}
                            className={classnames(s.listItem, repoId === item.id && s.active)}
                            onClick={() => repoId !== item.id
                                && history.push(getRepoRouter(orgSid, teamName, item.id))
                            }
                            title={item.scm_url}
                        >
                            {/* <Tooltip
                                title={
                                    <>
                                        <div className=" text-weight-medium mb-sm">{item.name}</div>
                                        <div className=" fs-12">{item.scm_url}</div>
                                    </>
                                }
                            ></Tooltip> */}
                            <div className={s.itemBody}>
                                <div className=" ellipsis text-weight-medium">
                                    {item.name}
                                    {item.symbol === 1 && (
                                        <Tooltip title="腾讯 ISV 合作伙伴">
                                            <img className={s.partnerIcon} src={partnerIcon} />
                                        </Tooltip>
                                    )}
                                </div>
                                <div className=" text-grey-6 fs-12 mt-xs overflow-hidden">
                                    <span>
                                        <GitBranchIcon /> {item.branch_count} 个分支
                                    </span>
                                    {/* 暂时隐藏 */}
                                    {false && (
                                        <Tag
                                            className=" float-right"
                                            color="rgba(158, 84, 10, 0.08)"
                                            style={{ color: 'rgb(160, 119, 8)' }}
                                        >
                                            {t('审核中')}
                                        </Tag>
                                    )}
                                </div>
                            </div>
                        </div>
                ))}
            </div>
        </Col>
  );
};
export default LeftList;
