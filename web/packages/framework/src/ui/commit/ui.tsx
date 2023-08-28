import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import { message } from 'tdesign-react';

import MicroApplication from '@src/meta/application';
import s from './style.scss';

export interface CommitUIProps {
  title: string;
  production: MicroApplication[];
  development: MicroApplication[];
  mode?: string;
  onExit: () => any;
  noExit?: boolean;
}

const CommitUI = ({
  title = '测试',
  development,
  production,
  onExit,
  noExit = false,
  mode = '',
}: CommitUIProps) => {
  const [hide, setHide] = useState(true);
  const prod = production.map(p => p.props).map(({ commitId }) => commitId);
  useEffect(() => {
    message.info(`已开启 ${mode}`);
  }, [mode]);
  return (
    <div
      className={s.buffetContainer}
      onMouseEnter={() => setHide(false)}
      onMouseLeave={() => setHide(true)}
    >
      {hide && <div className={s.dot} />}
      {!hide && (
        <div className={s.content}>
          <div className={s.header}>
            <span className={s.label}>{mode}</span>
            <span className={s.label}>
              <span className={cn(s.icon, s.current)} />
              {title}版本
            </span>
            <span className={s.label}>
              <span className={s.icon} />
              线上版本
            </span>
            {!noExit && (
              <span className={s.clean} onClick={onExit}>
                退出{title}
              </span>
            )}
          </div>
          {development.map((
            { props: { description, commitId, changeAt } }: MicroApplication,
            i: number,
          ) => (
            <div className={s.product} key={i}>
              <div className={s.version}>
                <span
                  className={cn(s.icon, {
                    [s.current]: prod.indexOf(commitId) < 0,
                  })}
                />
              </div>
              <div className={s.name}>{description}</div>
              <div className={s.commit}>{commitId}</div>
              <div className={s.time}>{changeAt}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CommitUI;
