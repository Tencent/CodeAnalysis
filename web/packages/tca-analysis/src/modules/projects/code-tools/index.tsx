// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 扩展功能
 */

import React, { useState, useEffect } from 'react';
// import { Link } from 'react-router-dom';
import cn from 'classnames';
// import { get } from 'lodash';

// import { Typography } from 'coding-oa-uikit';

import { getCodeTools } from '@src/services/projects';
// import { getProjectRouter } from '@src/utils/getRoutePath';

// import { TOOLS_STATUS } from '../constants';

import style from './style.scss';

interface CodeToolsProps {
  projectId: number;
  repoId: number;
}


const CodeTools = (props: CodeToolsProps) => {
  // const [list, setList] = useState([]) as any;
  const [setList] = useState([]) as any;
  const { repoId, projectId } = props;

  useEffect(() => {
    (async () => {
      const res = await getCodeTools(repoId, projectId, {
        limit: 12,
        offset: 0,
      });

      setList(res.results || []);
    })();
  }, []);


  return (
        <div className={cn(style.codeTools, style.toolCommon)}>
            {/* {
                list.map((item: any) => (
                    <Link
                        key={item.id}
                        className={style.tool}
                        to={`${getProjectRouter(repoId, projectId)}/code-tools/${get(item, 'checktool.name')}/scans`}
                    >
                        <div className={style.avatar}>{get(item, 'checktool.display_name[0]')}</div>
                        <div className={style.content}>
                            <div className={style.main}>
                                <div>
                                    <p className={style.title}>{get(item, 'checktool.display_name')}</p>
                                </div>
                                <span className={cn(style.toolStatus, style[`status${get(item, 'checktool.status')}`])}>
                                    {TOOLS_STATUS[get(item, 'checktool.status')]}
                                </span>
                            </div>
                            <Typography.Paragraph ellipsis={{ rows: 3 }} className={style.desc}>
                                {get(item, 'checktool.description')}
                            </Typography.Paragraph>
                        </div>
                    </Link>
                ))
            } */}
        </div>
  );
};


export default CodeTools;
