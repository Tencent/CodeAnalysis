// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支概览代码检查详情
 */
import React, { ReactNode } from 'react';
import { t } from '@src/utils/i18n';
import { Row, Col, Progress } from 'coding-oa-uikit';
// 项目内
import s from '../style.scss';
import { getMineFormatData } from '../utils';

interface IProps {
  mineData: any;
  latestLintData: any;
  briefCycData: any;
  briefDupData: any;
}

interface IMineColProps {
  title: string;
  formatData: any;
  children: ReactNode;
}

const MineCol = ({ title, formatData, children }: IMineColProps) => (
        <Col span={8}>
            <div className={s.coreItem}>
                <div className={s.tit}>{title}</div>
                <Progress
                    percent={formatData.progress}
                    size="small"
                    strokeColor="#0066ff"
                    trailColor="#b8c0cc"
                    format={() => `${formatData.count}/${formatData.total}`}
                />
                <div className=" text-grey-6 fs-12 mt-xs">{children}</div>
            </div>
        </Col>
);

const Mine = ({ mineData, latestLintData, briefCycData, briefDupData }: IProps) => {
  const formatLintData = getMineFormatData(mineData.lint_issue_num, latestLintData.total);
  const formatCycData = getMineFormatData(
    mineData.cyc_issue_num,
    briefCycData ? briefCycData.over_cc_func_count : '-',
  );
  const formatDupData = getMineFormatData(
    mineData.dup_issue_num,
    briefDupData ? briefDupData.duplicate_block_count : '-',
  );
  return (
        <div className={s.item}>
            <p className={s.header}>
                <span className={s.tit}>{t('与我相关')}</span>
            </p>
            <div className={s.content}>
                <Row gutter={20}>
                    <MineCol
                        title={t('代码检查')}
                        formatData={formatLintData}
                        children={`共${formatLintData.total}个未处理问题，其中存在${formatLintData.count}个与我相关`} // eslint-disable-line
                    />
                    <MineCol
                        title={t('圈复杂度')}
                        formatData={formatCycData}
                        children={`该分支共${formatCycData.total}个超标方法个数，其中存在${formatCycData.count}个与我相关`} // eslint-disable-line
                    />
                    <MineCol
                        title={t('重复代码')}
                        formatData={formatDupData}
                        children={`共${formatDupData.total}块重复代码，其中存在${formatDupData.count}个与我相关`} // eslint-disable-line
                    />
                </Row>
            </div>
        </div>
  );
};

export default Mine;
