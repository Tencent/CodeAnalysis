import React, { useRef } from 'react';
import cn from 'classnames';
import { find } from 'lodash';
import { Avatar, Tag, Tooltip, Divider } from 'tdesign-react';
import { RootListIcon, TimeIcon } from 'tdesign-icons-react';
import { useHistory } from 'react-router-dom';

import { formatDate } from '@tencent/micro-frontend-shared/util';

import style from './style.scss';
import tagStyle from '../style.scss';

interface TemplateCardProps {
  templateInfo: any;
  languages: any[];
}

const formatLang = (langList: string[], allLangs: any[]) => {
  const ellipsis = langList?.length > 3;
  let subLangList = langList;
  let extraInfo = '';
  if (ellipsis) {
    subLangList = langList.slice(0, 3);
    extraInfo = ` ... 等 ${langList.length} 种`;
  }
  const langString = subLangList.map((item: any) => (find(allLangs, { name: item })
    ? find(allLangs, { name: item })?.display_name
    : item))
    .join('、');
  return `${langString}${extraInfo}`;
};

const isParagraphEllipsis = (htmlDom: HTMLElement) => (htmlDom && htmlDom.offsetWidth < htmlDom.scrollWidth);

const TemplateCard = ({ templateInfo, languages }: TemplateCardProps) => {
  const history = useHistory();
  const ellipsisRef = useRef<HTMLParagraphElement>(null);

  return (
    <div className={style.cardContainer} onClick={() => {
      history.push(`${window.location.pathname}/${templateInfo.id}`);
    }}>
      <div className={style.cardBody}>
        <div className={style.avatar}>
          <Avatar shape="round" size="52px" className={templateInfo.scheme_key === 'public' ? style.systemTmpl : style.customTmpl}>
            {templateInfo.name.slice(0, 1)}
          </Avatar>
        </div>
        <div className={style.title}>
          <h3>{templateInfo.name}</h3>
          <Tooltip content={isParagraphEllipsis(ellipsisRef.current) && templateInfo.description}>
            <p ref={ellipsisRef} className={style.description}>{templateInfo.description}</p>
          </Tooltip>
        </div>
        <div className={style.category}>
          <Tag
            className={cn(tagStyle.tmplTag, { [tagStyle.sys]: templateInfo.scheme_key === 'public' })}
          >
            {templateInfo.scheme_key === 'public' ? '系统模板' : '自定义模板'}
          </Tag>
        </div>
      </div>
      <div className={style.footer}>
        <div>
          <RootListIcon /> <span className='fs-12'>{formatLang(templateInfo?.languages, languages)}</span>
        </div>
        <Divider layout="vertical" />
        <div>
          <TimeIcon /> <span className='fs-12'>{formatDate(templateInfo?.modified_time)}</span>
        </div>
      </div>
    </div>
  );
};

export default React.memo(TemplateCard);
